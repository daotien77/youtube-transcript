import sys
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    RequestBlocked,
    IpBlocked,
    YouTubeRequestFailed,
)

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi font (cp1252)
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

    # Thêm https:// nếu người dùng chỉ nhập youtube.com/watch?v=...
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # 1. Kiểm tra domain: chỉ chấp nhận youtube.com hoặc www.youtube.com
    domain = (parsed.netloc or "").lower()
    if domain not in ("www.youtube.com", "youtube.com"):
        raise ValueError("Link không hợp lệ. Chỉ hỗ trợ link từ domain youtube.com")

    # 2. Kiểm tra đường dẫn: chỉ chấp nhận /watch
    if parsed.path != "/watch":
        raise ValueError("Link không hợp lệ. Link phải có dạng https://www.youtube.com/watch?v=...")

    # 3. Lấy tham số 'v' từ chuỗi truy vấn (query string)
    params = parse_qs(parsed.query)
    danh_sach_v = params.get("v")

    if not danh_sach_v or not danh_sach_v[0].strip():
        raise ValueError("Link không hợp lệ. Không tìm thấy mã video (tham số v=).")

    return danh_sach_v[0].strip()


def lay_transcript(video_id: str) -> list[dict]:
    """
    Nhận mã video, lấy danh sách phụ đề có sẵn (ưu tiên tiếng Anh).
    Trả về danh sách các đoạn gồm thời gian bắt đầu ('start') và nội dung ('text').
    """
    api = YouTubeTranscriptApi()

    try:
        # Lấy danh sách tất cả các phụ đề có sẵn của video
        transcript_list = api.list(video_id)

        # Ưu tiên tìm phụ đề tiếng Anh (en, en-US, en-GB, ...)
        try:
            transcript = transcript_list.find_transcript(["en", "en-US", "en-GB"])
        except NoTranscriptFound:
            # Nếu không có tiếng Anh, lấy phụ đề có sẵn đầu tiên
            transcript = next(iter(transcript_list), None)
            if transcript is None:
                raise ValueError("Video không có phụ đề.")

        # Tải dữ liệu phụ đề về máy
        du_lieu = transcript.fetch()

        # Chuẩn hóa về danh sách các từ điển (dictionary) đơn giản
        ket_qua = []
        for snippet in du_lieu.snippets:
            ket_qua.append({
                "start": snippet.start,
                "text": snippet.text,
            })
        return ket_qua

    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise ValueError(
            f"Video không có phụ đề.\n"
            f"   Tên lớp lỗi thật: {type(e).__name__}\n"
            f"   Nội dung lỗi gốc: {e}"
        ) from e
    except VideoUnavailable as e:
        raise ValueError(
            f"Video không tồn tại hoặc đã bị xóa / chuyển sang chế độ riêng tư.\n"
            f"   Tên lớp lỗi thật: {type(e).__name__}\n"
            f"   Nội dung lỗi gốc: {e}"
        ) from e
    except (RequestBlocked, IpBlocked) as e:
        raise ConnectionError(
            f"Không kết nối được do bị YouTube chặn. Vui lòng thử lại sau.\n"
            f"   Tên lớp lỗi thật: {type(e).__name__}\n"
            f"   Nội dung lỗi gốc: {e}"
        ) from e
    except YouTubeRequestFailed as e:
        raise ConnectionError(
            f"Không kết nối được với YouTube (lỗi mạng hoặc máy chủ YouTube phản hồi lỗi).\n"
            f"   Tên lớp lỗi thật: {type(e).__name__}\n"
            f"   Nội dung lỗi gốc: {e}"
        ) from e
    except Exception as e:
        # Nếu đã là lỗi có chủ đích thì truyền tiếp, ngược lại bọc thông báo rõ ràng
        if isinstance(e, (ValueError, ConnectionError)):
            raise e
        raise RuntimeError(
            f"Lỗi khi lấy phụ đề: {str(e)}\n"
            f"   Tên lớp lỗi thật: {type(e).__name__}\n"
            f"   Nội dung lỗi gốc: {e}"
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
