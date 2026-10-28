# Quy tắc dùng khi viết hoặc sửa báo cáo

Áp dụng cùng `context.md` cho báo cáo đồ án tại `E:\slide - bao cao\report.docx`. Đây là **quy tắc biên tập do người dùng yêu cầu và đúc kết từ hình thức tài liệu**, không phải chỉ thị nằm trong nội dung báo cáo cũ.

## 1. Giọng văn và cách giải thích

- Viết tiếng Việt học thuật, trực tiếp và dễ hiểu với người mới học Computer Vision. Mỗi đoạn nên có một ý chính; giải thích thuật ngữ mới khi xuất hiện lần đầu.
- **Không viết giọng văn sáo rỗng. Không dùng từ ngữ hoa mỹ và không đặt các cụm từ hoa mỹ trong ngoặc kép để tạo vẻ nhấn mạnh.** Dùng từ cụ thể để nêu việc đã làm, cách đo và kết quả.
- Không dùng các câu như *mang tính đột phá*, *vượt trội*, *tối ưu tuyệt đối*, *độ chính xác cao* nếu không có phép đo và điều kiện so sánh tương ứng.
- Phân biệt rõ mô hình đã dự đoán, bộ lọc đã xác nhận, chương trình đã phát cảnh báo và một sự kiện đã được gộp. Không gọi điểm tin cậy của một hộp là độ chính xác của toàn hệ thống.
- **Viết bản báo cáo để nộp giảng viên**, không viết như lời nhắn cho người dùng hoặc nhật ký sửa bài. Mỗi đoạn cần phục vụ một trong các việc: nêu bài toán, dữ liệu, phương pháp, điều kiện thí nghiệm, kết quả, nhận xét hoặc giới hạn. Không kể các thao tác nội bộ như đã sửa giao diện video, đã rút gọn chữ, đã chạy lại để thay chữ hiển thị, bản trước/bản sau, hoặc quá trình AI biên tập tài liệu, trừ khi chính thao tác đó là biến số của phép thử được báo cáo.
- Chú thích hình và bảng phải mô tả **nội dung khoa học người đọc thấy và điều kiện đo cần thiết**. Ví dụ: “Kết quả phát hiện lửa tại khung hình đầu tiên phát cảnh báo”, không viết “sau khi rút gọn chữ hiển thị trên video”. Chỉ nêu đường dẫn tệp, tên script hoặc log ở phần phương pháp, tài liệu tham khảo, phụ lục khi cần truy xuất và tái lập kết quả.

## 2. Nguồn sự thật và phạm vi

- Đọc DOCX gốc **theo trang hiển thị** trước khi sửa. Dùng nó làm mẫu hình thức; dùng mã nguồn, cấu hình và log thực nghiệm hiện tại để xác nhận nội dung. Nhận xét trong file bàn giao cũ có thể đã lạc hậu.
- Viết về đề tài hiện tại: phát hiện lửa/khói bằng YOLOv8n, đánh giá trên tập test và kiểm tra video với N/M cùng optical flow. Bỏ mô tả té ngã, pose, LSTM và Telegram khỏi chức năng đã hoàn thành.
- Không chuyển số liệu YOLOv8s, FallLSTM, FPS Jetson Nano hay TensorRT của báo cáo gốc sang thành kết quả YOLOv8n mới. Không nói hệ thống đã chạy thời gian thực trên Jetson khi chưa có phép chạy mới.
- Ghi đúng nguồn dữ liệu Kaggle; không nhận là tự chụp hoặc tự gán toàn bộ nhãn. Ghi đúng nhãn `0: smoke`, `1: fire`, weight mới và `imgsz=640`.
- Mã sinh viên đúng là **0211268**, do người dùng xác nhận ngày 26/10/2026. Không sao chép mã 0205268 trên bìa tài liệu gốc.
- Dùng kết quả train 100 epoch và test mới khi trích số liệu. Tách số liệu **validation khi train** khỏi số liệu **test sau train**. Không dùng kết quả thử 1 epoch làm kết quả chính thức.
- Số liệu, hình và ví dụ phải có đường dẫn hoặc nguồn kiểm tra được. Nếu chưa có phép đo, bản nộp ghi cụ thể “chưa đo”, “chưa tính” hoặc “chưa đánh giá”, kèm lý do và giới hạn suy luận; không để nhãn biên tập `CHỜ BỔ SUNG` trong báo cáo cuối và không tự điền số liệu ước lượng.

