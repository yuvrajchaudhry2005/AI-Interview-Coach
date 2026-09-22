import hashlib
import html
import os
import re
import time
import uuid
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from foundry_client import (
    ask_agent,
    create_conversation,
    request_evaluation_report,
    request_study_plan,
    upload_resume,
)
from auth_store import (
    authenticate_user,
    create_user,
    delete_user,
    get_interview_history,
    init_database,
    save_interview_history,
)
from speech_service import speech_to_text_detailed

load_dotenv()

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"], .stMarkdown, .stText {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stApp {
    background:
        radial-gradient(1200px 500px at 8% -10%, rgba(96, 165, 250, 0.22), transparent 55%),
        radial-gradient(900px 420px at 100% 0%, rgba(167, 139, 250, 0.16), transparent 50%),
        linear-gradient(180deg, #F8FBFF 0%, #EEF4FB 100%) !important;
    color: #0F172A !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { visibility: hidden; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
    border-right: 1px solid #E2E8F0 !important;
}

[data-testid="stSidebar"] * { color: #0F172A !important; }

.brand-mark {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.35rem 0 0.85rem 0;
}
.brand-orb {
    width: 42px; height: 42px; border-radius: 14px;
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
    color: #fff; font-weight: 800; font-size: 1.15rem;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.28);
}
.brand-title { font-weight: 800; font-size: 1.05rem; letter-spacing: -0.02em; }
.brand-sub { font-size: 0.75rem; color: #64748B !important; }

.hero-wrap { text-align: center; padding: 0.6rem 0 0.2rem; }
.hero-title {
    font-size: 2.7rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.1;
    background: linear-gradient(90deg, #0F172A 10%, #2563EB 55%, #7C3AED 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0.45rem 0 0.4rem;
}
.hero-subtitle {
    max-width: 720px; margin: 0 auto 0.4rem;
    color: #475569; font-size: 1.08rem; line-height: 1.55;
}
.pill {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.32rem 0.85rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
    background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8;
}
.pill.green { background: #ECFDF5; border-color: #A7F3D0; color: #047857; }
.pill.amber { background: #FFFBEB; border-color: #FDE68A; color: #B45309; }
.pill.violet { background: #F5F3FF; border-color: #DDD6FE; color: #6D28D9; }

.stepper { display: flex; justify-content: center; gap: 0.55rem; flex-wrap: wrap; margin: 1.1rem 0 1.5rem; }
.step {
    display: flex; align-items: center; gap: 0.4rem;
    padding: 0.45rem 0.95rem; border-radius: 999px; font-size: 0.82rem; font-weight: 650;
    background: #fff; border: 1px solid #E2E8F0; color: #64748B;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.step.active {
    background: linear-gradient(135deg, #2563EB, #4F46E5);
    border-color: transparent; color: #fff;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.28);
}
.step.done { background: #ECFDF5; border-color: #A7F3D0; color: #047857; }

.soft-card {
    background: rgba(255,255,255,0.86);
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 1.35rem 1.45rem;
    box-shadow: 0 16px 40px -20px rgba(15, 23, 42, 0.18);
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}
.section-kicker {
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em;
    text-transform: uppercase; color: #2563EB; margin-bottom: 0.2rem;
}
.feature-card {
    background: #fff; border: 1px solid #E2E8F0; border-radius: 16px;
    padding: 1rem 1.05rem; height: 100%;
    box-shadow: 0 8px 20px -16px rgba(15, 23, 42, 0.4);
}
.feature-icon {
    width: 38px; height: 38px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    background: #EFF6FF; font-size: 1.1rem; margin-bottom: 0.55rem;
}
.feature-title { font-weight: 750; font-size: 0.95rem; }
.feature-desc { color: #64748B; font-size: 0.82rem; line-height: 1.45; margin-top: 0.2rem; }

.question-card {
    background: linear-gradient(180deg, #FFFFFF 0%, #F0F7FF 100%);
    border: 1px solid #BFDBFE;
    border-radius: 22px;
    padding: 1.5rem 1.7rem 1.45rem;
    box-shadow: 0 18px 40px -18px rgba(37, 99, 235, 0.28);
    margin: 0.4rem 0 1.1rem;
}
.question-text { font-size: 1.28rem; font-weight: 750; color: #0F172A; line-height: 1.5; }

.interviewer {
    display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.85rem;
}
.avatar {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg, #60A5FA, #2563EB);
    display: flex; align-items: center; justify-content: center;
    color: white; font-weight: 800; box-shadow: 0 8px 16px rgba(37,99,235,0.25);
}
.live-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #22C55E;
    box-shadow: 0 0 0 4px rgba(34,197,94,0.18);
    display: inline-block; margin-right: 0.35rem;
}

.score-ring {
    width: 148px; height: 148px; border-radius: 50%; margin: 0 auto;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background:
        radial-gradient(circle at 50% 42%, #FFFFFF 0 54%, transparent 55%),
        conic-gradient(#2563EB var(--pct), #DBEAFE 0);
    box-shadow: 0 14px 30px rgba(37, 99, 235, 0.18);
}
.score-num { font-size: 2.55rem; font-weight: 800; color: #1E40AF; line-height: 1; }
.score-lbl { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em; color: #3B82F6; }

.stat {
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 0.9rem 0.85rem; text-align: center; height: 100%;
}
.stat-l { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: #64748B; }
.stat-v { font-size: 1.15rem; font-weight: 800; color: #0F172A; margin-top: 0.25rem; }

.qscore {
    background: #fff; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 0.85rem 1rem; margin-bottom: 0.55rem;
}
.bar-bg { height: 8px; background: #E2E8F0; border-radius: 99px; overflow: hidden; margin-top: 0.45rem; }
.bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #60A5FA, #2563EB); }

.insight {
    border-radius: 14px; padding: 0.85rem 1rem; margin-bottom: 0.5rem; border: 1px solid;
}
.insight.good { background: #ECFDF5; border-color: #A7F3D0; color: #065F46; }
.insight.warn { background: #FFF7ED; border-color: #FED7AA; color: #9A3412; }
.insight.info { background: #EFF6FF; border-color: #BFDBFE; color: #1E3A8A; }
.insight.gap { background: #F5F3FF; border-color: #DDD6FE; color: #5B21B6; }

.hud {
    background: rgba(255,255,255,0.8); border: 1px solid #E2E8F0;
    border-radius: 16px; padding: 0.7rem 0.9rem; margin-bottom: 0.85rem;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div,
div[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 12px !important;
    color: #0F172A !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 0.55rem 1.15rem !important;
    border: 1px solid #E2E8F0 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB, #4F46E5) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 10px 20px -8px rgba(37, 99, 235, 0.55) !important;
}

div[data-testid="stFileUploader"] {
    background: #F8FAFC; border: 1.5px dashed #93C5FD; border-radius: 16px; padding: 0.6rem;
}
div[data-testid="stAudioInput"] {
    background: #F8FAFC; border: 1.5px dashed #CBD5E1; border-radius: 14px; padding: 0.55rem 0.7rem;
}

.resume-ok {
    background: #ECFDF5; border: 1.5px solid #A7F3D0; border-radius: 14px;
    padding: 0.9rem 1rem; display: flex; justify-content: space-between; align-items: center;
}

.auth-shell { max-width: 980px; margin: 2rem auto 0; }
.auth-panel {
    display: grid; grid-template-columns: 1.05fr 0.95fr; gap: 2.5rem; align-items: center;
    background: rgba(255,255,255,0.9); border: 1px solid #E2E8F0; border-radius: 24px;
    padding: 2.6rem; box-shadow: 0 20px 50px -24px rgba(15, 23, 42, 0.25);
}
.auth-copy { padding: 0.35rem 0 0.35rem 0.25rem; }
.auth-brand { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 2.1rem; }
.auth-brand-mark {
    width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center;
    justify-content: center; background: #102A43; color: #fff; font-weight: 800;
}
.auth-brand-name { color: #102A43; font-weight: 800; font-size: clamp(1.7rem, 3vw, 2.25rem); letter-spacing: 0.02em; }
.auth-copy h1 { font-size: 2.25rem; line-height: 1.12; margin-bottom: 0.7rem; }
.auth-copy p { color: #475569; line-height: 1.6; }
.auth-privacy { color: var(--muted); font-size: 0.76rem; margin-top: 1.5rem; }
.auth-points { display: grid; gap: 0.7rem; margin-top: 1.65rem; }
.auth-point { display: flex; align-items: center; gap: 0.65rem; color: #334E68; font-size: 0.87rem; }
.auth-point span {
    width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center;
    justify-content: center; background: #E6FFFA; color: #087F5B; font-weight: 800; font-size: 0.75rem;
}
.auth-form {
    background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 18px; padding: 1.25rem;
}
.auth-form h2 { color: #102A43; font-size: 1.2rem; margin: 0.15rem 0 0.25rem; }
.auth-form-caption { color: #627D98; font-size: 0.82rem; margin-bottom: 1rem; }
.history-row {
    display: flex; align-items: center; justify-content: space-between; gap: 1rem;
    padding: 0.9rem 1rem; margin-bottom: 0.55rem; background: #FFFFFF;
    border: 1px solid #E2E8F0; border-radius: 14px;
}
.history-meta { color: #64748B; font-size: 0.78rem; margin-top: 0.22rem; }
.history-score { font-size: 1.25rem; font-weight: 800; white-space: nowrap; }
.history-score small { color: #94A3B8; font-size: 0.72rem; font-weight: 700; }
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #D9E2EC !important; border-radius: 18px !important;
    background: rgba(248, 250, 252, 0.86) !important; padding: 0.35rem 1.1rem 0.8rem !important;
}

/* Reference-inspired visual system: charcoal surfaces, deep teal atmosphere, aqua signal. */
:root {
    --ink: #f1fbf8;
    --muted: #91aaa4;
    --aqua: #20e6c2;
    --aqua-soft: rgba(32, 230, 194, 0.12);
    --surface: #111817;
    --surface-raised: #17201f;
    --line: rgba(153, 190, 181, 0.22);
}

html, body, [class*="css"], .stMarkdown, .stText, label,
[data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] {
    color: var(--ink) !important;
}
.stApp {
    background:
        radial-gradient(800px 460px at 9% 0%, rgba(20, 117, 102, 0.48), transparent 64%),
        radial-gradient(680px 440px at 100% 12%, rgba(15, 74, 67, 0.42), transparent 64%),
        linear-gradient(145deg, #07100f 0%, #0b1715 46%, #101b1a 100%) !important;
}
section.main > div { max-width: 1260px; padding-top: 2.1rem; }
header[data-testid="stHeader"] { background: rgba(7, 16, 15, 0.68) !important; }
[data-testid="stSidebar"] {
    background: rgba(8, 17, 16, 0.94) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color: var(--ink) !important; }
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(32, 230, 194, 0.08) !important; border: 1px solid var(--line) !important;
}
.brand-mark { border-bottom: 1px solid var(--line); padding: 0.35rem 0 1rem; }
.brand-orb, .auth-brand-mark {
    background: var(--aqua) !important; color: #07100f !important; border-radius: 4px !important;
    box-shadow: 0 0 22px rgba(32, 230, 194, 0.24) !important;
}
.brand-title { color: var(--ink) !important; }
.auth-brand-name { color: var(--aqua) !important; font-size: clamp(1.7rem, 3vw, 2.25rem) !important; text-transform: uppercase; }
.brand-sub, .auth-form-caption { color: var(--muted) !important; }
.hero-wrap { padding: 1.2rem 0 0.7rem; }
.hero-title {
    background: none !important; -webkit-text-fill-color: initial !important;
    color: var(--aqua) !important; font-size: clamp(2.2rem, 5vw, 4rem);
    letter-spacing: 0.01em; text-transform: uppercase;
}
.hero-subtitle, .auth-copy p { color: var(--muted) !important; }
.pill {
    background: var(--aqua-soft) !important; border: 1px solid rgba(32, 230, 194, 0.55) !important;
    color: var(--aqua) !important; border-radius: 3px !important; text-transform: uppercase;
    letter-spacing: 0.08em; font-size: 0.68rem;
}
.pill.green, .pill.amber, .pill.violet { background: var(--aqua-soft) !important; border-color: rgba(32, 230, 194, 0.55) !important; color: var(--aqua) !important; }
.stepper { gap: 0.35rem; margin: 1rem 0 1.4rem; }
.step {
    background: transparent !important; border: 1px solid var(--line) !important; color: var(--muted) !important;
    border-radius: 3px !important; box-shadow: none !important; text-transform: uppercase; letter-spacing: 0.04em;
}
.step.active { background: var(--aqua) !important; color: #07100f !important; border-color: var(--aqua) !important; box-shadow: 0 0 18px rgba(32, 230, 194, 0.2) !important; }
.step.done { background: var(--aqua-soft) !important; border-color: rgba(32, 230, 194, 0.45) !important; color: var(--aqua) !important; }
.soft-card, .feature-card, .qscore, .history-row, .hud, .question-card, .auth-panel {
    background: rgba(17, 24, 23, 0.82) !important; border: 1px solid var(--line) !important;
    border-radius: 4px !important; box-shadow: 0 18px 40px rgba(0, 0, 0, 0.2) !important;
}
.feature-card { padding: 1.1rem; }
.feature-icon { background: var(--aqua-soft) !important; border-radius: 3px !important; color: var(--aqua); }
.feature-desc, .history-meta { color: var(--muted) !important; }
.feature-title, .section-kicker, .stat-l { color: var(--aqua) !important; }
.section-kicker { letter-spacing: 0.14em; }
.question-card { background: linear-gradient(145deg, #162422, #101817) !important; border-color: rgba(32, 230, 194, 0.42) !important; }
.question-text, .stat-v, .score-num { color: var(--ink) !important; }
.avatar { background: var(--aqua) !important; color: #07100f !important; box-shadow: 0 0 18px rgba(32, 230, 194, 0.2) !important; }
.live-dot { background: var(--aqua) !important; box-shadow: 0 0 0 4px rgba(32, 230, 194, 0.16) !important; }
.score-ring { background: radial-gradient(circle at 50% 42%, #111817 0 54%, transparent 55%), conic-gradient(var(--aqua) var(--pct), #243532 0) !important; box-shadow: 0 0 26px rgba(32, 230, 194, 0.18) !important; }
.score-lbl { color: var(--aqua) !important; }
.stat { background: var(--surface-raised) !important; border-color: var(--line) !important; border-radius: 3px !important; }
.bar-bg { background: #263532 !important; border-radius: 0 !important; }
.bar-fill { background: var(--aqua) !important; border-radius: 0 !important; }
.insight.good, .insight.warn, .insight.info, .insight.gap { background: var(--surface-raised) !important; border-color: var(--line) !important; color: var(--ink) !important; border-radius: 3px !important; }
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] > div, div[data-testid="stNumberInput"] input {
    background: #0d1514 !important; border: 1px solid var(--line) !important;
    border-radius: 3px !important; color: var(--ink) !important;
}
div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--aqua) !important; box-shadow: 0 0 0 2px rgba(32, 230, 194, 0.15) !important;
}
.stButton > button {
    background: var(--aqua) !important; color: #07100f !important; border: 1px solid var(--aqua) !important;
    border-radius: 3px !important; text-transform: uppercase; letter-spacing: 0.04em;
    box-shadow: 0 0 16px rgba(32, 230, 194, 0.14) !important;
}
.stButton > button:hover {
    background: #74f5dd !important; border-color: #74f5dd !important; color: #07100f !important;
    box-shadow: 0 0 22px rgba(32, 230, 194, 0.28) !important;
}
.stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"],
[data-testid="stFormSubmitButton"] button {
    background: var(--aqua) !important; color: #07100f !important; border-color: var(--aqua) !important;
    box-shadow: 0 0 20px rgba(32, 230, 194, 0.2) !important;
}
div[data-testid="stFileUploader"], div[data-testid="stAudioInput"] { background: #0d1514 !important; border-color: rgba(32, 230, 194, 0.48) !important; border-radius: 3px !important; }
.resume-ok { background: var(--aqua-soft) !important; border-color: rgba(32, 230, 194, 0.5) !important; border-radius: 3px !important; }
.auth-copy h1 { color: var(--ink) !important; text-transform: uppercase; letter-spacing: 0.01em; }
.auth-point { color: var(--muted) !important; }
.auth-point span { background: var(--aqua) !important; color: #07100f !important; border-radius: 3px !important; }
[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(17, 24, 23, 0.94) !important; border-color: var(--line) !important; border-radius: 4px !important; }
div[data-testid="stTabs"] button { color: var(--muted) !important; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: var(--aqua) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { background-color: var(--aqua) !important; }
div[data-testid="stAlert"] { background: var(--surface-raised) !important; border-color: var(--line) !important; color: var(--ink) !important; }
hr { border-color: var(--line) !important; }
@media (max-width: 760px) {
    .auth-shell { margin-top: 0.5rem; }
    .auth-panel { grid-template-columns: 1fr; gap: 1.25rem; padding: 1.35rem; }
    .auth-brand { margin-bottom: 1.2rem; }
    .auth-copy h1 { font-size: 1.8rem; }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_state():
    defaults = {
        "stage": "setup",
        "conversation_id": None,
        "vector_store_id": None,
        "role": "",
        "experience": "Intermediate (2-4 yrs)",
        "interview_type": "Technical",
        "target_questions": 6,
        "question_count": 1,
        "current_question": "",
        "messages": [],
        "session_start_time": None,
        "answer_text": "",
        "last_audio_hash": "",
        "last_engine": "",
        "evaluation_report": "",
        "study_plan": "",
        "speech_key": os.environ.get("SPEECH_KEY", ""),
        "speech_region": os.environ.get("SPEECH_REGION", "eastus"),
        "resume_name": "",
        "auth_user": None,
        "interview_session_id": str(uuid.uuid4()),
        "camera_enabled": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_interview():
    keep = {
        "speech_key": st.session_state.speech_key,
        "speech_region": st.session_state.speech_region,
        "auth_user": st.session_state.auth_user,
    }
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    for key, value in keep.items():
        st.session_state[key] = value
    init_state()
    st.rerun()


def logout_user():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()
    st.session_state.auth_user = None
    st.rerun()


def render_history_dashboard():
    history = get_interview_history(st.session_state.auth_user["id"])
    st.markdown('<div class="section-kicker">Your progress</div>', unsafe_allow_html=True)
    st.subheader(f"Welcome back, {st.session_state.auth_user['full_name'].split()[0]}")

    if not history:
        st.info("Your completed interviews and scores will appear here after your first session.")
        return

    scores = [row["score"] for row in history]
    best_score = max(scores)
    average_score = sum(scores) / len(scores)
    total_questions = sum(row["question_count"] for row in history)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat"><div class="stat-l">Interviews</div><div class="stat-v">{len(history)}</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat"><div class="stat-l">Average score</div><div class="stat-v">{average_score:.1f}/10</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat"><div class="stat-l">Best score</div><div class="stat-v">{best_score:.1f}/10</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat"><div class="stat-l">Questions asked</div><div class="stat-v">{total_questions}</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("#### Recent interviews")
    for row in history[:5]:
        completed = datetime.fromisoformat(row["completed_at"]).astimezone().strftime("%b %d, %Y")
        score_color = "#047857" if row["score"] >= 7.5 else "#B45309" if row["score"] >= 5 else "#6D28D9"
        st.markdown(
            f"""
            <div class="history-row">
                <div><strong>{html.escape(row['role'])}</strong><div class="history-meta">{html.escape(row['interview_type'])} · {completed} · {row['question_count']} questions</div></div>
                <div class="history-score" style="color:{score_color};">{row['score']:.1f}<small>/10</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def elapsed_str():
    if not st.session_state.session_start_time:
        return "00:00"
    elapsed = int(time.time() - st.session_state.session_start_time)
    return f"{elapsed // 60:02d}:{elapsed % 60:02d}"


def render_stepper(current):
    steps = [
        ("setup", "1 · Setup"),
        ("interview", "2 · Interview"),
        ("report", "3 · Report"),
        ("study_plan", "4 · Study Plan"),
    ]
    order = [s[0] for s in steps]
    current_idx = order.index(current)
    parts = ['<div class="stepper">']
    for i, (key, label) in enumerate(steps):
        cls = "step"
        if key == current:
            cls += " active"
        elif i < current_idx:
            cls += " done"
        prefix = "✓" if i < current_idx else ("●" if key == current else "○")
        parts.append(f'<div class="{cls}">{prefix} {label}</div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def parse_sections(markdown_text: str) -> dict:
    sections = {}
    current = "Overview"
    buf = []
    for line in (markdown_text or "").splitlines():
        if line.startswith("## "):
            sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        elif line.startswith("# "):
            continue
        else:
            buf.append(line)
    sections[current] = "\n".join(buf).strip()
    return {k: v for k, v in sections.items() if v}


def bullet_lines(text):
    items = []
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("-*•").strip()
        if line:
            items.append(line)
    return items


def extract_overall_score(report: str) -> float:
    match = re.search(r"Overall Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", report or "", re.I)
    if match:
        return float(match.group(1))
    return 0.0


def extract_question_scores(report):
    found = re.findall(
        r"Question\s+(\d+)\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10\s*[-–:]?\s*(.*)",
        report or "",
        re.I,
    )
    return [(q, float(score), note.strip()) for q, score, note in found]


def clean_interviewer_question(response: str) -> str:
    """Keep one current question when the model repeats prior question text."""
    text = re.sub(r"\n{3,}", "\n\n", (response or "").strip())
    markers = list(
        re.finditer(
            r"(?i)(?:^|\s)(?:for\s+)?the\s+(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+question\s*:\s*",
            text,
        )
    )
    if len(markers) > 1:
        text = text[markers[-1].end():].strip()
    return text


def extract_day_tasks(plan):
    found = re.findall(
        r"\*\*Day\s+(\d+)[:\.]?\s*(.*?)\*\*\s*[-–:]?\s*(.*)",
        plan or "",
        re.I,
    )
    tasks = []
    for day, title, desc in found:
        label = title.strip(" -–:") or f"Day {day}"
        tasks.append((f"Day {day}: {label}", desc.strip() or "Complete today's focused practice."))
    if tasks:
        return tasks
    return [
        ("Day 1: Core fundamentals", "Refresh role-specific concepts and core CS topics."),
        ("Day 2: Technical deep-dive", "Study the stack, APIs, and architecture trade-offs."),
        ("Day 3: Hands-on practice", "Solve 3–5 coding or system problems from weak areas."),
        ("Day 4: System design", "Sketch a scalable design and explain reliability choices."),
        ("Day 5: Behavioral STAR", "Write 5 STAR stories tied to resume projects."),
        ("Day 6: Timed mock", "Do a timed mock covering yesterday's gaps."),
        ("Day 7: Final review", "Polish talking points, GitHub, and rest well."),
    ]


def send_answer(answer: str):
    st.session_state.messages.append({"role": "user", "content": answer})
    # Do not modify the value of the answer_text widget here.
    # Streamlit forbids changing a widget's session-state value after
    # that widget has already been instantiated in the current run.
    # The interview uses a question-specific widget key, so the next
    # question automatically gets a fresh empty answer box.
    st.session_state.last_audio_hash = ""

    last_question = st.session_state.question_count >= st.session_state.target_questions
    analyze_prompt = f"""
Candidate's answer:
{answer}

Silently analyze this answer. Do not give scores, corrections, hints, or feedback.
"""
    if last_question:
        with st.spinner("Interview complete. Building your evaluation report..."):
            ask_agent(
                st.session_state.conversation_id,
                analyze_prompt + "\nThe interview is now complete. Do not ask another question.",
                st.session_state.vector_store_id,
            )
            st.session_state.evaluation_report = request_evaluation_report(
                st.session_state.conversation_id,
                st.session_state.vector_store_id,
            )
            st.session_state.stage = "report"
        st.rerun()

    with st.spinner("Listening complete. Preparing the next question..."):
        next_q = ask_agent(
            st.session_state.conversation_id,
            analyze_prompt
            + f"\nAsk ONLY the next single interview question "
            f"(Question #{st.session_state.question_count + 1} of {st.session_state.target_questions}). "
            "Return only that question. Do not repeat the previous answer, welcome message, or any earlier question.",
            st.session_state.vector_store_id,
        )
        next_q = clean_interviewer_question(next_q)
        st.session_state.question_count += 1
        st.session_state.current_question = next_q
        st.session_state.messages.append({"role": "assistant", "content": next_q})
    st.rerun()


init_state()
init_database()


def render_auth_page():
    left_column, form_column = st.columns([1.05, 0.95], gap="large")
    with left_column:
        st.markdown(
            """
            <div class="auth-copy">
                <div class="auth-brand">
                    <div class="auth-brand-mark">AI</div>
                    <div class="auth-brand-name">Interview Coach</div>
                </div>
                <span class="pill">Personal interview workspace</span>
                <h1>Build confidence before the real interview.</h1>
                <p>Sign in to keep your interview workspace private and return to your preparation whenever you are ready.</p>
                <div class="auth-points">
                    <div class="auth-point"><span>✓</span> Resume-grounded questions</div>
                    <div class="auth-point"><span>✓</span> Voice or typed answers</div>
                    <div class="auth-point"><span>✓</span> Personal report and study plan</div>
                </div>
                <p class="auth-privacy">Your resume and answers are processed by Microsoft Foundry to generate coaching. Scores are guidance, not hiring decisions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with form_column:
        with st.container(border=True):
            st.markdown('<h2>Welcome back</h2><div class="auth-form-caption">Your next strong answer starts here.</div>', unsafe_allow_html=True)
            login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
            with login_tab:
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
                if submitted:
                    if not email.strip() or not password:
                        st.error("Enter your email and password.")
                    else:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.auth_user = user
                            st.rerun()
                        else:
                            st.error("That email or password is incorrect.")
            with signup_tab:
                with st.form("signup_form"):
                    full_name = st.text_input("Full name", placeholder="Alex Morgan")
                    email = st.text_input("Email", placeholder="you@example.com")
                    password = st.text_input("Password", type="password")
                    confirm_password = st.text_input("Confirm password", type="password")
                    submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if submitted:
                    if not full_name.strip() or not email.strip() or not password:
                        st.error("Complete all fields to create your account.")
                    elif "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                        st.error("Enter a valid email address.")
                    elif len(password) < 8:
                        st.error("Your password must be at least 8 characters.")
                    elif password != confirm_password:
                        st.error("The passwords do not match.")
                    elif not create_user(full_name, email, password):
                        st.error("An account with that email already exists.")
                    else:
                        st.success("Account created. You can now log in.")


if not st.session_state.auth_user:
    render_auth_page()
    st.stop()

with st.sidebar:
    st.markdown(
        """
        <div class="brand-mark">
            <div class="brand-orb">AI</div>
            <div>
                <div class="brand-title">Interview Coach</div>
                <div class="brand-sub">Azure AI Foundry · GPT-4.1-mini</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    if st.session_state.stage != "setup":
        st.markdown("**Session**")
        st.caption(st.session_state.role or "Candidate")
        st.caption(f"{st.session_state.interview_type} · {st.session_state.experience}")
        st.caption(
            f"Progress {min(st.session_state.question_count, st.session_state.target_questions)}"
            f" / {st.session_state.target_questions}"
        )
        if st.button("Start a new session", use_container_width=True):
            reset_interview()
    else:
        st.info("Upload a resume and choose a role to begin a realistic mock interview.")

    with st.expander("Azure Speech (optional)", expanded=False):
        speech_key = st.text_input(
            "Speech key",
            value=st.session_state.speech_key,
            type="password",
        )
        speech_region = st.text_input(
            "Speech region",
            value=st.session_state.speech_region,
            placeholder="eastus",
        )
        if st.button("Save speech settings", use_container_width=True):
            st.session_state.speech_key = speech_key.strip()
            st.session_state.speech_region = speech_region.strip()
            os.environ["SPEECH_KEY"] = speech_key.strip()
            os.environ["SPEECH_REGION"] = speech_region.strip()
            st.success("Saved.")

    st.caption("Resume RAG via File Search · Voice via Azure Speech-to-Text")
    with st.expander("Privacy & responsible AI", expanded=False):
        st.caption("Resume files and interview answers are sent to Microsoft Foundry for question generation and evaluation. Camera frames are optional and are not saved. AI scores can be wrong or biased, so use them as practice guidance rather than a hiring decision.")
        st.caption("Local account and interview history are stored in interview_coach.db.")
        if st.checkbox("I understand local account data will be deleted", key="confirm_delete_account"):
            if st.button("Delete my account and history", key="delete_account", use_container_width=True):
                delete_user(st.session_state.auth_user["id"])
                logout_user()
    st.divider()
    st.caption(f"Signed in as {st.session_state.auth_user['email']}")
    if st.button("Log out", use_container_width=True):
        logout_user()


# ---------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------
if st.session_state.stage == "setup":
    render_history_dashboard()
    st.divider()
    st.markdown(
        """
        <div class="hero-wrap">
            <span class="pill">Hackathon-ready mock interviews</span>
            <h1 class="hero-title">Practice like it's the real interview.</h1>
            <p class="hero-subtitle">
                Upload your resume, pick a role, and sit across from an adaptive AI interviewer.
                You answer one question at a time. Feedback waits until the end — just like a real loop.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_stepper("setup")

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("📄", "Resume-grounded", "Questions pull from your actual projects via File Search."),
        ("🎯", "Adaptive loop", "Each answer quietly shapes the next question."),
        ("🎤", "Voice or type", "Speak into the mic on every question. Azure STT transcribes."),
        ("📊", "Report + plan", "Scores, gaps, and a 7-day checklist after you finish."),
    ]
    for col, (icon, title, desc) in zip((f1, f2, f3, f4), features):
        col.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown('<div class="section-kicker">Interview setup</div>', unsafe_allow_html=True)
        st.subheader("Who are you interviewing as?")

        chips = st.columns(4)
        presets = [
            ("Cloud Architect", "Azure Cloud Solutions Architect"),
            ("Backend Dev", "Backend Python Developer"),
            ("AI / ML", "Generative AI & ML Engineer"),
            ("Full Stack", "Full Stack Engineer"),
        ]
        for col, (label, value) in zip(chips, presets):
            if col.button(label, use_container_width=True):
                st.session_state.role = value
                st.rerun()

        st.text_input(
            "Target job role",
            key="role",
            placeholder="e.g. Senior Backend Developer",
        )

        c1, c2 = st.columns(2)
        with c1:
            st.selectbox(
                "Experience level",
                [
                    "Beginner (0-1 yrs)",
                    "Intermediate (2-4 yrs)",
                    "Advanced (5-8 yrs)",
                    "Senior / Lead (8+ yrs)",
                ],
                key="experience",
            )
        with c2:
            st.selectbox(
                "Interview type",
                ["Technical", "HR", "Behavioral", "Mixed"],
                key="interview_type",
            )

        st.slider(
            "Number of questions",
            min_value=3,
            max_value=10,
            key="target_questions",
            help="Choose how many questions this interview should contain.",
        )

    with right:
        st.markdown('<div class="section-kicker">Resume RAG</div>', unsafe_allow_html=True)
        st.subheader("Upload your PDF resume")
        st.caption("Indexed with Azure File Search so questions reference your real work.")

        resume_file = st.file_uploader("Resume PDF", type=["pdf"], label_visibility="collapsed")
        if resume_file:
            st.session_state.resume_name = resume_file.name
            kb = round(len(resume_file.getvalue()) / 1024, 1)
            st.markdown(
                f"""
                <div class="resume-ok">
                    <div>
                        <div style="font-weight:800;color:#065F46;">{html.escape(resume_file.name)}</div>
                        <div style="color:#059669;font-size:0.82rem;">{kb} KB · ready to index</div>
                    </div>
                    <span class="pill green">Attached</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="border:2px dashed #93C5FD;border-radius:16px;padding:1.6rem 1rem;
                            text-align:center;color:#64748B;background:#F8FBFF;">
                    Drop a PDF here. The interviewer will cite projects, tools, and skills from it.
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.caption("Tip: use STAR (Situation, Task, Action, Result) for behavioral answers.")

    st.write("")
    if st.button("Start interview", type="primary", use_container_width=True):
        if not (st.session_state.role or "").strip():
            st.error("Please enter a target job role.")
        elif not resume_file:
            st.error("Please upload a PDF resume.")
        else:
            with st.status("Preparing your interview room...", expanded=True) as status:
                selected_question_count = int(st.session_state.target_questions)
                st.write("Connecting to Azure AI Foundry")
                st.session_state.conversation_id = create_conversation()
                st.write("Indexing resume with File Search")
                st.session_state.vector_store_id = upload_resume(resume_file)
                st.write("Writing the first question from your resume")
                first_prompt = f"""
You are a professional interviewer for the role of {st.session_state.role}.
Experience level: {st.session_state.experience}.
Interview type: {st.session_state.interview_type}.
The candidate selected exactly {selected_question_count} questions for this interview.
The candidate resume is available via File Search.

Rules:
1. Conduct a realistic interview with exactly {selected_question_count} total questions.
2. Ask ONLY ONE question at a time. Never include two questions in one response.
3. Number each question mentally from 1 through {selected_question_count}.
4. Start with a brief, warm welcome, then question 1.
5. Ground questions in resume projects, tools, and impact where possible.
6. Never give scores, hints, or feedback during the interview.
7. Silently evaluate each answer and adapt later questions.
8. Keep questions concise and interview-like.
9. Return only the current question text after the welcome. Never repeat earlier question text.
"""
                first_q = ask_agent(
                    st.session_state.conversation_id,
                    first_prompt,
                    st.session_state.vector_store_id,
                )
                first_q = clean_interviewer_question(first_q)
                st.session_state.current_question = first_q
                st.session_state.messages = [{"role": "assistant", "content": first_q}]
                st.session_state.session_start_time = time.time()
                st.session_state.question_count = 1
                st.session_state.stage = "interview"
                status.update(label="Interview ready", state="complete")
            st.rerun()


# ---------------------------------------------------------------------------
# INTERVIEW
# ---------------------------------------------------------------------------
elif st.session_state.stage == "interview":
    st.session_state.current_question = clean_interviewer_question(
        st.session_state.current_question
    )
    total = max(1, st.session_state.target_questions)
    current = st.session_state.question_count

    h1, h2, h3, h4 = st.columns([1.6, 2.1, 0.9, 1.2])
    with h1:
        st.markdown(
            f"""
            <div class="hud">
                <span class="live-dot"></span>
                <strong>Live interview</strong>
                <div style="color:#64748B;font-size:0.82rem;margin-top:0.15rem;">
                    {html.escape(st.session_state.role)} · {html.escape(st.session_state.interview_type)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h2:
        st.progress(min(1.0, current / total), text=f"Question {current} of {total}")
    with h3:
        st.markdown(
            f'<div class="stat"><div class="stat-l">Time</div><div class="stat-v">{elapsed_str()}</div></div>',
            unsafe_allow_html=True,
        )
    with h4:
        if st.button("End & view report", use_container_width=True):
            with st.spinner("Generating your evaluation report..."):
                st.session_state.evaluation_report = request_evaluation_report(
                    st.session_state.conversation_id,
                    st.session_state.vector_store_id,
                )
                st.session_state.stage = "report"
            st.rerun()
        if st.button("Log out", key="interview_logout", use_container_width=True):
            logout_user()

    q_safe = html.escape(st.session_state.current_question).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="question-card">
            <div class="interviewer">
                <div class="avatar">IC</div>
                <div>
                    <div style="font-weight:800;">AI Interviewer</div>
                    <div style="font-size:0.78rem;color:#64748B;">Question {current} · no scores shown until the end</div>
                </div>
            </div>
            <div class="question-text">{q_safe}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-kicker">Your answer</div>', unsafe_allow_html=True)
    st.subheader("Type, speak, or optionally turn on your camera")

    mic_col, hint_col = st.columns([1.7, 1])
    with mic_col:
        audio = st.audio_input(
            "Record your answer",
            key=f"mic_q_{current}",
        )
    with hint_col:
        st.checkbox("Enable camera", key="camera_enabled")
        st.caption("Record, then we transcribe with Azure Speech-to-Text. Edit the text before sending if you want.")
        if st.session_state.last_engine:
            st.markdown(
                f'<span class="pill green">Transcribed · {html.escape(st.session_state.last_engine)}</span>',
                unsafe_allow_html=True,
            )

    if st.session_state.camera_enabled:
        camera_col, camera_hint_col = st.columns([1.7, 1])
        with camera_col:
            camera_frame = st.camera_input(
                "Camera",
                key=f"camera_q_{current}",
            )
        with camera_hint_col:
            st.caption("Camera is optional. Capture a frame only when you want to check your setup; it is not stored with your interview history.")
        if camera_frame is not None:
            st.image(camera_frame, caption="Camera enabled for this question", width=260)

    # Give every question its own answer widget key.
    # This avoids modifying a widget's session state after instantiation
    # and automatically gives the candidate a fresh answer box for each
    # new question.
    answer_key = f"answer_text_q_{current}"

    if audio is not None:
        audio_bytes = audio.getvalue()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if audio_hash != st.session_state.last_audio_hash:
            tmp_path = "voice_input.wav"
            with open(tmp_path, "wb") as handle:
                handle.write(audio_bytes)
            with st.spinner("Transcribing with Azure Speech-to-Text..."):
                text, err, engine = speech_to_text_detailed(
                    tmp_path,
                    speech_key=st.session_state.speech_key,
                    speech_region=st.session_state.speech_region,
                )
            if text and text.strip():
                # This assignment happens before the text-area widget is
                # instantiated in this run, so it is safe.
                st.session_state[answer_key] = text.strip()
                st.session_state.last_audio_hash = audio_hash
                st.session_state.last_engine = engine or "Speech"
                st.rerun()
            else:
                st.warning(err or "Could not recognize speech. Try again or type your answer.")

    st.text_area(
        "Answer",
        key=answer_key,
        height=140,
        placeholder="Speak with the microphone or type your answer here...",
        label_visibility="collapsed",
    )

    send_col, skip_col = st.columns([3, 1])
    with send_col:
        if st.button("Send answer", type="primary", use_container_width=True):
            answer = (st.session_state.get(answer_key) or "").strip()

            if not answer:
                st.warning("Please type or record an answer before sending.")
            else:
                send_answer(answer)
    with skip_col:
        st.caption("The interviewer waits. No live scoring.")

    with st.expander("Earlier questions", expanded=False):
        for msg in st.session_state.messages[:-1]:
            who = "Interviewer" if msg["role"] == "assistant" else "You"
            st.markdown(f"**{who}**")
            st.write(msg["content"])


# ---------------------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------------------
elif st.session_state.stage == "report":
    st.markdown(
        """
        <div class="hero-wrap">
            <span class="pill green">Interview complete</span>
            <h1 class="hero-title">Your evaluation report</h1>
            <p class="hero-subtitle">Scores and coaching notes stayed hidden until now — so the session felt like a real interview.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_stepper("report")
    st.info("This report is AI-generated practice guidance. It may contain errors or bias and should not be used as the sole hiring decision.")

    report = st.session_state.evaluation_report or ""
    sections = parse_sections(report)
    score = extract_overall_score(report)
    pct = max(0, min(100, int((score / 10) * 100))) if score else 0
    q_scores = extract_question_scores(report)
    save_interview_history(
        st.session_state.auth_user["id"],
        st.session_state.interview_session_id,
        st.session_state.role,
        st.session_state.interview_type,
        score,
        st.session_state.question_count,
    )

    if score >= 7.5:
        verdict, vcolor, vpill = "Job ready", "#047857", "green"
    elif score >= 5:
        verdict, vcolor, vpill = "Needs practice", "#B45309", "amber"
    else:
        verdict, vcolor, vpill = "Keep building", "#6D28D9", "violet"

    b1, b2, b3, b4 = st.columns([1.15, 1, 1, 1])
    with b1:
        st.markdown(
            f"""
            <div class="score-ring" style="--pct: {pct * 3.6}deg;">
                <div class="score-num">{score if score else "—"}</div>
                <div class="score-lbl">OUT OF 10</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b2:
        st.markdown(
            f'<div class="stat"><div class="stat-l">Role</div><div class="stat-v">{html.escape(st.session_state.role)}</div></div>',
            unsafe_allow_html=True,
        )
    with b3:
        st.markdown(
            f'<div class="stat"><div class="stat-l">Questions</div><div class="stat-v">{st.session_state.question_count}</div></div>',
            unsafe_allow_html=True,
        )
    with b4:
        st.markdown(
            f'<div class="stat"><div class="stat-l">Verdict</div><div class="stat-v" style="color:{vcolor};">{verdict}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    overview = sections.get("Overall Performance", "")
    if overview:
        st.markdown("#### Overall performance")
        st.markdown(overview)

    if q_scores:
        st.markdown("#### Question-wise scores")
        for qnum, qscore, note in q_scores:
            width = int(max(0, min(100, (qscore / 10) * 100)))
            st.markdown(
                f"""
                <div class="qscore">
                    <div style="display:flex;justify-content:space-between;gap:1rem;">
                        <strong>Question {html.escape(qnum)}</strong>
                        <span class="pill">{qscore}/10</span>
                    </div>
                    <div style="color:#475569;font-size:0.9rem;margin-top:0.25rem;">{html.escape(note)}</div>
                    <div class="bar-bg"><div class="bar-fill" style="width:{width}%;"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    elif sections.get("Question-Wise Scores"):
        st.markdown("#### Question-wise scores")
        st.markdown(sections["Question-Wise Scores"])

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### Strengths")
        for item in bullet_lines(sections.get("Strengths", "")) or ["Not enough signal yet."]:
            st.markdown(f'<div class="insight good">✓ {html.escape(item)}</div>', unsafe_allow_html=True)
        st.markdown("#### Communication")
        comm = sections.get("Communication Analysis", "")
        comm_html = html.escape(comm).replace("\n", "<br>") if comm else "Communication notes will appear here."
        st.markdown(f'<div class="insight info">{comm_html}</div>', unsafe_allow_html=True)
    with c_right:
        st.markdown("#### Weaknesses")
        for item in bullet_lines(sections.get("Weaknesses", "")) or ["None highlighted."]:
            st.markdown(f'<div class="insight warn">! {html.escape(item)}</div>', unsafe_allow_html=True)
        st.markdown("#### Technical gaps")
        for item in bullet_lines(sections.get("Technical Gaps", "")) or ["None highlighted."]:
            st.markdown(f'<div class="insight gap">◆ {html.escape(item)}</div>', unsafe_allow_html=True)

    st.markdown("#### Improvement suggestions")
    for item in bullet_lines(sections.get("Improvement Suggestions", "")) or []:
        st.markdown(f"- {item}")

    leftover_keys = [
        k
        for k in sections
        if k
        not in {
            "Overall Performance",
            "Question-Wise Scores",
            "Strengths",
            "Weaknesses",
            "Technical Gaps",
            "Communication Analysis",
            "Improvement Suggestions",
            "Overview",
        }
    ]
    if leftover_keys:
        with st.expander("Full report text"):
            st.markdown(report)

    a1, a2 = st.columns([1.6, 1])
    with a1:
        if st.button("Open personalized study plan", type="primary", use_container_width=True):
            if not st.session_state.study_plan:
                with st.spinner("Designing a 7-day plan from your gaps..."):
                    st.session_state.study_plan = request_study_plan(
                        st.session_state.conversation_id,
                        st.session_state.vector_store_id,
                    )
            st.session_state.stage = "study_plan"
            st.rerun()
    with a2:
        if st.button("Start a new interview", use_container_width=True):
            reset_interview()


# ---------------------------------------------------------------------------
# STUDY PLAN
# ---------------------------------------------------------------------------
elif st.session_state.stage == "study_plan":
    st.markdown(
        """
        <div class="hero-wrap">
            <span class="pill violet">Personalized prep</span>
            <h1 class="hero-title">Your 7-day study plan</h1>
            <p class="hero-subtitle">Topics and daily tasks generated from this interview. Check things off as you go.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_stepper("study_plan")

    plan = st.session_state.study_plan or ""
    sections = parse_sections(plan)

    topics = bullet_lines(sections.get("Personalized Topics to Improve", ""))
    if topics:
        st.markdown("#### Topics to improve")
        tcols = st.columns(min(3, len(topics)))
        for i, topic in enumerate(topics[:6]):
            tcols[i % len(tcols)].markdown(
                f'<div class="feature-card"><div class="feature-title">{html.escape(topic)}</div></div>',
                unsafe_allow_html=True,
            )

    if sections.get("Recommended Resources"):
        with st.expander("Recommended resources", expanded=False):
            st.markdown(sections["Recommended Resources"])

    st.markdown("#### Daily tasks")
    st.caption("Check a box when the day's work is done. Progress stays in this browser session.")
    tasks = extract_day_tasks(plan)
    done = 0
    for idx, (title, desc) in enumerate(tasks, 1):
        checked = st.checkbox(f"**{title}** — {desc}", key=f"study_task_{idx}")
        if checked:
            done += 1
    ratio = done / max(1, len(tasks))
    st.markdown(f"**Study progress:** {done} / {len(tasks)} days ({int(ratio * 100)}%)")
    st.progress(ratio)

    export = f"""# AI Interview Coach Report

- Role: {st.session_state.role}
- Experience: {st.session_state.experience}
- Interview type: {st.session_state.interview_type}
- Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

{st.session_state.evaluation_report}

---

{st.session_state.study_plan}
"""
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button(
            "Download report (.md)",
            data=export,
            file_name=f"interview_report_{(st.session_state.role or 'candidate').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with e2:
        if st.button("Back to report", use_container_width=True):
            st.session_state.stage = "report"
            st.rerun()
    with e3:
        if st.button("Start a new interview", type="primary", use_container_width=True):
            reset_interview()
