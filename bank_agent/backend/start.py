#!/usr/bin/env python3
"""
Startup script for Banking Agent Backend
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from root directory
load_dotenv(dotenv_path="/Users/kanavkahol/work/neurostack/.env")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"🚀 Starting Banking Agent Backend...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📊 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
