#!/bin/bash

# NeuroStack Setup Script
# This script helps automate the setup of NeuroStack development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if file exists
file_exists() {
    [ -f "$1" ]
}

# Function to check if directory exists
dir_exists() {
    [ -d "$1" ]
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status "Python version: $PYTHON_VERSION"
        
        # Check if version is 3.8 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible"
            return 0
        else
            print_error "Python 3.8+ is required"
            return 1
        fi
    else
        print_error "Python3 is not installed"
        return 1
    fi
}

# Function to setup virtual environment
setup_virtual_env() {
    print_status "Setting up virtual environment..."
    
    if ! dir_exists "venv"; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment is ready"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install NeuroStack in development mode
    pip install -e .
    
    # Install additional dependencies
    pip install python-dotenv
    
    print_success "Dependencies installed"
}

# Function to setup environment file
setup_env_file() {
    print_status "Setting up environment file..."
    
    if ! file_exists ".env"; then
        if file_exists "env.template"; then
            cp env.template .env
            print_success "Environment file created from template"
            print_warning "Please edit .env file with your actual values"
        else
            print_error "env.template not found"
            return 1
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Function to check Docker
check_docker() {
    print_status "Checking Docker installation..."
    
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version)
        print_success "Docker is installed: $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker info >/dev/null 2>&1; then
            print_success "Docker daemon is running"
            return 0
        else
            print_warning "Docker daemon is not running"
            print_status "Please start Docker and run this script again"
            return 1
        fi
    else
        print_warning "Docker is not installed"
        print_status "You can install Docker for easier local service management"
        return 1
    fi
}

# Function to setup local services with Docker
setup_local_services() {
    print_status "Setting up local services with Docker..."
    
    if ! check_docker; then
        print_warning "Skipping Docker services setup"
        return 1
    fi
    
    # Setup Redis
    if ! docker ps -a --format "table {{.Names}}" | grep -q "redis-neurostack"; then
        print_status "Starting Redis container..."
        docker run -d --name redis-neurostack -p 6379:6379 redis:7-alpine
        print_success "Redis container started"
    else
        if ! docker ps --format "table {{.Names}}" | grep -q "redis-neurostack"; then
            print_status "Starting existing Redis container..."
            docker start redis-neurostack
        fi
        print_success "Redis is running"
    fi
    
    # Setup PostgreSQL
    if ! docker ps -a --format "table {{.Names}}" | grep -q "postgres-neurostack"; then
        print_status "Starting PostgreSQL container..."
        docker run -d --name postgres-neurostack \
            -e POSTGRES_DB=neurostack \
            -e POSTGRES_USER=neurostack \
            -e POSTGRES_PASSWORD=neurostack123 \
            -p 5432:5432 \
            postgres:15
        print_success "PostgreSQL container started"
    else
        if ! docker ps --format "table {{.Names}}" | grep -q "postgres-neurostack"; then
            print_status "Starting existing PostgreSQL container..."
            docker start postgres-neurostack
        fi
        print_success "PostgreSQL is running"
    fi
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Test PostgreSQL connection
    if docker exec postgres-neurostack pg_isready -U neurostack >/dev/null 2>&1; then
        print_success "PostgreSQL is ready"
    else
        print_warning "PostgreSQL might not be ready yet"
    fi
}

# Function to check Azure CLI
check_azure_cli() {
    print_status "Checking Azure CLI installation..."
    
    if command_exists az; then
        AZURE_VERSION=$(az version --query '"azure-cli"' -o tsv)
        print_success "Azure CLI is installed: $AZURE_VERSION"
        
        # Check if logged in
        if az account show >/dev/null 2>&1; then
            ACCOUNT=$(az account show --query "user.name" -o tsv)
            SUBSCRIPTION=$(az account show --query "name" -o tsv)
            print_success "Logged in as: $ACCOUNT"
            print_success "Subscription: $SUBSCRIPTION"
            return 0
        else
            print_warning "Not logged in to Azure"
            print_status "Run 'az login' to authenticate"
            return 1
        fi
    else
        print_warning "Azure CLI is not installed"
        print_status "Install Azure CLI for Azure resource management"
        return 1
    fi
}

# Function to run setup verification
run_verification() {
    print_status "Running setup verification..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if setup check script exists
    if file_exists "debug/check_neurostack_setup.py"; then
        print_status "Running setup check..."
        python debug/check_neurostack_setup.py
    elif file_exists "../debug/check_neurostack_setup.py"; then
        print_status "Running setup check..."
        python ../debug/check_neurostack_setup.py
    else
        print_warning "Setup check script not found"
    fi
    
    # Test NeuroStack import
    print_status "Testing NeuroStack import..."
    if python -c "from neurostack import Agent, AgentConfig; print('✅ NeuroStack imports successfully')" 2>/dev/null; then
        print_success "NeuroStack import test passed"
    else
        print_error "NeuroStack import test failed"
        return 1
    fi
}

# Function to show next steps
show_next_steps() {
    echo
    print_success "Setup completed!"
    echo
    echo "Next steps:"
    echo "1. Edit your .env file with your Azure credentials"
    echo "2. Run: python debug/check_neurostack_setup.py"
    echo "3. Test with: python examples/simple_agent_example.py"
    echo "4. Read docs/SETUP_GUIDE.md for detailed instructions"
    echo
    echo "Local services (if using Docker):"
    echo "- Redis: localhost:6379"
    echo "- PostgreSQL: localhost:5432 (user: neurostack, password: neurostack123)"
    echo
    echo "Useful commands:"
    echo "- Start services: docker start redis-neurostack postgres-neurostack"
    echo "- Stop services: docker stop redis-neurostack postgres-neurostack"
    echo "- View logs: docker logs redis-neurostack"
    echo
}

# Main setup function
main() {
    echo "🚀 NeuroStack Setup Script"
    echo "=========================="
    echo
    
    # Check Python
    if ! check_python_version; then
        print_error "Python setup failed"
        exit 1
    fi
    
    # Setup virtual environment
    setup_virtual_env
    
    # Install dependencies
    install_dependencies
    
    # Setup environment file
    setup_env_file
    
    # Check Docker and setup local services
    setup_local_services
    
    # Check Azure CLI
    check_azure_cli
    
    # Run verification
    run_verification
    
    # Show next steps
    show_next_steps
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "NeuroStack Setup Script"
        echo
        echo "Usage: $0 [OPTION]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --no-docker    Skip Docker services setup"
        echo "  --verify-only  Only run verification"
        echo
        echo "This script will:"
        echo "1. Check Python version"
        echo "2. Setup virtual environment"
        echo "3. Install dependencies"
        echo "4. Create .env file from template"
        echo "5. Setup local services (Redis, PostgreSQL)"
        echo "6. Check Azure CLI"
        echo "7. Run verification tests"
        echo
        exit 0
        ;;
    --no-docker)
        print_warning "Skipping Docker services setup"
        # Override the setup_local_services function
        setup_local_services() {
            print_warning "Docker services setup skipped"
            return 0
        }
        main
        ;;
    --verify-only)
        print_status "Running verification only..."
        run_verification
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        print_status "Use --help for usage information"
        exit 1
        ;;
esac
