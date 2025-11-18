"""
Session state management utilities
"""

import streamlit as st
import uuid
from typing import Dict, Any


def initialize_session_state():
    """Initialize Streamlit session state with default values"""
    
    # Session ID for conversation history
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Settings
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "qwen"
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    
    if "top_k" not in st.session_state:
        st.session_state.top_k = 5
    
    if "use_rerank" not in st.session_state:
        st.session_state.use_rerank = True
    
    # Query input for quick questions
    if "query_input" not in st.session_state:
        st.session_state.query_input = ""


def add_message(message: Dict[str, Any]):
    """
    Add a message to the chat history
    
    Args:
        message: Message dict with id, type, content, timestamp, and optional sources
    """
    st.session_state.messages.append(message)


def clear_chat_history():
    """Clear all chat messages"""
    st.session_state.messages = []
    # Generate new session ID
    st.session_state.session_id = str(uuid.uuid4())


def get_message_count() -> int:
    """Get the number of messages in chat history"""
    return len(st.session_state.messages)


def get_last_message() -> Dict[str, Any]:
    """Get the last message from chat history"""
    if st.session_state.messages:
        return st.session_state.messages[-1]
    return None

