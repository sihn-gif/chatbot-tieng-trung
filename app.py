import streamlit as st
import google.generativeai as genai

# 1. Cấu hình giao diện Streamlit
st.set_page_config(page_title="Học Tiếng Trung AI", page_icon="🏮")
st.title("🏮 Chatbot Học Tiếng Trung")

# 2. Cấu hình Sidebar
with st.sidebar:
    st.header("Cài đặt")
    level = st.selectbox("Cấp độ của bạn:", 
        ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])
    
    # Nút bấm bắt đầu lại
    if st.button("🔄 Bắt đầu lại (Xoá lịch sử)"):
        st.session_state.clear()
        st.rerun()

# --- TÍNH NĂNG MỚI: Tự động reset chat nếu đổi cấp độ ---
if "current_level" not in st.session_state:
    st.session_state.current_level = level

if st.session_state.current_level != level:
    st.session_state.current_level = level
    if "messages" in st.session_state: del st.session_state["messages"]
    if "chat" in st.session_state: del st.session_state["chat"]
    st.rerun()
# ---------------------------------------------------------

# 3. Lấy API Key và cấu hình
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"⚠️ Lỗi cấu hình API Key: {e}\n\nVào Manage app → Settings → Secrets để thêm GEMINI_API_KEY.")
    st.stop()

# 4. Prompt hệ thống
SYSTEM_PROMPT = (
    "Bạn là giáo viên dạy tiếng Trung Quốc (Mandarin) nhiệt tình và kiên nhẫn. "
    "Học viên cấp độ: " + level + ". "
    "Quy tắc bắt buộc: "
    "1. Mỗi câu tiếng Trung LUÔN kèm Pinyin và dịch tiếng Việt theo định dạng: "
    "[Câu tiếng Trung] | Pinyin: ... | Nghĩa: ... "
    "2. Dùng từ vựng phù hợp cấp độ học viên. "
    "3. Sửa lỗi ngữ pháp nhẹ nhàng và giải thích ngắn gọn nếu học viên viết sai. "
    "4. Khi hỏi nghĩa từ: cung cấp Chữ Hán + Pinyin + Từ loại + Nghĩa tiếng Việt + 2 câu ví dụ. "
    "5. Luôn khuyến khích và động viên học viên."
)

# 5. Khởi tạo tin nhắn chào mừng
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好！(Nǐ hǎo!) — Xin chào! 😊\n\nHôm nay bạn muốn học chủ đề gì?\n- 🍜 Ẩm thực\n- ✈️ Du lịch\n- 💼 Công việc\n- 💬 Hội thoại cơ bản"
        }
    ]

# 6. Khởi tạo Model và Lịch sử Chat
if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Hoặc gemini-1.5-flash nếu 2.0 báo lỗi
            system_instruction=SYSTEM_PROMPT
        )
        st.session_state.chat = model.start_chat(history=[])
    except Exception as e:
        st.error(f"⚠️ Không khởi tạo được AI. Chi tiết lỗi: {e}")
        st.stop()

# 7. Hiển thị lại lịch sử chat trên màn hình
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Xử lý tin nhắn mới của người dùng
if prompt := st.chat_input("Nhập tin nhắn bằng tiếng Việt hoặc tiếng Trung..."):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hiển thị và xử lý phản hồi từ AI
    with st.chat_message("assistant"):
        with st.spinner("Cô giáo đang suy nghĩ..."):
            try:
                # Gửi tin nhắn vào session chat của Gemini
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
                st.markdown(reply)
                
                # Lưu vào lịch sử hiển thị
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                # SỬA LỖI Ở ĐÂY: In ra lỗi thật sự để bắt bệnh
                error_msg = f"⚠️ Lỗi gọi API Gemini: {str(e)}"
                st.error(error_msg)
                
                # Cảnh báo thêm cho người dùng dễ hiểu
                st.warning("Nếu lỗi có chữ 'API_KEY_INVALID' -> Bạn điền sai API Key. \nNếu có chữ '429' hoặc 'Quota' -> Bạn đã hết lượt dùng miễn phí API Key này hôm nay.")
