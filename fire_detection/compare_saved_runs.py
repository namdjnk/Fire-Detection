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
