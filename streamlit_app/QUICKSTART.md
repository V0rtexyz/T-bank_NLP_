# 🚀 Quick Start Guide - Streamlit Frontend

Get T-Plexity Streamlit UI running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Backend API running (Generation service at port 8012)
- pip or Poetry installed

## Step 1: Navigate to Streamlit App

```bash
cd streamlit_app
```

## Step 2: Install Dependencies

### Option A: Using pip (Simple)

```bash
pip install -r requirements.txt
```

### Option B: Using virtual environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure API URL

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - defaults to localhost:8002)
# API_BASE_URL=http://localhost:8012
```

## Step 4: Run the App

### Option A: Using start script (Easy)

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

### Option B: Manual start

```bash
streamlit run app.py
```

## Step 5: Open in Browser

The app will automatically open at:
```
http://localhost:8501
```

If it doesn't open automatically, navigate to the URL in your browser.

## 🎉 That's it!

You should now see the T-Plexity interface. Try asking:
- "Какие новости по рынку акций?"
- "Что происходит с долларом?"
- "Обзор инвестиций от банков"

## 🔧 Troubleshooting

### Port already in use?

```bash
streamlit run app.py --server.port 8505
```

### API not connecting?

1. Check if backend is running:
   ```bash
   curl http://localhost:8012/health
   ```

2. If using Docker, backend URL should be:
   ```
   API_BASE_URL=http://generation:8012
   ```

3. If running locally, backend URL should be:
   ```
   API_BASE_URL=http://localhost:8012
   ```

### Import errors?

Make sure you're in the right directory and dependencies are installed:
```bash
cd streamlit_app
pip install -r requirements.txt
```

## 📚 Next Steps

- Explore the **Settings** page (⚙️ icon in sidebar)
- Try different LLM models (Qwen, ChatGPT, DeepSeek)
- Adjust temperature and top-k settings
- Check out the **News Feed** page (placeholder for future feature)

## 🐳 Docker Alternative

If you prefer Docker:

```bash
# Build image
docker build -t tplexity-streamlit .

# Run container
docker run -p 8501:8501 \
  -e API_BASE_URL=http://localhost:8012 \
  tplexity-streamlit
```

## 🚀 Full Stack with Docker Compose

To run the entire T-Plexity stack:

```bash
# From project root
docker-compose up -d

# Streamlit will be available at http://localhost:8501
```

## 📖 Full Documentation

For detailed documentation, see:
- [Streamlit App README](README.md)
- [Main Project README](../README.md)

---

Need help? Check the [Troubleshooting](#-troubleshooting) section or open an issue on GitHub.

