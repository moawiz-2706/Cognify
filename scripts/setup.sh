#!/bin/bash

# Cognify Setup Script
echo "🚀 Setting up Cognify - Adaptive Learning Assistant"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file
echo "⚙️ Setting up environment configuration..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "📝 Created .env file. Please update it with your configuration."
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "from app.database import create_tables; create_tables()"

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend: python run.py (runs on port 3001)"
echo "2. Frontend: cd frontend && npm start (runs on port 7000)"
echo ""
echo "Don't forget to:"
echo "- Update .env with your API keys"
echo "- Set up PostgreSQL and Redis databases"
echo "- Configure your Google Gemini API key"
