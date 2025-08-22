#!/bin/bash

# Personal Site Installation Script
echo "🚀 Setting up Personal Site Project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements based on environment
if [ "$1" = "prod" ]; then
    echo "🏭 Installing production requirements..."
    pip install -r requirements-prod.txt
elif [ "$1" = "dev" ]; then
    echo "🛠️ Installing development requirements..."
    pip install -r requirements-dev.txt
else
    echo "📚 Installing base requirements..."
    pip install -r requirements.txt
fi

# Run Django migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if needed
echo "👤 Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo "✅ Installation complete!"
echo "🚀 To start the development server, run: make dev"
echo "🔧 To activate the virtual environment: source venv/bin/activate"
