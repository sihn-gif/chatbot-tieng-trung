import streamlit as st
from groq import Groq
from supabase import create_client
import uuid

st.set_page_config(
    page_title="Học Tiếng Trung AI",
    page_icon="🏮",
    layout="centered"
)

st.markdown("""
<style>
    /* Font & nền tổng */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Ẩn header/footer mặc định của Streamlit */
    #MainMenu, footer, header { visibility: hidden; }

    /* Nền trang */
    .stApp { background-color: #f9f9f8; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0efea;
        border-right: 1px solid #e5e5e3;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { font-size: 14px; font-weight: 600; color: #1a1a1a; }

    /* Bubble chat của user */
    [data-testid="stChatMessageContent"]:has(> div > p) {
        border-radius: 12px;
        padding: 2px 4px;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        font-size: 15px;
        line-height: 1.7;
        color: #1a1a1a;
    }

    /* Input chat */
    .stChatInput textarea {
        font-size: 15px;
        border-radius: 12px !important;
        border: 1px solid #d9d9d7 !important;
        background: #fff !important;
        padding: 12px 16px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    }
    .stChatInput textarea:focus {
        border-color: #1a1a1a !important;
        box-shadow: 0 0 0 2px rgba(26,26,26,0.08) !important;
    }

    /* Nút */
    .stButton > button {
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        border: 1px solid #d9d9d7;
        background: #fff;
        color: #1a1a1a;
        padding: 6px 14px;
        transition: all 0.15s;
    }
    .stButton > button:hover {
        background: #f0efea;
        border-color: #1a1a1a;
    }

    /* Title */
    h1 { font-size: 22px !important; font-weight: 600 !important; color: #1a1a1a !important; }

    /* Session tag */
    .session-tag {
        display: inline-block;
        background: #e8f5f0;
        color: #0f6e56;
        font-size: 11px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo clients
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("Thiếu API key. Vào Manage app → Secrets để thêm.")
    st.stop()

# Tạo hoặc lấy session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

# Sidebar
with st.sidebar:
    st.markdown("### 🏮 Cài đặt")
    level = st.selectbox("Cấp độ:", ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])

    st.markdown("---")
    st.markdown("**Lịch sử phiên học**")

    # Lấy danh sách session
    try:
        sessions = supabase.table("chat_history") \
            .select("session_id, content, created_at") \
            .eq("role", "user") \
            .order("created_at", desc=True) \
            .execute()

        seen = []
        for row in sessions.data:
            sid = row["session_id"]
            if sid not in seen:
                seen.append(sid)
                label = row["content"][:30] + "..." if len(row["content"]) > 30 else row["content"]
                is_current = sid == session_id
                btn_label = f"{'▶ ' if is_current else ''}{label}"
                if st.button(btn_label, key=f"sess_{sid}"):
                    st.session_state.session_id = sid
                    st.session_state.messages = []
                    st.rerun()
    except Exception:
        st.caption("Chưa có lịch sử.")

    st.markdown("---")
    if st.button("➕ Cuộc trò chuyện mới"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# System prompt
SYSTEM_PROMPT = (
    "Bạn là giáo viên dạy tiếng Trung Quốc (Mandarin) nhiệt tình và kiên nhẫn. "
    "Học viên cấp độ: " + level + ". "
    "Quy tắc bắt buộc: "
    "1. Mỗi câu tiếng Trung LUÔN kèm Pinyin và dịch tiếng Việt theo định dạng: "
    "[Câu tiếng Trung] | Pinyin: ... | Nghĩa: ... "
    "2. Dùng từ vựng phù hợp cấp độ. "
    "3. Sửa lỗi ngữ pháp nhẹ nhàng nếu học viên viết sai. "
    "4. Khi hỏi nghĩa từ: Chữ Hán + Pinyin + Từ loại + Nghĩa tiếng Việt + 2 câu ví dụ. "
    "5. Luôn khuyến khích học viên."
)

# Load tin nhắn từ DB nếu chưa có trong session
if "messages" not in st.session_state or st.session_state.get("loaded_session") != session_id:
    try:
        rows = supabase.table("chat_history") \
            .select("role, content") \
            .eq("session_id", session_id) \
            .order("created_at") \
            .execute()
        st.session_state.messages = [{"role": r["role"], "content": r["content"]} for r in rows.data]
    except Exception:
        st.session_state.messages = []
    st.session_state.loaded_session = session_id

# Tin nhắn chào mặc định
if not st.session_state.messages:
    welcome = "你好！(Nǐ hǎo!) — Xin chào! 😊\n\nHôm nay bạn muốn học chủ đề gì?\n- 🍜 Ẩm thực\n- ✈️ Du lịch\n- 💼 Công việc\n- 💬 Hội thoại cơ bản"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "role": "assistant",
            "content": welcome
        }).execute()
    except Exception:
        pass

# Header
st.title("🏮 Học Tiếng Trung AI")
st.markdown(f'<div class="session-tag">Phiên: {session_id[:8]}...</div>', unsafe_allow_html=True)

# Hiển thị tin nhắn
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Xử lý input
if prompt := st.chat_input("Nhập tiếng Việt hoặc tiếng Trung..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "role": "user",
            "content": prompt
        }).execute()
    except Exception:
        pass

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
    try:
        supabase.table("chat_history").insert({
            "session_id": session_id,
            "role": "assistant",
            "content": reply
        }).execute()
    except Exception:
        pass
