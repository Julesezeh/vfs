#!/bin/bash

# VFS Booking Bot Setup Script
# This script helps you set up the bot quickly

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          VFS Appointment Booking Bot - Setup                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p config
echo "✅ Directories created"
echo ""

# Copy configuration files if they don't exist
echo "Setting up configuration files..."

if [ ! -f "config/config.yaml" ]; then
    if [ -f "config/config.yaml.example" ]; then
        cp config/config.yaml.example config/config.yaml
        echo "✅ config.yaml created from example"
        echo "⚠️  Please edit config/config.yaml with your settings"
    else
        echo "❌ config.yaml.example not found"
    fi
else
    echo "ℹ️  config.yaml already exists"
fi

if [ ! -f "config/credentials.yaml" ]; then
    if [ -f "config/credentials.yaml.example" ]; then
        cp config/credentials.yaml.example config/credentials.yaml
        echo "✅ credentials.yaml created from example"
        echo "⚠️  Please edit config/credentials.yaml with your details"
    else
        echo "❌ credentials.yaml.example not found"
    fi
else
    echo "ℹ️  credentials.yaml already exists"
fi
echo ""

# Make main.py executable
chmod +x main.py
echo "✅ main.py is now executable"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! ✅                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration files:"
echo "   - config/config.yaml         (Telegram, proxy, settings)"
echo "   - config/credentials.yaml    (VFS login, applicant info)"
echo ""
echo "2. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the bot:"
echo "   python main.py"
echo ""
echo "For detailed instructions, see:"
echo "   - QUICKSTART.md (quick setup guide)"
echo "   - README.md (full documentation)"
echo ""
echo "Good luck! 🍀"
