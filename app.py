import streamlit as st
import streamlit.components.v1 as components
import json
from transcript import lay_ma_video, lay_transcript


def dinh_dang_thoi_gian(giay: float) -> str:
    """
    Chuyển đổi số giây thành định dạng mốc thời gian [mm:ss].
    Ví dụ: 65 giây -> [01:05]
    """
    giay_tong = int(giay)
    phut = giay_tong // 60
    s = giay_tong % 60
    return f"[{phut:02d}:{s:02d}]"


def tao_nut_copy(van_ban: str):
    """
    Hiển thị nút Copy sử dụng HTML + JavaScript.
    Khi bấm, nội dung van_ban được copy vào clipboard của trình duyệt.

    Cách hoạt động:
    - Sử dụng Clipboard API hiện đại (navigator.clipboard.writeText) 
    - Có fallback dùng execCommand cho trình duyệt cũ
    - Hiển thị thông báo thành công/thất bại
    """
    van_ban_json = json.dumps(van_ban)

    html_code = """
    <div style="margin: 10px 0;">
        <button id="copyBtn" style="
            padding: 10px 20px;
            font-size: 14px;
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        ">
            <span id="copyIcon">📋</span>
            <span>Copy transcript</span>
        </button>
    </div>

    <script>
        const copyBtn = document.getElementById('copyBtn');
        const copyIcon = document.getElementById('copyIcon');
        const originalText = copyBtn.innerHTML;
        const textToCopy = """ + van_ban_json + """;

        copyBtn.addEventListener('click', async function() {
            copyBtn.disabled = true;
            copyIcon.textContent = '⏳';
            
            try {
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(textToCopy);
                    copyBtn.innerHTML = '<span id="copyIcon">✅</span><span>Đã copy!</span>';
                } else {
                    throw new Error('clipboard not supported');
                }
            } catch (err) {
                // Fallback: sử dụng textarea ẩn
                try {
                    const textarea = document.createElement('textarea');
                    textarea.value = textToCopy;
                    textarea.style.position = 'fixed';
                    textarea.style.left = '-9999px';
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    copyBtn.innerHTML = '<span id="copyIcon">✅</span><span>Đã copy!</span>';
                } catch (fallbackErr) {
                    copyBtn.innerHTML = '<span id="copyIcon">❌</span><span>Không copy được!</span>';
                }
            }
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.disabled = false;
            }, 2000);
        });

        copyBtn.addEventListener('mouseenter', function() {
            if (!copyBtn.disabled) {
                copyBtn.style.transform = 'translateY(-2px)';
                copyBtn.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
            }
        });

        copyBtn.addEventListener('mouseleave', function() {
            copyBtn.style.transform = 'translateY(0)';
            copyBtn.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
        });
    </script>
    """

    components.html(html_code, height=80)


# 1. Tiêu đề ứng dụng
st.title("YouTube Transcript")

# 2. Khởi tạo session_state để lưu dữ liệu phụ đề giữa các lần render
if "transcript_data" not in st.session_state:
    st.session_state.transcript_data = None

# 3. Ô dán link YouTube
url = st.text_input("Dán link YouTube tại đây (dạng https://www.youtube.com/watch?v=...):")

# 4. Nút bấm "Lấy transcript"
if st.button("Lấy transcript"):
    if not url:
        st.warning("Vui lòng dán link YouTube trước khi bấm lấy phụ đề.")
    else:
        try:
            with st.spinner("Đang lấy phụ đề từ YouTube..."):
                # Bước 1: Trích xuất mã video từ link
                ma_video = lay_ma_video(url)

                # Bước 2: Tải phụ đề và lưu vào session_state
                st.session_state.transcript_data = lay_transcript(ma_video)

            st.success(f"Lấy thành công {len(st.session_state.transcript_data)} đoạn phụ đề!")
        except Exception as e:
            # Xóa dữ liệu cũ nếu gặp lỗi và hiện thông báo
            st.session_state.transcript_data = None
            st.error(str(e))

# 5. Khu vực hiển thị kết quả, công tắc mốc thời gian và nút Download
if st.session_state.transcript_data:
    # Công tắc bật/tắt mốc thời gian: đổi trạng thái sẽ re-render ngay mà không tải lại video
    hien_moc_thoi_gian = st.toggle("Hiện mốc thời gian [mm:ss]", value=False)

    # Tạo nội dung hiển thị theo trạng thái của công tắc
    if hien_moc_thoi_gian:
        cac_dong = [
            f"{dinh_dang_thoi_gian(doan['start'])} {doan['text']}"
            for doan in st.session_state.transcript_data
        ]
    else:
        cac_dong = [doan["text"] for doan in st.session_state.transcript_data]

    noi_dung_hien_thi = "\n".join(cac_dong)

    # Hiển thị nội dung phụ đề
    st.text_area("Nội dung transcript:", value=noi_dung_hien_thi, height=350)

    # Nút Copy: dùng JavaScript để copy vào clipboard, không cần tải file
    tao_nut_copy(noi_dung_hien_thi)

    # Nút Download file .txt: tải trực tiếp qua trình duyệt, app không tự lưu vào ổ cứng
    st.download_button(
        label="Download file .txt",
        data=noi_dung_hien_thi,
        file_name="transcript.txt",
        mime="text/plain",
    )

