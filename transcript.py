import sys
import json
import subprocess
import tempfile
import os
import re
from urllib.parse import urlparse, parse_qs

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def lay_ma_video(url: str) -> str:
    """
    Trích xuất mã video từ link YouTube dạng youtube.com/watch?v=...
    Chỉ hỗ trợ đúng định dạng này, các dạng khác sẽ báo lỗi rõ ràng.
    """
    if not isinstance(url, str):
        raise ValueError("Link không hợp lệ. Vui lòng nhập link dạng https://www.youtube.com/watch?v=...")

    url = url.strip()
    if not url:
        raise ValueError("Vui lòng nhập đường link YouTube.")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    domain = (parsed.netloc or "").lower()
    if domain not in ("www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com"):
        raise ValueError("Link không hợp lệ. Chỉ hỗ trợ link từ domain youtube.com")

    if parsed.path != "/watch" and domain in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        raise ValueError("Link không hợp lệ. Link phải có dạng https://www.youtube.com/watch?v=...")

    if domain == "youtu.be":
        video_id = parsed.path.lstrip("/")
        if not video_id:
            raise ValueError("Link không hợp lệ. Không tìm thấy mã video.")
        return video_id

    params = parse_qs(parsed.query)
    danh_sach_v = params.get("v")

    if not danh_sach_v or not danh_sach_v[0].strip():
        raise ValueError("Link không hợp lệ. Không tìm thấy mã video (tham số v=).")

    return danh_sach_v[0].strip()


def _parse_vtt(content: str) -> list[dict]:
    """Parse nội dung VTT thành danh sách các đoạn."""
    segments = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        time_pattern = re.search(r'(\d+:)?(\d+):(\d+)\.(\d+)\s*-->\s*(\d+:)?(\d+):(\d+)\.(\d+)', line)
        if time_pattern:
            start_match = time_pattern.group(1)
            start_min = int(time_pattern.group(2))
            start_sec = int(time_pattern.group(3))
            start_ms = int(time_pattern.group(4))

            if start_match:
                start_min += int(start_match.rstrip(':')) * 60

            start_time = start_min * 60 + start_sec + start_ms / 1000.0

            text_parts = []
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line == 'WEBVTT' or re.search(r'\d+:\d+:\d+', next_line):
                    break
                text_parts.append(next_line)
                i += 1

            text = ' '.join(text_parts).strip()
            if text:
                segments.append({"start": start_time, "text": text})
        else:
            i += 1

    return segments


def lay_transcript(video_id: str) -> list[dict]:
    """
    Nhận mã video, lấy danh sách phụ đề có sẵn (ưu tiên tiếng Anh).
    Trả về danh sách các đoạn gồm thời gian bắt đầu ('start') và nội dung ('text').
    Sử dụng yt-dlp để tránh bị YouTube chặn IP server.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        subtitle_file = os.path.join(tmpdir, "subtitle.vtt")

        try:
            cmd = [
                "yt-dlp",
                "--write-subs",
                "--sub-langs", "en",
                "--skip-download",
                "-o", os.path.join(tmpdir, "video.%(ext)s"),
                f"https://www.youtube.com/watch?v={video_id}"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir
            )

            vtt_files = []
            for f in os.listdir(tmpdir):
                if f.endswith('.vtt'):
                    vtt_files.append(os.path.join(tmpdir, f))

            if not vtt_files:
                cmd_vi = cmd.copy()
                cmd_vi[cmd_vi.index("--sub-langs")] = "--sub-langs"
                cmd_vi[cmd_vi.index("en")] = "vi"
                result = subprocess.run(
                    cmd_vi,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=tmpdir
                )

                vtt_files = []
                for f in os.listdir(tmpdir):
                    if f.endswith('.vtt'):
                        vtt_files.append(os.path.join(tmpdir, f))

            if not vtt_files:
                raise ValueError("Video không có phụ đề hoặc không thể truy xuất phụ đề.")

            with open(vtt_files[0], 'r', encoding='utf-8') as f:
                content = f.read()

            segments = _parse_vtt(content)

            if not segments:
                raise ValueError("Không thể phân tích nội dung phụ đề.")

            return segments

        except subprocess.TimeoutExpired:
            raise ConnectionError(
                "Không kết nối được do bị YouTube chặn hoặc quá thời gian chờ.\n"
                "   Tên lớp lỗi: TimeoutExpired"
            )
        except FileNotFoundError:
            raise RuntimeError(
                "yt-dlp chưa được cài đặt trên máy chủ.\n"
                "   Vui lòng cài đặt: pip install yt-dlp"
            )
        except Exception as e:
            error_msg = str(e)
            if "RequestBlocked" in error_msg or "blocked" in error_msg.lower():
                raise ConnectionError(
                    f"Không kết nối được do bị YouTube chặn. Vui lòng thử lại sau.\n"
                    f"   Tên lớp lỗi thật: RequestBlocked\n"
                    f"   Nội dung lỗi gốc: {e}"
                )
            raise RuntimeError(
                f"Lỗi khi lấy phụ đề: {e}\n"
                f"   Tên lớp lỗi thật: {type(e).__name__}"
            ) from e


if __name__ == "__main__":
    # Link mẫu: Video đầu tiên trên YouTube "Me at the zoo"
    link_mac_dinh = "https://www.youtube.com/watch?v=jNQXAC9IVRw"

    # Cho phép truyền link từ dòng lệnh, hoặc hỏi trực tiếp, hoặc dùng mặc định
    if len(sys.argv) > 1:
        link_kiem_tra = sys.argv[1]
    elif sys.stdin.isatty():
        nhap = input(f"Nhập link YouTube (nhấn Enter để dùng link mẫu): ").strip()
        link_kiem_tra = nhap if nhap else link_mac_dinh
    else:
        link_kiem_tra = link_mac_dinh

    print(f"\n=== ĐANG KIỂM TRA VỚI LINK: {link_kiem_tra} ===\n")

    try:
        # Bước 1: Trích xuất mã video
        ma_video = lay_ma_video(link_kiem_tra)
        print(f"-> Mã video trích xuất: {ma_video}")

        # Bước 2: Lấy phụ đề
        print("-> Đang tải phụ đề từ YouTube...")
        danh_sach_phu_de = lay_transcript(ma_video)
        print(f"-> Lấy thành công {len(danh_sach_phu_de)} đoạn phụ đề:\n")

        # In tối đa 5 đoạn đầu tiên để xem thử
        for doan in danh_sach_phu_de[:5]:
            giay_tong = int(doan["start"])
            phut = giay_tong // 60
            giay = giay_tong % 60
            print(f"[{phut:02d}:{giay:02d}] {doan['text']}")

        if len(danh_sach_phu_de) > 5:
            print(f"... và còn {len(danh_sach_phu_de) - 5} đoạn phụ đề tiếp theo.")

    except Exception as loi:
        print(f"-> Báo lỗi: {loi}")
        # In tên lớp lỗi thật nếu chưa xuất hiện trong chuỗi lỗi
        if "Tên lớp lỗi thật:" not in str(loi):
            print(f"   Tên lớp lỗi thật: {type(loi).__name__}")
            print(f"   Nội dung lỗi gốc: {loi}")
