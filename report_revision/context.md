# Bối cảnh báo cáo đồ án thị giác máy tính

## Nguồn và cách đọc tài liệu

- Tài liệu gốc: `E:\slide - bao cao\report.docx` (39 trang).
- Bản sao đối chiếu nội dung và hình thức: `E:\DA_TGMT_LUU_TRU_20261026\report_revision\_archive_20261026\revision_20261024\tmp\original_reference.docx`. Bản sao có cùng SHA-256 với tài liệu gốc: `c0ca3ef2a253f370b62d5c9aebc9dfc575a7d19f4578e350d9407edf9254f7cb`.
- Đây là **báo cáo của đề tài cũ**. Các câu nói rằng hệ thống đã chạy trên Jetson Nano, có cảnh báo Telegram, phát hiện té ngã hoặc đạt một chỉ số nào đó chỉ là nội dung trong tài liệu gốc. Không coi chúng là bằng chứng cho đề tài cháy/khói hiện tại.
- Các mục dưới đây tách rõ **nội dung của DOCX gốc** và **trạng thái mới được đối chiếu từ dự án**.

## Thông tin trên bìa DOCX gốc

- Trường Đại học Xây dựng Hà Nội, Khoa Công nghệ Thông tin.
- Loại tài liệu: Báo cáo đồ án thị giác máy tính.
- Tên trên bìa cũ: *Nghiên cứu và xây dựng hệ thống phát hiện cháy/khói*; phụ đề tiếng Anh còn mô tả phát hiện té ngã theo thời gian thực trên thiết bị biên.
- Bìa gốc ghi Đinh Xuân Nam – 0205268. Ngày 26/10/2026, người dùng xác nhận **mã sinh viên đúng là 0211268**. Báo cáo hiện tại ghi 0211268; bìa slide đã được sửa theo mã đúng. Giảng viên hướng dẫn: Nguyễn Đình Quý. Ngành: Khoa học máy tính. Địa điểm và thời gian: Hà Nội, tháng 10 năm 2026.
- Khi sửa báo cáo, giữ thông tin trường/khoa và dùng mã sinh viên 0211268 đã được người dùng xác nhận; tên đề tài, phụ đề phải khớp phạm vi mới.

## Đề tài và cấu trúc của DOCX gốc

Đề tài cũ kết hợp hai nhánh: YOLOv8 phát hiện lửa/khói; YOLOv8-pose trích xuất keypoint và mạng LSTM phân loại té ngã. Bản gốc còn mô tả cảnh báo qua Telegram, tối ưu TensorRT và triển khai Jetson Nano. Báo cáo trình bày ba notebook Kaggle cho các bước cũ. Những phần này giải thích vì sao vẫn có đoạn văn và số liệu không phù hợp với đề tài mới.

Thứ tự lớn của báo cáo gốc:

1. Bìa, tóm tắt, mục lục.
2. Chương 1 – Giới thiệu bài toán: bối cảnh, mục tiêu, phạm vi, cấu trúc báo cáo.
3. Chương 2 – Cơ sở lý thuyết: phát hiện đối tượng, YOLOv8, chỉ số đánh giá; sau đó là pose, LSTM và TensorRT của phạm vi cũ.
4. Chương 3 – Dữ liệu: dữ liệu cháy/khói và dữ liệu té ngã của phạm vi cũ.
5. Chương 4 – Phương pháp thực hiện: kiến trúc, huấn luyện, hai mô-đun, tích hợp cảnh báo và triển khai.
6. Chương 5 – Kết quả thực nghiệm và đánh giá: môi trường, kết quả từng mô-đun, hiệu năng và thảo luận.
7. Chương 6 – Kết luận và hướng phát triển; tiếp theo là tài liệu tham khảo và phụ lục cấu hình/cách chạy.

