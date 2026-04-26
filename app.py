import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Học Tiếng Trung AI", page_icon="🏮")

st.title("🏮 Chatbot Học Tiếng Trung")

# Sidebar chọn cấp độ
with st.sidebar:
    st.header("Cài đặt")
    level = st.selectbox("Cấp độ của bạn:", 
        ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])
    if st.button("🔄 Bắt đầu lại"):
        st.session_state.messages = []
        st.rerun()

# Cấu hình Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

SYSTEM_PROMPT = f"""Bạn là giáo viên dạy tiếng Trung nhiệt tình. Học viên cấp độ: {level}.
- Mỗi câu tiếng Trung LUÔN kèm Pinyin và dịch tiếng Việt
- Sửa lỗi ngữ pháp nhẹ nhàng nếu học viên viết sai
- Khi hỏi nghĩa từ: cung cấp Chữ Hán + Pinyin + Từ loại + Nghĩa + 2 ví dụ
- Dùng từ vựng phù hợp cấp độ học viên"""

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=SYSTEM_PROMPT)
    chat = model.start_chat()
    response = chat.send_message("Hãy chào học viên và hỏi hôm nay muốn học gì.")
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.session_state.chat = chat

# Hiển thị lịch sử
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Ô nhập tin nhắn
if prompt := st.chat_input("Nhập tin nhắn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang trả lời..."):
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})