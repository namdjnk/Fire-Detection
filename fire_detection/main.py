"""
main.py — Fire & Smoke Detection System
========================================
Entry point: CLI argument parsing, video capture loop, evaluation report.

Usage
-----
  python main.py --source 0                        # webcam
  python main.py --source video.mp4                # video file
  python main.py --source clean.mp4 --eval         # false-alarm evaluation
  python main.py --source video.mp4 --show_flow    # debug optical flow
  python main.py --source video.mp4 --no_display   # headless (server / eval)

Keyboard shortcuts (when window is open)
-----------------------------------------
  Q  — Quit
  S  — Save screenshot
  F  — Toggle optical-flow overlay
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import cv2
import yaml

from pipeline import FireSmokePipeline


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="🔥 Fire & Smoke Alert System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--source",     default="0",
                   help="Video source: 0 = webcam, or path to video file")
    p.add_argument("--config",     default="config.yaml",
                   help="Path to config.yaml  (default: config.yaml)")
    p.add_argument("--model",      default=None,
                   help="Override model weights path from config")
    p.add_argument("--eval",       action="store_true",
                   help="Evaluation mode: measure false alarms on a clean video")
    p.add_argument("--show_flow",  action="store_true",
                   help="Overlay optical-flow arrows for smoke debug")
    p.add_argument("--no_display", action="store_true",
                   help="Disable OpenCV window (useful for headless / eval)")
    return p.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

def load_config(path: str) -> dict:
    cfg_path = Path(path)
    if not cfg_path.exists():
        print(f"[ERROR] Config file not found: {cfg_path.resolve()}")
        sys.exit(1)
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ══════════════════════════════════════════════════════════════════════════════
# EVENT COUNTER  —  Gom alert liên tiếp thành sự kiện
# ══════════════════════════════════════════════════════════════════════════════

class EventCounter:
    """
    Gom các alert liên tiếp vào cùng một sự kiện nếu cách nhau < gap_s giây.
    Giúp --eval đếm sự kiện (incident) thay vì số lần báo.
    Ví dụ: một cảnh nhầm kéo dài 5 phút chỉ bị đếm là 1 sự kiện, không phải ~5 alert.
    """

    def __init__(self, gap_s: float = 60.0):
        """gap_s: khoảng cách tối thiểu giữa 2 sự kiện riêng (giây)."""
        self.gap_s        = gap_s
        self._last: float | None = None
        self.events: int  = 0
        self.total_alerts: int = 0

    def record(self, timestamp_s: float) -> None:
        """Ghi nhận một alert tại timestamp_s."""
        self.total_alerts += 1
        if self._last is None or (timestamp_s - self._last) > self.gap_s:
            self.events += 1
        self._last = timestamp_s


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATION REPORT
# ══════════════════════════════════════════════════════════════════════════════

def print_eval_report(
    pipeline: FireSmokePipeline,
    source: str,
    video_fps: float,
    event_counter: EventCounter,
) -> None:
    s       = pipeline.stats
    T       = s["total"]
    fire_a  = s["fire_alerts"]
    smk_a   = s["smoke_alerts"]
    total_a = fire_a + smk_a
    dur_s   = T / max(video_fps, 1.0)

    far_min  = total_a / max(dur_s / 60,   1e-9)
    far_hour = total_a / max(dur_s / 3600, 1e-9)

    print("\n" + "═" * 58)
    print("  🎯  FALSE ALARM EVALUATION REPORT")
    print("═" * 58)
    print(f"  Source                  : {source}")
    print(f"  Duration                : {dur_s:.1f}s  ({T} frames @ {video_fps:.1f} fps)")
    print()
    print(f"  Raw fire  frames        : {s['fire_raw']:>5}  ({100*s['fire_raw']/max(T,1):.2f}%)")
    print(f"  Raw smoke frames        : {s['smoke_raw']:>5}  ({100*s['smoke_raw']/max(T,1):.2f}%)")
    print()
    print(f"  Fire  alerts triggered  : {fire_a}")
    print(f"  Smoke alerts triggered  : {smk_a}")
    print(f"  TOTAL false alarms      : {total_a}")
    print()
    print(f"  False alarm rate        : {far_min:.4f} / min")
    print(f"                          : {far_hour:.2f} / hour")
    print("═" * 58)
    print()

    # ── Advice ────────────────────────────────────────────────────────────────
    if total_a == 0:
        print("  ✅  Zero false alarms — excellent specificity!")
    elif far_min < 0.10:
        print("  ✅  Low false alarm rate — good specificity.")
    elif far_min < 0.50:
        print("  ⚠️   Moderate false alarms. Consider:")
        print("       • Increase confirmation thresholds  (fire_threshold / smoke_threshold)")
        print("       • Raise model confidence            (model.conf: 0.50+)")
        print("       • Raise smoke motion threshold      (smoke_motion_threshold: 0.45+)")
    else:
        print("  ❌  High false alarm rate. Recommended changes to config.yaml:")
        print("       • confirmation.fire_threshold  → increase (e.g. 14)")
        print("       • confirmation.smoke_threshold → increase (e.g. 16)")
        print("       • model.conf                   → increase (e.g. 0.55)")
        print("       • smoke_motion_threshold        → increase (e.g. 0.50)")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    args = parse_args()

    # ── Config ────────────────────────────────────────────────────────────────
    cfg = load_config(args.config)
    if args.model:
        cfg["model"]["weights"] = args.model
    if args.show_flow:
        cfg["show_optical_flow"] = True

    # ── Source ────────────────────────────────────────────────────────────────
    source = int(args.source) if args.source.isdigit() else args.source
    cap    = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {args.source}")
        sys.exit(1)

    total_f   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    print(f"[Source]  {args.source}")
    print(f"          frames={total_f if total_f > 0 else '?'}  fps={video_fps:.1f}")

    if args.eval:
        print("\n" + "─" * 58)
        print("  EVALUATION MODE")
        print("  ⚠  Provide a video that does NOT contain fire or smoke.")
        print("     All triggered alerts will be counted as false alarms.")
        print("─" * 58 + "\n")

    # ── Pipeline ──────────────────────────────────────────────────────────────
    pipeline   = FireSmokePipeline(cfg)
    show_gui   = not args.no_display
    win_name   = "Fire & Smoke Monitor"

    # ── Loop ──────────────────────────────────────────────────────────────────
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Đọc TRƯỚC khi process() để phát hiện alert mới trong frame này
            if args.eval:
                prev_total = (
                    pipeline.stats["fire_alerts"] + pipeline.stats["smoke_alerts"]
                )

            vis = pipeline.process(frame)

            # Nếu alert tăng lên → ghi nhận sự kiện FA
            if args.eval:
                new_total = (
                    pipeline.stats["fire_alerts"] + pipeline.stats["smoke_alerts"]
                )
                if new_total > prev_total:
                    ts_s = pipeline.stats["total"] / max(video_fps, 1.0)
                    event_counter.record(ts_s)

            if show_gui:
                cv2.imshow(win_name, vis)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    print("Quit.")
                    break

                elif key == ord("s"):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fn = f"screenshot_{ts}.jpg"
                    cv2.imwrite(fn, vis)
                    print(f"[Screenshot] {fn}")

                elif key == ord("f"):
                    pipeline.show_flow = not pipeline.show_flow
                    state = "ON" if pipeline.show_flow else "OFF"
                    print(f"[Optical Flow] {state}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        cap.release()
        cv2.destroyAllWindows()

    # ── Summary ───────────────────────────────────────────────────────────────
    pipeline.print_stats()

    if args.eval:
        print_eval_report(pipeline, args.source, video_fps, event_counter)


if __name__ == "__main__":
    main()
