import streamlit as st
from groq import Groq

st.set_page_config(page_title="Học Tiếng Trung AI", page_icon="🏮")
st.title("🏮 Chatbot Học Tiếng Trung")

with st.sidebar:
    st.header("Cài đặt")
    level = st.selectbox("Cấp độ của bạn:",
        ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])
    if st.button("🔄 Bắt đầu lại"):
        st.session_state.messages = []
        st.rerun()

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Thiếu GROQ_API_KEY trong Secrets. Vào Manage app → Secrets để thêm.")
    st.stop()

SYSTEM_PROMPT = (
    "Bạn là giáo viên dạy tiếng Trung Quốc (Mandarin) nhiệt tình và kiên nhẫn. "
    "Học viên cấp độ: " + level + ". "
    "Quy tắc bắt buộc: "
    "1. Mỗi câu tiếng Trung LUÔN kèm Pinyin và dịch tiếng Việt theo định dạng: "
    "[Câu tiếng Trung] | Pinyin: ... | Nghĩa: ... "
    "2. Dùng từ vựng phù hợp cấp độ học viên. "
    "3. Sửa lỗi ngữ pháp nhẹ nhàng nếu học viên viết sai. "
    "4. Khi hỏi nghĩa từ: Chữ Hán + Pinyin + Từ loại + Nghĩa tiếng Việt + 2 câu ví dụ. "
    "5. Luôn khuyến khích và động viên học viên."
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "你好！(Nǐ hǎo!) — Xin chào! 😊\n\nHôm nay bạn muốn học chủ đề gì?\n- 🍜 Ẩm thực\n- ✈️ Du lịch\n- 💼 Công việc\n- 💬 Hội thoại cơ bản"
        }
    ]

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
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"⚠️ Lỗi: {str(e)}"
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
