# Hướng dẫn tập trình bày đồ án phát hiện cháy và khói

Tài liệu này dùng cùng báo cáo cuối `E:\DA_TGMT\report_revision\Fire_detection.docx` (bản bảo vệ `E:\DA_TGMT\BAO_VE\smoke_fire_detection.docx`) và slide bảo vệ `E:\DA_TGMT\BAO_VE\smoke_fire_detection.pptx`. Phần **Bài nói mẫu** viết như lời một sinh viên đang bảo vệ đồ án. Hãy hiểu ý rồi nói bằng lời của mình; không cần học thuộc từng câu. Các phần **Giải thích** và **Câu hỏi thường gặp** dùng để chuẩn bị trả lời, không đọc nguyên văn khi trình bày.

## 1. Bảy ý cần nhớ trước khi tập nói

| Câu hỏi | Câu trả lời ngắn |
|---|---|
| Bài toán là gì? | Xác định vị trí **lửa** và **khói** trong ảnh hoặc khung hình video, sau đó tạo cảnh báo và lưu bằng chứng trên máy. |
| Dữ liệu từ đâu? | Bộ **Smoke-Fire-Detection-YOLO** do `sayedgamal99` đăng trên Kaggle; ảnh và nhãn hộp giới hạn đã có sẵn. Em không tự chụp hay tự gán toàn bộ nhãn. |
| Mô hình nào? | **YOLOv8n** khởi tạo từ `yolov8n.pt`, rồi **fine-tune** cho hai lớp `0: smoke`, `1: fire`. Đây không phải mạng nơ-ron do em thiết kế từ đầu. |
| Huấn luyện thế nào? | Một lần huấn luyện chính thức **100 epoch**, toàn bộ dữ liệu train (`fraction=1`), `imgsz=640`, `batch=16`, một GPU Tesla T4 trên Kaggle. Lần 1 epoch trên 2% dữ liệu trước đó chỉ để thử môi trường. |
| Kết quả test ảnh? | Trên **4.291 ảnh test hợp lệ**, **5.166 đối tượng**: Precision **74,27%**, Recall **67,45%**, mAP50 **73,70%**, mAP50–95 **41,63%**. mAP50 của smoke **79,13%**, fire **68,27%**. |
| Chương trình video làm gì thêm? | Đọc từng khung, chạy YOLO, kiểm tra chuyển động ở vùng khói, xác nhận bằng cửa sổ N/M, rồi lưu ảnh cảnh báo, video và nhật ký cục bộ. |
| Giới hạn quan trọng? | Mới kiểm tra trên bốn video chọn trước. Một phép chạy video sạch trên CPU đạt 4,32 khung/giây khi tính cả khởi động và ghi MP4; chưa gán nhãn sự kiện video đầy đủ và chưa thử trên Jetson Nano. |

**Phân biệt ba thứ:** hộp YOLO là *dự đoán trên một khung hình*; **lần báo** là lúc chương trình lưu một cảnh báo sau khi qua bộ lọc và khoảng chờ; **sự kiện** là nhiều lần báo gần nhau được gộp thành một đợt cháy hoặc khói trong một video. Không dùng ba từ này thay nhau.

## 2. Bài nói mẫu khoảng 5–6 phút

### Mở đầu — khoảng 30 giây

> Em chào thầy cô. Đồ án của em là hệ thống phát hiện lửa và khói trong ảnh, video bằng YOLOv8n. Mục tiêu là xác định vùng có dấu hiệu lửa hoặc khói, hiển thị vị trí để người xem kiểm tra, và lưu cảnh báo trên máy. Em kế thừa mã nguồn của một dự án rộng hơn, sau đó thu hẹp phạm vi về lửa và khói. Bản hiện tại không trình bày phát hiện té ngã hay gửi Telegram như chức năng đã hoàn thành.

### Dữ liệu và huấn luyện — khoảng 1 phút

