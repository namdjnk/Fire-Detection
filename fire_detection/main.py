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
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Keep runtime files beside the project on E:, including when launched elsewhere.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _key, _folder in {"YOLO_CONFIG_DIR": "ultralytics", "MPLCONFIGDIR": "matplotlib",
                      "TEMP": "tmp", "TMP": "tmp"}.items():
    _cache = PROJECT_ROOT / ".cache" / _folder
    _cache.mkdir(parents=True, exist_ok=True)
    os.environ[_key] = str(_cache)

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
    p.add_argument("--config",     default=str(Path(__file__).with_name("config.yaml")),
                   help="Path to config.yaml (default: beside main.py)")
    p.add_argument("--model",      default=None,
                   help="Override model weights path from config")
    p.add_argument("--eval",       action="store_true",
                   help="Evaluation mode: measure false alarms on a clean video")
    p.add_argument("--show_flow",  action="store_true",
                   help="Overlay optical-flow arrows for smoke debug")
    p.add_argument("--no_display", action="store_true",
                   help="Disable OpenCV window (useful for headless / eval)")
    p.add_argument("--output_dir", default=None, help="Directory for this run's results")
    p.add_argument("--save_video", action="store_true", help="Save annotated MP4 without audio")
    p.add_argument("--max_side", type=int, default=0,
                   help="Resize before processing; longest side in pixels (0 = original)")
    return p.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

def load_config(path: str) -> dict:
    cfg_path = Path(path).resolve()
    if not cfg_path.exists():
        print(f"[ERROR] Config file not found: {cfg_path.resolve()}")
        sys.exit(1)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for mapping, key in [(cfg["model"], "weights"), (cfg, "output_dir")]:
        value = Path(mapping[key])
        if not value.is_absolute():
            mapping[key] = str((cfg_path.parent / value).resolve())
    return cfg


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

    far_min  = event_counter.events / max(dur_s / 60,   1e-9)
    far_hour = event_counter.events / max(dur_s / 3600, 1e-9)

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
    print(f"  Repeated alert messages : {total_a}")
    print(f"  False alarm events      : {event_counter.events}")
    print(f"  Event merge gap         : {event_counter.gap_s:.1f}s")
    print()
    print(f"  False event rate        : {far_min:.4f} / min")
    print(f"                          : {far_hour:.2f} / hour")
    print("═" * 58)
    print()

    # ── Advice ────────────────────────────────────────────────────────────────
    if total_a == 0:
        print("  No false alerts observed in this clip; longer clean videos are needed.")
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
    if args.max_side < 0 or args.max_side == 1:
        raise ValueError("--max_side must be 0 or at least 2")

    # ── Config ────────────────────────────────────────────────────────────────
    cfg = load_config(args.config)
    if args.model:
        cfg["model"]["weights"] = args.model
    if args.show_flow:
        cfg["show_optical_flow"] = True
    run_dir = (Path(args.output_dir).resolve() if args.output_dir else
               Path(cfg["output_dir"]) / f"{Path(args.source).stem}_{datetime.now():%Y%m%d_%H%M%S_%f}")
    run_dir.mkdir(parents=True, exist_ok=True)
    if (run_dir / "frames.jsonl").exists():
        raise FileExistsError(f"Run already exists; choose a new --output_dir: {run_dir}")
    cfg["output_dir"] = str(run_dir)

    # ── Source ────────────────────────────────────────────────────────────────
    source = int(args.source) if args.source.isdigit() else args.source
    cap    = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {args.source}")
        sys.exit(1)

    total_f   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    source_size = [int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]

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
    event_counter = EventCounter()
    writer = None
    processed_size = None
    alert_times = []
    frame_log = (run_dir / "frames.jsonl").open("w", encoding="utf-8")
    reached_eof = False

    # ── Loop ──────────────────────────────────────────────────────────────────
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                reached_eof = True
                break

            h, w = frame.shape[:2]
            if args.max_side and max(h, w) > args.max_side:
                scale = args.max_side / max(h, w)
                frame = cv2.resize(frame, (max(2, int(w * scale) // 2 * 2),
                                          max(2, int(h * scale) // 2 * 2)), interpolation=cv2.INTER_AREA)
            processed_size = [frame.shape[1], frame.shape[0]]

            # Đọc TRƯỚC khi process() để phát hiện alert mới trong frame này
            prev_counts = {kind: pipeline.stats[f"{kind}_alerts"] for kind in ("fire", "smoke")}

            vis = pipeline.process(frame)

            # Nếu alert tăng lên → ghi nhận sự kiện FA
            ts_s = (pipeline.stats["total"] - 1) / video_fps
            for kind, previous in prev_counts.items():
                if pipeline.stats[f"{kind}_alerts"] > previous:
                    event_counter.record(ts_s)
                    alert_times.append(dict(type=kind, video_time_s=ts_s))
            frame_log.write(json.dumps(dict(frame=pipeline.stats["total"] - 1,
                                            time_s=ts_s, **pipeline.last_frame)) + "\n")
            if args.save_video:
                if writer is None:
                    writer = cv2.VideoWriter(str(run_dir / "annotated.mp4"),
                                             cv2.VideoWriter_fourcc(*"mp4v"), video_fps,
                                             (vis.shape[1], vis.shape[0]))
                    if not writer.isOpened():
                        raise RuntimeError("Cannot create annotated.mp4")
                writer.write(vis)
            if pipeline.stats["total"] % 100 == 0:
                print(f"[Progress] {pipeline.stats['total']}/{total_f}", flush=True)

            if show_gui:
                cv2.imshow(win_name, vis)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    print("Quit.")
                    break

                elif key == ord("s"):
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fn = run_dir / f"screenshot_{ts}.jpg"
                    cv2.imwrite(str(fn), vis)
                    print(f"[Screenshot] {fn}")

                elif key == ord("f"):
                    pipeline.show_flow = not pipeline.show_flow
                    state = "ON" if pipeline.show_flow else "OFF"
                    print(f"[Optical Flow] {state}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        cap.release()
        frame_log.close()
        if writer is not None:
            writer.release()
        if show_gui:
            cv2.destroyAllWindows()

    # ── Summary ───────────────────────────────────────────────────────────────
    pipeline.print_stats()
    summary = dict(source=args.source, config=cfg, names=pipeline.yolo.names,
                   source_fps=video_fps, expected_frames=total_f, stats=pipeline.stats,
                   processed_duration_s=pipeline.stats["total"] / video_fps,
                   all_frames_processed=reached_eof and total_f > 0 and pipeline.stats["total"] == total_f,
                   source_size=source_size, processed_size=processed_size,
                   max_side=args.max_side, clean_video_eval=args.eval,
                   event_merge_gap_s=event_counter.gap_s, alert_events=event_counter.events,
                   alerts=alert_times)
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Results] {run_dir}")

    if args.eval:
        print_eval_report(pipeline, args.source, video_fps, event_counter)


if __name__ == "__main__":
    main()
