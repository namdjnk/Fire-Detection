# Bản sao code hiện tại

Ngày chụp nội dung: 28/10/2026. Nội dung mỗi file được giữ nguyên trong khối mã. Đây là tài liệu để đọc code; chạy chương trình bằng các file nguồn gốc. Weight `.pt`, môi trường Python và dữ liệu/video không được chuyển thành văn bản.

## fire_detection/compare_saved_runs.py

Nguồn: `fire_detection/compare_saved_runs.py`

```python
"""Compare postprocessing decisions using the SAME saved frame observations.

This does not rerun YOLO, measure inference speed, or compute detection accuracy.
Full-mode replay must reproduce every saved confirmation and alert exactly.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


MODES = {"yolo": "YOLO", "nm": "YOLO + N/M", "flow": "YOLO + N/M + optical flow"}


def replay(rows, summary, mode):
    cfg = summary["config"]
    settings = cfg["confirmation"]
    fire_window = deque(maxlen=settings["window_size"])
    smoke_window = deque(maxlen=settings["window_size"])
    cooldown = 0
    alerts = []
    counts = dict(fire=0, smoke=0)
    for row in rows:
        motion_pass = bool(row["smoke_raw"] and any(
            score >= cfg["smoke_motion_threshold"] for score in row["smoke_motion_scores"]))
        assert motion_pass == row["smoke_motion_pass"]
        fire_window.append(int(row["fire_raw"]))
        smoke_window.append(int(motion_pass if mode == "flow" else row["smoke_raw"]))
        fire = row["fire_raw"] if mode == "yolo" else sum(fire_window) >= settings["fire_threshold"]
        smoke = row["smoke_raw"] if mode == "yolo" else sum(smoke_window) >= settings["smoke_threshold"]
        if mode == "flow":
            assert fire == row["fire_confirmed"] and smoke == row["smoke_confirmed"]
        counts["fire"] += int(fire)
        counts["smoke"] += int(smoke)
        # Match pipeline: fire priority, shared cooldown, tick after processing.
        if cooldown == 0 and (fire or smoke):
            alerts.append(dict(type="fire" if fire else "smoke", video_time_s=row["time_s"]))
            cooldown = cfg["cooldown_frames"]
        cooldown = max(0, cooldown - 1)
    events = sum(i == 0 or alert["video_time_s"] - alerts[i - 1]["video_time_s"]
                 > summary["event_merge_gap_s"] for i, alert in enumerate(alerts))
    if mode == "flow":
        assert alerts == summary["alerts"], "Replay does not match original alerts"
        assert events == summary["alert_events"]
        for kind in counts:
            assert counts[kind] == summary["stats"][f"{kind}_confirmed_frames"]
            assert sum(a["type"] == kind for a in alerts) == summary["stats"][f"{kind}_alerts"]
    return dict(confirmed_frames=counts, alert_events=events, alert_messages=len(alerts),
                first_alert_s=alerts[0]["video_time_s"] if alerts else None, alerts=alerts)


def main():
    project = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=project / "DATA/results/main_v2_conf025_side640")
    args = parser.parse_args()
    root = args.runs.resolve()
    clips = {}
    common = None
    for name in ("video_chay", "video_khoi", "video_khong_chay", "video_khong_chay2"):
        folder = root / name
        summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
        payload = (folder / "frames.jsonl").read_bytes()
        rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
        assert summary["all_frames_processed"]
        assert len(rows) == summary["stats"]["total"] == summary["expected_frames"]
        assert all(row["frame"] == i and abs(row["time_s"] - i / summary["source_fps"]) < 1e-6
                   for i, row in enumerate(rows))
        cfg = summary["config"]
        signature = {key: cfg[key] for key in ("model", "confirmation", "smoke_motion_threshold", "cooldown_frames")}
        signature.update(max_side=summary["max_side"], event_merge_gap_s=summary["event_merge_gap_s"])
        if common is None:
            common = signature
        assert signature == common, "Input settings differ between clips"
        clips[name] = dict(source=summary["source"], frame_count=len(rows),
                           duration_s=summary["processed_duration_s"], clean=summary["clean_video_eval"],
                           observations_sha256=hashlib.sha256(payload).hexdigest(),
                           modes={mode: replay(rows, summary, mode) for mode in MODES})
    result = dict(method="Replay postprocessing on saved observations; full mode verified against original logs",
                  settings=common, clips=clips)
    output = root / "ablation_saved_observations"
    output.mkdir(exist_ok=True)
    (output / "comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# So sánh trên bốn video demo", "",
             "## Phương pháp", "",
             "Tính lại quyết định từ kết quả từng khung hình đã lưu của cùng một lần chạy YOLO. "
             "Không chạy lại suy luận. Cả ba cách dùng cùng weight, ngưỡng conf=0,25, imgsz=640; "
             "ảnh được thu nhỏ cạnh dài còn 640 pixel trước xử lý. "
             "N/M: lửa 10/20, khói 12/20; ngưỡng chuyển động 0,35. "
             "Mỗi clip bắt đầu với trạng thái rỗng. Cùng dùng thời gian chờ 90 khung hình và ưu tiên cảnh báo lửa. "
             "Gộp các lần báo cách nhau không quá 60 giây thành một sự kiện, riêng từng clip.", "",
             "Đã đối chiếu: cách đầy đủ tái tạo đúng từng quyết định xác nhận, thời điểm và loại cảnh báo "
             "trong nhật ký gốc của cả bốn video.", "",
             "## Bảng ngắn để trình bày", "",
             "| Cách xử lý | Khung hình xác nhận lửa / 643 (video lửa) | Khung hình xác nhận khói / 534 (video khói) | Sự kiện cảnh báo trên hai video sạch |",
             "|---|---:|---:|---:|"]
    for mode, label in MODES.items():
        fire = clips["video_chay"]["modes"][mode]["confirmed_frames"]["fire"]
        smoke = clips["video_khoi"]["modes"][mode]["confirmed_frames"]["smoke"]
        false_events = sum(c["modes"][mode]["alert_events"] for c in clips.values() if c["clean"])
        lines.append(f"| {label} | {fire} | {smoke} | {false_events} |")
    lines += ["", "Với YOLO đơn thuần, cột xác nhận chính là khung hình có phát hiện. "
              "Đây là số khung hình kích hoạt điều kiện, không phải precision, recall hay mAP. "
              "N/M có thể duy trì xác nhận khi khung hình hiện tại không có phát hiện, nên số này có thể tăng.",
              "", "## Chi tiết cảnh báo", "",
              "| Video | Thời lượng (giây) | Cách xử lý | Sự kiện | Số lần báo | Lần báo đầu từ đầu clip (giây) |",
              "|---|---:|---|---:|---:|---:|"]
    for name, clip in clips.items():
        for mode, label in MODES.items():
            item = clip["modes"][mode]
            first = "—" if item["first_alert_s"] is None else f"{item['first_alert_s']:.3f}"
            lines.append(f"| {name} | {clip['duration_s']:.2f} | {label} | {item['alert_events']} | {item['alert_messages']} | {first} |")
    clean_seconds = sum(c["duration_s"] for c in clips.values() if c["clean"])
    lines += ["", "## Cách diễn giải và giới hạn", "",
              f"- Hai video sạch có tổng thời lượng {clean_seconds:.2f} giây. Cả ba cách đều không có cảnh báo trên các clip này.",
              "- Cả ba cách đều tạo cảnh báo lửa trên video lửa và cảnh báo khói trên video khói. "
              "Số sự kiện phụ thuộc quy tắc gộp, không phải số sự kiện thực tế được gán nhãn.",
              "- Bộ lọc chuyển động làm giảm rõ số khung hình xác nhận khói trong clip khói. "
              "Bộ video này chưa chứng minh bộ lọc giảm báo nhầm so với YOLO.",
              "- Chưa có nhãn đúng/sai cho từng khung hình hoặc mốc bắt đầu sự kiện. "
              "Không gọi số khung hình xác nhận là độ chính xác hoặc recall; "
              "mốc báo đầu tính từ đầu clip không phải độ trễ so với lúc bắt đầu cháy.",
              "- Không đo hoặc so sánh FPS, tốc độ suy luận trong phép tính lại này.",
              "- Không thay đổi cấu hình chương trình hoặc weight sau phép so sánh.",
              "", "## Gợi ý trình bày ngắn", "",
              "Chiếu một đoạn video lửa, một đoạn video khói, rồi nêu kết quả hai video sạch. "
              "Dùng bảng ba dòng để giải thích tác động của N/M và optical flow. "
              "Kết luận giới hạn trong bốn video demo; không khẳng định optical flow tốt hơn khi số liệu chưa chứng minh.", ""]
    (output / "KET_QUA_SO_SANH.md").write_text("\n".join(lines), encoding="utf-8")
    print(output / "KET_QUA_SO_SANH.md")
    print("PASS: all full-mode confirmations and alerts reproduced for all four videos")


if __name__ == "__main__":
    main()
```