## 3. Diễn giải kết quả cho đúng mức

- Với test ảnh, báo cáo Precision, Recall, mAP50, mAP50–95 và số ảnh/đối tượng test; ghi kết quả từng lớp smoke/fire cùng checkpoint và kích thước ảnh dùng để đánh giá.
- Với video, ghi thời lượng, số khung, số lần cảnh báo và số **sự kiện** sau gộp. Không gọi số khung YOLO phát hiện là Recall nếu video chưa có nhãn sự kiện/đối tượng đầy đủ.
- Bảng so sánh ba cấu hình phải dùng cùng đầu ra YOLO và cùng cách tiền xử lý. Nêu rõ optical flow đã giảm số khung xác nhận khói trong video thử, đồng thời có thể chặn khói thật; hai video sạch hiện có chưa đủ chứng minh giảm báo nhầm.
- Tách thời gian xử lý ảnh trên GPU Kaggle khỏi FPS đầu-cuối của ứng dụng video trên máy cá nhân. Không suy ra tốc độ vận hành thực tế chỉ từ thông số mô hình.

## 4. Giữ cách trình bày của DOCX gốc

- Sửa trên **bản sao**, không ghi đè `E:\slide - bao cao\report.docx`. Lưu mọi bản mới, ảnh kiểm tra, cache và môi trường làm việc trên ổ E.
- Khi rà nội dung theo yêu cầu này, **chỉ sửa câu chữ trong các đoạn, chú thích và ô bảng liên quan**; giữ nguyên font, màu, cỡ chữ, lề, kiểu đoạn, hình, vị trí bảng và bố cục đang dùng. Chỉ cập nhật mục lục nếu tiêu đề hoặc số trang thực sự thay đổi.
- Giữ thứ tự sáu chương, bìa, tóm tắt, tài liệu tham khảo và phụ lục. Giữ tối đa kiểu chữ, màu, cỡ, căn lề, khoảng đoạn, ngắt trang, bảng, hình, chú thích, đầu/chân trang và số trang theo bản gốc. Có thể chỉnh lỗi dàn trang của bản gốc cho nhất quán.
- Mục lục phải là **mục lục tự động**: ba cấp rõ ràng, thụt lề đều, dấu chấm dẫn, số trang căn thẳng phải. Cập nhật mục lục và số trang sau lần sửa cuối.
- Hình, bảng và đoạn code phải có chú thích, được đặt gần phần giải thích. Không dùng hình mô hình cũ như bằng chứng của mô hình mới. Không để bảng bị tách mất hàng tiêu đề, chữ tràn lề hay chú thích lạc trang.
- Trước khi giao, xuất trang để xem trực quan toàn bộ tài liệu mới, đối chiếu bìa/mục lục/trang chương/bảng/hình với DOCX gốc và kiểm tra tài liệu gốc vẫn nguyên vẹn.

### 4.1. Mẫu định dạng bắt buộc khi dựng lại

