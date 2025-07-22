"""
Test script for GCP setup with NeuroStack.

This script tests Vertex AI, Cloud Functions, and other GCP services.
"""

import asyncio
import os
import structlog
from neurostack import GCPIntegration

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

async def test_gcp_setup():
    """Test the GCP setup with Vertex AI and other services."""
    
    # Load configuration from environment variables
    gcp_config = {
        "project_id": os.getenv("GCP_PROJECT_ID"),
        "vertex_ai": {
            "location": os.getenv("VERTEX_AI_LOCATION", "us-central1")
        },
        "functions": {
            "region": os.getenv("CLOUD_FUNCTIONS_REGION", "us-central1")
        },
        "cloud_run": {
            "region": os.getenv("CLOUD_RUN_REGION", "us-central1")
        }
    }
    
    print("🚀 Testing GCP Setup")
    print(f"Project ID: {gcp_config['project_id']}")
    print(f"Vertex AI Location: {gcp_config['vertex_ai']['location']}")
    print(f"Cloud Functions Region: {gcp_config['functions']['region']}")
    print(f"Cloud Run Region: {gcp_config['cloud_run']['region']}")
    
    # Check for service account credentials
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        print(f"Service Account: {credentials_path}")
        if os.path.exists(credentials_path):
            print("✅ Service account file exists")
        else:
            print("❌ Service account file not found")
    else:
        print("⚠️  No service account path set (using default credentials)")
    
    if not gcp_config['project_id']:
        print("❌ Missing required environment variable: GCP_PROJECT_ID")
        print("Please set GCP_PROJECT_ID")
        return
    
    # Initialize GCP integration
    print("\n🔧 Initializing GCP integration...")
    gcp_integration = GCPIntegration(gcp_config)
    
    # Initialize services
    success = await gcp_integration.initialize()
    if not success:
        print("❌ Failed to initialize GCP integration")
        return
    
    print("✅ GCP integration initialized successfully")
    
    # Test 1: Vertex AI Text Generation
    print("\n📝 Testing Vertex AI Text Generation...")
    if gcp_integration.vertex_ai:
        try:
            model_name = os.getenv("VERTEX_AI_MODEL_NAME", "text-bison")
            text_result = await gcp_integration.vertex_ai.predict_text(
                model_name,
                "Hello! Please respond with a short greeting and confirm you're working through Vertex AI."
            )
            print(f"✅ Vertex AI Text Generation Result: {text_result}")
        except Exception as e:
            print(f"❌ Vertex AI Text Generation Failed: {e}")
    else:
        print("❌ Vertex AI not available")
    
    # Test 2: Cloud Functions
    print("\n⚡ Testing Cloud Functions...")
    if gcp_integration.functions:
        try:
            # This would require an actual deployed function
            function_result = await gcp_integration.functions.invoke_function(
                "test-function",
                {"message": "Hello from NeuroStack"}
            )
            print(f"✅ Cloud Functions Result: {function_result}")
        except Exception as e:
            print(f"❌ Cloud Functions Failed: {e}")
    else:
        print("❌ Cloud Functions not available")
    
    # Test 3: Cloud Run
    print("\n🏃 Testing Cloud Run...")
    if gcp_integration.cloud_run:
        try:
            # This would require an actual deployed service
            service_result = await gcp_integration.cloud_run.deploy_service(
                "test-service",
                "gcr.io/your-project/test-image:latest"
            )
            print(f"✅ Cloud Run Result: {service_result}")
        except Exception as e:
            print(f"❌ Cloud Run Failed: {e}")
    else:
        print("❌ Cloud Run not available")
    
    # Test 4: Health Check
    print("\n🏥 Testing Health Check...")
    health = await gcp_integration.health_check()
    print(f"Overall Status: {health.get('overall_status', 'unknown')}")
    
    if 'services' in health:
        for service in health['services']:
            if isinstance(service, dict):
                service_name = service.get('service', 'unknown')
                status = service.get('status', 'unknown')
                print(f"  {service_name}: {status}")
    
    print("\n🎉 GCP Setup Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_gcp_setup()) 