DOCX gốc có 12 bảng, hình/biểu đồ và nhiều đoạn ngắt section do cách tạo tài liệu cũ. Một số tiêu đề cuối tài liệu nằm trong header hoặc phần mục lục cũ, nên cần xem **trang hiển thị thực tế**, không chỉ đọc danh sách paragraph hay sao chép số section.

## Phong cách trình bày quan sát từ DOCX gốc

- Khổ A4. Trang bìa có hai đường kẻ xanh, tên đề tài màu xanh đậm, thông tin sinh viên/giảng viên thành cụm giữa trang và địa điểm/thời gian ở gần cuối trang.
- Chữ nội dung chủ yếu là Times New Roman 12 pt, căn đều hai lề, giãn dòng khoảng 1,57; một số đoạn đầu dòng thụt 1,27 cm. Vùng chữ bên trái khoảng 3,5 cm, bên phải khoảng 2,5 cm.
- Tiêu đề chương khoảng 17 pt, đậm, xanh đậm; mục cấp hai khoảng 14 pt xanh; cấp ba khoảng 12 pt xám đậm. Chương mới bắt đầu ở trang mới.
- Bảng có hàng tiêu đề nền xanh đậm, chữ trắng, các hàng xen kẽ trắng và xanh rất nhạt; chú thích bảng đặt phía trên. Chú thích hình đặt dưới hình, phần nhãn `Hình/Bảng N:` xanh đậm và phần mô tả in nghiêng.
- Đầu trang ở các trang nội dung có tên đồ án in nghiêng và gạch xanh; số trang nằm giữa chân trang. Mục lục dùng phân cấp, dấu chấm dẫn và số trang căn phải.

### Đối chiếu với ảnh người dùng gửi ngày 25/10/2026

Người dùng mở bản sửa và thấy hai lỗi mà bản PDF xuất từ Microsoft Word không bộc lộ: bìa hiện chữ không chân (thay vì Times New Roman) và thiếu hai đường kẻ xanh; mục lục hiện chữ xanh gạch chân, số trang dính sát tên mục, không có chấm dẫn và không căn phải. Ảnh bản gốc do người dùng gửi cho thấy bìa chữ Times New Roman cùng hai đường xanh, mục lục ba cấp với số trang cùng trục bên phải; cấp 2/3 có chấm dẫn. Đây là bằng chứng trực quan ưu tiên khi đánh giá khả năng hiển thị của DOCX trên trình xem người dùng đang dùng.

Kiểm tra OOXML của bản sửa trước cho thấy hai đường kẻ bìa vẫn là đối tượng neo nổi (`AlternateContent` chứa DrawingML/VML); mục lục lưu tab trong style `TOC1/2/3`, còn nhiều đoạn mục lục mang font theo theme và các dòng chứa run kiểu `Hyperlink`. Vì vậy một trình xem không xử lý đầy đủ các phần này có thể hiển thị như ảnh lỗi, dù Microsoft Word xuất PDF đúng. Khi sửa cần đặt Times New Roman trực tiếp trên run và đoạn quan trọng; dùng đường kẻ có cấu trúc tương thích hơn; đặt tab căn phải và dấu chấm dẫn trực tiếp trên từng đoạn mục lục; bỏ hình thức gạch chân/xanh mặc định của hyperlink.

Ngày 25/10/2026, người dùng xác nhận ảnh bản sửa được chụp từ **trình xem DOCX của Codex**, còn ảnh bản gốc từ **WPS Office**. Đã mở đồng thời `report.docx` và `Bao_cao_chay_khoi_sua_bia_muc_luc.docx` trong WPS ở cùng mức zoom 72%: mục lục bản sửa hiện ba cấp, cấp 2/3 có chấm dẫn, tất cả số trang căn một cột bên phải như bản gốc. Sai khác lớn trong hai ảnh gửi lần này đến từ **hai ứng dụng hiển thị khác nhau**, không phải bằng chứng mục lục của bản sửa sai khi mở bằng WPS. Vẫn có sai khác nội dung: mục đầu bản gốc là “Tóm tắt”, bản sửa là “TÓM TẮT (ABSTRACT)”; số trang thay đổi do nội dung báo cáo mới ngắn hơn. Khi đánh giá hình thức, mở cả hai DOCX trong cùng WPS và cùng mức zoom; không kết luận lỗi định dạng từ ảnh Codex so với ảnh WPS.