> Em dùng bộ Smoke-Fire-Detection-YOLO được công bố trên Kaggle. Bộ dữ liệu có ảnh và file nhãn theo định dạng YOLO; số 0 là khói và số 1 là lửa. Em kiểm tra đường dẫn dữ liệu, cách ánh xạ lớp và một số ảnh đi kèm nhãn trước khi train. Em giữ cách chia train, validation và test có sẵn. Có 14.101 ảnh train, 3.094 ảnh validation và 4.291 ảnh test được bộ nạp sử dụng sau khi bỏ qua các mẫu không hợp lệ.
>
> Em chọn YOLOv8n vì đây là phiên bản nhỏ của YOLOv8 và có thể fine-tune từ trọng số `yolov8n.pt`. Em không xây một kiến trúc mạng mới. Lần train chính thức chạy 100 epoch trên một GPU Tesla T4 của Kaggle, với kích thước đầu vào 640 và batch 16. Sau train, em dùng file `best.pt` của lần chạy này để đánh giá và chạy chương trình video. Lần chạy 1 epoch trên 2% dữ liệu trước đó chỉ dùng kiểm tra xem notebook và đường dẫn hoạt động.

### Cách chương trình xử lý video — khoảng 1 phút

> Khi đọc video, chương trình xử lý từng khung hình. YOLO trả về các hộp giới hạn, tên lớp và điểm tin cậy. Với khói, chương trình còn tính optical flow giữa hai khung liên tiếp trong vùng hộp để lấy một điểm chuyển động; vùng có điểm thấp hơn ngưỡng có thể bị loại. Sau đó, bộ lọc N/M xem tín hiệu có xuất hiện đủ lâu hay không: lửa cần ít nhất 10 trong 20 khung gần nhất, khói cần 12 trong 20 khung. Khi đủ điều kiện, chương trình tạo cảnh báo cục bộ, lưu ảnh và nhật ký. Khoảng chờ 90 khung giúp tránh lưu một cảnh báo ở mọi khung liên tiếp.
>
> Trên video trình bày, em giữ giao diện gọn: chỉ có hộp và chữ **FIRE** hoặc **SMOKE**. Điểm tin cậy, điểm chuyển động và trạng thái bộ lọc vẫn có trong dữ liệu lưu để kiểm tra, nhưng không phủ thêm lên video.

### Kết quả — khoảng 1 phút 30 giây

> Em đánh giá `best.pt` trên tập test ảnh độc lập với tập train. Trên 4.291 ảnh hợp lệ và 5.166 đối tượng, Precision trung bình là 74,27%, Recall 67,45%, mAP50 73,70%, mAP50–95 41,63%. mAP50 theo lớp là 79,13% cho khói và 68,27% cho lửa. Những con số này đo khả năng phát hiện hộp trên **ảnh test**; chúng không phải độ chính xác của toàn bộ chương trình video.
>
> Em cũng chạy bốn video demo. Video lửa dài 21,45 giây tạo 8 lần báo, được gộp thành 1 sự kiện. Video khói dài 17,80 giây tạo 3 lần báo, cũng gộp thành 1 sự kiện. Hai video sạch dài 15,07 và 10,27 giây không có cảnh báo quan sát được. Tổng thời lượng video sạch khoảng 25,33 giây; phạm vi này còn nhỏ nên em không kết luận hệ thống đã hết báo nhầm.
>
> Để xem tác dụng của xử lý video, em tính lại ba cấu hình từ **cùng đầu ra YOLO đã lưu**: chỉ YOLO; YOLO cộng N/M; YOLO cộng N/M và optical flow. Ở video khói, số khung được xác nhận thay đổi từ 376 sang 385 rồi còn 63. Số 385 có thể lớn hơn 376 vì cửa sổ N/M còn giữ trạng thái qua vài khung không có hộp. Flow làm giảm mạnh số khung xác nhận khói, nhưng cũng có nguy cơ chặn khói thật. Hai video sạch đều có 0 cảnh báo ngay từ YOLO, nên thí nghiệm này chưa chứng minh flow làm giảm báo nhầm trên video sạch.

### Cho xem video và kết luận — khoảng 1 phút