## fire_detection/config.yaml

Nguồn: `fire_detection/config.yaml`

```yaml
# ══════════════════════════════════════════════════════════════════════════════
# config.yaml — Fire & Smoke Alert System
# ══════════════════════════════════════════════════════════════════════════════
# Chỉnh file này để thay đổi tham số mà không cần sửa code.
# ══════════════════════════════════════════════════════════════════════════════


# ── Model ─────────────────────────────────────────────────────────────────────
model:
  weights: ../Models/fire_smoke_v2_best.pt   # tương đối từ thư mục chứa config
  imgsz:   640                      # input size: 416 (nhanh) hoặc 640 (chính xác hơn)
  conf:    0.25                     # ngưỡng thử nghiệm với weight mới


# ── Device ────────────────────────────────────────────────────────────────────
device: auto          # auto | cuda | cpu


# ── N/M Sliding Window Confirmation ──────────────────────────────────────────
#
#   Xác nhận sự kiện chỉ khi phát hiện trong N/M frame gần nhất.
#   Ví dụ: fire_threshold=10, window_size=20 → cần 10/20 frame = 50%
#
confirmation:
  window_size:      20   # M — độ dài cửa sổ trượt (số frame nhìn lại)
  fire_threshold:   10   # N fire  — 10/20 = 50%  (nhạy hơn, lửa cần phát hiện nhanh)
  smoke_threshold:  12   # N smoke — 12/20 = 60%  (chặt hơn, khói nhiều false positive)


# ── Smoke Motion — Optical Flow ────────────────────────────────────────────────
#
#   Khói phải có đặc điểm chuyển động mới được xác nhận:
#     - Magnitude cao (chuyển động nhiều)
#     - Entropy hướng cao (turbulent, không phải vật thể cứng)
#     - Drift lên trên (fy < 0 trong ảnh)
#
#   Score = 0.35 × magnitude + 0.45 × direction_entropy + 0.20 × upward_drift
#
smoke_motion_threshold: 0.35    # 0.0–1.0  |  tăng = chặt hơn, ít false alarm
show_optical_flow: false        # true = hiển thị mũi tên flow (debug)


# ── Alert System ──────────────────────────────────────────────────────────────
cooldown_frames: 90    # ~3s @ 30fps — khoảng cách tối thiểu giữa 2 alert

output_dir: ../DATA/results/main_pipeline    # tương đối từ thư mục chứa config


# ── Ghi chú tuning ────────────────────────────────────────────────────────────
#
#   Nếu false alarm quá nhiều (đo bằng --eval):
#     1. Tăng confirmation.fire_threshold  lên 13-15
#     2. Tăng confirmation.smoke_threshold lên 15-17
#     3. Tăng model.conf                   lên 0.50-0.55
#     4. Tăng smoke_motion_threshold        lên 0.45-0.55
#
#   Nếu bỏ sót cháy thật:
#     1. Giảm confirmation.fire_threshold  xuống 7-8
#     2. Giảm model.conf                   xuống 0.30-0.35
#     3. Giảm smoke_motion_threshold        xuống 0.25
#
```

## fire_detection/eval_metrics.py

Nguồn: `fire_detection/eval_metrics.py`

```python
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
```

## fire_detection/main.py

Nguồn: `fire_detection/main.py`

```python
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
```

## fire_detection/pipeline.py

Nguồn: `fire_detection/pipeline.py`

```python
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
```

## fire_detection/requirements.txt

Nguồn: `fire_detection/requirements.txt`

```text
# Core
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0

# YOLO (fire/smoke detection)
ultralytics>=8.4.0

# Computer Vision
opencv-python>=4.8.0

# Config
pyyaml>=6.0
```

## fire_detection/score_probe.py

Nguồn: `fire_detection/score_probe.py`

```python
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
```
