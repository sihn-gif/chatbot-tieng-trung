import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Học Tiếng Trung AI", page_icon="🏮")
st.title("🏮 Chatbot Học Tiếng Trung")

with st.sidebar:
    st.header("Cài đặt")
    level = st.selectbox("Cấp độ của bạn:", 
        ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])
    if st.button("🔄 Bắt đầu lại"):
        for key in ["messages", "chat"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Thiếu GEMINI_API_KEY trong Secrets. Vào Manage app → Secrets để thêm vào.")
    st.stop()

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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好！(Nǐ hǎo!) — Xin chào! 😊\n\nHôm nay bạn muốn học chủ đề gì?\n- 🍜 Ẩm thực\n- ✈️ Du lịch\n- 💼 Công việc\n- 💬 Hội thoại cơ bản"
        }
    ]

if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT
        )
        st.session_state.chat = model.start_chat(history=[])
    except Exception as e:
        st.error("Không khởi tạo được model. Kiểm tra API key.")
        st.stop()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Nhập tin nhắn bằng tiếng Việt hoặc tiếng Trung..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang trả lời..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
            except Exception as e:
                reply = "⚠️ Có lỗi xảy ra. Có thể do API key hết quota hoặc mạng. Vui lòng thử lại sau."
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
