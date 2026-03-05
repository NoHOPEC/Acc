#!/bin/bash

echo "========================================="
echo "  Telegram Account Manager Bot"
echo "========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your configuration"
    exit 1
fi

echo "✅ Configuration file found"
echo ""

echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

echo "🚀 Starting bot..."
echo "========================================="
echo ""

python3 bot.py
