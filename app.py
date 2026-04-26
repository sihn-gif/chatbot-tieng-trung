import streamlit as st
from groq import Groq
from supabase import create_client
from datetime import datetime
import uuid

st.set_page_config(page_title="Học Tiếng Trung AI", page_icon="🏮")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("Thiếu API key. Vào Manage app → Secrets để thêm.")
    st.stop()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

session_id = st.session_state.session_id

with st.sidebar:
    st.title("🏮 Học Tiếng Trung")
    level = st.selectbox("Cấp độ:", ["Mới bắt đầu", "HSK 1", "HSK 2", "HSK 3", "HSK 4+"])

    st.markdown("---")
    if st.button("➕ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**🕐 Lịch sử phiên học**")

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

                dt = datetime.fromisoformat(row["created_at"].replace("Z", ""))
                date_str = dt.strftime("%d/%m/%Y %H:%M")
                label = row["content"][:28] + "..." if len(row["content"]) > 28 else row["content"]
                prefix = "▶ " if sid == session_id else ""

                if st.button(
                    f"{prefix}{label}\n🕐 {date_str}",
                    key=f"sess_{sid}",
                    use_container_width=True
                ):
                    st.session_state.session_id = sid
                    st.session_state.messages = []
                    st.rerun()

    except Exception as e:
        st.caption(f"Chưa có lịch sử.")

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

st.title("🏮 Học Tiếng Trung AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
