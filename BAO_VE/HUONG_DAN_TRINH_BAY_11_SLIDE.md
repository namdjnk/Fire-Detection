# Tập bảo vệ đồ án theo 11 slide

Mở `smoke_fire_detection.pptx` trong cùng thư mục này. Bài nói dưới đây dài khoảng **5–6 phút**, đã tính khoảng 20 giây xem video. Hãy nhớ ý chính rồi nói bằng lời của mình, không cần đọc nguyên văn. Mở `smoke_fire_detection.docx` khi thầy cô muốn xem cách làm hoặc bảng kết quả chi tiết.

## Trước khi nói: hiểu câu chuyện của bài

1. **Dữ liệu:** dùng ảnh có nhãn lửa/khói từ Kaggle. Nhãn là câu trả lời chuẩn để mô hình học; `0` là khói, `1` là lửa.
2. **Mô hình:** lấy YOLOv8n có sẵn rồi *fine-tune*, tức là huấn luyện tiếp bằng bộ dữ liệu hai lớp. Weight `fire_smoke_v2_best.pt` là kết quả được chọn để chạy thử và đánh giá.
3. **Ứng dụng:** đọc video từng khung, YOLO vẽ hộp, bộ lọc kiểm tra tín hiệu qua nhiều khung và chương trình lưu cảnh báo cục bộ.

Một câu để nhớ: **“Em dùng dữ liệu có nhãn để huấn luyện tiếp YOLOv8n, kiểm tra trên ảnh test, rồi đưa weight vào chương trình xử lý video.”**

## Bài nói theo từng slide

| Slide / thời gian gợi ý | Em nói gì | Điều cần chỉ trên màn hình |
|---|---|---|
| **1. Tên đề tài** / 20 giây | “Em chào thầy cô. Đề tài của em là phát hiện lửa và khói bằng YOLOv8n. Em sẽ trình bày dữ liệu, cách huấn luyện, chương trình xử lý video và kết quả đã đo.” | Tên đề tài và tên sinh viên. |
| **2. Bối cảnh, mục tiêu** / 25 giây | “Bài toán là tìm vùng có lửa hoặc khói trên từng khung hình. Chương trình không lưu cảnh báo ngay sau một hộp dự đoán; nó kiểm tra tín hiệu qua nhiều khung rồi mới lưu ảnh và nhật ký trên máy.” | Ảnh ví dụ và ba mục tiêu. |
| **3. Kiến trúc** / 25 giây | “Video được tách thành các khung. YOLO trả về hộp, lớp và điểm tin cậy. Với khói, em kiểm tra thêm chuyển động; sau đó dùng cửa sổ N/M để xác nhận trước khi báo.” | Chỉ lần lượt ba khối trái sang phải. |
| **4. Dữ liệu** / 35 giây | “Em dùng bộ Smoke-Fire-Detection-YOLO trên Kaggle, đã có ảnh và hộp nhãn. Em kiểm tra thứ tự lớp trước khi train: 0 là smoke, 1 là fire. Bộ nạp sử dụng 14.101 ảnh train, 3.094 ảnh validation và 4.291 ảnh test hợp lệ; test được giữ để đánh giá sau huấn luyện.” | Chỉ nguồn dữ liệu, hai lớp và ba số lượng ảnh. |
| **5. Huấn luyện** / 35 giây | “Em không thiết kế mạng mới. Em fine-tune YOLOv8n từ `yolov8n.pt` trên Kaggle với một GPU T4, 100 epoch, batch 16 và kích thước ảnh 640. File dùng trong ứng dụng là `fire_smoke_v2_best.pt`. Lần thử 1 epoch trên 2% dữ liệu chỉ để kiểm tra notebook trước khi chạy chính thức.” | Chỉ tên mô hình, thông số và weight. |
| **6. Optical flow** / 25 giây | “Optical flow ước lượng chuyển động giữa hai khung gần nhau. Em tính điểm chuyển động cho vùng YOLO dự đoán là khói, với ngưỡng 0,35. Bộ lọc có thể loại vùng đứng yên, nhưng cũng có thể bỏ sót khói thật chuyển động yếu.” | Chỉ công thức/ba thành phần và giới hạn. |
| **7. So sánh ba cấu hình** / 30 giây | “Trên cùng log của video khói 534 khung, YOLO có 376 khung có hộp khói. Thêm N/M có 385 khung ở trạng thái xác nhận vì cửa sổ có thể giữ tín hiệu qua khung không có hộp. Thêm flow còn 63 khung xác nhận. Đây là số khung, không phải Recall; kết quả cho thấy flow lọc mạnh và cần thử thêm để biết có bỏ sót khói thật hay không.” | Chỉ ba cột và câu ghi chú dưới biểu đồ. |
| **8. Video** / 30 giây nói + khoảng 20 giây chiếu | “Em chạy một video lửa và một video khói: lửa 21,45 giây tạo 8 lần báo, khói 17,80 giây tạo 3 lần báo; mỗi clip được gộp thành một sự kiện. Hai clip sạch tổng 25,33 giây chưa quan sát thấy cảnh báo. Bây giờ em chiếu ngắn mỗi loại một đoạn; chữ trên video chỉ là FIRE hoặc SMOKE để dễ nhìn.” | Mở `video_chay_demo.mp4`, rồi `video_khoi_demo.mp4`; chỉ chiếu khoảng 10 giây mỗi tệp. |
| **9. mAP50 từng lớp** / 20 giây | “Trên tập test ảnh, mAP50 của khói là 79,13%, của lửa là 68,27%. Đây là chỉ số về hộp phát hiện trên ảnh có nhãn, không phải tỉ lệ cảnh báo đúng của video.” | Chỉ hai thanh và tên lớp. |
| **10. Bảng test** / 35 giây | “Đánh giá weight này ở kích thước ảnh 640 trên 4.291 ảnh test hợp lệ, 5.166 đối tượng. Kết quả chung là Precision 74,27%, Recall 67,45%, mAP50 73,70% và mAP50–95 41,63%. Bảng còn tách kết quả của smoke và fire để thấy lửa khó hơn trong tập test này.” | Chỉ dòng tổng và hai dòng từng lớp. |
| **11. Kết luận, giới hạn** / 25 giây | “Em đã huấn luyện và đánh giá mô hình hai lớp, chạy chương trình trên bốn video và đối chiếu ba cấu hình lọc. Một phép chạy video sạch trên CPU đạt 4,32 khung/giây khi tính cả khởi động và ghi tệp. Video thử còn ngắn; em chưa tính Precision/Recall theo sự kiện và chưa thử trên Jetson Nano. Em xin cảm ơn thầy cô.” | Chỉ hai cột: đã làm và còn thiếu. |

