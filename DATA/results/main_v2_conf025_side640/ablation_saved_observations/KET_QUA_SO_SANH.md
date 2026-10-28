# So sánh trên bốn video demo

## Phương pháp

Tính lại quyết định từ kết quả từng khung hình đã lưu của cùng một lần chạy YOLO. Không chạy lại suy luận. Cả ba cách dùng cùng weight, ngưỡng conf=0,25, imgsz=640; ảnh được thu nhỏ cạnh dài còn 640 pixel trước xử lý. N/M: lửa 10/20, khói 12/20; ngưỡng chuyển động 0,35. Mỗi clip bắt đầu với trạng thái rỗng. Cùng dùng thời gian chờ 90 khung hình và ưu tiên cảnh báo lửa. Gộp các lần báo cách nhau không quá 60 giây thành một sự kiện, riêng từng clip.

Đã đối chiếu: cách đầy đủ tái tạo đúng từng quyết định xác nhận, thời điểm và loại cảnh báo trong nhật ký gốc của cả bốn video.

## Bảng ngắn để trình bày

| Cách xử lý | Khung hình xác nhận lửa / 643 (video lửa) | Khung hình xác nhận khói / 534 (video khói) | Sự kiện cảnh báo trên hai video sạch |
|---|---:|---:|---:|
| YOLO | 643 | 376 | 0 |
| YOLO + N/M | 634 | 385 | 0 |
| YOLO + N/M + optical flow | 634 | 63 | 0 |

Với YOLO đơn thuần, cột xác nhận chính là khung hình có phát hiện. Đây là số khung hình kích hoạt điều kiện, không phải precision, recall hay mAP. N/M có thể duy trì xác nhận khi khung hình hiện tại không có phát hiện, nên số này có thể tăng.

## Chi tiết cảnh báo

| Video | Thời lượng (giây) | Cách xử lý | Sự kiện | Số lần báo | Lần báo đầu từ đầu clip (giây) |
|---|---:|---|---:|---:|---:|
| video_chay | 21.45 | YOLO | 1 | 8 | 0.000 |
| video_chay | 21.45 | YOLO + N/M | 1 | 8 | 0.300 |
| video_chay | 21.45 | YOLO + N/M + optical flow | 1 | 8 | 0.300 |
| video_khoi | 17.80 | YOLO | 1 | 6 | 0.000 |
| video_khoi | 17.80 | YOLO + N/M | 1 | 6 | 0.367 |
| video_khoi | 17.80 | YOLO + N/M + optical flow | 1 | 3 | 0.367 |
| video_khong_chay | 15.07 | YOLO | 0 | 0 | — |
| video_khong_chay | 15.07 | YOLO + N/M | 0 | 0 | — |
| video_khong_chay | 15.07 | YOLO + N/M + optical flow | 0 | 0 | — |
| video_khong_chay2 | 10.27 | YOLO | 0 | 0 | — |
| video_khong_chay2 | 10.27 | YOLO + N/M | 0 | 0 | — |
| video_khong_chay2 | 10.27 | YOLO + N/M + optical flow | 0 | 0 | — |

## Cách diễn giải và giới hạn

- Hai video sạch có tổng thời lượng 25.33 giây. Cả ba cách đều không có cảnh báo trên các clip này.
- Cả ba cách đều tạo cảnh báo lửa trên video lửa và cảnh báo khói trên video khói. Số sự kiện phụ thuộc quy tắc gộp, không phải số sự kiện thực tế được gán nhãn.
- Bộ lọc chuyển động làm giảm rõ số khung hình xác nhận khói trong clip khói. Bộ video này chưa chứng minh bộ lọc giảm báo nhầm so với YOLO.
- Chưa có nhãn đúng/sai cho từng khung hình hoặc mốc bắt đầu sự kiện. Không gọi số khung hình xác nhận là độ chính xác hoặc recall; mốc báo đầu tính từ đầu clip không phải độ trễ so với lúc bắt đầu cháy.
- Không đo hoặc so sánh FPS, tốc độ suy luận trong phép tính lại này.
- Không thay đổi cấu hình chương trình hoặc weight sau phép so sánh.

## Gợi ý trình bày ngắn

Chiếu một đoạn video lửa, một đoạn video khói, rồi nêu kết quả hai video sạch. Dùng bảng ba dòng để giải thích tác động của N/M và optical flow. Kết luận giới hạn trong bốn video demo; không khẳng định optical flow tốt hơn khi số liệu chưa chứng minh.
