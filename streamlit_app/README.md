# T-Plexity Streamlit Frontend

Modern web interface for T-Plexity — an intelligent system that aggregates and analyzes investment Telegram news in real-time.

## 🎨 Overview

T-Plexity Streamlit frontend provides an intuitive interface for:
- 💬 **AI Chat**: RAG-powered Q&A about markets and investments
- 🔍 **Document Search**: Hybrid semantic search through Telegram messages
- 📊 **Statistics**: System monitoring and health checks

## ✨ Features

- **Chat Interface**: Conversational AI with source transparency
- **Hybrid Search**: Combines keyword (BM25) and semantic (vector) search
- **Real-time Stats**: Service health monitoring
- **T-Bank Theme**: Yellow-black color scheme with modern design
- **Responsive**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Backend services running (Retriever, Generation)

### Installation

```bash
# Navigate to streamlit_app directory
cd streamlit_app

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets (copy and edit)
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit .streamlit/secrets.toml with your backend URLs
```

### Configuration

Edit `.streamlit/secrets.toml`:

```toml
RETRIEVER_URL = "http://localhost:8001"
GENERATION_URL = "http://localhost:8002"
```

### Run

```bash
streamlit run Home.py
```

The app will be available at `http://localhost:8501`

## 📁 Project Structure

```
streamlit_app/
├── Home.py                      # Main landing page
├── pages/
│   ├── 1_💬_Chat.py            # Chat interface
│   ├── 2_🔍_Search.py          # Document search
│   └── 3_📊_Stats.py           # Statistics & monitoring
├── utils/
│   ├── __init__.py
│   └── api_client.py           # Backend API client
├── .streamlit/
│   ├── config.toml             # Streamlit configuration
│   └── secrets.toml.example    # Secrets template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔌 API Integration

The frontend communicates with two backend microservices:

### Retriever Service (Port 8001)
- `POST /retriever/search` - Document search
- `GET /health` - Health check

### Generation Service (Port 8002)
- `POST /generation/generate` - RAG-based answer generation
- `POST /generation/clear-session` - Clear chat history
- `GET /health` - Health check

## 🎨 Customization

### Theme

Edit `.streamlit/config.toml` to customize colors:

```toml
[theme]
primaryColor = "#FFDD2D"         # T-Bank Yellow
backgroundColor = "#FAFAFA"       # Light gray
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1F1F1F"            # Dark text
```

### API URLs

Update in `.streamlit/secrets.toml` or via environment variables:

```bash
export RETRIEVER_URL="http://your-retriever:8001"
export GENERATION_URL="http://your-generation:8002"
```

## 💬 Chat Interface

**Features:**
- Session-based conversations
- Source transparency (links to Telegram messages)
- Adjustable parameters (temperature, top_k, reranking)
- Quick question templates
- Chat history management

**Parameters:**
- **Top K**: Number of documents for context (1-10)
- **Temperature**: Response creativity (0.0-1.0)
- **Reranking**: Improve relevance (slower)
- **Max Tokens**: Response length (100-2000)

## 🔍 Search Interface

**Features:**
- Hybrid search (keyword + semantic)
- Adjustable weights for BM25 and vector search
- Optional reranking
- Direct links to source messages
- Search results with metadata

**Parameters:**
- **Top K**: Number of results (1-50)
- **Sparse Weight**: Keyword search importance (0.0-1.0)
- **Dense Weight**: Semantic search importance (0.0-1.0)
- **Reranking**: Optional result refinement

## 📊 Statistics

**Displays:**
- Service health status (Retriever, Generation)
- Platform overview metrics
- System information
- Service URLs and connectivity

## 🐛 Troubleshooting

### Connection Errors

If you see connection errors:

1. **Check backend services are running:**
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   ```

2. **Verify URLs in secrets.toml:**
   ```bash
   cat .streamlit/secrets.toml
   ```

3. **Check firewall/ports:**
   Ensure ports 8001, 8002, and 8501 are open

### Module Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Streamlit Won't Start

```bash
# Clear cache
streamlit cache clear

# Try different port
streamlit run Home.py --server.port 8502
```

## 🔧 Development

### Local Development

```bash
# Run with auto-reload
streamlit run Home.py --server.runOnSave true

# Run with debugging
streamlit run Home.py --logger.level debug
```

### Adding New Pages

1. Create file in `pages/` with format: `N_emoji_Name.py`
2. Pages are auto-discovered and sorted by number
3. Use `st.set_page_config()` at the top of each page

Example:
```python
# pages/4_⚙️_Settings.py
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️")
st.title("⚙️ Settings")
```

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t tplexity-frontend .
docker run -p 8501:8501 tplexity-frontend
```

### Streamlit Cloud

1. Push to GitHub
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repository
4. Add secrets in dashboard

## 🔐 Security

- Never commit `.streamlit/secrets.toml`
- Use environment variables for production
- Enable authentication if deploying publicly
- Set `enableCORS = false` in production

## 📚 Documentation

- [Streamlit Docs](https://docs.streamlit.io)
- [T-Plexity Architecture](../ARCHITECTURE.md)
- [Backend API Docs](../src/tplexity/README.md)

## 🤝 Contributing

1. Follow existing code style
2. Test all pages before committing
3. Update README for new features
4. Use meaningful commit messages

## 📄 License

Part of the T-Plexity project. See main repository for license.

## 🆘 Support

For issues:
- Check this README
- Review Streamlit documentation
- Open issue in main repository

---

Built with ❤️ using Streamlit and FastAPI
