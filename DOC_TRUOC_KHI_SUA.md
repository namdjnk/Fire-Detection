# Đọc dự án và tiếp tục sửa từ GitHub

Kho này lưu code, weight, tài liệu gốc, bản đọc Markdown và bằng chứng thực nghiệm của đồ án phát hiện lửa/khói bằng YOLOv8n. Các đường dẫn bên dưới tính từ gốc kho, dùng được khi clone sang máy khác. Tiền tố `E:\DA_TGMT` trong tài liệu và log là vị trí máy cũ, không phải yêu cầu về vị trí trên máy mới.

## Thứ tự đọc

1. Đọc [AGENTS.md](AGENTS.md), [bối cảnh](report_revision/context.md) và [quy tắc](report_revision/rules.md), đặc biệt phần cập nhật 28/10/2026 ở cuối bối cảnh.
2. Đọc [mã nguồn dạng Markdown](docs/markdown/01_CODE_HIEN_TAI.md), [báo cáo](docs/markdown/02_BAO_CAO_WORD.md) và [11 slide](docs/markdown/03_BAO_CAO_POWERPOINT.md). Mở các ảnh đi kèm để hiểu sơ đồ và biểu đồ.
3. Đọc [bản đồ bằng chứng](docs/markdown/04_DU_LIEU_VA_KET_QUA.md); mở JSON/CSV/JSONL gốc khi cần kiểm tra số liệu. Bản Markdown giúp tìm nguồn, không thay thế kết quả gốc.
4. Kiểm tra [manifest](docs/markdown/FILE_MANIFEST.json) để biết chính xác file nguồn của bản trích. SHA-256 là mã băm dùng để nhận biết nội dung file có thay đổi hay không.

## Phân biệt phiên bản trước khi sửa

| Vai trò | File trong kho |
|---|---|
| Code hiện hành | [fire_detection](fire_detection) |
| Weight hiện hành | [Models/fire_smoke_v2_best.pt](Models/fire_smoke_v2_best.pt) |
| Báo cáo bản sửa ngày 27/10, nguồn của Markdown mới | [smoke_fire_detection.docx](report_revision/fix_review_20261027/output/smoke_fire_detection.docx) |
| Slide bản sửa ngày 27/10, nguồn của Markdown mới | [smoke_fire_detection.pptx](report_revision/fix_review_20261027/output/smoke_fire_detection.pptx) |
| Bộ bảo vệ đã có từ 26/10, vẫn giữ nguyên | [BAO_VE](BAO_VE) |
| Báo cáo và slide cùng phiên bản bộ bảo vệ | [Fire_detection.docx](report_revision/Fire_detection.docx), [PPTX](slides/output/Bao_ve_chay_khoi_YOLOv8n_nen_trang.pptx) |

Bản sửa 27/10 thay hình kiến trúc YOLOv8 trong Word và sửa một số nội dung/hiển thị slide. Lượt tải Git ngày 28/10 giữ cả hai phiên bản, không tự thay bản trong `BAO_VE`. Khi người dùng chỉ nói tiếp tục bản sửa mới, bắt đầu từ `fix_review_20261027/output`; khi yêu cầu bộ mang bảo vệ, đối chiếu `BAO_VE` và xác định thay đổi cần đồng bộ. Không dùng bản sao Markdown ngày 27/10 cũ trên máy vì nó lấy nguồn từ `BAO_VE`.

## Nguyên tắc đối chiếu

- Chỉ có fire/smoke; không nhận té ngã, LSTM, Telegram, TensorRT hoặc Jetson là chức năng đã hoàn thành.
- Nhãn `0: smoke`, `1: fire`; train 100 epoch. Phân biệt validation lúc train với test sau train. Không lấy hàng cuối `results.csv` làm số liệu test.
- N/M là ít nhất N tín hiệu trong M khung gần nhất, không bắt buộc liên tiếp. Khói qua ngưỡng chuyển động trước khi được tính vào cửa sổ N/M.
- Số lần thông báo, số khung xác nhận và số sự kiện sau gộp là các đại lượng khác nhau. Bốn video ngắn chưa đủ kết luận hiệu quả ở mọi cảnh.
- Sửa nguồn thật rồi tạo lại Markdown; không chỉ sửa bản trích và báo rằng đã sửa Word/PPT/code. Markdown không giữ font, ngắt trang hay toàn bộ cấu trúc slide. Muốn sửa hình thức phải mở file gốc và xem bản render.

## Có gì và thiếu gì trên Git

Đã đưa lên: code/config/thư viện cần cài, weight mới, DOCX/PPTX của hai phiên bản, Markdown và hình đọc kèm, video đã xử lý, log khung hình và tổng kết, cấu hình train, CSV train, biểu đồ train/test, nguồn video và hướng dẫn bảo vệ.

Không đưa lên: môi trường `.venv`, cache, bản sao trùng, bản dựng tạm, video MP4 đầu vào dung lượng lớn, weight khởi tạo và checkpoint cuối không dùng. Bộ ảnh huấn luyện đầy đủ cũng không nằm trong thư mục dự án hiện tại. Các file bị loại vẫn giữ trên máy, không bị xóa.

Muốn chạy lại video: tải theo [NGUON_VIDEO.md](DATA/videos/NGUON_VIDEO.md), đặt đúng tên trong `DATA/videos`. Muốn đánh giá lại tập test: tải bộ Kaggle `sayedgamal99/Smoke-Fire-Detection-YOLO`, kiểm tra cấu trúc và sửa `path` trong bản sao `fire_smoke_data.yaml` cho máy mới. YAML đã lưu dùng đường dẫn Kaggle, không chạy nguyên trạng ở mọi máy. Môi trường gốc không được đóng băng đầy đủ nên không cam kết kết quả chạy lại khớp tuyệt đối.

Đọc/sửa nội dung không cần cài torch hoặc tải lại toàn bộ dataset. Không coi việc chỉ đọc Git là đã chạy lại mô hình. Một số kết quả test số học hiện chỉ được ghi trong tài liệu; xem giới hạn nguồn trong bản đồ bằng chứng.

## Câu nhắn dùng ở cuộc trò chuyện khác

> Hãy đọc kho https://github.com/namdjnk/Fire-Detection, bắt đầu từ DOC_TRUOC_KHI_SUA.md rồi đọc context.md, rules.md và docs/markdown. Đối chiếu code và kết quả gốc trước khi sửa. Tiếp tục từ bản Word/PPT sửa ngày 27/10 trong report_revision/fix_review_20261027/output, giữ kiểu trình bày và không bịa số liệu. Trước hết nói rõ bạn đã đọc những nguồn nào và nguồn nào chưa truy cập được. Sau đó thực hiện yêu cầu sửa của tôi.

Nếu kho là riêng tư, cuộc trò chuyện/máy khác cần được cấp quyền đọc hoặc nhận bản ZIP tải từ GitHub; một liên kết đơn thuần không tự cấp quyền.
