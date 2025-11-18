#!/bin/bash
# T-Plexity Streamlit Frontend - Run Script

echo "🚀 Starting T-Plexity Streamlit Frontend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if secrets file exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  Warning: .streamlit/secrets.toml not found"
    echo "📝 Copy .streamlit/secrets.toml.example and configure it"
    echo ""
fi

# Run Streamlit
echo "✅ Starting Streamlit app on http://localhost:8501"
echo ""
streamlit run Home.py