> Sau đây em cho xem ngắn một đoạn lửa và một đoạn khói. Hộp và chữ trên màn hình là dự đoán YOLO; cảnh báo thực tế còn phải qua các điều kiện của chương trình. Em lưu kết quả để có thể đối chiếu thời điểm báo với nhật ký.
>
> Kết luận của em là đã fine-tune và đánh giá được mô hình hai lớp trên tập test ảnh, tích hợp được chương trình video và kiểm tra các bộ lọc trên bốn clip. Trên máy cá nhân dùng CPU, một phép chạy video sạch 308 khung mất 71,252 giây tính cả khởi động và ghi MP4, tương đương 4,32 khung/giây; chưa đủ để xử lý video nguồn 30 khung/giây theo thời gian thực. Em chưa gán nhãn sự kiện cho nhiều video để tính Precision và Recall theo sự kiện, và chưa thử trên thiết bị biên.

**Hai video để mở khi bảo vệ:**

- Lửa: `E:\DA_TGMT\DATA\results\presentation_simple\video_chay\annotated.mp4`.
- Khói: `E:\DA_TGMT\DATA\results\presentation_simple\video_khoi\annotated.mp4`.

Nếu thời gian rất ngắn, chỉ chiếu khoảng 10–15 giây tiêu biểu của mỗi video. Hai video được tạo lại để gọn phần hiển thị; số cảnh báo và nhật ký khung hình đã được đối chiếu với lần chạy trước. Bảng video sạch trong báo cáo lấy từ lần chạy đủ khung tại `E:\DA_TGMT\DATA\results\main_v2_conf025_side640`.

## 3. Bản nói gọn khoảng 2 phút

> Em làm đề tài phát hiện lửa và khói trong ảnh, video. Em dùng bộ dữ liệu đã gán nhãn trên Kaggle, với lớp 0 là smoke và lớp 1 là fire. Em fine-tune YOLOv8n từ trọng số có sẵn trong 100 epoch trên Kaggle T4; đây không phải mô hình do em thiết kế từ đầu. Trọng số `best.pt` được đánh giá trên 4.291 ảnh test hợp lệ và đạt Precision 74,27%, Recall 67,45%, mAP50 73,70%.
>
> Trong video, YOLO tìm hộp lửa/khói. Chương trình kiểm tra chuyển động của khói, xác nhận tín hiệu qua cửa sổ 20 khung rồi mới lưu cảnh báo. Video lửa tạo 8 lần báo, video khói 3 lần báo; mỗi video được gộp thành 1 sự kiện. Hai video sạch tổng cộng 25,33 giây không có cảnh báo. Em đã so sánh YOLO, YOLO cộng N/M và YOLO cộng N/M với optical flow trên cùng dữ liệu khung hình. Flow giảm số khung khói được xác nhận nhưng có thể làm bỏ sót khói thật.
>
> Kết quả của em chứng minh chương trình hoạt động trên tập test ảnh và bốn video này. Một lần chạy video sạch trên CPU đạt 4,32 khung/giây khi tính toàn bộ thời gian lệnh, thấp hơn 30 khung/giây của video nguồn. Em chưa thử trên Jetson Nano nên không khẳng định khả năng chạy thời gian thực trên thiết bị đó.

## 4. Giải thích nhanh các thuật ngữ để không học vẹt

