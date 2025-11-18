"""T-Plexity Search - Semantic document search"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.api_client import get_api_client

st.set_page_config(page_title="T-Plexity Search", page_icon="🔍", layout="wide")

# Custom CSS
st.markdown("""
<style>
.search-result {
    background: white;
    border: 2px solid #FFDD2D;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.75rem 0;
}

.result-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.result-id {
    font-weight: 700;
    color: #1F1F1F;
}

.result-score {
    background: #FFDD2D;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-weight: 600;
    color: #1F1F1F;
}

.result-text {
    color: #333;
    line-height: 1.6;
    margin: 0.75rem 0;
}

.result-meta {
    color: #666;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = []

# Header
st.title("🔍 Document Search")
st.markdown("Search through investment news using hybrid semantic search")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Search Settings")
    
    top_k = st.slider("Number of results", 1, 50, 10)
    use_rerank = st.checkbox("Use reranking", value=False)
    
    if use_rerank:
        top_n = st.slider("After reranking", 1, top_k, min(5, top_k))
    else:
        top_n = top_k
    
    st.divider()
    
    st.markdown("### ⚖️ Hybrid Weights")
    sparse_weight = st.slider("Keyword weight", 0.0, 1.0, 0.5, 0.1)
    dense_weight = st.slider("Semantic weight", 0.0, 1.0, 0.5, 0.1)
    
    st.divider()
    
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.search_results = []
        st.rerun()

# Search interface
col1, col2 = st.columns([5, 1])

with col1:
    search_query = st.text_input(
        "Search",
        placeholder="e.g., 'tech stocks' or 'Fed policy'",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Example queries
if not st.session_state.search_results:
    st.markdown("### 💡 Examples:")
    examples = [
        "Technology stocks",
        "Federal Reserve rates",
        "Market volatility",
        "AI companies",
        "Crypto trends"
    ]
    
    cols = st.columns(5)
    for idx, ex in enumerate(examples):
        with cols[idx]:
            if st.button(ex, key=f"ex{idx}", use_container_width=True):
                search_query = ex
                search_button = True

# Perform search
if search_button and search_query:
    with st.spinner("🔍 Searching..."):
        try:
            api = get_api_client()
            result = asyncio.run(api.search_documents(
                query=search_query,
                top_k=top_k,
                top_n=top_n,
                use_rerank=use_rerank,
                sparse_weight=sparse_weight,
                dense_weight=dense_weight,
            ))
            
            st.session_state.search_results = result.get("results", [])
            
            if "error" in result:
                st.error(f"Error: {result['error']}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.search_results = []

# Display results
if st.session_state.search_results:
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Results", len(st.session_state.search_results))
    with col2:
        avg_score = sum(r.get("score", 0) for r in st.session_state.search_results) / len(st.session_state.search_results)
        st.metric("Avg Score", f"{avg_score:.3f}")
    with col3:
        st.metric("Query", search_query[:20] + "...")
    
    st.divider()
    
    for idx, result in enumerate(st.session_state.search_results, 1):
        doc_id = result.get("doc_id", "Unknown")
        score = result.get("score", 0.0)
        text = result.get("text", "")
        metadata = result.get("metadata", {})
        
        link = metadata.get("link", "#")
        channel = metadata.get("channel_id", "Unknown")
        date = metadata.get("date", "N/A")
        views = metadata.get("views", "N/A")
        
        st.markdown(f"""
        <div class="search-result">
            <div class="result-header">
                <div class="result-id">#{idx} · {doc_id}</div>
                <div class="result-score">Score: {score:.4f}</div>
            </div>
            <div class="result-text">{text}</div>
            <div class="result-meta">
                📢 {channel} | 📅 {date} | 👁️ {views} views
                <br><a href="{link}" target="_blank">🔗 View original</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif search_query and not st.session_state.search_results:
    st.info("No results found")

# Empty state
if not st.session_state.search_results and not search_query:
    st.info("👋 Enter a query to search through investment news from Telegram channels")

# Info
with st.expander("ℹ️ About Search"):
    st.markdown("""
    **Hybrid Search** combines:
    - **Keyword (BM25)**: Exact term matching
    - **Semantic (Vectors)**: Meaning understanding
    
    **Reranking** improves relevance but takes longer.
    """)

