# Bản đọc Markdown của đồ án

Bắt đầu từ [hướng dẫn ở gốc kho](../../DOC_TRUOC_KHI_SUA.md). Bộ này được tạo ngày 28/10/2026 để đọc và tiếp tục sửa ở máy khác.

- [01 — Code hiện tại](01_CODE_HIEN_TAI.md): nguyên văn 7 file code/cấu hình/thư viện.
- [02 — Báo cáo Word](02_BAO_CAO_WORD.md): văn bản, 13 bảng, 5 công thức và 8 hình từ bản sửa 27/10.
- [03 — PowerPoint](03_BAO_CAO_POWERPOINT.md): chữ, bảng, ghi chú của 11 slide, kèm ảnh slide đã xuất trong lần sửa 27/10.
- [04 — Dữ liệu và kết quả](04_DU_LIEU_VA_KET_QUA.md): các số liệu cùng file bằng chứng để kiểm tra.
- [FILE_MANIFEST.json](FILE_MANIFEST.json): nguồn trích và SHA-256. Đường dẫn nguồn tính từ gốc kho.

Nguồn Word/PPT là `report_revision/fix_review_20261027/output`, khác bộ `BAO_VE`. Không chỉnh Word/PPT bằng cách chỉ sửa Markdown. File Python thật trong `fire_detection` là nguồn chuẩn của code.

## Cập nhật khi nguồn thay đổi

Script [export_markdown.py](tools/export_markdown.py) dùng Python và `lxml`, xác định gốc kho từ vị trí script nên không phụ thuộc ổ E. Từ gốc kho chạy:

```powershell
python docs/markdown/tools/export_markdown.py
```

Script trích lại code, Word/PPT và hình nhúng trong Word, kiểm tra không thiếu đoạn chữ, rồi ghi manifest. Script **không render lại ảnh toàn slide**; sau khi sửa PPT phải xuất lại ảnh bằng PowerPoint hoặc công cụ render phù hợp, thay đúng `assets/slides/slide_01.png` đến `slide_11.png`. Nếu chưa render lại, không dùng ảnh cũ để đánh giá slide mới. Ảnh Word được trích lại nhưng không thể hiện bố cục toàn trang.

Khi sửa kết quả thực nghiệm, cập nhật cả bản đồ bằng chứng. Cần mang theo thư mục `assets` để liên kết hình hoạt động. Mở DOCX/PPTX gốc để kiểm tra font, ngắt trang, vị trí và hiệu ứng.
