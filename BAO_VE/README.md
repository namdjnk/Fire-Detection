# Bộ file dùng khi bảo vệ

Đây là **bản sao để mang đi trình bày**. Mã nguồn, weight, dữ liệu và kết quả gốc vẫn ở các thư mục hiện hành trong `E:\DA_TGMT`. File `FILE_MANIFEST.json` ghi đường dẫn nguồn và SHA-256 để kiểm tra bản sao.

## Mở theo thứ tự

1. `smoke_fire_detection.pptx` — 11 slide, nền trắng, chữ đen.
2. `video_chay_demo.mp4` và `video_khoi_demo.mp4` — dùng ở slide 8. Mở trước để chắc máy trình chiếu phát được; khi nói chỉ chiếu khoảng 10 giây mỗi video.
3. `smoke_fire_detection.docx` — mở nếu thầy cô hỏi nội dung chi tiết hoặc muốn xem bảng kết quả.
4. `HUONG_DAN_TRINH_BAY_11_SLIDE.md` — bài nói và câu hỏi đáp để tập trước buổi bảo vệ.
5. `NGUON_VIDEO.md` — liên kết nguồn của bốn video kiểm thử và trang điều kiện sử dụng Pexels/Pixabay.

## Cần làm trước ngày bảo vệ

- [ ] Tập nói slide 1–5 cho trôi chảy, sau đó slide 6–11; thử toàn bài trong 5–6 phút. Không đọc nguyên văn trên slide.
- [ ] Mở đủ PPTX, DOCX và hai MP4 trên **đúng máy sẽ trình chiếu**; kiểm tra font, hình, video và phím chuyển slide.
- [ ] Nếu thầy cô hỏi nguồn video, mở `NGUON_VIDEO.md`; đọc đúng mã Pexels/Pixabay và trang điều kiện sử dụng ghi trong file. Với video sạch thứ hai, liên kết đã lưu là đường dẫn tải Pexels, không phải trang chi tiết.
- [ ] Chuẩn bị một bản sao bộ `BAO_VE` trên USB hoặc nơi lưu dự phòng. Giữ bản gốc trên ổ E.
- [ ] Nhớ ba số liệu: **4.291 ảnh test**, **mAP50 chung 73,70%**, **100 epoch**. Biết nói rõ mAP50 là chỉ số phát hiện hộp trên ảnh test.

## Khi thầy cô hỏi “còn thiếu gì?”

Trả lời thẳng: hiện mới thử bốn clip ngắn; chưa có bộ video được gán nhãn sự kiện để tính Precision/Recall theo sự kiện và chưa chạy trên Jetson Nano. Một phép chạy video sạch 308 khung trên CPU mất 71,252 giây tính cả khởi động và ghi MP4, tương đương 4,32 khung/giây. Hai video sạch tổng cộng khoảng 25,33 giây không xuất hiện cảnh báo, nhưng chưa đủ để khẳng định hết báo nhầm.

Không cần train lại chỉ để mang bài này đi bảo vệ: đã có lần train chính thức 100 epoch, weight và kết quả test. Nếu thầy cô yêu cầu mở rộng thí nghiệm, hãy xác định phép đo cụ thể trước khi chạy thêm.
