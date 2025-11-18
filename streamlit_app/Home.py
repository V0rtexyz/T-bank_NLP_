"""T-Plexity Streamlit Frontend - Home Page"""

import streamlit as st

st.set_page_config(
    page_title="T-Plexity - Investment Intelligence",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with T-Bank yellow accent
st.markdown("""
<style>
.main-title {
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    color: #1F1F1F;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-size: 1.3rem;
    text-align: center;
    color: #666;
    margin-bottom: 2rem;
}

.feature-card {
    background: white;
    border: 2px solid #FFDD2D;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.feature-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1F1F1F;
    margin-bottom: 0.5rem;
}

.feature-description {
    color: #666;
    line-height: 1.6;
}

.stat-box {
    background: linear-gradient(135deg, #FFDD2D 0%, #FFD700 100%);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(255, 221, 45, 0.3);
}

.stat-value {
    font-size: 2.5rem;
    font-weight: 900;
    color: #1F1F1F;
}

.stat-label {
    color: #1F1F1F;
    font-weight: 600;
    margin-top: 0.5rem;
}

.stButton>button {
    background-color: #FFDD2D;
    color: #1F1F1F;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    font-size: 1.1rem;
}

.stButton>button:hover {
    background-color: #FFD700;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">💡 T-Plexity</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Investment Intelligence from Telegram Channels</p>', unsafe_allow_html=True)

st.divider()

# Quick actions
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Start Chat", use_container_width=True, type="primary"):
        st.switch_page("pages/1_💬_Chat.py")

with col2:
    if st.button("🔍 Search Documents", use_container_width=True):
        st.switch_page("pages/2_🔍_Search.py")

with col3:
    if st.button("📊 Statistics", use_container_width=True):
        st.switch_page("pages/3_📊_Stats.py")

st.divider()

# Stats
st.markdown("### 📈 Platform Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-value">50+</div>
        <div class="stat-label">Telegram Channels</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-value">&lt;30s</div>
        <div class="stat-label">Average Latency</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-value">24/7</div>
        <div class="stat-label">Monitoring</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-value">100%</div>
        <div class="stat-label">Source Linked</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Features
st.markdown("### ✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Real-Time Aggregation</div>
        <div class="feature-description">
            Fresh investment news from Telegram channels indexed instantly.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Hybrid Search</div>
        <div class="feature-description">
            Combines keyword and semantic search for best results.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI-Powered Insights</div>
        <div class="feature-description">
            RAG-based generation with source transparency.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔗</div>
        <div class="feature-title">Source Transparency</div>
        <div class="feature-description">
            Every answer links to original Telegram messages.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# How it works
st.markdown("### 🔧 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 1️⃣ Monitor")
    st.write("Continuously track 50+ investment Telegram channels")

with col2:
    st.markdown("#### 2️⃣ Index")
    st.write("Instantly index content for semantic search")

with col3:
    st.markdown("#### 3️⃣ Analyze")
    st.write("Generate AI insights using RAG")

# Sidebar
with st.sidebar:
    st.markdown("## 📱 T-Plexity")
    st.markdown("**Investment Intelligence Platform**")
    
    st.divider()
    
    st.markdown("### Navigation")
    st.page_link("Home.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_💬_Chat.py", label="Chat", icon="💬")
    st.page_link("pages/2_🔍_Search.py", label="Search", icon="🔍")
    st.page_link("pages/3_📊_Stats.py", label="Statistics", icon="📊")
    
    st.divider()
    
    st.markdown("### About")
    st.info("""
    T-Plexity aggregates and analyzes investment news from Telegram channels using AI.
    """)
    
    st.divider()
    
    st.caption("Built with Streamlit & FastAPI")

