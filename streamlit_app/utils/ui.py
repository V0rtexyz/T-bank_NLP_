"""
UI rendering utilities for Streamlit app
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any


def apply_custom_css():
    """Apply T-Bank themed custom CSS"""
    st.markdown(
        """
        <style>
        /* T-Bank color scheme */
        :root {
            --tbank-yellow: #FFDD2D;
            --tbank-yellow-dark: #FFD700;
            --tbank-black: #1F1F1F;
            --tbank-black-light: #2A2A2A;
            --tbank-gray: #9E9E9E;
            --tbank-gray-light: #E0E0E0;
        }
        
        /* Main container styling */
        .main {
            background-color: #FAFAFA;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: var(--tbank-black);
            color: white;
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: white;
        }
        
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            color: var(--tbank-yellow) !important;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button[kind="primary"] {
            background-color: var(--tbank-yellow);
            color: var(--tbank-black);
            border: none;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: var(--tbank-yellow-dark);
            box-shadow: 0 4px 12px rgba(255, 221, 45, 0.3);
        }
        
        .stButton > button[kind="secondary"] {
            background-color: transparent;
            color: var(--tbank-yellow);
            border: 2px solid var(--tbank-yellow);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: var(--tbank-yellow);
            color: var(--tbank-black);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 8px;
            border: 2px solid #E0E0E0;
            padding: 12px;
            font-size: 16px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--tbank-yellow);
            box-shadow: 0 0 0 2px rgba(255, 221, 45, 0.2);
        }
        
        /* Message bubbles */
        .user-message {
            background-color: #F5F5F5;
            border-left: 4px solid var(--tbank-yellow);
            padding: 16px;
            border-radius: 8px;
            margin: 10px 0;
        }
        
        .assistant-message {
            background-color: white;
            border: 1px solid #E0E0E0;
            padding: 16px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .message-header {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .user-icon {
            color: var(--tbank-yellow);
            margin-right: 8px;
            font-size: 1.2em;
        }
        
        .assistant-icon {
            color: #4CAF50;
            margin-right: 8px;
            font-size: 1.2em;
        }
        
        .timestamp {
            color: var(--tbank-gray);
            font-size: 0.85em;
            margin-left: auto;
        }
        
        /* Source cards */
        .source-card {
            background-color: #FAFAFA;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            transition: all 0.2s ease;
        }
        
        .source-card:hover {
            border-color: var(--tbank-yellow);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .source-header {
            font-weight: 600;
            color: var(--tbank-black);
            margin-bottom: 4px;
        }
        
        .source-text {
            color: #555;
            font-size: 0.9em;
            line-height: 1.5;
        }
        
        .source-link {
            color: var(--tbank-yellow);
            text-decoration: none;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .source-link:hover {
            text-decoration: underline;
        }
        
        /* Metrics */
        .metric-container {
            display: flex;
            gap: 16px;
            margin: 12px 0;
            flex-wrap: wrap;
        }
        
        .metric-item {
            background-color: #F5F5F5;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.85em;
        }
        
        .metric-label {
            color: var(--tbank-gray);
            font-weight: 600;
        }
        
        .metric-value {
            color: var(--tbank-black);
            font-weight: 700;
        }
        
        /* Loading animation */
        .loading-container {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            background-color: white;
            border-radius: 8px;
            border: 1px solid #E0E0E0;
        }
        
        .loading-text {
            color: var(--tbank-gray);
            font-style: italic;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_message(message: Dict[str, Any]):
    """
    Render a chat message (user or assistant)
    
    Args:
        message: Message dict with type, content, timestamp, and optional sources
    """
    if message["type"] == "user":
        st.markdown(
            f"""
            <div class="user-message">
                <div class="message-header">
                    <span class="user-icon">👤</span>
                    <span>You</span>
                    <span class="timestamp">{format_timestamp(message["timestamp"])}</span>
                </div>
                <div>{message["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:  # assistant
        # Main answer
        st.markdown(
            f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span class="assistant-icon">🤖</span>
                    <span>T-Plexity AI</span>
                    <span class="timestamp">{format_timestamp(message["timestamp"])}</span>
                </div>
            """,
            unsafe_allow_html=True
        )
        
        # Show detailed answer
        st.markdown(message["content"])
        
        # Show timing metrics if available
        if any(key in message for key in ["search_time", "generation_time", "total_time"]):
            metrics_html = '<div class="metric-container">'
            if "search_time" in message and message["search_time"]:
                metrics_html += f'<div class="metric-item"><span class="metric-label">Search:</span> <span class="metric-value">{message["search_time"]:.2f}s</span></div>'
            if "generation_time" in message:
                metrics_html += f'<div class="metric-item"><span class="metric-label">Generation:</span> <span class="metric-value">{message["generation_time"]:.2f}s</span></div>'
            if "total_time" in message:
                metrics_html += f'<div class="metric-item"><span class="metric-label">Total:</span> <span class="metric-value">{message["total_time"]:.2f}s</span></div>'
            metrics_html += '</div>'
            st.markdown(metrics_html, unsafe_allow_html=True)
        
        # Show sources if available
        if "sources" in message and message["sources"]:
            st.markdown("**📚 Sources:**")
            for source in message["sources"]:
                render_source_card(source)
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_source_card(source: Dict[str, Any]):
    """
    Render a source card
    
    Args:
        source: Source dict with doc_id and metadata
    """
    metadata = source.get("metadata", {})
    
    # Extract information from metadata
    channel_name = metadata.get("channel_name", "Unknown Channel")
    channel_username = metadata.get("channel_username", "")
    message_id = metadata.get("message_id", "")
    text = metadata.get("text", "No preview available")
    timestamp = metadata.get("timestamp", "")
    
    # Build Telegram URL
    url = ""
    if channel_username and message_id:
        url = f"https://t.me/{channel_username}/{message_id}"
    
    # Truncate text for preview
    preview_text = text[:200] + "..." if len(text) > 200 else text
    
    # Format timestamp
    formatted_time = format_timestamp(timestamp) if timestamp else ""
    
    # Render source card
    st.markdown(
        f"""
        <div class="source-card">
            <div class="source-header">📢 {channel_name}</div>
            <div class="source-text">{preview_text}</div>
            <div style="margin-top: 8px; display: flex; justify-content: space-between; align-items: center;">
                {f'<span class="timestamp">{formatted_time}</span>' if formatted_time else ''}
                {f'<a href="{url}" target="_blank" class="source-link">View in Telegram →</a>' if url else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_loading():
    """Render loading animation"""
    st.markdown(
        """
        <div class="loading-container">
            <div class="loading-text">🔍 Searching for relevant information...</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div class="loading-container" style="margin-top: 8px;">
            <div class="loading-text">🤖 Generating answer...</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_timestamp(timestamp_str: str) -> str:
    """
    Format ISO timestamp to readable format
    
    Args:
        timestamp_str: ISO format timestamp string
    
    Returns:
        Formatted timestamp string
    """
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%H:%M:%S")
    except:
        return timestamp_str

