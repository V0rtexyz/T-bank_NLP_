"""
Settings Page - Advanced configuration and system information
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import apply_custom_css
from utils.api import get_api_status, clear_session
from utils.session import initialize_session_state

st.set_page_config(
    page_title="Settings | T-Plexity",
    page_icon="⚙️",
    layout="wide"
)

apply_custom_css()
initialize_session_state()

st.markdown("# ⚙️ Settings")
st.markdown("### Configure T-Plexity settings")
st.markdown("---")

# API Configuration
st.markdown("## 🔌 API Configuration")

col1, col2 = st.columns(2)

with col1:
    api_url = os.getenv("API_BASE_URL", "http://localhost:8002")
    st.text_input(
        "API Base URL",
        value=api_url,
        disabled=True,
        help="The backend API URL (set via environment variable)"
    )

with col2:
    status = get_api_status()
    if status["healthy"]:
        st.success("✅ API is healthy and reachable")
    else:
        st.error("❌ API is not reachable")

st.markdown("---")

# Model Settings
st.markdown("## 🤖 Model Settings")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### LLM Provider")
    model_options = ["qwen", "chatgpt", "deepseek"]
    new_model = st.selectbox(
        "Select Language Model",
        model_options,
        index=model_options.index(st.session_state.get("llm_provider", "qwen")),
        help="Choose which language model to use for generation"
    )
    if new_model != st.session_state.get("llm_provider"):
        st.session_state.llm_provider = new_model
        st.success(f"✅ Model changed to {new_model}")

    st.markdown("### Temperature")
    new_temp = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.get("temperature", 0.7),
        step=0.1,
        help="Higher values make output more random, lower more focused"
    )
    if new_temp != st.session_state.get("temperature"):
        st.session_state.temperature = new_temp

with col2:
    st.markdown("### Number of Sources")
    new_top_k = st.slider(
        "Top K",
        min_value=1,
        max_value=10,
        value=st.session_state.get("top_k", 5),
        help="Number of relevant documents to retrieve"
    )
    if new_top_k != st.session_state.get("top_k"):
        st.session_state.top_k = new_top_k

    st.markdown("### Reranking")
    new_rerank = st.checkbox(
        "Use Reranking",
        value=st.session_state.get("use_rerank", True),
        help="Use reranking to improve source relevance (slower but more accurate)"
    )
    if new_rerank != st.session_state.get("use_rerank"):
        st.session_state.use_rerank = new_rerank

st.markdown("---")

# Session Management
st.markdown("## 🗂️ Session Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Current Session")
    st.code(st.session_state.session_id, language=None)
    
    message_count = len(st.session_state.get("messages", []))
    st.metric("Messages in History", message_count)

with col2:
    st.markdown("### Actions")
    
    if st.button("🔄 Start New Session", type="secondary", use_container_width=True):
        try:
            # Clear session on backend
            clear_session(st.session_state.session_id)
            # Reset local session
            st.session_state.messages = []
            import uuid
            st.session_state.session_id = str(uuid.uuid4())
            st.success("✅ Started new session!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error clearing session: {str(e)}")
    
    if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.success("✅ Chat history cleared!")
        st.rerun()

st.markdown("---")

# System Information
st.markdown("## 📊 System Information")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Frontend")
    st.markdown("**Framework:** Streamlit")
    st.markdown(f"**Version:** {st.__version__}")
    st.markdown("**Status:** 🟢 Running")

with col2:
    st.markdown("### Backend")
    st.markdown("**API Type:** FastAPI")
    status = get_api_status()
    st.markdown(f"**Status:** {'🟢 Healthy' if status['healthy'] else '🔴 Unavailable'}")

with col3:
    st.markdown("### Models Available")
    st.markdown("- Qwen")
    st.markdown("- ChatGPT")
    st.markdown("- DeepSeek")

st.markdown("---")

# About
st.markdown("## ℹ️ About T-Plexity")

st.markdown(
    """
    **T-Plexity** is an intelligent investment intelligence system that:
    
    - 🔍 Aggregates news from Telegram investment channels
    - 🤖 Uses AI to answer questions about markets and investments
    - 📚 Provides transparent source citations
    - 💡 Offers real-time insights powered by RAG (Retrieval-Augmented Generation)
    
    ### Technology Stack
    - **Frontend:** Streamlit
    - **Backend:** FastAPI
    - **Vector DB:** Qdrant
    - **LLMs:** Qwen, ChatGPT, DeepSeek
    - **Memory:** Redis
    - **Monitoring:** Telegram Bot API
    
    ### Version
    - **T-Plexity:** v0.1.0
    - **Frontend:** Streamlit Edition
    
    ---
    
    Built with ❤️ by the T-Plexity team
    """
)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #9E9E9E; padding: 20px;'>
        <p>Go back to <a href="/" target="_self" style="color: #FFDD2D; text-decoration: none;">Main Chat</a></p>
    </div>
    """,
    unsafe_allow_html=True
)

