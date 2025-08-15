# NeuroStack Debug Tools

This folder contains debugging, verification, and testing tools for the NeuroStack project.

## 🔍 **Available Tools**

- **[check_neurostack_setup.py](check_neurostack_setup.py)** - Automated setup verification script

## 🚀 **Usage**

### Setup Verification

```bash
# Run setup verification
python check_neurostack_setup.py

# Run with virtual environment
source ../venv/bin/activate && python check_neurostack_setup.py
```

## 📋 **Debug Tools Structure**

```
debug/
├── README.md                    # This file - Debug tools index
└── check_neurostack_setup.py   # Setup verification script
```

## 🔗 **Related Files**

- **Documentation**: `../docs/` - Setup guides and references
- **Scripts**: `../scripts/` - Automation scripts
- **Examples**: `../examples/` - Usage examples

## 📖 **Tool Details**

### check_neurostack_setup.py

**Purpose**: Verify NeuroStack development environment setup

**Features**:
- ✅ Azure OpenAI configuration check
- ✅ Azure Cognitive Services verification
- ✅ Azure Functions connection test
- ✅ Azure Storage configuration check
- ✅ Azure Service Bus verification
- ✅ Local services (Redis, PostgreSQL) check
- ✅ Basic settings validation
- ✅ RAG configuration verification

**Output**:
- Detailed status report for each service
- Connection type detection (Direct vs APIM)
- Readiness assessment
- Next steps guidance

**Example Output**:
```
🎉 READY FOR NEUROSTACK DEVELOPMENT!
   ✅ Azure OpenAI configured
   ✅ Basic settings configured
   🚀 Optional services: Cognitive Services, Azure Functions, Azure Storage, Service Bus, Redis, Database
```

## 🔧 **Troubleshooting**

If verification fails:
1. Check your `.env` file configuration
2. Verify Azure service endpoints and keys
3. Ensure local services are running (if using Docker)
4. Check network connectivity to Azure services

---

**Need Help?** Check the troubleshooting section in `../docs/SETUP_GUIDE.md`