### Đối chiếu trực quan chi tiết với bản sửa ngày 25/10/2026

Các nhận xét sau được kiểm tra trên trang xuất từ Word của DOCX gốc (39 trang) và bản sửa trước (32 trang), cùng bằng cách đọc thuộc tính đoạn và style của hai tệp. Số trang dưới đây là vị trí trang trong tệp PDF xuất ra, tính cả bìa.

| Thành phần | Bản gốc | Điều cần sửa so với bản trước |
|---|---|---|
| Bìa (trang 1) | Tên trường/khoa ở giữa gần đầu trang; hai đường xanh; tên đề tài xanh đậm thành hai dòng; khối sinh viên/giảng viên/ngành ở giữa; địa điểm gần cuối | Bìa bản trước khá sát; giữ nguyên hình thức này, chỉ thay chữ đúng phạm vi fire/smoke |
| Tóm tắt (trang 2) | Tiêu đề xanh đậm bắt đầu cách mép trên khoảng 2,4 cm; thân bài Times New Roman 12 pt, căn đều | Bản trước đẩy tiêu đề xuống khoảng 5 cm; kéo lên theo bản gốc |
| Mục lục (trang 3–5) | Tiêu đề đen lớn ở khoảng 5 cm từ mép trên; cấp 1 xanh đậm, đậm và **không có chấm dẫn**; cấp 2 và 3 có chấm dẫn, thụt lề lần lượt khoảng 0,6 cm và 1,5 cm; số trang cùng một trục bên phải | Giữ mục lục tự động nhưng chỉnh cấp 1 không dùng chấm dẫn và giữ nhịp cách dòng của bản gốc |
| Trang mở đầu chương (ví dụ chương 1 trang 6, chương 2 trang 9, chương 5 trang 27) | Tên chương xanh đậm 17 pt bắt đầu ở khoảng 2,4 cm từ mép trên; sau đó là mục cấp 2 xanh 14 pt, mục cấp 3 xám 12 pt; không có header trên trang đầu chương | Bản trước bắt đầu tên chương ở khoảng 5 cm, tạo khoảng trắng lớn phía trên; phải đưa lên |
| Trang nội dung tiếp theo | Header nghiêng ở bên phải kèm đường xanh; số trang giữa chân trang; thân bài bắt đầu dưới header | Bản trước cơ bản giống, không đổi tùy tiện |
| Đoạn nội dung | Times New Roman 12 pt; căn đều; giãn dòng khoảng 1,566; nhiều đoạn sau đoạn đầu thụt dòng đầu 1,27 cm và cách trước khoảng 6 pt; vùng chữ thực tế từ khoảng 3,5 cm đến 18,5 cm theo chiều ngang A4 | Bản trước kế thừa font qua style Normal, nhưng style Body Text/Heading không khai báo tên font trực tiếp; cần đặt rõ Times New Roman để tránh thay font khi mở máy khác |
| Khung nhấn mạnh chương 1 | Trên trang 7 có khung “Vấn đề đặt ra”: thanh tiêu đề xanh, chữ trắng; thân khung nền xanh rất nhạt và viền xanh | Bản trước thay bằng đoạn thường; cần đưa lại kiểu khung này với nội dung mới |
| Bảng (ví dụ bảng 5.1 ở trang 27) | Chú thích ở trên, nhãn xanh đậm, nội dung nghiêng; đầu bảng xanh đậm chữ trắng; hàng thân xen kẽ trắng và xanh nhạt; đường đáy đen | Bản trước khá gần, giữ cỡ chữ và độ rộng bảng theo vùng chữ gốc |
| Hình (ví dụ trang 10, 16, 28–29) | Hình nằm giữa vùng chữ; chú thích ở dưới; không để chú thích lạc sang trang khác | Dùng hình của mô hình mới nhưng giữ cách đặt và kiểu chú thích |
| Tài liệu tham khảo và phụ lục A | Tiêu đề bắt đầu khoảng 5 cm từ mép trên; không có header trên trang mở đầu | Bản trước gần đúng; giữ |
| Phụ lục B (trang 39) | Tiêu đề bắt đầu khoảng 2,4 cm từ mép trên; listing code viền xanh, nền xám rất nhạt, chữ đơn cách, chú thích nằm dưới | Bản trước bắt đầu khoảng 5 cm; đưa tiêu đề lên như bản gốc |

