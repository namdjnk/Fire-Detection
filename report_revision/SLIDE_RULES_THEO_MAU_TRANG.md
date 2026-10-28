# Quy tắc sửa slide theo mẫu gốc — phiên bản nền trắng

## 1. Phạm vi và nguồn mẫu

- **File mẫu để đối chiếu:** `C:\Users\nofea\Downloads\Slide.pptx` (11 slide). Xem chính file này ở chế độ trình chiếu khi sửa; không lấy slide cũ ở thư mục khác làm mẫu thay thế.
- **Mục tiêu:** giữ cách chia trang, thứ tự trình bày, vị trí tiêu đề, thẻ nội dung, ảnh, biểu đồ và bảng của file mẫu; viết lại nội dung theo đề tài hiện tại **phát hiện lửa và khói bằng YOLOv8n**.
- **Ngoại lệ màu do người dùng yêu cầu:** đổi toàn bộ nền tối thành **trắng** và chữ trắng thành **đen**. Những màu nhấn khác được làm đậm vừa đủ để đọc rõ trên nền trắng. Đây là quy tắc cho bản slide mới, không phải mô tả màu của file mẫu.
- Chỉ dùng các số liệu đã kiểm tra trong `E:\DA_TGMT\report_revision\context.md`, `E:\DA_TGMT\report_revision\rules.md`, báo cáo hoàn thiện, mã nguồn và kết quả thí nghiệm hiện tại. Số chưa có chứng cứ ghi **CHỜ BỔ SUNG**.

## 2. Kích thước, chữ và khoảng trống

| Thành phần | Quy tắc áp dụng |
|---|---|
| Khổ slide | Giữ **16:9**, kích thước mẫu **20 × 11,25 inch**. Không đổi sang 4:3. |
| Font | Dùng **Arial** như file mẫu cho tất cả tiêu đề, nội dung, số liệu, chú thích và nhãn biểu đồ. Không dùng font serif của báo cáo DOCX cho slide. |
| Tiêu đề trang nội dung | Đặt gần góc trên trái; mép trái chữ khoảng **1,11 inch**, mép trên khoảng **0,90 inch**. Phía trước có thanh dọc màu xanh đậm, rộng khoảng **0,08 inch**, cao khoảng **0,89 inch**, tại x ≈ **0,95 inch**. Trang 5 có tiêu đề hai dòng và thanh dọc cao hơn. Chữ tiêu đề đen, cỡ xấp xỉ **40 pt** như mẫu. |
| Tiêu đề trong thẻ | Thường đậm, khoảng **24–29 pt**. Màu nhấn có thể dùng xanh đậm, cam đậm, xanh lam đậm hoặc đỏ đậm theo chức năng của thẻ. |
| Chữ nội dung | Theo mẫu khoảng **19–21 pt**; nhãn biểu đồ/bảng có thể **18–20 pt**. Chữ chính màu đen. Không thu chữ quá nhỏ để nhét đoạn văn dài; rút câu cho gọn. |
| Nhịp bố cục | Giữ khoảng trống rộng giữa tiêu đề và nội dung. Các thẻ cùng hàng phải có chiều cao, mép trên và khoảng cách đều nhau. Không kéo ảnh méo để lấp khoảng trắng. |

Các tọa độ trên là số đo từ file mẫu, dùng làm mốc khi căn chỉnh; nếu câu chữ mới dài hơn, ưu tiên rút gọn nội dung rồi mới điều chỉnh kích thước hộp chữ.

## 3. Bảng đổi màu bắt buộc

| Thành phần | Trong slide mẫu | Bản mới nền trắng |
|---|---|---|
| Nền toàn trang | Xanh đen gần `#090E1C` | **`#FFFFFF`**; phủ kín slide, kể cả lớp nền của ảnh hoặc nhóm đối tượng cũ. |
| Tiêu đề và chữ nội dung trắng | `#FFFFFF` / `#F9FAFA` | **`#000000`**. Chữ phụ hoặc nhãn ít quan trọng có thể `#333333`, nhưng không dùng xám nhạt. |
| Thẻ nội dung xanh đen | Các khối xanh đen, đôi khi là **ảnh nền** chứ không phải shape có fill | `#F5F7F9` hoặc trắng, có viền `#D9E1E8` mảnh; giữ đúng kích thước, góc bo và vị trí. Nếu thẻ là ảnh, phải thay/tạo lại thẻ sáng, không chỉ đổi màu chữ. |
| Xanh ngọc | Xấp xỉ `#0FB981` | `#007A58` cho thanh dọc, đường kẻ, tiêu đề nhấn và dấu đầu dòng. |
| Tím | Xấp xỉ `#695CFB` | `#5846C8` cho hình minh họa/chuỗi dữ liệu phụ; không dùng cho đoạn chữ dài. |
| Cam | Xấp xỉ `#F59D0A` | `#A45C00` cho nhãn lửa hoặc thông tin cần phân biệt. |
| Xanh lam | Xấp xỉ `#3B81F5` | `#2457B8` cho nhãn/bars thứ hai. |
| Đỏ | Xấp xỉ `#EF4444` | `#B4232E` cho cảnh báo, lỗi hoặc hạn chế. |
| Đường lưới biểu đồ/bảng | Sáng mờ trên nền tối | `#D9E1E8`; chữ nhãn, trục và số liệu đều đen. |

