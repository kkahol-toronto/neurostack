#!/bin/bash

# Bank Agent Data System Setup Script

echo "🏦 Bank Agent Data System Setup"
echo "================================"

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed. Please install MySQL first."
    echo "   macOS: brew install mysql"
    echo "   Ubuntu: sudo apt-get install mysql-server"
    echo "   CentOS: sudo yum install mysql-server"
    exit 1
fi

echo "✅ MySQL found: $(mysql --version)"

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if MySQL service is running
echo "🔍 Checking MySQL service..."
if ! mysql -u root -p -e "SELECT 1;" &> /dev/null; then
    echo "⚠️  MySQL service may not be running or credentials are needed."
    echo "   Please ensure MySQL is running and you have the correct credentials."
    echo "   You can start MySQL with: sudo systemctl start mysql"
fi

# Create database schema
echo "🗄️  Creating database schema..."
read -p "Enter MySQL root password: " mysql_password

if mysql -u root -p"$mysql_password" < data/schema.sql; then
    echo "✅ Database schema created successfully"
else
    echo "❌ Failed to create database schema"
    echo "   Please check your MySQL credentials and try again"
    exit 1
fi

# Generate sample data
echo "📊 Generating sample data..."
cd data
python generate_data.py

echo ""
echo "🎉 Bank Agent Data System Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Review the generated data: mysql -u root -p bank_agent_db"
echo "   2. Run sample queries from the README"
echo "   3. Integrate with NeuroStack agents"
echo ""
echo "📚 Documentation: README.md"
echo "🔧 Customization: Edit data/generate_data.py"
