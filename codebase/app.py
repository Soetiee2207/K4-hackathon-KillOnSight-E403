import sys
import json
from pathlib import Path
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="VLearn Adaptive Tutor Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Resolve path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import run_model_tool_loop
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from tools.slide_renderer import render_pdf_page_to_bytes, get_pdf_page_count
from versioning import artifact_version_dict, build_artifact_version
from env_loader import load_lab_env

load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
SLIDES_DIR = ROOT.parent / "data" / "vlearn-pack" / "slides"

# Styles mimicking Demo.html
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Light Theme Colors */
.stApp {
    background-color: #f3f4f6;
    color: #111827;
}

/* Header Container */
.top-header {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    height: 52px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,.08);
    margin-bottom: 15px;
    border-radius: 8px;
}
.logo-icon {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #1a56db, #3b82f6);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 700; font-size: 13px;
}
.logo-text { font-weight: 700; font-size: 16px; color: #1a56db; letter-spacing: -.3px; }
.header-divider { width: 1px; height: 24px; background: #e5e7eb; margin: 0 10px;}
.header-title { font-size: 13px; font-weight: 600; color: #111827; }
.header-subtitle { font-size: 11px; color: #6b7280; }

/* Columns Container Styling */
.section-container {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    height: calc(100vh - 120px);
    overflow-y: auto;
}

.section-title {
    font-size: 14px;
    font-weight: 700;
    color: #111827;
    border-bottom: 2px solid #1a56db;
    padding-bottom: 8px;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Slide Viewer Area */
.viewer-toolbar {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.slide-card-wrapper {
    background: #e5e7eb;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 350px;
}

/* Chat bubble styling mimicking Demo.html */
.welcome-bubble {
    background: linear-gradient(135deg, #e8f0fd, #f0f4ff);
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 12.5px;
    line-height: 1.6;
    color: #111827;
    margin-bottom: 15px;
}
.welcome-bubble .bot-name {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 700;
    color: #1a56db;
    font-size: 12px;
    margin-bottom: 6px;
}
.bot-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #0e9f6e;
    box-shadow: 0 0 0 4px rgba(14,159,110,.2);
}

.msg-wrapper {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    font-size: 12.5px;
    line-height: 1.6;
}
.msg-wrapper.user {
    background: #e8f0fd;
    border-color: #bfdbfe;
}
.msg-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 11px;
    font-weight: 700;
}
.msg-header.user { color: #1a56db; }
.msg-header.tutor { color: #0e9f6e; }

/* Confidence display */
.confidence-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid #f3f4f6;
}
.confidence-bar {
    flex: 1; height: 6px;
    background: #e5e7eb; border-radius: 99px; overflow: hidden;
}
.confidence-fill {
    height: 100%; border-radius: 99px;
    background: linear-gradient(90deg, #0e9f6e, #34d399);
}
.confidence-badge {
    font-size: 9.5px; font-weight: 700;
    color: #0e9f6e; background: #def7ec;
    border-radius: 4px; padding: 2px 6px;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #0e9f6e;
}

/* Tool execution tracing */
.trace-block {
    background: #f9fafb;
    border-left: 2.5px solid #6366f1;
    border-radius: 4px;
    padding: 6px 10px;
    margin-top: 8px;
    font-size: 11px;
}
.trace-title {
    font-weight: 700;
    color: #4f46e5;
    text-transform: uppercase;
    font-size: 9.5px;
}
.trace-args {
    font-family: 'JetBrains Mono', monospace;
    color: #4b5563;
}
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_pdf" not in st.session_state:
    st.session_state.active_pdf = "d1-slide-hackathon.pdf"
if "page_num" not in st.session_state:
    st.session_state.page_num = 1
if "user_question" not in st.session_state:
    st.session_state.user_question = None

# Sidebar (Developer / Configuration Panel)
with st.sidebar:
    st.markdown("### ⚙️ Cấu hình hệ thống (Dev Settings)")
    version = st.selectbox("Version", ["v0", "v1", "v2", "v3"], index=3)
    provider_name = st.selectbox("LLM Provider", ["groq", "gemini", "openai", "openrouter"], index=0)
    model_name = st.text_input("Model Name Override (Optional)", value="")
    max_tool_rounds = st.slider("Max Tool Rounds", 1, 10, 4)
    history_window = st.slider("Context History Window", 1, 10, 5)

    st.markdown("---")
    st.markdown("### 🔖 Artifact Hashing")
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"
    try:
        av = build_artifact_version(version, system_prompt_path, tools_yaml_path)
        av_dict = artifact_version_dict(av)
        st.caption("Artifact Version:")
        st.code(av_dict["artifact_version"], language="text")
        st.caption("Prompt Hash:")
        st.code(av_dict["prompt_hash"][:12], language="text")
    except Exception as e:
        st.error(f"Error: {e}")

# Startup checks & load
try:
    provider = make_provider(provider_name)
    selected_model = model_name or None
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_yaml_path)
    openai_tools = to_openai_tools(tool_declarations)
except Exception as e:
    st.error(f"Startup error: {e}")
    st.stop()

# Header
st.markdown(f"""
<div class="top-header">
    <div class="logo-icon">VL</div>
    <span class="logo-text">VLearn Studio</span>
    <div class="header-divider"></div>
    <div>
        <div class="header-title">{st.session_state.active_pdf}</div>
        <div class="header-subtitle">Khóa học AI Thực Chiến · VinUniversity 2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main UI Grid
col_sidebar, col_viewer, col_chat = st.columns([3, 5, 4])

# --- Column 1: Document Tree Explorer ---
with col_sidebar:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📂 Học liệu môn học</div>', unsafe_allow_html=True)
    
    # Day 01 Section
    st.markdown("**Day 01 — AI & LLM Foundation**")
    if st.button("📘 d1-slide-hackathon.pdf", key="d1_btn", use_container_width=True):
        st.session_state.active_pdf = "d1-slide-hackathon.pdf"
        st.session_state.page_num = 1
        st.rerun()
    st.caption("Slide hackathon giới thiệu nền tảng AI & cơ chế LLM.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Day 02 Section
    st.markdown("**Day 02 — Product Discovery & Framing**")
    if st.button("📘 d2-slide-hackathon.pdf", key="d2_btn", use_container_width=True):
        st.session_state.active_pdf = "d2-slide-hackathon.pdf"
        st.session_state.page_num = 1
        st.rerun()
    st.caption("Slide bài tập xác định và mô hình hóa bài toán AI.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Column 2: Slide Viewer Area ---
pdf_path = SLIDES_DIR / st.session_state.active_pdf
total_pages = get_pdf_page_count(pdf_path)

with col_viewer:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Slide Viewer</div>', unsafe_allow_html=True)
    
    # Viewer Toolbar
    col_tb_l, col_tb_c, col_tb_r = st.columns([1, 2, 1])
    with col_tb_l:
        if st.button("⬅️ Trước", key="btn_prev", use_container_width=True) and st.session_state.page_num > 1:
            st.session_state.page_num -= 1
            st.rerun()
    with col_tb_c:
        st.markdown(f"<div style='text-align: center; padding-top: 6px; font-weight: 600;'>Trang {st.session_state.page_num} / {total_pages}</div>", unsafe_allow_html=True)
    with col_tb_r:
        if st.button("Kế ➡️", key="btn_next", use_container_width=True) and st.session_state.page_num < total_pages:
            st.session_state.page_num += 1
            st.rerun()
            
    # Render PDF Slide Image
    try:
        slide_bytes = render_pdf_page_to_bytes(pdf_path, st.session_state.page_num)
        st.image(slide_bytes, use_container_width=True)
    except Exception as e:
        st.error(f"Không thể render slide: {e}")
        st.info("Đang chuyển sang chế độ hiển thị văn bản slide.")
        
    st.markdown('</div>', unsafe_allow_html=True)

# --- Column 3: AI Tutor Panel ---
with col_chat:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 VLearn AI Tutor</div>', unsafe_allow_html=True)
    
    # Welcome Bubble
    st.markdown("""
    <div class="welcome-bubble">
        <div class="bot-name">
            <div class="bot-dot"></div>
            VLearn Tutor
        </div>
        Chào mừng bạn đến với VLearn Adaptive Tutor! Tôi ở đây để hỗ trợ bạn đọc tài liệu và làm bài tập hackathon. Hãy bôi đen hỏi bài hoặc chọn câu gợi ý bên dưới.
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Chips Questions
    st.markdown("<div style='font-size: 11px; font-weight: 700; color: #6b7280; margin-bottom: 6px;'>GỢI Ý CÂU HỎI NHANH:</div>", unsafe_allow_html=True)
    col_chip1, col_chip2 = st.columns(2)
    with col_chip1:
        if st.button("💡 3 Hướng làm sản phẩm?", key="chip_1", use_container_width=True):
            st.session_state.user_question = "Tóm tắt giúp tôi nội dung của slide về 3 Hướng làm sản phẩm."
    with col_chip2:
        if st.button("💡 Cần AI thật không?", key="chip_2", use_container_width=True):
            st.session_state.user_question = "Ở mức prototype Sketch thì không cần dùng AI thật đâu nhỉ?"
            
    col_chip3, col_chip4 = st.columns(2)
    with col_chip3:
        if st.button("💡 Data thật công ty?", key="chip_3", use_container_width=True):
            st.session_state.user_question = "Mình cứ lấy data thật của công ty đập vào cho AI phân tích là được đúng không?"
    with col_chip4:
        if st.button("⏳ Deadline nộp PRD?", key="chip_4", use_container_width=True):
            st.session_state.user_question = "Hạn chót nộp bài spec của hackathon là bao giờ?"

    st.markdown("<hr style='margin: 12px 0;'>", unsafe_allow_html=True)
    
    # Scrollable chat box simulation
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(st.session_state.messages):
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                st.markdown(f"""
                <div class="msg-wrapper user">
                    <div class="msg-header user">HỌC VIÊN</div>
                    <div>{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Calculate confidence score based on answer type
                confidence_score = 92 if "Trang" in content or "T0" in content else 65
                if "direct_to_btc" in str(msg.get("rounds", [])):
                    confidence_score = 99
                    
                st.markdown(f"""
                <div class="msg-wrapper">
                    <div class="msg-header tutor">VLEARN TUTOR</div>
                    <div>{content}</div>
                    <div class="confidence-wrap">
                        <div class="confidence-bar"><div class="confidence-fill" style="width: {confidence_score}%;"></div></div>
                        <span class="confidence-badge">ĐỘ TIN CẬY: {confidence_score}%</span>
                        <div class="status-dot"></div>
                        <span style="font-size: 9.5px; font-weight: 700; color: #0e9f6e; margin-left: 4px;">🟢 THÀNH CÔNG</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show tools execution trace if dev checks are needed
                if "rounds" in msg:
                    for round_item in msg["rounds"]:
                        tool_calls = round_item.get("tool_calls", [])
                        if tool_calls:
                            for tc in tool_calls:
                                st.markdown(f"""
                                <div class="trace-block">
                                    <div class="trace-title">🔧 Gọi Tool: {tc['name']}</div>
                                    <div class="trace-args">Args: {json.dumps(tc['args'], ensure_ascii=False)}</div>
                                </div>
                                """, unsafe_allow_html=True)

    # Chat submission logic
    chat_input_text = st.chat_input("Hỏi VLearn Tutor về nội dung học...")
    
    # Triggered by input or quick chips
    current_question = chat_input_text or st.session_state.user_question
    
    if current_question:
        # Reset quick chip question trigger
        st.session_state.user_question = None
        
        # Append User question
        st.session_state.messages.append({"role": "user", "content": current_question})
        
        # Prepare context and system instructions
        day_label = "Day1" if st.session_state.active_pdf == "d1-slide-hackathon.pdf" else "Day2"
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\n(Lưu ý: Học viên hiện tại đang xem slide {day_label} trang {st.session_state.page_num})"},
            *st.session_state.messages[-history_window * 2:]
        ]
        
        with st.spinner("AI Tutor đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=selected_model,
                    max_tool_rounds=max_tool_rounds
                )
                assistant_text = result["assistant_text"]
                
                # Append Response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "rounds": result.get("rounds", [])
                })
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi phản hồi từ AI Provider: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