Không để chữ trắng trên nền trắng, chữ đen trên thẻ đen, hoặc vùng ảnh nền tối còn che các thẻ sáng. Riêng ảnh chụp minh họa có thể giữ màu gốc của ảnh; yêu cầu nền trắng áp dụng cho **nền slide và các khối giao diện**.

## 4. Quy tắc cho từng slide

| Slide | Bố cục cần giữ từ mẫu | Nội dung của đề tài hiện tại |
|---|---|---|
| **1 — Bìa** | Cụm trường/khoa và tên môn **căn giữa ở phía trên**; tên đề tài lớn ở giữa (khoảng 2 dòng); thông tin sinh viên/MSSV/giảng viên ở nửa dưới, có **thanh dọc** phân hai nhóm; hình nét đơn ở góc phải dưới. | Đặt tên đề tài lửa/khói; lấy đúng tên sinh viên, MSSV và giảng viên từ báo cáo cuối. Bỏ tên thành viên, té ngã và thiết bị biên của slide cũ nếu không thuộc bài hiện tại. Nền trắng, tiêu đề đen; thanh dọc xanh đậm; hình nét tím đậm. |
| **2 — Bối cảnh** | Tiêu đề trái trên; nội dung dạng gạch đầu dòng ở **nửa trái**; một ảnh lớn ở **nửa phải**. | Nêu vấn đề phát hiện cháy/khói từ video; thay ảnh Jetson cũ bằng ảnh/video minh họa có nguồn rõ. Không dùng số liệu tai nạn từ slide cũ khi chưa đối chiếu nguồn. |
| **3 — Tổng quan hệ thống** | Ba thẻ ngang, vị trí gần x = **1,13 / 7,25 / 13,38 inch**, phần thân thẻ bắt đầu gần y = **4,11 inch**. Mỗi thẻ có số thứ tự, tiêu đề và đoạn ngắn. | Ba bước gợi ý: video/ảnh đầu vào → YOLOv8n nhận diện fire/smoke → lọc theo thời gian và hiển thị kết quả. Không giữ nhánh té ngã hoặc Telegram. |
| **4 — Dữ liệu** | Hai thẻ lớn đặt cạnh nhau; đầu thẻ có biểu tượng và tiêu đề màu nhấn. | Thẻ trái: nguồn dữ liệu Kaggle và hai nhãn `0: smoke`, `1: fire`. Thẻ phải: cách chia train/val/test, số ảnh hoặc cách kiểm tra nhãn. Chỉ ghi số đã xác minh; không chép số liệu cũ của mẫu. |
| **5 — Mô hình phát hiện** | Bố cục **trái chữ, phải ảnh lớn**. Ảnh phải gần nửa chiều rộng slide và cao gần hết trang; tiêu đề trái có thể xuống hai dòng. | Mô tả YOLOv8n, weight đang dùng và một ảnh kết quả thật. Không giữ YOLOv8s, TensorRT/Jetson, 150 epoch hoặc số tham số của bài cũ. |
| **6 — Bộ lọc chuyển động/khói** | Tiêu đề trái trên; **hình minh họa lớn bên trái**, phần giải thích bên phải; dòng nhấn và đường kẻ ngang trong nửa phải. | Dùng ảnh/video hoặc sơ đồ `smoke_score` và optical flow; giải thích ngắn khung hình tĩnh, khói chuyển động, điều kiện lọc. Thay toàn bộ keypoint/pose. |
| **7 — Ba thành phần kỹ thuật** | Ba thẻ ngang giống slide 3, mỗi thẻ có tiêu đề nhấn và 3–5 dòng. | Có thể dùng ba thẻ cho YOLO, xác nhận N/M, optical flow. Chỉ khẳng định tác dụng khi có ablation/video kiểm chứng; không còn BiLSTM, attention hay regularization của bài cũ. |
| **8 — Xác nhận trên video** | Hai thẻ lớn trái/phải; đầu thẻ có biểu tượng và màu nhấn khác nhau. | Một thẻ giải thích N/M; thẻ còn lại giải thích cách gộp cảnh báo thành sự kiện hoặc cách hiển thị nhãn fire/smoke trong video. Bỏ Telegram và logic té ngã. |
| **9 — Biểu đồ so sánh** | Biểu đồ **hai thanh ngang** chiếm phần giữa, ghi giá trị ở đầu thanh; có đường kẻ ngang và lời giải thích dưới biểu đồ. | Chỉ điền phép so sánh có cùng tập test và cùng điều kiện. Có thể so mAP50 fire/smoke hoặc hai cấu hình có kết quả thật. **Không dùng** 76,8%, 91,2%, +14,4% hay nhãn YOLOv8s từ slide mẫu. Nếu chưa có cặp số thích hợp, ghi `CHỜ BỔ SUNG` thay vì vẽ thanh giả. |
| **10 — Bảng kết quả** | Một bảng rộng gần kín trang, bắt đầu dưới tiêu đề; ghi chú ngắn phía dưới. | Dựng lại **bảng thật nền trắng, viền xám nhạt, chữ đen**. File mẫu khi xuất ra có vùng bảng đen làm chữ khó thấy, nên không giữ nguyên ảnh/vùng đen đó. Ghi Precision, Recall, mAP50, mAP50–95 theo smoke/fire cùng nguồn weight và `imgsz`; bỏ cột FPS Jetson nếu chưa đo. |
| **11 — Đánh giá** | Hai thẻ lớn song song, thẻ trái biểu tượng/tiêu đề xanh; thẻ phải biểu tượng/tiêu đề đỏ; thân là gạch đầu dòng. | Trái: những gì đã được test và quan sát. Phải: giới hạn đã biết như ảnh dễ nhầm, khói khó nhận, video mẫu còn ít. Không giữ các ưu/nhược điểm pose, LSTM, Telegram từ bài cũ. |

