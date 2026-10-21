"""
score_probe.py — In smoke_score từng frame để xác nhận bộ lọc chuyển động
=========================================================================

Chạy trên đoạn TĨNH (không có khói/lửa):
  python score_probe.py --source clean_clip.mp4 --label STATIC

Chạy trên đoạn CÓ KHÓI:
  python score_probe.py --source smoke_clip.mp4 --label SMOKE

  Nếu bộ lọc hoạt động đúng:
    STATIC → score ≈ 0.000 (gần như toàn bộ frame)
    SMOKE  → score ≈ 0.35–0.55 (tùy cường độ chuyển động)

Script mô phỏng toàn bộ ROI = toàn khung hình (không cần YOLO),
vì mục đích chỉ là kiểm tra MotionAnalyzer độc lập.
Truyền --bbox để giới hạn vùng nếu muốn.

Ví dụ với bbox cố định:
  python score_probe.py --source smoke.mp4 --bbox 100 80 400 300
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

# Thêm thư mục cha vào path để import pipeline
sys.path.insert(0, str(Path(__file__).parent))
from pipeline import MotionAnalyzer


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Kiểm tra smoke_score trên video")
    p.add_argument("--source", required=True, help="Đường dẫn video hoặc 0 cho webcam")
    p.add_argument("--label",  default="VIDEO",
                   help="Nhãn hiển thị trong output (STATIC / SMOKE / ...)")
    p.add_argument("--bbox",   nargs=4, type=int, default=None,
                   metavar=("X1","Y1","X2","Y2"),
                   help="Bounding box cố định (mặc định: toàn khung hình)")
    p.add_argument("--max_frames", type=int, default=300,
                   help="Số frame tối đa để phân tích (default: 300)")
    p.add_argument("--show",   action="store_true",
                   help="Hiển thị video khi chạy (cần GUI)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[ERROR] Không mở được: {source}")
        sys.exit(1)

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_f   = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"\n{'═'*62}")
    print(f"  SMOKE SCORE PROBE  [{args.label}]")
    print(f"{'─'*62}")
    print(f"  Source    : {source}")
    print(f"  FPS       : {video_fps:.1f}   Frames: {total_f if total_f>0 else '?'}")
    print(f"  Max frames: {args.max_frames}")
    print(f"{'─'*62}")
    print(f"  {'Frame':>6}  {'BBox':^22}  {'Score':>6}  Verdict")
    print(f"{'─'*62}")

    analyzer = MotionAnalyzer(debug=False)  # debug=False: không in từng pixel
    scores: list[float] = []
    frame_idx = 0

    try:
        while frame_idx < args.max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            H, W = frame.shape[:2]

            # Xác định bbox
            if args.bbox:
                x1, y1, x2, y2 = args.bbox
            else:
                x1, y1, x2, y2 = 0, 0, W, H  # toàn khung hình

            bbox = (x1, y1, x2, y2)

            # Tính score
            analyzer.update(frame)
            score = analyzer.smoke_score(bbox)

            if frame_idx > 0:  # frame 0 chưa có flow → bỏ qua
                scores.append(score)
                verdict = "PASS" if score >= 0.35 else "block"
                print(
                    f"  {frame_idx:>6}  "
                    f"({x1},{y1})-({x2},{y2})  "
                    f"{score:>6.3f}  {verdict}"
                )

            if args.show:
                bar_w = int(W * min(score, 1.0))
                cv2.rectangle(frame, (0, H-20), (W, H), (20,20,20), -1)
                cv2.rectangle(frame, (0, H-20), (bar_w, H), (40,90,160), -1)
                cv2.putText(frame, f"smoke_score: {score:.3f}  [{args.label}]",
                            (8, H-5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220,220,220), 1)
                cv2.imshow("Score Probe", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_idx += 1

    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        cap.release()
        if args.show:
            cv2.destroyAllWindows()

    # ── Thống kê ──────────────────────────────────────────────────────────
    if not scores:
        print("[WARNING] Không đủ frame để thống kê.")
        return

    arr = np.array(scores)
    n_pass  = int((arr >= 0.35).sum())
    n_block = len(arr) - n_pass

    print(f"{'═'*62}")
    print(f"  TỔNG KẾT  [{args.label}]  ({len(arr)} frame phân tích)")
    print(f"{'─'*62}")
    print(f"  mean score  : {arr.mean():.4f}")
    print(f"  median      : {float(np.median(arr)):.4f}")
    print(f"  min / max   : {arr.min():.4f} / {arr.max():.4f}")
    print(f"  std         : {arr.std():.4f}")
    print(f"{'─'*62}")
    print(f"  score >= 0.35 (PASS)  : {n_pass:>4} frame  ({100*n_pass/len(arr):.1f}%)")
    print(f"  score <  0.35 (block) : {n_block:>4} frame  ({100*n_block/len(arr):.1f}%)")
    print(f"{'═'*62}\n")

    # ── Verdict ───────────────────────────────────────────────────────────
    pass_rate = n_pass / len(arr)
    if args.label.upper() == "STATIC":
        if pass_rate < 0.05:
            print("  ✅  Bộ lọc hoạt động đúng: cảnh tĩnh gần như không qua ngưỡng.")
        elif pass_rate < 0.20:
            print("  ⚠️   Bộ lọc tương đối ổn: một số frame tĩnh vẫn qua (có thể do rung camera nhẹ).")
        else:
            print("  ❌  Bộ lọc vẫn để lọt cảnh tĩnh. Cân nhắc tăng _MOV_THR hoặc _MIN_MOVING_FRAC.")
    else:
        if pass_rate > 0.50:
            print("  ✅  Bộ lọc nhận diện được chuyển động khói (>50% frame qua ngưỡng).")
        elif pass_rate > 0.20:
            print("  ⚠️   Bộ lọc nhận một phần. Có thể cần giảm smoke_motion_threshold.")
        else:
            print("  ❌  Bộ lọc chặn khói thật. Giảm smoke_motion_threshold hoặc _MOV_THR.")


if __name__ == "__main__":
    main()
