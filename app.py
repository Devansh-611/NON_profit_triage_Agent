import streamlit as st
from triage.llm_service import LLMService
from triage.decision_engine import DecisionEngine
from triage.response_generator import ResponseGenerator
from triage.gmail_fetcher import fetch_latest_email, send_reply

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(
    page_title="AI Triage old Agent",
    page_icon="🤖",
    layout="wide"
)

# ------------------------------
# Custom CSS - Warm Editorial Theme
# ------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    background-color: #faf7f2;
    color: #2c2416;
}

.stApp {
    background: #faf7f2;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #2c2416 !important;
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #e8dcc8 !important;
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f0c060 !important;
    border-bottom: 1px solid rgba(240,192,96,0.3);
    padding-bottom: 8px;
    margin-bottom: 12px;
}

/* Hero */
.hero-section {
    background: linear-gradient(135deg, #2c2416 0%, #3d3020 60%, #4a3828 100%);
    border-radius: 20px;
    padding: 52px 56px 44px;
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(240,192,96,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(240,192,96,0.07) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-tag {
    display: inline-block;
    font-family: 'Lato', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #f0c060;
    border: 1px solid rgba(240,192,96,0.4);
    border-radius: 20px;
    padding: 5px 14px;
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 700;
    color: #faf7f2;
    line-height: 1.15;
    margin-bottom: 14px;
}
.hero-title span {
    color: #f0c060;
    font-style: italic;
}
.hero-subtitle {
    font-family: 'Lato', sans-serif;
    font-size: 1.05rem;
    font-weight: 300;
    color: #c8b898;
    line-height: 1.7;
    max-width: 520px;
}

/* Cards */
.card {
    background: #ffffff;
    border: 1px solid #e8e0d0;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(44,36,22,0.06);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.card:hover {
    box-shadow: 0 6px 24px rgba(44,36,22,0.1);
    transform: translateY(-1px);
}
.card-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #a08060;
    margin-bottom: 10px;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 7px 18px;
    border-radius: 30px;
    font-size: 0.88rem;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.badge-intent { background: #fff3d6; color: #8a5a00; border: 1px solid #f0c060; }
.badge-high   { background: #ffeaea; color: #b03030; border: 1px solid #e08080; }
.badge-medium { background: #fff8e0; color: #8a6a00; border: 1px solid #d4a800; }
.badge-low    { background: #eafaf0; color: #207040; border: 1px solid #70c090; }

/* Entity chips */
.entity-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.entity-chip {
    background: #f5f0e8;
    border: 1px solid #d8cbb8;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.85rem;
    color: #4a3828;
}
.entity-chip strong {
    font-weight: 700;
    color: #2c2416;
    margin-right: 4px;
}
.entity-type {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #a08060;
    margin-left: 4px;
}

/* Reply box */
.reply-card {
    background: linear-gradient(135deg, #fffdf8 0%, #fff9ee 100%);
    border: 1px solid #e8d8b0;
    border-left: 4px solid #f0c060;
    border-radius: 16px;
    padding: 28px 32px;
    margin-top: 8px;
}
.reply-card p {
    font-family: 'Lato', sans-serif;
    font-size: 1rem;
    line-height: 1.85;
    color: #3a2c18;
    white-space: pre-wrap;
}

/* Textarea */
.stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #d8cbb8 !important;
    border-radius: 12px !important;
    color: #2c2416 !important;
    font-family: 'Lato', sans-serif !important;
    font-size: 0.97rem !important;
    padding: 16px 18px !important;
    line-height: 1.7 !important;
    transition: border-color 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: #f0c060 !important;
    box-shadow: 0 0 0 3px rgba(240,192,96,0.15) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'Lato', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    color: #a08060 !important;
}

/* Button */
.stButton > button {
    background: #2c2416 !important;
    color: #faf7f2 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 40px !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    box-shadow: 0 4px 16px rgba(44,36,22,0.25) !important;
}
.stButton > button:hover {
    background: #f0c060 !important;
    color: #2c2416 !important;
    box-shadow: 0 6px 24px rgba(240,192,96,0.35) !important;
    transform: translateY(-1px) !important;
}

hr { border-color: #e8e0d0 !important; margin: 2rem 0 !important; }
.stSpinner > div { border-top-color: #f0c060 !important; }
.stAlert { border-radius: 12px !important; }

.placeholder-box {
    background: #ffffff;
    border: 2px dashed #e8d8b0;
    border-radius: 16px;
    padding: 60px 40px;
    text-align: center;
    color: #c0a880;
}
.placeholder-icon { font-size: 3rem; margin-bottom: 16px; }
.placeholder-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: #a08060;
    margin-bottom: 8px;
}
.placeholder-text { font-size: 0.9rem; line-height: 1.7; color: #c0a880; }
            
/* ===== FIX: Make full-width content truly full ===== */
.block-container {
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.markdown("## 🤖 About")
    st.markdown("---")
    st.markdown("""
    This AI triage agent helps non-profit teams automatically classify, prioritize, and respond to incoming emails and support requests.

    *Powered by:*
    - 🧠 LLM Service (Text processing)
    - ⚙️ Decision Engine (Analysis)
    - ✉️ Response Generator (Reply drafting)
    """)
    st.markdown("---")
    st.markdown("### 🎯 Intent Types")
    st.markdown("- Donation Inquiry")
    st.markdown("- Emergency Request")
    st.markdown("- Insurance Claim")
    st.markdown("- Complaint")
    st.markdown("- Promotional")
    st.markdown("---")
    st.markdown("### 🚦 Urgency Levels")
    st.markdown("🔴 *High* — Immediate attention needed")
    st.markdown("🟡 *Medium* — Address soon")
    st.markdown("🟢 *Low* — Normal queue")

# ------------------------------
# Hero Section
# ------------------------------
st.markdown("""
<div class='hero-section'>
    <div class='hero-tag'>✦ AI-AGENT</div>
    <div class='hero-title'>Non-Profit Support<br><span>Triage Agent</span></div>
    <div class='hero-subtitle'>Analyze incoming emails, classify intent, detect urgency, and generate thoughtful replies — all in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Process & Display Results
# ------------------------------
def process_and_display(text):
    try:
        with st.spinner("Processing with AI..."):
            llm = LLMService()
            decision_engine = DecisionEngine()
            response_gen = ResponseGenerator()

            structured = llm.process_text(text)
            decision = decision_engine.analyze(structured)
            response = response_gen.generate(decision)

        # Auto send reply if sender info available
        sender = st.session_state.get("sender")
        subject = st.session_state.get("subject", "Your Request")
        if sender:
            sent = send_reply(sender, subject, response)
            if sent:
                st.success(f"Reply automatically sent to {sender}")
            else:
                st.error("Failed to send reply")

        # Clear session after processing
        for key in ["auto_msg", "auto_process", "sender", "subject"]:
            if key in st.session_state:
                del st.session_state[key]

        # Intent
        st.markdown(f"""
        <div class='card'>
            <div class='card-label'> Detected Intent</div>
            <span class='badge badge-intent'>{decision['intent'].title()}</span>
        </div>""", unsafe_allow_html=True)

        # Urgency
        urgency = decision['urgency']
        urg_cls = "badge-high" if "high" in urgency.lower() else ("badge-medium" if "medium" in urgency.lower() else "badge-low")
        urg_icon = "🔴" if "high" in urgency.lower() else ("🟡" if "medium" in urgency.lower() else "🟢")
        st.markdown(f"""
        <div class='card'>
            <div class='card-label'>🚦 Urgency Level</div>
            <span class='badge {urg_cls}'>{urg_icon} {urgency.title()}</span>
        </div>""", unsafe_allow_html=True)

        # Entities
        entities = decision["entities"]
        if entities:
            chips = "".join([
                f"<span class='entity-chip'><strong>{k.capitalize()}:</strong> {v if v else 'None'}</span>"
                for k, v in entities.items()
            ])
            st.markdown(f"""
            <div class='card'>
                <div class='card-label'>📌 Extracted Information</div>
                <div class='entity-wrap'>{chips}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='card'>
                <div class='card-label'>📌 Extracted Information</div>
                <span style='color:#c0a880;font-style:italic;font-size:0.9rem;'>No entities extracted</span>
            </div>""", unsafe_allow_html=True)

        # Response
        st.markdown(f"""
        <div class='card'>
            <div class='card-label'>✉️ Generated Response</div>
            <div class='reply-card'><p>{response}</p></div>
        </div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")

# ------------------------------
# Main Layout
# ------------------------------
left, right = st.columns([1, 1.1], gap="large")

with left:
    st.markdown("<div class='card-label' style='font-size:0.72rem;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#a08060;margin-bottom:10px;'>📩 Incoming Email / Request</div>", unsafe_allow_html=True)

    default_text = st.session_state.get("auto_msg", "")

    user_input = st.text_area(
        label="input",
        label_visibility="collapsed",
        placeholder="Paste the incoming email or support request here...\n\nExample: 'Hi, I'd like to donate $500 to your food drive. How do I proceed?'",
        height=220,
        value=default_text
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("📬 Fetch & Process Latest Email"):
        with st.spinner("Fetching email..."):
            result = fetch_latest_email()
        if result:
            st.session_state["auto_msg"] = result["body"]
            st.session_state["sender"] = result["sender"]
            st.session_state["subject"] = result["subject"]
            st.session_state["auto_process"] = True
            st.rerun()
        else:
            st.info("No emails found.")

with right:
    if st.session_state.get("auto_process") and default_text.strip():
        process_and_display(default_text)
    else:
        st.markdown("""
        <div class='placeholder-box'>
            <div class='placeholder-icon'>🤖</div>
            <div class='placeholder-title'>Ready to Analyze</div>
            <div class='placeholder-text'>Click <strong>Fetch & Process Latest Email</strong><br>to automatically fetch, analyze,<br>and reply to your latest email</div>
        </div>""", unsafe_allow_html=True)