DOCX gốc có 56 section do công cụ tạo tài liệu cũ và một số lề section bất thường. Con số section không phải mục tiêu cần sao chép; phải so **vùng chữ hiển thị và vị trí thực tế trên trang**. Bản gốc dùng `Normal` Times New Roman 11 pt, `Body Text` Times New Roman 12 pt, Heading 1/2/3 Times New Roman 17/14/12 pt. Phần lớn thân bài và chú thích phải dùng font phù hợp theo vai trò, còn code/listing dùng font đơn cách như mẫu.

## Phạm vi và bằng chứng hiện tại, ngoài DOCX gốc

Phần này lấy từ mã nguồn, tệp kết quả và lịch sử làm việc của dự án `E:\DA_TGMT`, để người viết **không lặp lại các khẳng định cũ** trong DOCX.

- Đề tài hiện tại: phát hiện **fire** và **smoke** bằng YOLOv8n; cảnh báo và lưu kết quả cục bộ. Té ngã, LSTM, Telegram và khẳng định triển khai Jetson Nano không còn thuộc kết quả đã hoàn thành của đề tài này.
- Trọng số đang dùng: `E:\DA_TGMT\Models\fire_smoke_v2_best.pt`; khớp mã băm với `best.pt` của lần train mới. Thứ tự nhãn: `0: smoke`, `1: fire`; `imgsz=640`.
- Huấn luyện chính thức: YOLOv8n khởi tạo từ `yolov8n.pt`, 100 epoch, `fraction=1`, `batch=16`, một GPU Tesla T4 trên Kaggle. Chứng cứ chính ở `E:\DA_TGMT\DATA\training\train_official_v2\fire_smoke_runs\train_official_v2\args.yaml`, `results.csv` và `weights\best.pt`. Lần thử 1 epoch trên 2% dữ liệu chỉ là bước kiểm tra trước đó.
- Đánh giá `best.pt` trên **4.291 ảnh test hợp lệ**, 5.166 đối tượng: Precision `0,7427`, Recall `0,6745`, mAP50 `0,7370`, mAP50–95 `0,4163`. Theo lớp: smoke mAP50 `0,7913`, fire mAP50 `0,6827`. Chứng cứ ở kết quả test trong `E:\DA_TGMT\DATA\training\train_official_v2\runs\detect\val`; tên thư mục `val` là tên nơi thư viện lưu kết quả, lời gọi đánh giá dùng `split="test"`.
- Mã chạy hiện tại ở `E:\DA_TGMT\fire_detection\main.py`, `pipeline.py`, `config.yaml`. Hậu xử lý gồm xác nhận cửa sổ N/M (`10/20` cho fire, `12/20` cho smoke) và điểm chuyển động khói từ optical flow với ngưỡng `0,35`.
- Bốn video demo đã chạy ở `E:\DA_TGMT\DATA\results\main_v2_conf025_side640`: một video lửa, một video khói và hai video sạch. Video lửa và khói có cảnh báo; hai video sạch dài tổng cộng khoảng 25,33 giây không có cảnh báo quan sát được. Bảng so sánh YOLO, YOLO + N/M, YOLO + N/M + flow được tính lại từ cùng log khung hình. Phạm vi này chưa chứng minh hiệu quả trên mọi cảnh hay FPS đầu-cuối.
- Sau đó, giao diện video được rút gọn trong `fire_detection/pipeline.py`: chỉ vẽ hộp và một tên lớp `FIRE`/`SMOKE` cho mỗi lớp đang xuất hiện; không vẽ điểm tin cậy, điểm chuyển động, banner, thanh tỷ lệ, FPS hoặc số khung. Đây là thay đổi hiển thị, còn logic lưu ảnh cảnh báo, log, N/M và optical flow giữ nguyên.
- Hai video lửa/khói đã chạy lại đủ khung tại `E:\DA_TGMT\DATA\results\presentation_simple`: lửa 643 khung/8 lần báo/1 sự kiện, khói 534 khung/3 lần báo/1 sự kiện. `frames.jsonl`, thống kê và thời điểm cảnh báo khớp lần chạy trước. Hai video sạch chưa chạy lại bằng giao diện rút gọn; số liệu video sạch trong báo cáo vẫn lấy từ lần chạy đã lưu ở `main_v2_conf025_side640`.
- Bản báo cáo giao mới nhất: `E:\DA_TGMT\report_revision\Fire_detection.docx`; bản sao trong bộ bảo vệ là `E:\DA_TGMT\BAO_VE\smoke_fire_detection.docx` (hai file có cùng SHA-256). Tài liệu có 31 trang trong Word, mục lục tự động. Bản này giữ hai đường bìa dạng đường viền đoạn, Times New Roman ở bìa và các cấp tiêu đề, tab căn phải và chấm dẫn của 60 mục lục; số chương trong tiêu đề cấp 1 và mục lục dùng dạng `1  GIỚI THIỆU...` như báo cáo gốc, không có dấu chấm sau số. Đã cập nhật trường mục lục bằng Word rồi mở file cuối trong WPS ở trang mục lục: ba cấp, chấm dẫn và cột số trang hiển thị đúng. Kiểm tra tự động trước đó: 60/60 mục lục trỏ đúng trang, không có nội dung té ngã/Telegram/LSTM, trọng số mới khớp bản train, tài liệu gốc giữ nguyên SHA-256. Sau lần cập nhật Word ngày 26/10, mục đầu trong mục lục hiển thị `TÓM TẮT`, khớp tiêu đề trang.
- Slide bảo vệ đã làm xong tại `E:\DA_TGMT\slides\output\Bao_ve_chay_khoi_YOLOv8n_nen_trang.pptx`: 11 slide theo bố cục của `C:\Users\nofea\Downloads\Slide.pptx`, đổi nền trắng và chữ đen; nội dung lấy từ code và kết quả mới. Đã mở bản cuối trong PowerPoint và xem từng trang sau khi xuất PDF. Biểu đồ hai thanh trên slide 9 là các shape PowerPoint có thể chỉnh sửa; bảng trên slide 10 là bảng PowerPoint. Video demo vẫn là hai tệp riêng ở `E:\DA_TGMT\DATA\results\presentation_simple`.
- Bản slide mang đi bảo vệ được đổi tên thành `E:\DA_TGMT\BAO_VE\smoke_fire_detection.pptx`; bản ở `slides\output` có cùng nội dung. Ngày 26/10/2026, hai bản được sửa duy nhất mã sinh viên trên slide bìa từ 0205268 thành 0211268 theo xác nhận của người dùng; đã xuất và so ảnh slide bìa trước/sau, giữ nguyên bố cục.
- Kiểm tra lại `smoke_fire_detection.docx` ngày 26/10/2026 sau khi sửa thành bản nộp giảng viên: tài liệu có 31 trang, 60 dòng mục lục; đối chiếu tiêu đề với trang PDF cho kết quả 60/60 đúng. Bản DOCX/PDF không còn nhãn biên tập `CHỜ BỔ SUNG`: các phép chưa thực hiện được ghi rõ “chưa tính”, “chưa thử” và giới hạn kết luận. Chú thích Hình 5.4–5.5 chỉ mô tả kết quả phát hiện, không nhắc việc rút gọn giao diện. Đã rà văn bản khác để bỏ câu kể về quá trình chỉnh sửa, giữ số liệu, phương pháp, nguồn và hạn chế có bằng chứng. Style, header/footer và 8 ảnh trong DOCX được đối chiếu là không đổi; Word xuất 31 trang, WPS mở đúng 31 trang và hiển thị trang hình kết quả. Mục lục tự động được Word cập nhật sau khi sửa tiêu đề.
- Ngày 26/10/2026 đo thêm tốc độ chạy video trên máy cá nhân CPU: `video_khong_chay2.mp4` 308/308 khung, `--max_side 640 --no_display --save_video --eval`, tổng thời gian toàn lệnh 71,252 giây, bằng 4,323 khung/giây (báo cáo làm tròn 4,32). Thời gian gồm Python/khởi động mô hình, giải mã, suy luận, hậu xử lý, ghi MP4 và kết quả; đây là **một phép chạy trên video sạch**, không phải FPS ổn định trên mọi video hoặc kết quả Jetson. Chứng cứ ở `E:\DA_TGMT\DATA\results\fps_measure_20261026\measurement.json`, `console2.log`, `run2\summary.json`. Bản DOCX được cập nhật các câu ở tóm tắt, chương 5 và kết luận; cả hai bản DOCX cùng SHA-256 `E730D92462FB102BEBDEB0B5B602F95245875142854AEC01391BD6375379E9AD`, 31 trang và giữ 8 ảnh, 13 bảng. Các chỉ số không có nhãn sự kiện hoặc thiết bị vẫn để đúng trạng thái chưa tính/chưa thử.
- Slide 11 và hai bản PPTX được đổi đúng một câu về giới hạn tốc độ, cùng SHA-256 `C69DEAD12A4D1756EB926D35E2F8899DA19316C3D86D79A67AA73935442B4CCE`. Ảnh xuất trực tiếp từ PowerPoint của slide 11 trước/sau cho thấy bố cục không đổi. Hướng dẫn trình bày trong `BAO_VE` và `report_revision` đã sửa lời nói cho khớp phép đo mới; manifest trong `BAO_VE` được cập nhật cho DOCX và PPTX.
- Đã khôi phục nguồn bốn MP4 từ lịch sử tải Brave ngày 23/10/2026, đối chiếu mã video, chuỗi URL tải và số byte khớp tệp hiện có: `video_chay` = Pexels 4743951; `video_khoi` = Pexels 26629191; `video_khong_chay` = Pixabay 11496; `video_khong_chay2` = Pexels 35010963. Ba tệp Pexels và một tệp Pixabay cũng khớp miền trong metadata `Zone.Identifier`. URL cụ thể và liên kết điều kiện sử dụng chính thức ở `E:\DA_TGMT\DATA\videos\NGUON_VIDEO.md`; mục 3.3.1 của báo cáo chứa liên kết bấm được. Với clip 35010963, lịch sử chỉ còn đường dẫn tải chính xác, không có trang chi tiết, nên không tự suy đoán trang chi tiết.
- Ngày 26/10/2026, các bản DOCX cũ, thư mục dựng/kiểm tra trung gian, video kết quả cũ, checkpoint từng epoch, một ZIP video trùng lặp và mã/weight té ngã cũ được chuyển ra `E:\DA_TGMT_LUU_TRU_20261026` trên cùng ổ E. `MOVE_LOG.csv` trong thư mục đó ghi vị trí cũ/mới của 42 mục, khoảng 1,05 GB. Không xóa bản gốc hoặc đổi đường dẫn của báo cáo cuối, PPT cuối, weight đang dùng, code hiện tại, log test chính hay video demo.
- README ở gốc dự án đã được cập nhật để chỉ đúng mã, weight, tài liệu và kết quả của đề tài cháy/khói hiện tại. Bản README SafeVision AI cũ được sao lưu nguyên vẹn tại `E:\DA_TGMT_LUU_TRU_20261026\report_revision\_archive_20261026\legacy_README.md`. Các thư mục mã/weight té ngã cũ còn trong lịch sử Git và trong thư mục lưu trữ ngoài dự án; không phải chức năng hiện tại.
- Bộ mang đi bảo vệ nằm ở `E:\DA_TGMT\BAO_VE`: bản sao của PPTX cuối, DOCX cuối, hai MP4 trình bày và `NGUON_VIDEO.md`; kèm `HUONG_DAN_TRINH_BAY_11_SLIDE.md`, `README.md` và `FILE_MANIFEST.json`. Năm bản sao trong manifest đã được so SHA-256 với file nguồn và khớp. Nội dung gốc vẫn ở vị trí cũ trên ổ E.

