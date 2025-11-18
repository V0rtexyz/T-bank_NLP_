"""T-Plexity Statistics - System monitoring"""

import streamlit as st
import asyncio
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client

st.set_page_config(page_title="T-Plexity Stats", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
.stat-card {
    background: linear-gradient(135deg, #FFDD2D 0%, #FFD700 100%);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 900;
    color: #1F1F1F;
}

.stat-label {
    color: #1F1F1F;
    font-weight: 600;
}

.health-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 700;
}

.health-ok {
    background: #4CAF50;
    color: white;
}

.health-error {
    background: #F44336;
    color: white;
}

.service-card {
    background: white;
    border: 2px solid #FFDD2D;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 System Statistics")
st.markdown("Monitor T-Plexity services and database")

# Sidebar
with st.sidebar:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    st.divider()
    st.info("Real-time system monitoring")

# Service Health
st.markdown("### 🏥 Service Health")

api = get_api_client()

col1, col2 = st.columns(2)

with col1:
    with st.spinner("Checking Retriever..."):
        try:
            retriever_ok = asyncio.run(api.health_check("retriever"))
            badge_class = "health-ok" if retriever_ok else "health-error"
            badge_text = "✅ Healthy" if retriever_ok else "❌ Down"
            
            st.markdown(f"""
            <div class="service-card">
                <strong>🔍 Retriever Service</strong><br>
                <code>{api.retriever_url}</code><br>
                <span class="health-badge {badge_class}">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    with st.spinner("Checking Generation..."):
        try:
            generation_ok = asyncio.run(api.health_check("generation"))
            badge_class = "health-ok" if generation_ok else "health-error"
            badge_text = "✅ Healthy" if generation_ok else "❌ Down"
            
            st.markdown(f"""
            <div class="service-card">
                <strong>🤖 Generation Service</strong><br>
                <code>{api.generation_url}</code><br>
                <span class="health-badge {badge_class}">{badge_text}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# Statistics
st.markdown("### 📚 Platform Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">50+</div>
        <div class="stat-label">Channels</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">24/7</div>
        <div class="stat-label">Monitoring</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{datetime.now().strftime("%H:%M")}</div>
        <div class="stat-label">Last Update</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# System Info
with st.expander("ℹ️ System Information"):
    st.markdown(f"""
    **Platform:** T-Plexity  
    **Version:** 1.0.0  
    **Frontend:** Streamlit {st.__version__}  
    **Backend:** FastAPI Microservices  
    
    **Services:**
    - Retriever: `{api.retriever_url}`
    - Generation: `{api.generation_url}`
    
    **Last Refresh:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    """)

# Footer
st.caption("T-Plexity Statistics & Monitoring")

