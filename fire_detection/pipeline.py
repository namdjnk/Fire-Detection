"""
pipeline.py — Fire & Smoke Detection Pipeline
==============================================
Components
----------
  MotionAnalyzer        : Dense optical flow (Farneback) — smoke motion scoring
  SlidingWindowConfirm  : N/M frame confirmation window
  AlertSystem           : Local alert image and structured log
  FireSmokePipeline     : Orchestrates all components per frame
"""
from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import torch


# ══════════════════════════════════════════════════════════════════════════════
# 1. MOTION ANALYZER  —  Optical Flow for Smoke Verification
# ══════════════════════════════════════════════════════════════════════════════

class MotionAnalyzer:
    """
    Dense optical flow using Farneback algorithm.

    Smoke motion signature
    ─────────────────────
      • High flow magnitude      — active, turbulent movement
      • High direction entropy   — random angles (not rigid-body translation)
      • Upward drift component   — hot gases rise (fy < 0 in image coords)

    Score = 0.35 × mag_score + 0.45 × entropy + 0.20 × upward_score  ∈ [0, 1]

    v2 fix: entropy và upward chỉ tính trên pixel thực sự chuyển động
    (mag > _MOV_THR). Trả 0.0 nếu tỉ lệ pixel chuyển động < _MIN_MOVING_FRAC.
    Histogram entropy được trọng số theo magnitude để cảnh tĩnh có nhiễu
    nhỏ không tạo ra entropy cao giả.
    """

    _FB_PARAMS = dict(
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0,
    )

    # Pixel có mag nhỏ hơn ngưỡng này coi là đứng yên
    _MOV_THR: float = 0.3
    # Cần ít nhất 10% pixel ROI chuyển động, nếu không trả 0.0
    _MIN_MOVING_FRAC: float = 0.10

    def __init__(self, debug: bool = False):
        self._prev_gray: np.ndarray | None = None
        self._flow: np.ndarray | None = None  # (H, W, 2) — updated each frame
        self.debug = debug  # nếu True, in score từng lần gọi smoke_score

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, frame: np.ndarray) -> None:
        """Compute dense optical flow for the full frame. Call once per frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._prev_gray is not None:
            self._flow = cv2.calcOpticalFlowFarneback(
                self._prev_gray, gray, None, **self._FB_PARAMS
            )
        else:
            self._flow = None
        self._prev_gray = gray

    def smoke_score(self, bbox: tuple[int, int, int, int]) -> float:
        """
        Return smoke-motion score [0.0, 1.0] for a detection bounding box.

        Returns:
          0.5  — optical flow not yet available (first frame)
          0.0  — ROI gần như tĩnh (< _MIN_MOVING_FRAC pixel chuyển động)
          score — tính từ mag / entropy / upward CHỈ trên pixel chuyển động
        """
        if self._flow is None:
            return 0.5

        H, W = self._flow.shape[:2]
        x1, y1, x2, y2 = bbox
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(W - 1, x2), min(H - 1, y2)

        if x2 <= x1 or y2 <= y1:
            return 0.5

        roi = self._flow[y1:y2, x1:x2]          # (h, w, 2)
        fx_all = roi[..., 0].ravel()
        fy_all = roi[..., 1].ravel()

        # ── Magnitude (tính trên toàn ROI để có mag_score) ────────────────
        mag_all = np.sqrt(fx_all ** 2 + fy_all ** 2)
        mean_mag = float(np.mean(mag_all))
        mag_score = min(mean_mag / 4.0, 1.0)    # saturate at 4 px/frame

        # ── Lọc pixel chuyển động ─────────────────────────────────────────
        moving_mask = mag_all > self._MOV_THR
        moving_frac = float(moving_mask.mean())

        if moving_frac < self._MIN_MOVING_FRAC:
            # ROI gần như tĩnh — không có tín hiệu khói
            if self.debug:
                print(
                    f"[MotionAnalyzer] bbox={bbox}  "
                    f"moving_frac={moving_frac:.3f} < {self._MIN_MOVING_FRAC}  "
                    f"→ score=0.000"
                )
            return 0.0

        fx_mov = fx_all[moving_mask]
        fy_mov = fy_all[moving_mask]
        mag_mov = mag_all[moving_mask]

        # ── Direction Entropy — trọng số theo magnitude ───────────────────
        # Dùng mag làm weight: pixel chuyển động nhẹ đóng góp ít hơn
        angles = np.arctan2(fy_mov, fx_mov)
        hist, _ = np.histogram(
            angles,
            bins=8,
            range=(-np.pi, np.pi),
            weights=mag_mov,              # trọng số theo độ lớn
        )
        hist = hist.astype(float) / (hist.sum() + 1e-8)
        entropy = -float(np.sum(hist * np.log(hist + 1e-9))) / np.log(8)  # 0–1

        # ── Upward Drift — chỉ trên pixel chuyển động ────────────────────
        # fy < 0 = chuyển động lên (trục y ảnh hướng xuống)
        mean_fy_mov = float(np.mean(fy_mov))
        mean_mag_mov = float(np.mean(mag_mov))
        upward = float(np.clip(-mean_fy_mov / (mean_mag_mov + 1e-6), 0.0, 1.0))

        score = float(np.clip(
            0.35 * mag_score + 0.45 * entropy + 0.20 * upward,
            0.0, 1.0
        ))

        if self.debug:
            print(
                f"[MotionAnalyzer] bbox={bbox}  "
                f"moving={moving_frac:.2%}  "
                f"mag={mag_score:.3f}  ent={entropy:.3f}  up={upward:.3f}  "
                f"→ score={score:.3f}"
            )

        return score

    def draw_flow(self, frame: np.ndarray, step: int = 16, scale: float = 3.0) -> np.ndarray:
        """Overlay sparse optical flow arrows for visual debugging."""
        if self._flow is None:
            return frame
        H, W = frame.shape[:2]
        vis = frame.copy()
        for y in range(0, H, step):
            for x in range(0, W, step):
                dx, dy = self._flow[y, x]
                if np.sqrt(dx ** 2 + dy ** 2) < 0.5:
                    continue
                pt2 = (int(x + dx * scale), int(y + dy * scale))
                cv2.arrowedLine(vis, (x, y), pt2, (0, 200, 200), 1, tipLength=0.4)
        return vis


# ══════════════════════════════════════════════════════════════════════════════
# 2. SLIDING WINDOW CONFIRMATION  —  N / M Frame Logic
# ══════════════════════════════════════════════════════════════════════════════

class SlidingWindowConfirm:
    """
    Confirms a sustained event: fires only when the event is detected in
    at least N of the last M frames.

    Advantages over N-consecutive:
      • Handles brief single-frame misses without resetting the counter
      • More robust on flickering detections
    """

    def __init__(self, window_size: int = 20, threshold: int = 10):
        self.M = window_size
        self.N = threshold
        self._buf: deque[int] = deque(maxlen=window_size)

    def update(self, detected: bool) -> bool:
        """Push new observation. Returns True when confirmed."""
        self._buf.append(1 if detected else 0)
        return sum(self._buf) >= self.N

    @property
    def ratio(self) -> float:
        """Detection ratio in current window [0, 1]."""
        return sum(self._buf) / len(self._buf) if self._buf else 0.0

    def reset(self) -> None:
        self._buf.clear()


# ══════════════════════════════════════════════════════════════════════════════
# 3. ALERT SYSTEM  —  Image Save · Structured Log
# ══════════════════════════════════════════════════════════════════════════════

class AlertSystem:
    """
    Manages the full alert lifecycle:
      1. Save alert image  (with drawn timestamp)
      2. Write log entry   (Python logging → file + console)

    Cooldown prevents repeated alerts for the same event.
    """

    def __init__(
        self,
        save_dir: str = "outputs",
        cooldown_frames: int = 90,
    ):
        self._img_dir = Path(save_dir) / "images"
        self._img_dir.mkdir(parents=True, exist_ok=True)

        self._cooldown_total = cooldown_frames

        self._cooldown: int = 0
        self._global_frame: int = 0
        self._counts = {"fire": 0, "smoke": 0}

        # ── Logger setup ──────────────────────────────────────────────────
        log_path = Path(save_dir) / "alerts.log"
        self._log = logging.getLogger("FireSmoke")
        self._log.setLevel(logging.DEBUG)
        if not self._log.handlers:
            fmt = logging.Formatter(
                "%(asctime)s  %(levelname)-8s  %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh = logging.FileHandler(str(log_path), encoding="utf-8")
            fh.setFormatter(fmt)
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            self._log.addHandler(fh)
            self._log.addHandler(sh)

        self._log.info("Alert system initialised  save_dir=%s", Path(save_dir).resolve())

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def in_cooldown(self) -> bool:
        return self._cooldown > 0

    def trigger(
        self,
        alert_type: str,
        frame: np.ndarray,
        detections: list[dict],
        conf_score: float,
    ) -> bool:
        """
        Fire an alert. Returns True if alert was accepted (not in cooldown).
        frame : annotated frame (with bounding boxes already drawn)
        """
        if self.in_cooldown:
            return False

        ts = datetime.now()
        ts_file = ts.strftime("%Y%m%d_%H%M%S")
        ts_display = ts.strftime("%Y-%m-%d %H:%M:%S")

        # ── Save image ────────────────────────────────────────────────────
        fname = f"alert_{alert_type}_{ts_file}_f{self._global_frame:06d}.jpg"
        fpath = self._img_dir / fname
        stamped = frame.copy()
        cv2.putText(
            stamped, ts_display,
            (10, stamped.shape[0] - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
        )
        cv2.imwrite(str(fpath), stamped)

        # ── Log ───────────────────────────────────────────────────────────
        det_str = ", ".join(f"{d['label']}@{d['conf']:.2f}" for d in detections)
        self._log.warning(
            "ALERT  type=%-5s  score=%.2f  frame=%d  dets=[%s]  file=%s",
            alert_type.upper(), conf_score, self._global_frame, det_str, fname,
        )

        # ── State ─────────────────────────────────────────────────────────
        self._cooldown = self._cooldown_total
        self._counts[alert_type] += 1
        return True

    def tick(self) -> None:
        """Advance the cooldown timer by one processed frame."""
        self._global_frame += 1
        if self._cooldown > 0:
            self._cooldown -= 1

    @property
    def counts(self) -> dict:
        return dict(self._counts)

# ══════════════════════════════════════════════════════════════════════════════
# 4. FIRE-SMOKE PIPELINE  —  Orchestrator
# ══════════════════════════════════════════════════════════════════════════════

class FireSmokePipeline:
    """
    Per-frame orchestrator.

    Processing order
    ────────────────
      1  YOLO detection  → raw fire / smoke boxes
      2  Optical flow    → smoke motion score
      3  N/M windows     → sustained confirmation
      4  Render          → annotated frame with bboxes
      5  Alert           → save · log (if confirmed & not in cooldown)
    """

    def __init__(self, cfg: dict):
        from ultralytics import YOLO

        # ── Device ───────────────────────────────────────────────────────
        dev = cfg.get("device", "auto")
        self.device = ("cuda" if torch.cuda.is_available() else "cpu") if dev == "auto" else dev

        # ── YOLO ─────────────────────────────────────────────────────────
        weights = cfg["model"]["weights"]
        print(f"[Pipeline] Loading model : {weights}")
        print(f"[Pipeline] Device        : {self.device}")
        self.yolo       = YOLO(weights)
        self.conf_thr   = float(cfg["model"].get("conf",  0.40))
        self.imgsz      = int(cfg["model"].get("imgsz", 640))

        # ── Confirmation windows ─────────────────────────────────────────
        M       = cfg["confirmation"]["window_size"]
        N_fire  = cfg["confirmation"]["fire_threshold"]
        N_smoke = cfg["confirmation"]["smoke_threshold"]
        self._fire_win  = SlidingWindowConfirm(M, N_fire)
        self._smoke_win = SlidingWindowConfirm(M, N_smoke)

        # ── Motion ───────────────────────────────────────────────────────
        self._motion           = MotionAnalyzer()
        self._smoke_motion_thr = float(cfg.get("smoke_motion_threshold", 0.35))
        self.show_flow         = bool(cfg.get("show_optical_flow", False))

        # ── Alert ────────────────────────────────────────────────────────
        self._alert = AlertSystem(
            save_dir=cfg.get("output_dir", "outputs"),
            cooldown_frames=int(cfg.get("cooldown_frames", 90)),
        )

        # ── Runtime stats ─────────────────────────────────────────────────
        self.stats = dict(total=0, fire_raw=0, smoke_raw=0,
                          fire_alerts=0, smoke_alerts=0, smoke_motion_pass=0,
                          fire_confirmed_frames=0, smoke_confirmed_frames=0)
        self.last_frame = {}

        print("[Pipeline] Ready.\n")

    # ── Main entry ────────────────────────────────────────────────────────────

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        Process one frame. Return boxes with only FIRE/SMOKE labels.
        """
        self.stats["total"] += 1

        # ── 1. YOLO ──────────────────────────────────────────────────────
        res = self.yolo(
            frame,
            imgsz=self.imgsz,
            conf=self.conf_thr,
            device=self.device,
            verbose=False,
        )[0]

        fire_dets, smoke_dets = [], []
        if res.boxes is not None:
            for box in res.boxes:
                lbl  = res.names[int(box.cls[0])]
                conf = float(box.conf[0])
                bbox = tuple(map(int, box.xyxy[0]))
                d = dict(label=lbl, conf=conf, bbox=bbox)
                if lbl == "fire":
                    fire_dets.append(d)
                elif lbl == "smoke":
                    smoke_dets.append(d)

        if fire_dets:
            self.stats["fire_raw"] += 1
        if smoke_dets:
            self.stats["smoke_raw"] += 1

        # ── 2. Optical flow ───────────────────────────────────────────────
        self._motion.update(frame)
        smoke_motion = [self._motion.smoke_score(d["bbox"]) for d in smoke_dets]
        verified_smoke = bool(
            smoke_dets and any(s >= self._smoke_motion_thr for s in smoke_motion)
        )

        # ── 3. N/M Confirmation ───────────────────────────────────────────
        fire_confirmed  = self._fire_win.update(bool(fire_dets))
        smoke_confirmed = self._smoke_win.update(verified_smoke)
        fire_ratio  = self._fire_win.ratio
        smoke_ratio = self._smoke_win.ratio
        self.stats["smoke_motion_pass"] += int(verified_smoke)
        self.stats["fire_confirmed_frames"] += int(fire_confirmed)
        self.stats["smoke_confirmed_frames"] += int(smoke_confirmed)
        self.last_frame = dict(
            fire_raw=bool(fire_dets), smoke_raw=bool(smoke_dets),
            smoke_motion_scores=smoke_motion, smoke_motion_pass=verified_smoke,
            fire_confirmed=fire_confirmed, smoke_confirmed=smoke_confirmed,
            fire_ratio=fire_ratio, smoke_ratio=smoke_ratio,
        )

        # ── 4. Render bounding boxes ──────────────────────────────────────
        vis = frame.copy()
        if self.show_flow:
            vis = self._motion.draw_flow(vis)

        for d in fire_dets:
            x1, y1, x2, y2 = d["bbox"]
            cv2.rectangle(vis, (x1, y1), (x2, y2), (15, 30, 200), 2)

        if fire_dets:
            x1, y1, _, _ = max(fire_dets, key=lambda d: d["conf"])["bbox"]
            cv2.putText(
                vis, "FIRE",
                (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (15, 30, 200), 2,
            )

        for d in smoke_dets:
            x1, y1, x2, y2 = d["bbox"]
            color = (40, 160, 40)
            cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)

        if smoke_dets:
            x1, y1, _, _ = max(smoke_dets, key=lambda d: d["conf"])["bbox"]
            cv2.putText(
                vis, "SMOKE",
                (x1, max(y1 - 8, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2,
            )

        # ── 5. Alert ──────────────────────────────────────────────────────
        all_dets = fire_dets + smoke_dets
        if fire_confirmed and not self._alert.in_cooldown:
            if self._alert.trigger("fire", vis, all_dets, fire_ratio):
                self.stats["fire_alerts"] += 1
        elif smoke_confirmed and not self._alert.in_cooldown:
            if self._alert.trigger("smoke", vis, smoke_dets, smoke_ratio):
                self.stats["smoke_alerts"] += 1

        self._alert.tick()
        return vis

    # ── Stats ─────────────────────────────────────────────────────────────────

    def print_stats(self) -> None:
        T      = self.stats["total"]
        fire_a = self.stats["fire_alerts"]
        smk_a  = self.stats["smoke_alerts"]
        total  = fire_a + smk_a

        print("\n" + "═" * 56)
        print("  📊  PIPELINE STATISTICS")
        print("═" * 56)
        print(f"  Total frames processed    : {T}")
        print(f"  Fire  raw detections      : {self.stats['fire_raw']:>5}  ({100*self.stats['fire_raw']/max(T,1):.1f}%)")
        print(f"  Smoke raw detections      : {self.stats['smoke_raw']:>5}  ({100*self.stats['smoke_raw']/max(T,1):.1f}%)")
        print(f"  Fire  alerts triggered    : {fire_a}")
        print(f"  Smoke alerts triggered    : {smk_a}")
        print(f"  Total alerts              : {total}")
        print(f"  Smoke frames passing flow : {self.stats['smoke_motion_pass']}")
        print(f"  Fire confirmed frames     : {self.stats['fire_confirmed_frames']}")
        print(f"  Smoke confirmed frames    : {self.stats['smoke_confirmed_frames']}")
        print("═" * 56 + "\n")
