# Prompts cho Antigravity: app lấy transcript YouTube

## Chuẩn bị (làm 1 lần)
1. Tạo thư mục `youtube-transcript` ở đâu đó dễ nhớ.
2. Copy file `GEMINI.md` vào thư mục đó (thư mục gốc, không phải thư mục con).
3. Mở **đúng thư mục này** làm workspace trong Antigravity.
4. Đặt mức tự chủ của agent ở mức hỏi trước khi chạy lệnh.

## Quy trình mỗi vòng
1. Gửi prompt của vòng đó.
2. Đọc kế hoạch agent đưa ra, đồng ý hoặc chỉnh.
3. Để agent làm, duyệt các lệnh nó xin chạy.
4. Tự chạy thử kết quả.
5. Gửi prompt giải thích (ở cuối file) trước khi sang vòng sau.

---

## Vòng 1: Môi trường

```text
Vòng 1: chuẩn bị môi trường.
Hãy tạo môi trường ảo Python (venv) cho project này, tạo requirements.txt
gồm streamlit và youtube-transcript-api, rồi tạo app.py chỉ hiện dòng chữ
"Xin chào" bằng Streamlit để tôi kiểm tra môi trường chạy được.
Cho tôi biết chính xác các lệnh trên Windows để kích hoạt môi trường ảo và
chạy app. Chưa viết chức năng nào khác.
```

Kiểm tra: mở được trang web local và thấy chữ "Xin chào".

---

## Vòng 2: Lấy transcript (chưa có giao diện)

```text
Vòng 2: viết transcript.py.
Cần 2 hàm:
1. Hàm nhận link YouTube dạng youtube.com/watch?v=..., trả về mã video.
   Link không hợp lệ thì báo lỗi rõ ràng.
2. Hàm nhận mã video, lấy phụ đề có sẵn (ưu tiên tiếng Anh), trả về danh sách
   gồm thời điểm bắt đầu và nội dung từng đoạn.
Nếu video không có phụ đề hoặc không kết nối được thì báo lỗi riêng cho từng
trường hợp. Chưa làm giao diện.
Sau đó hướng dẫn tôi chạy thử trong terminal với một link thật.
```

Kiểm tra: terminal in ra được transcript của một video có phụ đề. Thử thêm một link sai để xem thông báo lỗi.

---

## Vòng 3: Giao diện cơ bản

```text
Vòng 3: viết app.py.
Giao diện gồm: tiêu đề, ô dán link, nút "Lấy transcript".
Khi bấm nút, gọi các hàm trong transcript.py và hiển thị transcript trên
trang dưới dạng văn bản. Chưa làm công tắc mốc thời gian và nút Download.
Giữ code ngắn và dễ đọc.
```

Kiểm tra: dán link thật, bấm nút, thấy transcript.

---

## Vòng 4: Công tắc mốc thời gian và Download

```text
Vòng 4: thêm 2 chức năng vào app.py.
1. Công tắc bật/tắt mốc thời gian. Khi bật, mỗi dòng có dạng [mm:ss] trước
   nội dung. Đổi công tắc thì nội dung đổi ngay, không phải lấy lại từ YouTube.
2. Nút Download file .txt. Nội dung file giống hệt nội dung đang hiển thị
   (có hoặc không có mốc thời gian tùy công tắc). App không tự lưu file.
```

Kiểm tra: bật/tắt công tắc, bấm Download, mở file .txt xem có đúng không.

---

## Vòng 5: Xử lý lỗi

```text
Vòng 5: hoàn thiện xử lý lỗi trong app.py.
Hiển thị thông báo tiếng Việt, rõ ràng, trong các trường hợp:
- Link không hợp lệ.
- Video không có phụ đề.
- Không kết nối được hoặc bị YouTube chặn.
App không được bị treo hay hiện lỗi kỹ thuật dài. Sau đó liệt kê cho tôi các
trường hợp tôi nên tự thử để kiểm tra từng thông báo.
```

Kiểm tra: tự thử link sai, video không có phụ đề, và tắt wifi rồi thử.

---

## Prompt giải thích (dùng sau mỗi vòng)

```text
Giải thích các file bạn vừa viết cho tôi, từng phần một, bằng ngôn ngữ đơn giản.
Chỉ ra 2 chỗ quan trọng nhất tôi cần hiểu và 1 lỗi người mới hay mắc ở phần này.
Cuối cùng cho tôi một bài tập nhỏ để tự sửa code (ví dụ đổi một dòng chữ hoặc
một hành vi) và nói rõ kết quả mong đợi.
```

## Khi gặp lỗi

```text
App bị lỗi. Đây là những gì tôi làm: [mô tả]. Đây là thông báo lỗi:
[dán nguyên văn]. Hãy giải thích nguyên nhân bằng ngôn ngữ đơn giản trước,
rồi mới sửa.
```

Nếu thư viện lấy transcript bỗng ngừng chạy với mọi video, thử cập nhật trước: `pip install --upgrade youtube-transcript-api`.