**Nếu thầy cô giới hạn thời gian:** ưu tiên slide 4, 5, 8, 10, 11; nói nhanh slide 6–7. Chỉ chiếu một clip 10 giây nếu còn thời gian. Bản nói gọn khoảng 2 phút nằm trong `E:\DA_TGMT\report_revision\HUONG_DAN_BAO_VE_DO_AN_FIRE_SMOKE.md`.

## Ba câu rất dễ bị hỏi

### “Dữ liệu và nhãn em lấy từ đâu? Em có tự gán nhãn không?”

“Em dùng bộ Smoke-Fire-Detection-YOLO do `sayedgamal99` công bố trên Kaggle. Bộ này đã có ảnh và file nhãn YOLO; em kiểm tra cấu trúc, thứ tự lớp và ảnh/nhãn tương ứng trước khi train. Em không nhận là mình tự chụp hay tự gán toàn bộ dữ liệu.”

### “Em tự xây mô hình hay chỉ dùng YOLO có sẵn?”

“Em dùng kiến trúc YOLOv8n có sẵn và fine-tune từ weight `yolov8n.pt` cho hai lớp của bài. Phần em thực hiện là kiểm tra dữ liệu, huấn luyện chính thức 100 epoch, chọn weight, đánh giá test và tích hợp bộ lọc N/M cùng optical flow vào chương trình video.”

### “73,70% có nghĩa hệ thống báo cháy đúng 73,70% không?”

“Không. 73,70% là mAP50 của **hộp phát hiện trên ảnh test có nhãn**. Em chưa có bộ video được gán nhãn sự kiện đầy đủ để tính tỉ lệ cảnh báo đúng của toàn hệ thống. Hai clip sạch không có cảnh báo, nhưng tổng cộng chỉ khoảng 25,33 giây.”

## Khi thầy cô hỏi sâu hơn

- **Vì sao có 8 cảnh báo mà chỉ 1 sự kiện?** Một đám cháy có thể làm chương trình báo lại nhiều lần sau khoảng chờ. Các lần báo gần nhau được gộp thành một sự kiện để không đếm một đám cháy thành nhiều vụ.
- **N/M là gì?** Trong cửa sổ 20 khung gần nhất, cần tín hiệu hợp lệ ở ít nhất 10 khung cho lửa hoặc 12 khung cho khói. Không bắt buộc các khung đó liên tục.
- **Vì sao flow còn 63 khung?** Ngưỡng chuyển động loại nhiều khung nghi là khói. Điều này cũng có thể loại khói thật, nên đây là giới hạn cần nói thẳng.
- **Có chạy trên Jetson Nano chưa?** Chưa. Đề tài cũ có nhắc thiết bị đó, nhưng bản hiện tại chưa có phép thử và số FPS đầu cuối trên Jetson.
- **Nếu trình chiếu video lỗi?** Mở trực tiếp hai tệp MP4 trong thư mục này bằng trình phát video. Nếu vẫn lỗi, trình bày số liệu ở slide 8 và chỉ hình minh họa; không đổi số liệu.

## Tự tập ngay, từng bước

**Buổi tập đầu:** mở slide 1–5, bật đồng hồ 2 phút 20 giây và thử giải thích bằng lời của bạn mà không đọc bảng trên. Nếu vấp ở chữ *fine-tune*, hãy nói “huấn luyện tiếp mô hình YOLOv8n có sẵn trên dữ liệu lửa/khói”. Sau đó đối chiếu phần bạn vừa nói với bảng trên, sửa đúng một chỗ chưa rõ và tập lại. Khi ổn 5 slide đầu mới tập slide 6–11.

Trước hôm bảo vệ, mở thử PPTX, DOCX và **cả hai MP4** trên máy sẽ trình chiếu; kiểm tra hình, tiếng (video demo không cần âm thanh), font chữ và thời gian mở. Giữ bộ file trong `BAO_VE` trên ổ E, đồng thời sao chép thêm ra USB nếu cần. Không sửa số liệu bằng trí nhớ khi file và lời nói khác nhau.
