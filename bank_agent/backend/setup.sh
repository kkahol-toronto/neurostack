#!/bin/bash

echo "🚀 Setting up Banking Agent Backend..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python 3 and pip3 are available"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Make sure to activate your venv first."
    echo "   Run: source /path/to/your/venv/bin/activate"
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Ensure your root .env file has Azure OpenAI credentials"
echo "2. Run: python start.py"
echo "3. Test with: python test_api.py"
echo ""
echo "🔗 API Documentation will be available at: http://localhost:8000/docs"