| Thuật ngữ | Hiểu đơn giản | Khi nói cần tránh |
|---|---|---|
| **Nhãn** | Đáp án gốc của dữ liệu: lớp nào và hộp nằm ở đâu. `0: smoke`, `1: fire`. | Đừng nói `fire` và `smoke` là hai mô hình riêng. |
| **YOLOv8n** | Mạng phát hiện đối tượng; chữ `n` là biến thể nhỏ. | Đừng nói em phát minh ra YOLOv8n. |
| **Fine-tune** | Tiếp tục huấn luyện trọng số đã có trên dữ liệu đúng hai lớp của bài. | Đừng nói train từ số 0. |
| **Epoch** | Một lượt mô hình học qua tập train. | 100 epoch không có nghĩa mỗi ảnh được xem đúng 100 lần theo cùng một cách, vì có tăng cường dữ liệu. |
| **Batch 16** | Mỗi bước cập nhật dùng một nhóm khoảng 16 ảnh. | Đừng nhầm batch với số lớp. |
| **`best.pt`** | Tệp lưu trọng số được chọn từ quá trình train/validation; dùng để suy luận và test. | Không thể “mở như ảnh” để nhìn các hộp; phải nạp tệp vào YOLO rồi chạy ảnh/video. |
| **Precision** | Trong các hộp mô hình dự đoán là đúng lớp, phần nào thực sự đúng theo cách đánh giá. | Không gọi đây là xác suất đúng của một hộp. |
| **Recall** | Trong các đối tượng thật cần tìm, mô hình tìm được phần nào. | Không lấy số khung video có hộp chia tổng số khung để gọi là Recall. |
| **mAP50** | Điểm tổng hợp đường Precision–Recall khi hộp dự đoán được so với nhãn ở mức IoU 0,5. | Không gọi mAP50 là độ chính xác 73,70% của toàn hệ thống cảnh báo. |
| **Optical flow** | Ước lượng sự dịch chuyển giữa hai khung hình; bài này chỉ dùng để kiểm tra vùng khói YOLO đã tìm. | Không nói flow tự nhận diện khói nếu không có YOLO. |
| **N/M** | Trong M khung gần nhất, cần ít nhất N khung có tín hiệu hợp lệ để xác nhận. | Không nói cần N khung liên tục. |
| **Ablation** | Thử bỏ hoặc thêm từng thành phần để xem kết quả thay đổi ra sao. | Không diễn giải bảng ba cấu hình là ba lần train mô hình khác nhau. |

**Một điểm kỹ thuật cần hiểu:** luồng code hiện tại tính điểm optical flow cho hộp khói **trước khi đưa tín hiệu khói vào cửa sổ N/M**. Với lửa, tín hiệu YOLO đi thẳng vào cửa sổ N/M. Tên cấu hình “YOLO + N/M + flow” là cách gọi các thành phần có mặt, không phải thứ tự thực thi từng dòng code.

## 5. Thầy có thể hỏi gì và em trả lời ra sao?

### 1. Em lấy dữ liệu ở đâu? Em tự gán nhãn không?

> Em dùng bộ Smoke-Fire-Detection-YOLO trên Kaggle của tài khoản sayedgamal99. Ảnh và nhãn YOLO đã có sẵn. Em kiểm tra đường dẫn, cấu trúc nhãn và mẫu ảnh trước khi train, chứ không nhận là mình tự chụp và gán toàn bộ dữ liệu. Một dòng nhãn ghi class ID cùng tâm, rộng và cao của hộp ở dạng chuẩn hóa.

Nếu thầy hỏi **một dòng `1 ...` nghĩa là gì**: số đầu `1` là lớp **fire**; bốn số sau mô tả hộp. Với bộ dữ liệu này `0` mới là **smoke**.

### 2. Em tự xây mô hình hay dùng mô hình có sẵn?

> Em dùng kiến trúc YOLOv8n có sẵn và trọng số khởi tạo `yolov8n.pt`, rồi fine-tune trên dữ liệu lửa/khói. Phần em thực hiện trong phạm vi đồ án là chuẩn bị và kiểm tra dữ liệu, chạy huấn luyện, đánh giá trọng số mới, tích hợp chương trình video và kiểm tra bộ lọc cảnh báo. Em không tuyên bố đã đề xuất kiến trúc mạng mới.

Nếu hỏi về **mã nguồn kế thừa**, nói rõ: mã ban đầu thuộc bài SafeVision AI rộng hơn; bản này giữ nhánh fire/smoke, bỏ chức năng té ngã và Telegram khỏi phạm vi hoàn thành. Không nói mình viết toàn bộ mã ban đầu từ đầu.

### 3. Vì sao nói đã train 100 epoch khi trước đây mới thử 1 epoch?

