import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Import everything from rag.py ─────────────────────────────
from rag import (
    smart_search,
    generate_answer,
    chunks,
    metadata
)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="LexAI — Indian Legal Research",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.lex-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border-left: 5px solid #c9a84c;
}
.lex-title {
    font-family: 'EB Garamond', serif;
    font-size: 2.8rem;
    color: #f0e6d3;
    margin: 0;
}
.lex-subtitle {
    color: #c9a84c;
    font-size: 0.9rem;
    margin-top: 0.4rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Dynamically adapt to Light/Dark Mode using Streamlit variables */
.answer-box {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-left: 4px solid #c9a84c;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    line-height: 1.8;
}

.source-box {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.85rem;
}

.source-box-web {
    border-left: 3px solid #0d6e34;
}

.text-muted {
    color: var(--text-color);
    opacity: 0.7;
}

.stButton > button {
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: white !important;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-size: 1rem;
    font-weight: 500;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div class="lex-header">
    <div class="lex-title">⚖️ LexAI</div>
    <div class="lex-subtitle">Indian Legal Research Assistant · Moot Court Edition</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    mode = st.radio(
        "Argument Mode",
        ["Both sides", "Petitioner", "Respondent"]
    )

    num_chunks = st.slider(
        "Document chunks to retrieve",
        min_value=1, max_value=5, value=3
    )

    st.markdown("---")
    st.markdown("### 📚 Loaded Documents")
    unique_sources = list(set(m["source"] for m in metadata))
    for src in unique_sources:
        st.markdown(f"📄 `{src}`")

    st.markdown("---")
    st.markdown("### 💡 Try these questions")
    examples = [
        "Arguments for right to privacy under Article 21",
        "What is the basic structure doctrine?",
        "Freedom of speech under Article 19",
        "Rights of accused under Article 22",
        "When is Habeas Corpus issued?",
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state["question"] = ex

# ── Main input ────────────────────────────────────────────────
question = st.text_area(
    "Enter your legal research question",
    value=st.session_state.get("question", ""),
    height=100,
    placeholder="e.g. What are the constitutional arguments for right to privacy under Article 21?"
)

col1, col2 = st.columns([1, 5])
with col1:
    search_btn = st.button("🔍 Research")
with col2:
    if st.button("🗑️ Clear"):
        st.session_state["question"] = ""
        st.rerun()

# ── Search ────────────────────────────────────────────────────
if search_btn and question.strip():

    with st.spinner("🔍 Searching legal documents..."):
        T_c, T_m, T_s, web_result = smart_search(question, k=num_chunks)

    if web_result:
        st.info("🌐 Web augmented — local docs had low relevance, searched web too")
    else:
        st.success("📄 Local only — strong matches found in your documents")

    with st.spinner("⚖️ Generating legal research..."):
        try:
            answer = generate_answer(question, T_c, T_m, web_result,)

            st.markdown("### Research Results")
            st.markdown(f'<div class="answer-box">{answer}</div>',
                        unsafe_allow_html=True)

# Local sources
            if T_c:
                st.markdown("#### 📄 Local Document Sources")
                for meta, chunk in zip(T_m, T_c):
                    source = meta["source"].replace(".pdf", "")
                    preview = chunk[:150].replace("\n", " ") + "..."
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>{source}</strong><br>
                        <span class="text-muted" style="font-size:0.8rem">{preview}</span><br>
                    </div>
                    """, unsafe_allow_html=True)

            # Web sources
            if web_result:
                st.markdown("#### 🌐 Web Sources")
                for r in web_result:
                    st.markdown(f"""
                    <div class="source-box source-box-web">
                        <strong>{r['title']}</strong><br>
                        <span class="text-muted" style="font-size:0.8rem">
                            {r['body'][:150]}...
                        </span><br>
                        <a href="{r['url']}" target="_blank" style="color:#0d6e34;font-size:0.75rem;font-weight:600;">
                            View source →
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.download_button(
                label="📥 Download Research",
                data=f"QUESTION:\n{question}\n\nMODE: {mode}\n\n{'='*50}\n\nANSWER:\n{answer}",
                file_name="legal_research.txt",
                mime="text/plain"
            )

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                st.error("⏳ Gemini quota exceeded. Wait a minute and try again.")
            else:
                st.error(f"Error: {err}")

elif search_btn:
    st.warning("Please enter a question first.")

else:
    st.markdown("""
    <div style="text-align:center;padding:3rem;color:#888;">
        <div style="font-size:3rem">⚖️</div>
        <div style="font-size:1.1rem;margin-top:1rem;
                    font-family:'EB Garamond',serif;">
            Ask any Indian legal research question above
        </div>
        <div style="font-size:0.85rem;margin-top:0.5rem;">
            Searches your local documents · Auto web search if needed
            · Powered by Gemini
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.75rem;color:#aaa;">
    LexAI · Built with RAG · Powered by Gemini · Indian Law Focus
</div>
""", unsafe_allow_html=True)