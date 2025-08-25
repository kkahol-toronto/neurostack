# NeuroStack Scripts

This folder contains automation and setup scripts for the NeuroStack project.

## 🔧 **Available Scripts**

- **[setup_neurostack.sh](setup_neurostack.sh)** - Automated setup script for development environment

## 🚀 **Usage**

### Setup Script

```bash
# Make script executable (if needed)
chmod +x setup_neurostack.sh

# Run the setup script
./setup_neurostack.sh

# Run with options
./setup_neurostack.sh --help          # Show help
./setup_neurostack.sh --no-docker     # Skip Docker services
./setup_neurostack.sh --verify-only   # Only run verification
```

## 📋 **Scripts Structure**

```
scripts/
├── README.md                    # This file - Scripts index
└── setup_neurostack.sh         # Automated setup script
```

## 🔗 **Related Files**

- **Documentation**: `../docs/` - Setup guides and references
- **Debug Tools**: `../debug/` - Setup verification and debugging tools
- **Examples**: `../examples/` - Usage examples

## 📖 **Script Details**

### setup_neurostack.sh

**Purpose**: Automated setup of NeuroStack development environment

**Features**:
- ✅ Python version check
- ✅ Virtual environment setup
- ✅ Dependency installation
- ✅ Environment file creation
- ✅ Docker services setup (Redis, PostgreSQL)
- ✅ Azure CLI verification
- ✅ Setup verification

**Requirements**:
- Python 3.8+
- Git
- Docker (optional, for local services)
- Azure CLI (optional, for Azure resource management)

---

**Need Help?** Check the documentation in `../docs/` or run `./setup_neurostack.sh --help`
