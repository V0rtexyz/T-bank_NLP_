"""
News Feed Page - Browse recent Telegram messages
"""

import streamlit as st
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ui import apply_custom_css, format_timestamp

st.set_page_config(
    page_title="News Feed | T-Plexity",
    page_icon="📰",
    layout="wide"
)

apply_custom_css()

st.markdown("# 📰 News Feed")
st.markdown("### Recent messages from Telegram channels")
st.markdown("---")

# Info message
st.info(
    """
    📌 **Note**: The News Feed feature requires additional backend endpoints. 
    This is a placeholder page that can be implemented when the backend API 
    provides a `/news` or `/documents/recent` endpoint.
    
    **Expected functionality:**
    - Display recent messages from monitored Telegram channels
    - Filter by channel name
    - Search within messages
    - Direct links to original Telegram posts
    """
)

# Mock data for demonstration
st.markdown("### 🎯 Placeholder Example")

with st.expander("Example News Items", expanded=True):
    # Example 1
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 16px; margin: 10px 0;">
            <div style="font-weight: 600; color: #1F1F1F; margin-bottom: 8px;">
                📢 T-Bank Investments
            </div>
            <div style="color: #555; font-size: 0.95em; line-height: 1.5; margin-bottom: 8px;">
                Рынок акций показывает положительную динамику. Индекс Мосбиржи вырос на 1.2% за день...
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9E9E9E; font-size: 0.85em;">Today, 14:30</span>
                <a href="#" style="color: #FFDD2D; text-decoration: none; font-size: 0.85em; font-weight: 600;">View in Telegram →</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Example 2
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 16px; margin: 10px 0;">
            <div style="font-weight: 600; color: #1F1F1F; margin-bottom: 8px;">
                📢 Сбер Инвестиции
            </div>
            <div style="color: #555; font-size: 0.95em; line-height: 1.5; margin-bottom: 8px;">
                Центробанк сохранил ключевую ставку на уровне 16%. Решение соответствует ожиданиям рынка...
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9E9E9E; font-size: 0.85em;">Today, 12:15</span>
                <a href="#" style="color: #FFDD2D; text-decoration: none; font-size: 0.85em; font-weight: 600;">View in Telegram →</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Example 3
    st.markdown(
        """
        <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; padding: 16px; margin: 10px 0;">
            <div style="font-weight: 600; color: #1F1F1F; margin-bottom: 8px;">
                📢 Альфа Инвестиции
            </div>
            <div style="color: #555; font-size: 0.95em; line-height: 1.5; margin-bottom: 8px;">
                Доллар продолжает укрепляться против рубля. Текущий курс: 95.2₽/$...
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #9E9E9E; font-size: 0.85em;">Yesterday, 18:45</span>
                <a href="#" style="color: #FFDD2D; text-decoration: none; font-size: 0.85em; font-weight: 600;">View in Telegram →</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Implementation guide
with st.expander("🔧 Implementation Guide"):
    st.markdown(
        """
        ### To implement this feature:
        
        1. **Backend API Endpoint**
           - Create `GET /api/news` or `GET /documents/recent` endpoint
           - Should return recent documents with metadata
           - Support pagination and filtering
        
        2. **API Response Format**
           ```json
           {
             "items": [
               {
                 "doc_id": "doc_123",
                 "channel_name": "T-Bank Investments",
                 "channel_username": "tb_invest_official",
                 "message_id": 12345,
                 "text": "Message text...",
                 "timestamp": "2024-01-01T12:00:00Z",
                 "url": "https://t.me/tb_invest_official/12345"
               }
             ],
             "total": 100,
             "page": 1,
             "page_size": 20
           }
           ```
        
        3. **Frontend Implementation**
           - Add API call in `utils/api.py`
           - Implement pagination
           - Add filtering by channel
           - Add search functionality
        
        4. **Example Code**
           ```python
           # In utils/api.py
           def fetch_news(page=1, page_size=20, channel=None):
               params = {"page": page, "page_size": page_size}
               if channel:
                   params["channel"] = channel
               response = client.get(f"{API_BASE_URL}/news", params=params)
               return response.json()
           
           # In this page
           news_data = fetch_news(page=1)
           for item in news_data["items"]:
               render_news_card(item)
           ```
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