Nếu cần giảm số slide để nói trong thời gian ngắn, chỉ gộp trang **sau khi** đã có bản 11 slide bám mẫu; không thay hàng loạt bằng một mẫu thiết kế khác.

## 5. Ảnh, biểu đồ, bảng và nội dung

- Ảnh dùng để chứng minh kết quả phải là ảnh đầu ra của **weight mới** hoặc video demo hiện tại; không dùng ảnh minh họa như bằng chứng đạt chỉ số. Ghi nguồn nhỏ, rõ ràng nếu ảnh lấy từ nơi khác.
- Giữ tỉ lệ ảnh gốc; dùng crop để vừa khung. Với ảnh nằm trên nền trắng, thêm viền xám rất mảnh nếu mép ảnh trùng màu nền.
- Biểu đồ dùng màu đậm trên nền trắng; trục, nhãn và giá trị màu đen. Ghi tên chỉ số và tập dữ liệu, không chỉ đặt hai con số phần trăm.
- Bảng slide 10 phải đủ tương phản khi chiếu: hàng tiêu đề có thể nền xanh rất nhạt với chữ đen, hàng thân trắng/xám nhạt xen kẽ, đường kẻ mảnh. Không dùng nền đen để giấu chữ.
- Đoạn chữ trên slide nên ngắn hơn báo cáo. Không chuyển nguyên văn một trang DOCX thành slide. Tránh câu sáo rỗng và mọi khẳng định không có phép đo.
- Số liệu hoặc tính năng liên quan té ngã, pose, LSTM, TensorRT, Jetson Nano, Telegram trong **slide mẫu** là nội dung của đề tài cũ; không đưa sang bài hiện tại.

## 6. Cách kiểm tra bản PPT đã sửa

1. Mở file mẫu và bản mới trong **cùng PowerPoint/WPS**, cùng chế độ trình chiếu và cùng tỷ lệ; so từng trang về vị trí tiêu đề, chiều rộng các cột, thẻ, ảnh và khoảng trắng.
2. Kiểm tra đủ 11 slide: mọi nền toàn trang phải trắng; mọi chữ chính đen; thẻ và biểu đồ có viền/màu đủ thấy; không còn mảng xanh đen hoặc bảng đen do ảnh nền cũ.
3. Đọc thử ở chế độ trình chiếu toàn màn hình: không có chữ tràn thẻ, ảnh méo, số liệu nhỏ khó đọc hoặc đối tượng cũ nằm dưới đối tượng mới.
4. Đối chiếu số liệu trong slide với báo cáo và kết quả lưu trên ổ E. Mục nào chưa được xác nhận phải ghi `CHỜ BỔ SUNG` hoặc bỏ hẳn, không điền số theo mẫu cũ.
5. Lưu bản PPT mới trên ổ E với tên riêng; giữ nguyên `C:\Users\nofea\Downloads\Slide.pptx` để còn đối chiếu.
