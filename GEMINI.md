# GEMINI.md

## Về người dùng
- Tôi là người mới học lập trình, dùng Windows 11.
- Giải thích bằng tiếng Việt, đơn giản, ngắn gọn. Giữ nguyên thuật ngữ tiếng Anh khi cần.
- Mục tiêu của tôi là hiểu code, không chỉ chạy được.

## Cách làm việc
- Trước khi viết code, nói kế hoạch trong 3-5 dòng và chờ tôi đồng ý.
- Mỗi lần chỉ làm đúng 1 vòng việc tôi giao. Không làm trước vòng sau.
- Sau khi viết xong, nói ngắn: file nào được tạo hoặc sửa, mỗi file làm gì.
- Nói rõ cách chạy và cách kiểm tra kết quả.
- Không xóa file, không cài thêm thư viện ngoài danh sách khi chưa hỏi tôi.
- Không biết hoặc không chắc thì nói thẳng, không đoán.

## Về project
Tên: youtube-transcript

Mục tiêu: app chạy local trên máy tôi. Tôi dán link YouTube, app lấy transcript và hiển thị.

Công nghệ:
- Python
- Streamlit (giao diện web chạy local)
- youtube-transcript-api (lấy transcript)
- Dùng môi trường ảo (venv), ghi thư viện vào requirements.txt

Cấu trúc file:
- app.py: giao diện Streamlit
- transcript.py: logic lấy transcript, tách riêng khỏi giao diện
- requirements.txt: danh sách thư viện

## Chức năng
1. Ô dán link và nút "Lấy transcript".
2. Chỉ hỗ trợ link dạng youtube.com/watch?v=... (lấy mã video từ tham số v=). Link khác thì báo không hợp lệ.
3. Chỉ lấy phụ đề có sẵn, ưu tiên tiếng Anh. Không dịch, không tạo phụ đề.
4. Hiển thị transcript trên trang. Có công tắc bật/tắt mốc thời gian (dạng [mm:ss]).
5. Nút Download file .txt, nội dung giống đang hiển thị. Tôi tự chọn nơi lưu. App không tự lưu file.

## Thông báo lỗi (bằng tiếng Việt, rõ ràng, không làm app bị treo)
- Link không hợp lệ.
- Video không có phụ đề.
- Không kết nối được hoặc bị YouTube chặn.

## Không làm (giữ app đơn giản)
- Không dịch, không tóm tắt bằng AI.
- Không đăng nhập, không lưu lịch sử, không dùng database.
- Không hỗ trợ youtu.be, Shorts, playlist.

## Phong cách code
- Code ngắn, dễ đọc, tên biến rõ nghĩa.
- Comment bằng tiếng Việt cho những chỗ quan trọng.
- Mỗi hàm làm một việc.
