"""
T-Plexity Streamlit Frontend
Modern web interface for T-Plexity - intelligent investment Telegram news aggregation
"""

import streamlit as st
from datetime import datetime
import uuid

# Configure page
st.set_page_config(
    page_title="T-Plexity | Investment Intelligence",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "T-Plexity - AI-powered investment news aggregation from Telegram channels"
    }
)

# Import utilities
from utils.api import (
    search_query,
    clear_session,
    get_api_status
)
from utils.ui import (
    apply_custom_css,
    render_message,
    render_source_card,
    render_loading
)
from utils.session import (
    initialize_session_state,
    add_message,
    clear_chat_history
)

# Initialize session state
initialize_session_state()

# Apply custom CSS
apply_custom_css()

# Sidebar
with st.sidebar:
    st.markdown("# 💡 T-Plexity")
    st.markdown("### Investment Intelligence")
    st.markdown("---")
    
    # Quick questions
    st.markdown("### 🎯 Quick Questions")
    quick_questions = [
        "Какие новости по рынку акций?",
        "Что происходит с долларом?",
        "Обзор инвестиций от банков",
        "Последние новости от ЦБ РФ",
    ]
    
    for question in quick_questions:
        if st.button(question, key=f"quick_{question}", use_container_width=True):
            st.session_state.query_input = question
            st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("### ⚙️ Settings")
    
    # Model selection
    model_options = ["qwen", "chatgpt", "deepseek"]
    st.session_state.llm_provider = st.selectbox(
        "LLM Model",
        model_options,
        index=model_options.index(st.session_state.get("llm_provider", "qwen")),
        help="Select the language model to use for generation"
    )
    
    # Temperature
    st.session_state.temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.get("temperature", 0.7),
        step=0.1,
        help="Higher values make output more random, lower more focused"
    )
    
    # Top K
    st.session_state.top_k = st.slider(
        "Number of Sources",
        min_value=1,
        max_value=10,
        value=st.session_state.get("top_k", 5),
        help="Number of source documents to retrieve"
    )
    
    # Use rerank
    st.session_state.use_rerank = st.checkbox(
        "Use Reranking",
        value=st.session_state.get("use_rerank", True),
        help="Use reranking to improve source relevance"
    )
    
    st.markdown("---")
    
    # Clear history button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        clear_chat_history()
        st.success("Chat history cleared!")
        st.rerun()
    
    st.markdown("---")
    
    # API Status
    with st.expander("📊 API Status"):
        status = get_api_status()
        if status["healthy"]:
            st.success("✅ API is healthy")
        else:
            st.error("❌ API is unavailable")
        st.caption(f"Checked: {datetime.now().strftime('%H:%M:%S')}")

# Main content
st.markdown("# 💡 T-Plexity")
st.markdown("### AI-powered investment intelligence from Telegram channels")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        render_message(message)

# Input area
st.markdown("---")

# Create two columns for input and button
col1, col2 = st.columns([6, 1])

with col1:
    # Get query from session state if it was set by quick question
    default_query = st.session_state.get("query_input", "")
    query = st.text_input(
        "Ask about investments, markets, or financial news...",
        value=default_query,
        key="query_text_input",
        placeholder="Например: Какие акции сейчас перспективны?",
        label_visibility="collapsed"
    )
    # Clear the query_input after reading
    if "query_input" in st.session_state:
        del st.session_state.query_input

with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Handle search
if search_button or (query and query != ""):
    if query and query.strip():
        # Add user message
        user_message = {
            "id": str(uuid.uuid4()),
            "type": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        }
        add_message(user_message)
        
        # Show user message immediately
        with chat_container:
            render_message(user_message)
        
        # Show loading state
        with chat_container:
            loading_placeholder = st.empty()
            with loading_placeholder:
                render_loading()
        
        # Call API
        try:
            result = search_query(
                query=query,
                top_k=st.session_state.top_k,
                use_rerank=st.session_state.use_rerank,
                temperature=st.session_state.temperature,
                llm_provider=st.session_state.llm_provider,
                session_id=st.session_state.session_id
            )
            
            # Remove loading
            loading_placeholder.empty()
            
            # Add assistant message with sources
            assistant_message = {
                "id": str(uuid.uuid4()),
                "type": "assistant",
                "content": result["detailed_answer"],
                "timestamp": datetime.now().isoformat(),
                "sources": result.get("sources", []),
                "short_answer": result.get("short_answer", ""),
                "search_time": result.get("search_time"),
                "generation_time": result.get("generation_time"),
                "total_time": result.get("total_time")
            }
            add_message(assistant_message)
            
            # Rerun to show the new message
            st.rerun()
            
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ Error: {str(e)}")
            st.error("Please check if the backend API is running.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #9E9E9E; padding: 20px;'>
        <p>Built with ❤️ using Streamlit | Powered by T-Plexity</p>
        <p style='font-size: 0.8em;'>Investment intelligence from Telegram channels</p>
    </div>
    """,
    unsafe_allow_html=True
)