> Lần 1 epoch trên 2% dữ liệu chỉ là phép chạy thử để xem môi trường Kaggle, đường dẫn và thư viện hoạt động. Sau đó em có lần huấn luyện chính thức `train_official_v2` với `epochs=100`, `fraction=1`, `batch=16`, `imgsz=640`. Báo cáo dùng log và `best.pt` của lần chính thức, không dùng số liệu của dry run làm kết quả.

### 4. Train, validation và test khác nhau thế nào?

> Train dùng để cập nhật trọng số. Validation được theo dõi trong lúc train và giúp chọn checkpoint. Test được dùng sau khi train để báo cáo kết quả cuối. Em không lấy số validation ở epoch 100 rồi gọi là kết quả test. Test thực tế có 4.291 ảnh hợp lệ sau khi bộ nạp bỏ qua 15 tệp.

### 5. Nếu thầy bảo 73,70% nghĩa là mô hình đúng 73,70% mọi trường hợp?

> Không ạ. 73,70% là **mAP50 trung bình trên hai lớp của tập test ảnh có nhãn hộp**. Nó không phải xác suất đúng của từng hộp, cũng không phải tỷ lệ đúng của cảnh báo video. Mỗi lớp khác nhau: smoke 79,13%, fire 68,27% theo mAP50.

### 6. Vì sao trong bảng N/M có 385 khung khói, nhiều hơn 376 khung YOLO?

> YOLO đếm khung hiện tại có hộp khói. Cửa sổ N/M nhớ tín hiệu của các khung gần đây. Khi một vài khung sau không còn hộp, trạng thái xác nhận vẫn có thể còn đúng, nên số khung xác nhận có thể lớn hơn số khung hiện tại có hộp. Đây không phải thêm 9 khung khói thật theo nhãn gốc.

### 7. Optical flow đã chứng minh giảm báo giả chưa?

> Chưa. Trên video khói thử nghiệm, nó làm số khung xác nhận khói giảm từ 385 xuống 63, nhưng khói thật cũng có thể bị chặn. Hai video sạch đều không có cảnh báo từ YOLO, nên chưa có tình huống báo giả để chứng minh bộ lọc đã sửa được. Muốn kết luận cần nhiều video âm và video khói có nhãn thời điểm/đối tượng.

### 8. `smoke_score` tính thế nào? Vì sao vùng đèn tĩnh có thể bị loại?

> Chương trình dùng Farneback optical flow trong hộp khói YOLO. Các pixel chuyển động được xét theo độ lớn, độ phân tán hướng và xu hướng đi lên; ba phần được ghép với trọng số 0,35, 0,45 và 0,20. Nếu dưới 10% pixel trong vùng có độ lớn chuyển động vượt 0,3 thì score trả về 0. Một phép thử lặp lại khung đèn đường tĩnh cho 12 cặp khung sau khung đầu có điểm 0. Đây là kiểm tra kỹ thuật của phép tính, không phải bằng chứng chung rằng mọi đèn đường đều không báo giả.

### 9. Vì sao 8 lần cảnh báo lửa chỉ là 1 sự kiện?

> Chương trình có khoảng chờ 90 khung nên trong cùng một đám lửa đang tồn tại có thể lưu nhiều lần báo theo thời gian. Khi tổng hợp báo cáo, các lần báo cách nhau không quá 60 giây được gộp thành một sự kiện trong video đó. Vì vậy 8 lần báo trong clip lửa này thuộc cùng 1 sự kiện quan sát được.

### 10. Em đã chứng minh hệ thống chạy thời gian thực chưa? Có chạy Jetson không?

> Chưa. Thời gian suy luận trên ảnh test bằng GPU Kaggle không phải tốc độ xử lý video trên máy cá nhân. Em đã chạy một video sạch 308 khung trên CPU, không mở cửa sổ nhưng có ghi MP4; cả lệnh mất 71,252 giây, tương đương 4,32 khung/giây. Đây là một lần chạy, gồm cả thời gian khởi động. Em chưa thử trên Jetson Nano nên không kết luận tốc độ của thiết bị đó.