## Những điểm còn thiếu

Đo tốc độ xử lý trên thêm video, nhiều lần chạy và cấu hình phần cứng; độ trễ từ thời điểm sự kiện thật bắt đầu; Precision/Recall theo sự kiện video; thử nghiệm trên thiết bị biên; phép rà trùng dữ liệu; phép so sánh công bằng giữa weight ban đầu và weight sau huấn luyện trên cùng tập test. Trong bản nộp, nêu đúng việc chưa tính/chưa thử và giới hạn suy luận, không để nhãn biên tập.

## Cập nhật kiểm kê Git ngày 28/10/2026

- Phát hiện bản sửa ngày 27/10 tại `report_revision/fix_review_20261027/output/smoke_fire_detection.docx` và `smoke_fire_detection.pptx`. Script sửa đã lưu cho thấy Word thay hình kiến trúc YOLOv8; PPT sửa diễn giải N/M, ngưỡng chuyển động, giới hạn so sánh, hiển thị hình và giới hạn tốc độ. Hai file này chưa được đồng bộ vào `BAO_VE`, `report_revision/Fire_detection.docx` hoặc `slides/output`; các đường dẫn “bản cuối” phía trên mô tả bộ đã có ngày 26/10, không bao quát bản sửa 27/10.
- Code `fire_detection/eval_metrics.py` hiện dùng split test, không ép confidence video vào model.val khi không truyền --conf, tách số thông báo khỏi số sự kiện và ghi N/A khi log cũ thiếu số sự kiện. Đây là trạng thái mã nguồn kiểm tra ngày 28/10, không phải bằng chứng đã chạy lại test.
- Bản Markdown ngày 27/10 cũ dùng nguồn BAO_VE. Bản mới `docs/markdown` trích từ hai file output sửa 27/10 và code hiện hành; có 7 file code, 13 bảng Word, 8 hình, 5 công thức, 11 slide và kiểm tra không thiếu run chữ. Lượt 28/10 chỉ đọc/trích/tải Git, không chỉnh nội dung hoặc bố cục DOCX/PPTX.
- Có hướng dẫn đọc từ máy khác ở `DOC_TRUOC_KHI_SUA.md`. Khi clone, thay tiền tố `E:\DA_TGMT` trong chỉ dẫn bằng thư mục gốc kho. Log lịch sử giữ nguyên đường dẫn để bảo toàn chứng cứ.
- Kiểm kê test tại `DATA/training/train_official_v2/runs/detect/val` chỉ thấy hình/biểu đồ, không có log số test độc lập. Các số Precision/Recall/mAP test được giữ từ báo cáo và bối cảnh trước; chưa tái tính trong lượt này. Cần log Kaggle gốc hoặc phép đánh giá mới để kiểm chứng độc lập. Toàn bộ dataset ảnh/nhãn và notebook train chính thức cũng không có trong cây dự án hiện tại.
