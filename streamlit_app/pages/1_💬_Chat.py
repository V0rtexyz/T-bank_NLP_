"""T-Plexity Chat - AI-powered Q&A with RAG"""

import streamlit as st
import asyncio
from datetime import datetime
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client

st.set_page_config(page_title="T-Plexity Chat", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #FFDD2D;
}

.user-message {
    background-color: #FFF9E6;
    margin-left: 10%;
}

.assistant-message {
    background-color: #F5F5F5;
    margin-right: 10%;
}

.source-card {
    background-color: white;
    border: 1px solid #FFDD2D;
    border-radius: 6px;
    padding: 0.75rem;
    margin: 0.5rem 0;
}

.stButton>button[kind="primary"] {
    background-color: #FFDD2D;
    color: #1F1F1F;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Header
st.title("💬 T-Plexity Chat")
st.markdown("Ask questions about investment markets and get AI-powered answers")

# Sidebar settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    top_k = st.slider("Number of sources", 1, 10, 5)
    use_rerank = st.checkbox("Use reranking", value=True)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 1000, 100)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🔄 New", use_container_width=True):
            api = get_api_client()
            asyncio.run(api.clear_session(st.session_state.session_id))
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
    
    st.divider()
    st.metric("Messages", len(st.session_state.messages))

# Quick questions
if len(st.session_state.messages) == 0:
    st.markdown("### 💡 Try asking:")
    
    questions = [
        "Latest trends in tech stocks?",
        "Federal Reserve policy updates?",
        "Market volatility analysis?",
    ]
    
    cols = st.columns(3)
    for idx, q in enumerate(questions):
        with cols[idx]:
            if st.button(q, key=f"q{idx}", use_container_width=True):
                st.session_state.quick_q = q

# Display messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 T-Plexity:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
        
        if msg.get("sources"):
            with st.expander(f"📚 {len(msg['sources'])} source(s)"):
                for idx, src in enumerate(msg["sources"], 1):
                    metadata = src.get("metadata", {})
                    st.markdown(f"""
                    <div class="source-card">
                        <strong>Source {idx}:</strong> {src.get('doc_id', 'Unknown')}<br>
                        <small>📅 {metadata.get('date', 'N/A')} | 📢 {metadata.get('channel_id', 'N/A')}</small><br>
                        <a href="{metadata.get('link', '#')}" target="_blank">🔗 View original</a>
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
query = st.chat_input("Ask anything about investment markets...")

# Handle quick question
if "quick_q" in st.session_state:
    query = st.session_state.quick_q
    del st.session_state.quick_q

if query:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    with st.spinner("🤔 Thinking..."):
        try:
            api = get_api_client()
            result = asyncio.run(api.generate_answer(
                query=query,
                top_k=top_k,
                use_rerank=use_rerank,
                temperature=temperature,
                max_tokens=max_tokens,
                session_id=st.session_state.session_id
            ))
            
            answer = result.get("detailed_answer", result.get("answer", "No answer"))
            sources = result.get("sources", [])
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "sources": sources
            })
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Empty state
if not st.session_state.messages:
    st.info("👋 Start a conversation by asking a question about investment markets!")

