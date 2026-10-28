# Dữ liệu và bằng chứng cho báo cáo

Các liên kết dưới đây trỏ đến file gốc trong cùng kho. Các con số được phân loại theo nguồn để lần đọc sau không nhầm việc đọc tài liệu với việc chạy lại thí nghiệm.

## Mô hình và huấn luyện

| Nội dung | Nguồn |
|---|---|
| Weight dùng cho ứng dụng | [fire_smoke_v2_best.pt](../../Models/fire_smoke_v2_best.pt) |
| Weight tốt nhất của lần train | [best.pt](../../DATA/training/train_official_v2/fire_smoke_runs/train_official_v2/weights/best.pt) — cùng SHA-256 với weight ứng dụng |
| 100 epoch, batch 16, imgsz 640, fraction 1 | [args.yaml](../../DATA/training/train_official_v2/fire_smoke_runs/train_official_v2/args.yaml) |
| Loss và chỉ số từng epoch | [results.csv](../../DATA/training/train_official_v2/fire_smoke_runs/train_official_v2/results.csv) — chỉ số validation, không phải kết quả test |
| Dữ liệu, nhãn 0 smoke và 1 fire | [fire_smoke_data.yaml](../../DATA/training/train_official_v2/fire_smoke_data.yaml) |
| Cấu hình chương trình | [config.yaml](../../fire_detection/config.yaml) |

Bộ ảnh nguồn được tài liệu ghi là Kaggle `sayedgamal99/Smoke-Fire-Detection-YOLO`. Toàn bộ ảnh/nhãn train/test và notebook train chính thức không có trong thư mục hiện hành để đưa lên Git. Không suy ra rằng clone kho đã có đủ dữ liệu để train lại. Không dùng notebook đề tài cũ trong lịch sử Git thay cho nguồn của lần train này.

## Đánh giá ảnh test

Báo cáo/bối cảnh lưu: 4.291 ảnh hợp lệ, 5.166 đối tượng, Precision 0,7427, Recall 0,6745, mAP50 0,7370, mAP50–95 0,4163; smoke mAP50 0,7913 và fire mAP50 0,6827.

Các hình test đã lưu ở [runs/detect/val](../../DATA/training/train_official_v2/runs/detect/val), gồm đường PR/F1/P/R, ma trận nhầm lẫn và ví dụ dự đoán. Tên thư mục `val` không chứng minh split là validation; bối cảnh ghi lời gọi chính thức dùng test. Code hiện tại [eval_metrics.py](../../fire_detection/eval_metrics.py) dùng `split="test"` và không ép ngưỡng confidence video vào đánh giá ảnh.

**Giới hạn truy xuất:** lần kiểm kê 28/10 không thấy bản log/JSON kết quả test dạng số trong thư mục test, chỉ có các hình. Các số trên được bảo tồn từ báo cáo và bối cảnh đã có; lượt này không tính lại chúng từ ảnh hay chạy test lại. Khi cần kiểm chứng số chính xác độc lập, cần lấy log gốc từ lần chạy Kaggle hoặc tải đúng dataset và đánh giá lại, ghi thành phép chạy mới. Không lấy `results.csv` của train thay thế log test thiếu.

## Video và phép so sánh hậu xử lý

Đọc [comparison.json](../../DATA/results/main_v2_conf025_side640/ablation_saved_observations/comparison.json) và [KET_QUA_SO_SANH.md](../../DATA/results/main_v2_conf025_side640/ablation_saved_observations/KET_QUA_SO_SANH.md). Phép so sánh dùng cùng quan sát YOLO đã lưu, không train/chạy ba mô hình riêng.

| Clip | Thư mục log gốc | Loại |
|---|---|---|
| video_chay | [log và summary](../../DATA/results/main_v2_conf025_side640/video_chay) | Lửa |
| video_khoi | [log và summary](../../DATA/results/main_v2_conf025_side640/video_khoi) | Khói |
| video_khong_chay | [log và summary](../../DATA/results/main_v2_conf025_side640/video_khong_chay) | Sạch |
| video_khong_chay2 | [log và summary](../../DATA/results/main_v2_conf025_side640/video_khong_chay2) | Sạch |

Trong mỗi thư mục, `frames.jsonl` ghi từng khung, `summary.json` ghi cấu hình và thống kê, `alerts.log` ghi thông báo. Dùng [compare_saved_runs.py](../../fire_detection/compare_saved_runs.py) để tính lại từ log đã có:

```powershell
python fire_detection/compare_saved_runs.py
```

Lệnh này ghi lại bảng so sánh trong thư mục kết quả, không chạy YOLO. Code có các kiểm tra rằng chế độ đầy đủ tái hiện xác nhận và cảnh báo đã lưu. Phân biệt `alert_messages` (số lần thông báo), `alert_events` (sự kiện sau gộp), `confirmed_frames` (số khung xác nhận). Không dùng số khung để gọi là Recall khi chưa có nhãn đầy đủ.

Video giao diện rút gọn nằm trong [presentation_simple](../../DATA/results/presentation_simple): clip lửa 643 khung/8 thông báo/1 sự kiện, clip khói 534 khung/3 thông báo/1 sự kiện. Hai video sạch lấy kết quả từ lần chạy `main_v2_conf025_side640`, không phải lần rút gọn. Hai video demo để mở nhanh ở [BAO_VE](../../BAO_VE).

## Tốc độ CPU

[measurement.json](../../DATA/results/fps_measure_20261026/measurement.json), [console2.log](../../DATA/results/fps_measure_20261026/console2.log) và [summary.json](../../DATA/results/fps_measure_20261026/run2/summary.json) ghi 308/308 khung, 71,252 giây, 4,323 khung/giây. Đây là một phép đo toàn lệnh trên video sạch, tính cả khởi động, giải mã và ghi MP4. Chưa chứng minh tốc độ ổn định trên nhiều cảnh hay hiệu năng Jetson.

## File tải lại và file không đồng bộ

Video gốc: dùng [NGUON_VIDEO.md](../../DATA/videos/NGUON_VIDEO.md) để tải đúng nguồn/tên. Các log giữ đường dẫn máy cũ nhằm bảo toàn bằng chứng; khi chạy mới dùng đường dẫn của bản clone. Môi trường Python và cache phải tạo lại ở nơi đủ dung lượng. Không chuyển weight, ảnh hay video thành văn bản rồi xem đó là bản thay thế dữ liệu nhị phân.