### 11. Vì sao video chỉ hiện một chữ FIRE hoặc SMOKE dù có nhiều hộp?

> Đây là lựa chọn trình bày để video dễ nhìn. Chương trình vẫn vẽ các hộp YOLO, nhưng chỉ ghi một tên cho mỗi lớp xuất hiện trong khung hình. Việc bỏ điểm số và thanh trạng thái khỏi video không thay đổi điều kiện xác nhận hay nhật ký đã lưu.

### 12. Dữ liệu và video có hạn chế gì?

> Bộ ảnh có thể có mẫu trùng hoặc cảnh tương tự giữa các tập; em chưa hoàn thành kiểm tra độc lập theo nguồn ảnh. Nguồn bốn video đã được truy lại và ghi ở tệp `DATA/videos/NGUON_VIDEO.md`. Bốn clip ngắn chưa đủ đánh giá ở nhiều ánh sáng, góc nhìn và loại khói. Em sẽ bổ sung video có nhãn sự kiện và đo Precision/Recall theo sự kiện trong bước tiếp theo.

## 6. Khi không chắc câu trả lời

Nói phần mình **đã kiểm tra được** và phần **chưa đo**, thay vì đoán. Ví dụ:

> Phần đó hiện em chưa có phép đo đủ tin cậy. Báo cáo ghi rõ giới hạn thay vì tự điền số liệu. Điều em đã kiểm tra là kết quả trên 4.291 ảnh test, nhật ký của bốn video và một phép đo tốc độ trên CPU. Để trả lời chính xác hơn, em cần bổ sung dữ liệu có nhãn hoặc phép chạy trên thiết bị đích.

Nếu được hỏi ai làm phần nào, trả lời đúng quá trình: **mã kế thừa đã được chỉnh sửa; em sử dụng công cụ hỗ trợ để rà soát và biên tập, sau đó đối chiếu code, cấu hình và log**. Tránh nhận toàn bộ mã ban đầu là mình tự viết.

## 7. Tự tập một vòng trước buổi bảo vệ

1. Đọc **Bảy ý cần nhớ** rồi tự nói lại mà không nhìn file. Dấu hiệu làm đúng: phân biệt được train, test, cảnh báo và sự kiện.
2. Bấm giờ nói **Bài nói mẫu** một lần. Khi đến phần video, chỉ vào hộp và chữ FIRE/SMOKE, rồi giải thích đó là phần hiển thị; cảnh báo có điều kiện riêng.
3. Nhờ một người hỏi ngẫu nhiên ba câu ở mục 5. Nếu không trả lời được, đọc lại đúng phần giải thích thuật ngữ liên quan rồi thử lần nữa.

### Tệp để đối chiếu nếu thầy yêu cầu bằng chứng

| Cần chứng minh | Tệp trên ổ E |
|---|---|
| Cấu hình train 100 epoch | `E:\DA_TGMT\DATA\training\train_official_v2\fire_smoke_runs\train_official_v2\args.yaml` |
| Trọng số đang dùng | `E:\DA_TGMT\Models\fire_smoke_v2_best.pt` |
| Cấu hình chạy video | `E:\DA_TGMT\fire_detection\config.yaml` |
| Luồng YOLO, flow, N/M và cảnh báo | `E:\DA_TGMT\fire_detection\pipeline.py` |
| Nhật ký của bốn video | `E:\DA_TGMT\DATA\results\main_v2_conf025_side640` |
| Bảng ba cấu hình | `E:\DA_TGMT\DATA\results\main_v2_conf025_side640\ablation_saved_observations\comparison.json` |
| Báo cáo Word hoàn chỉnh | `E:\DA_TGMT\BAO_VE\smoke_fire_detection.docx` |

**Việc tự làm ngay:** mở hai video ở mục 2, tập nói riêng đoạn **Kết quả** và **Cho xem video** một lần, rồi tự trả lời câu 5, 7 và 10 mà không nhìn đáp án. Ba câu này kiểm tra bạn có phân biệt được chỉ số ảnh, hiệu quả bộ lọc và giới hạn thời gian thực hay không.
