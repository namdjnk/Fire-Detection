# Đồ án phát hiện lửa và khói bằng YOLOv8n

Đây là phiên bản **hiện tại** của đồ án Thị giác máy tính. Chương trình dùng một mô hình YOLOv8n để tìm vùng lửa (`fire`) và khói (`smoke`) trong ảnh/video, rồi xác nhận tín hiệu qua nhiều khung và lưu cảnh báo trên máy.

**Đọc hoặc tiếp tục sửa từ GitHub/máy khác:** mở [DOC_TRUOC_KHI_SUA.md](DOC_TRUOC_KHI_SUA.md). Bản đọc được ngay trên GitHub nằm trong [docs/markdown](docs/markdown/README.md), gồm code, báo cáo Word, nội dung slide, hình và chỉ dẫn bằng chứng. Có bản sửa Word/PPT ngày 27/10 trong `report_revision/fix_review_20261027/output`, chưa thay thế bộ `BAO_VE`; xem hướng dẫn để chọn đúng phiên bản.

## Bắt đầu từ đâu

| Cần xem | Đường dẫn |
|---|---|
| Mã chạy video | `E:\DA_TGMT\fire_detection\main.py`, `pipeline.py`, `config.yaml` |
| Weight đang dùng | `E:\DA_TGMT\Models\fire_smoke_v2_best.pt` |
| Báo cáo cuối | `E:\DA_TGMT\report_revision\Fire_detection.docx` (bản mang đi bảo vệ: `E:\DA_TGMT\BAO_VE\smoke_fire_detection.docx`) |
| Slide cuối | `E:\DA_TGMT\slides\output\Bao_ve_chay_khoi_YOLOv8n_nen_trang.pptx` |
| Hai video trình bày | `E:\DA_TGMT\DATA\results\presentation_simple\video_chay\annotated.mp4` và `...\video_khoi\annotated.mp4` |
| Hướng dẫn bảo vệ | `E:\DA_TGMT\BAO_VE\HUONG_DAN_TRINH_BAY_11_SLIDE.md` |
| Bộ file mang đi bảo vệ | `E:\DA_TGMT\BAO_VE` |

## Bài đã làm và số liệu chính

- Nguồn ảnh/nhãn: bộ **Smoke-Fire-Detection-YOLO** của `sayedgamal99` trên Kaggle. Nhãn `0 = smoke`, `1 = fire`.
- Fine-tune YOLOv8n từ `yolov8n.pt` trong 100 epoch trên một GPU Tesla T4 của Kaggle; batch 16, ảnh 640 × 640. Lần thử 1 epoch/2% trước đó chỉ là kiểm tra môi trường.
- Tập test có 4.291 ảnh hợp lệ và 5.166 đối tượng. Weight hiện tại đạt Precision 74,27%, Recall 67,45%, mAP50 73,70%, mAP50–95 41,63%. mAP50 theo lớp: khói 79,13%; lửa 68,27%.
- Video: YOLO dự đoán từng khung; khói được kiểm tra thêm bằng optical flow; cửa sổ N/M xác nhận tín hiệu trước khi lưu cảnh báo. Giao diện video chỉ hiện hộp và chữ `FIRE` hoặc `SMOKE`.
- Đã thử bốn video: một clip lửa, một clip khói, hai clip sạch. Hai clip sạch dài tổng cộng khoảng 25,33 giây không có cảnh báo quan sát được. Phạm vi này chưa đủ kết luận tỉ lệ báo nhầm trong thực tế.

Các số liệu chi tiết, phương pháp đánh giá và giới hạn nằm trong báo cáo cuối và `E:\DA_TGMT\report_revision\context.md`.

## Cấu trúc thư mục

| Thư mục | Vai trò hiện tại |
|---|---|
| `fire_detection` | Mã chương trình đang dùng. |
| `Models\fire_smoke_v2_best.pt` | Weight đang dùng khi chạy và đánh giá. |
| `DATA\training`, `DATA\results`, `DATA\videos` | Minh chứng train/test, kết quả chạy và video đầu vào. Giữ nguyên để đối chiếu. |
| `report_revision`, `slides\output` | Báo cáo, quy tắc biên tập và slide cuối. |
| `BAO_VE` | Bản sao gọn của file cần mở khi trình bày, kèm hướng dẫn. |
| `E:\DA_TGMT_LUU_TRU_20261026` | Bản nháp, checkpoint theo epoch, kết quả chạy cũ và mã SafeVision AI cũ đã được chuyển khỏi dự án để lưu trữ. Có `MOVE_LOG.csv` ghi từng đường dẫn cũ và mới. Không dùng làm kết quả chính. |

## Chạy thử code

Dùng môi trường Python đã cài tại `E:\DA_TGMT\.venv`. Mở PowerShell trong thư mục dự án rồi chạy ví dụ sau:

```powershell
& 'E:\DA_TGMT\.venv\Scripts\python.exe' 'E:\DA_TGMT\fire_detection\main.py' --source 'E:\DA_TGMT\DATA\videos\video_chay.mp4' --save_video
```

Dấu hiệu chạy đúng: chương trình nạp `fire_smoke_v2_best.pt`, hiện hộp và tên `FIRE`/`SMOKE` trên video, đồng thời tạo kết quả trong thư mục được cấu hình ở `fire_detection\config.yaml`. Nếu chỉ cần mở mẫu khi bảo vệ, dùng hai video đã kết xuất trong `BAO_VE`, không cần chạy lại toàn bộ.

Đã có **một phép đo tốc độ toàn lệnh trên CPU**: 308 khung trong 71,252 giây, tương đương 4,323 khung/giây, gồm khởi động và ghi MP4; bằng chứng ở `DATA/results/fps_measure_20261026/measurement.json`. Chưa đo tốc độ ổn định trên nhiều video, độ chính xác theo sự kiện video hoặc chạy trên Jetson Nano. Bài hiện tại không có chức năng phát hiện té ngã hay gửi Telegram. Mã và weight cũ của nhánh té ngã được giữ ở `E:\DA_TGMT_LUU_TRU_20261026`; chúng vẫn còn trong lịch sử Git, nhưng không còn nằm trong thư mục làm việc hiện tại.
