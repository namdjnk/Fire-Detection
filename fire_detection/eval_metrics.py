"""
eval_metrics.py — Đo YOLO metrics + bảng ablation cho báo cáo
=============================================================

Chạy:
  # Bước 1: đo P/R/mAP50 trên tập test
  python eval_metrics.py --mode yolo --data <path/to/data.yaml>

  # Bước 2: xây bảng ablation (cần đã có file log từ --eval)
  python eval_metrics.py --mode ablation \\
      --log_yolo_only     logs/yolo_only.txt \\
      --log_yolo_nm       logs/yolo_nm.txt \\
      --log_yolo_nm_flow  logs/yolo_nm_flow.txt

Yêu cầu:
  - ultralytics >= 8.4.0
  - Chạy từ thư mục fire_detection/ (hoặc truyền --weights / --data đúng đường dẫn)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ══════════════════════════════════════════════════════════════════════════════
# YOLO VALIDATION — P / R / mAP50 per class
# ══════════════════════════════════════════════════════════════════════════════

def run_yolo_val(weights: str, data: str, imgsz: int, conf: float | None, device: str) -> None:
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics chưa được cài. Chạy: pip install ultralytics")
        sys.exit(1)

    weights_path = Path(weights)
    if not weights_path.exists():
        print(f"[ERROR] Weights không tìm thấy: {weights_path.resolve()}")
        print("  Đảm bảo chạy script từ thư mục fire_detection/, hoặc truyền đường dẫn đầy đủ.")
        sys.exit(1)

    data_path = Path(data)
    if not data_path.exists():
        print(f"[ERROR] data.yaml không tìm thấy: {data_path.resolve()}")
        sys.exit(1)

    print(f"\n{'═'*60}")
    print(f"  YOLO VALIDATION")
    print(f"{'═'*60}")
    print(f"  Weights : {weights_path.resolve()}")
    print(f"  Data    : {data_path.resolve()}")
    print(f"  imgsz   : {imgsz}")
    print(f"  conf    : {conf}")
    print(f"  device  : {device}")
    print(f"{'═'*60}\n")

    model = YOLO(str(weights_path))

    # Kiểm tra imgsz train từ model metadata (nếu có)
    if hasattr(model, "model") and hasattr(model.model, "args"):
        train_imgsz = getattr(model.model.args, "imgsz", None)
        if train_imgsz and int(train_imgsz) != imgsz:
            print(
                f"[WARNING] imgsz truyền vào ({imgsz}) != imgsz lúc train ({train_imgsz}). "
                f"Kết quả có thể lệch. Nên dùng --imgsz {train_imgsz}."
            )

    # The official test call does not override conf. Keep the library's
    # validation default; the application's video threshold is a separate setting.
    options = {} if conf is None else {"conf": conf}
    results = model.val(
        data=str(data_path),
        imgsz=imgsz,
        device=device,
        verbose=True,
        split="test",   # dùng tập test, không phải val
        plots=True,
        project=str(PROJECT_ROOT / "DATA/results/test_evaluation"),
        name="test",
        **options,
    )

    # ── In bảng per-class ──────────────────────────────────────────────────
    names   = results.names          # {0: 'fire', 1: 'smoke', ...}
    box     = results.box            # metrics object

    # Per-class P, R, mAP50
    p_list     = box.p.tolist()       # [P_class0, P_class1, ...]
    r_list     = box.r.tolist()
    ap50_list  = box.ap50.tolist()

    print(f"\n{'═'*60}")
    print(f"  PER-CLASS METRICS  (split=test, conf={conf}, imgsz={imgsz})")
    print(f"{'─'*60}")
    print(f"  {'Class':<12}  {'P':>7}  {'R':>7}  {'mAP50':>7}")
    print(f"{'─'*60}")

    for cls_id, name in names.items():
        if cls_id < len(p_list):
            print(
                f"  {name:<12}  "
                f"{p_list[cls_id]:>7.4f}  "
                f"{r_list[cls_id]:>7.4f}  "
                f"{ap50_list[cls_id]:>7.4f}"
            )

    # Overall (mean)
    print(f"{'─'*60}")
    print(
        f"  {'mean (all)':<12}  "
        f"{box.mp:>7.4f}  "
        f"{box.mr:>7.4f}  "
        f"{box.map50:>7.4f}"
    )
    print(f"{'═'*60}\n")

    # ── Ghi ra file để dùng trong báo cáo ─────────────────────────────────
    out_file = Path(results.save_dir) / "yolo_metrics.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"weights={weights_path.resolve()}\n")
        f.write(f"data={data_path.resolve()}\n")
        f.write(f"imgsz={imgsz}  conf={conf}\n\n")
        f.write(f"{'Class':<12}  {'P':>7}  {'R':>7}  {'mAP50':>7}\n")
        f.write("-"*40 + "\n")
        for cls_id, name in names.items():
            if cls_id < len(p_list):
                f.write(
                    f"{name:<12}  "
                    f"{p_list[cls_id]:>7.4f}  "
                    f"{r_list[cls_id]:>7.4f}  "
                    f"{ap50_list[cls_id]:>7.4f}\n"
                )
        f.write("-"*40 + "\n")
        f.write(f"{'mean':<12}  {box.mp:>7.4f}  {box.mr:>7.4f}  {box.map50:>7.4f}\n")
        f.write(f"mAP50-95 (all)={box.map:.4f}\n")

    print(f"  [Saved] {out_file.resolve()}")


# ══════════════════════════════════════════════════════════════════════════════
# ABLATION TABLE — đọc từ log --eval
# ══════════════════════════════════════════════════════════════════════════════

def _parse_eval_log(log_path: str) -> dict:
    """Read clean-video reports, keeping messages distinct from merged events.

    Legacy reports have message rates, not event rates. Never present those
    legacy rates as event metrics when the event count is unavailable.
    """
    result = dict.fromkeys(("duration", "fa_min", "fa_hour", "total_alerts", "events"), "N/A")
    path = Path(log_path)
    if not path.exists():
        print(f"[WARNING] Log không tìm thấy: {path}. Dùng N/A.")
        return result

    text = path.read_text(encoding="utf-8", errors="ignore")
    event_rate = False
    for line in text.splitlines():
        line = line.strip()
        if "Duration" in line and "frames" in line:
            # "Duration  : 300.0s  (9000 frames @ 30.0 fps)"
            try:
                dur_part = line.split(":")[1].strip()
                dur_s = float(dur_part.split("s")[0].strip())
                result["duration"] = f"{dur_s:g}s"
            except Exception:
                result["duration"] = "?"
        if re.match(r"(?:Repeated alert messages|Total alerts|TOTAL false alarms)\s*:", line):
            try:
                result["total_alerts"] = line.split(":")[-1].strip()
            except Exception:
                result["total_alerts"] = "?"
        if re.match(r"False alarm events\s*:", line):
            result["events"] = line.split(":", 1)[1].strip()
        if "/ min" in line and "False event rate" in line:
            event_rate = True
            try:
                result["fa_min"] = line.split(":")[-1].replace("/ min", "").strip()
            except Exception:
                result["fa_min"] = "?"
        if "/ hour" in line and event_rate:
            try:
                result["fa_hour"] = line.split(":")[-1].replace("/ hour", "").strip()
            except Exception:
                result["fa_hour"] = "?"

    return result


def print_ablation_table(
    log_yolo_only: str,
    log_yolo_nm: str,
    log_yolo_nm_flow: str,
) -> None:
    """
    In bảng ablation 3 dòng:
      Hàng 1 — YOLO đơn thuần    (không có N/M, không có optical flow)
      Hàng 2 — YOLO + N/M        (confirmation window, không có optical flow)
      Hàng 3 — YOLO + N/M + Flow (bản đầy đủ)

    Để có log "YOLO đơn thuần", cần chạy với config tạm:
      confirmation.window_size=1
      confirmation.fire_threshold=1, confirmation.smoke_threshold=1
      smoke_motion_threshold=0.0  (tức là luôn pass)
    rồi redirect stdout ra file log.

    Cả ba lần chạy phải dùng cùng video, weight, conf, tiền xử lý, cooldown
    và quy tắc gộp sự kiện. Chỉ dùng --eval với video đã xác nhận là sạch.
    Bảng trong báo cáo hiện dùng compare_saved_runs.py trên cùng log khung
    hình; không cần chạy lại YOLO để tái lập bảng đó.
    """

    rows = [
        ("YOLO only",         log_yolo_only),
        ("YOLO + N/M",        log_yolo_nm),
        ("YOLO + N/M + Flow", log_yolo_nm_flow),
    ]

    print(f"\n{'═'*72}")
    print(f"  ABLATION TABLE — False Alarm Rate on Clean Video (sự kiện/giờ)")
    print(f"{'─'*72}")
    print(f"  {'System':<22}  {'Duration':>10}  {'Messages':>9}  {'Events':>7}  {'Evt/min':>8}  {'Evt/hour':>8}")
    print(f"{'─'*72}")

    for label, log_path in rows:
        d = _parse_eval_log(log_path)
        print(
            f"  {label:<22}  "
            f"{d['duration']:>10}  "
            f"{d['total_alerts']:>9}  "
            f"{d['events']:>7}  "
            f"{d['fa_min']:>8}  "
            f"{d['fa_hour']:>8}"
        )

    print(f"{'═'*72}")
    print()
    print("  Lưu ý:")
    print("  • FA/hour ở đây đo trên video sạch (không có cháy) = false alarm rate.")
    print("  • Cần đo thêm recall/độ trễ trên video có cháy thật để hoàn chỉnh.")
    print("  • Clip ngắn chỉ cho biết quan sát trên clip đó; cần thêm video sạch dài và đa dạng.")
    print("  • Log cũ thiếu số sự kiện được ghi N/A; không đổi số lần báo thành số sự kiện.")
    print()

    # Ghi ra file
    out_file = PROJECT_ROOT / "DATA/results/evaluation_tools/ablation_table.txt"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("ABLATION TABLE\n")
        f.write(f"{'System':<22}  {'Duration':>10}  {'Messages':>9}  {'Events':>7}  {'Evt/min':>8}  {'Evt/hour':>8}\n")
        f.write("-"*60 + "\n")
        for label, log_path in rows:
            d = _parse_eval_log(log_path)
            f.write(
                f"{label:<22}  "
                f"{d['duration']:>10}  "
                f"{d['total_alerts']:>9}  "
                f"{d['events']:>7}  "
                f"{d['fa_min']:>8}  "
                f"{d['fa_hour']:>8}\n"
            )
    print(f"  [Saved] {out_file.resolve()}\n")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="eval_metrics.py — YOLO metrics + ablation table",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--mode", choices=["yolo", "ablation"], required=True,
                   help="yolo: đo P/R/mAP50 | ablation: in bảng từ log")

    # YOLO mode
    p.add_argument("--weights",  default=str(PROJECT_ROOT / "Models/fire_smoke_v2_best.pt"),
                   help="Đường dẫn weights (.pt)")
    p.add_argument("--data",     default=None,
                   help="Đường dẫn data.yaml của dataset (bắt buộc cho mode=yolo)")
    p.add_argument("--imgsz",   type=int, default=640)
    p.add_argument("--conf", type=float, default=None,
                   help="Mặc định không ghi đè ngưỡng đánh giá của Ultralytics, như lời gọi test chính thức; khác ngưỡng video 0.25")
    p.add_argument("--device",  default="auto")

    # Ablation mode
    p.add_argument("--log_yolo_only",    default="logs/yolo_only.txt")
    p.add_argument("--log_yolo_nm",      default="logs/yolo_nm.txt")
    p.add_argument("--log_yolo_nm_flow", default="logs/yolo_nm_flow.txt")

    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "yolo":
        if args.data is None:
            print("[ERROR] --data bắt buộc cho mode=yolo")
            print("  Ví dụ: python eval_metrics.py --mode yolo --data ../../datasets/fire/Fire_and_Smoke/data.yaml")
            sys.exit(1)

        device = ("cuda" if __import__("torch").cuda.is_available() else "cpu") \
                 if args.device == "auto" else args.device

        run_yolo_val(
            weights=args.weights,
            data=args.data,
            imgsz=args.imgsz,
            conf=args.conf,
            device=device,
        )

    elif args.mode == "ablation":
        print_ablation_table(
            log_yolo_only=args.log_yolo_only,
            log_yolo_nm=args.log_yolo_nm,
            log_yolo_nm_flow=args.log_yolo_nm_flow,
        )


if __name__ == "__main__":
    main()