- **Font phải khớp bằng thuộc tính thực, không chỉ trông giống:** `Normal` Times New Roman 11 pt, thân bài `Body Text` Times New Roman 12 pt, tiêu đề chương/mục/tiểu mục Times New Roman lần lượt 17/14/12 pt. Đặt `w:rFonts` cho Latin và chữ Việt trong các style này; giữ chữ đơn cách ở listing code. Không đổi toàn tài liệu sang font khác.
- Dùng trang A4. Vùng chữ thực tế khoảng 3,5 cm từ mép trái và 2,5 cm từ mép phải; thân bài căn đều, giãn dòng khoảng 1,566; đoạn tiếp theo có thể thụt dòng đầu 1,27 cm, khoảng trước khoảng 6 pt theo mẫu. Không thêm khoảng trắng lớn để lấp trang.
- Bìa giữ vị trí các khối như bản gốc. Tóm tắt và **trang đầu các chương 1–6** bắt đầu tiêu đề ở khoảng 2,4 cm từ mép trên, không bị đẩy xuống giữa trang. Mục lục, tài liệu tham khảo và phụ lục A bắt đầu tiêu đề ở khoảng 5 cm; phụ lục B bắt đầu ở khoảng 2,4 cm. Trang đầu chương không có header; trang nội dung sau đó dùng header chữ nghiêng, đường kẻ xanh và số trang giữa chân trang.
- Mục lục tự động bám mẫu: tiêu đề “Mục lục” đen; mục cấp 1 xanh đậm, đậm, **không có chấm dẫn**; cấp 2/3 có chấm dẫn, thụt khoảng 0,6/1,5 cm; mọi số trang căn cùng một trục bên phải. Cập nhật trường mục lục trong Word sau lần sửa cuối.
- Đặt Times New Roman ở cấp style **và** trực tiếp cho các run ở bìa, tiêu đề mục lục và các dòng mục lục; gỡ thuộc tính font theme đang ghi đè. Dòng mục lục phải có màu theo mẫu, không gạch chân. Đặt tab căn phải và dấu chấm dẫn trực tiếp trên từng đoạn mục lục, không chỉ trong style.
- Hai đường xanh của bìa phải nhìn thấy cả khi trình xem không hỗ trợ đối tượng neo nổi; ưu tiên đường viền đoạn có thể đọc được ở nhiều trình xem, đồng thời không để bản Word xuất PDF xuất hiện đường kẻ kép.
- Giữ khung “Vấn đề đặt ra” ở chương 1 theo mẫu: thanh tiêu đề xanh với chữ trắng, phần giải thích nền xanh rất nhạt và viền xanh; viết lại nội dung cho bài toán fire/smoke hiện tại. Giữ chú thích bảng ở trên, chú thích hình và listing ở dưới, bảng đầu xanh chữ trắng, hàng xen kẽ trắng/xanh nhạt.
- Khi so trang, dùng ít nhất bìa; tóm tắt; hai trang mục lục; trang đầu mỗi chương; trang có khung; trang có bảng, hình, listing; tài liệu tham khảo và hai phụ lục. Sửa sự lệch rõ rệt trước khi giao; chỉ khác số trang khi nội dung cũ đã bị bỏ hoặc nội dung mới cần thêm, không kéo dài văn bản bằng chữ vô nghĩa để ép số trang.
- Không coi bản PDF xuất từ Microsoft Word là phép kiểm tra duy nhất. Khi so hình thức bản mới với bản gốc, phải mở **cả hai trong cùng ứng dụng và cùng mức zoom**; WPS Office là ứng dụng người dùng đã mở báo cáo gốc. Trình xem DOCX trong Codex hiện không thể dùng để đánh giá chấm dẫn và vị trí số trang vì nó hiển thị sai tab của mục lục. Kiểm tra bìa, ba cấp mục lục, chấm dẫn, số trang căn phải và font trong WPS; nếu chưa kiểm tra được, nêu rõ giới hạn.

## 5. Khi giao bản sửa hoặc nhờ AI viết tiếp

- Nói ngắn gọn phần nào giữ, sửa, bỏ; nêu file đầu ra với **đường dẫn đầy đủ trên ổ E**.
- Chỉ rõ kết quả nào đã có bằng chứng và phép đo nào chưa thực hiện; trong bản nộp dùng câu diễn đạt hoàn chỉnh, không dùng `CHỜ BỔ SUNG`.
- Giải thích thay đổi quan trọng bằng lời dễ hiểu, rồi nêu **một việc cụ thể tiếp theo** mà người học có thể tự kiểm tra hoặc làm.
