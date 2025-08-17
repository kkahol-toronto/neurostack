"""
Test script for Azure APIM setup with NeuroStack.

This script tests both text generation and image analysis using the same APIM endpoint.
"""

import asyncio
import os
import structlog
from neurostack import AzureIntegration

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

async def test_apim_setup():
    """Test the APIM setup with both text and image analysis."""
    
    # Load configuration from environment variables
    azure_config = {
        "openai": {
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "key": os.getenv("AZURE_OPENAI_KEY"),
            "deployment_name": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        }
    }
    
    print("🚀 Testing Azure APIM Setup")
    print(f"Endpoint: {azure_config['openai']['endpoint']}")
    print(f"Deployment: {azure_config['openai']['deployment_name']}")
    print(f"Key configured: {'Yes' if azure_config['openai']['key'] else 'No'}")
    
    if not azure_config['openai']['endpoint'] or not azure_config['openai']['key']:
        print("❌ Missing required environment variables!")
        print("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY")
        return
    
    # Initialize Azure integration
    print("\n🔧 Initializing Azure integration...")
    azure_integration = AzureIntegration(azure_config)
    
    # Initialize services
    success = await azure_integration.initialize()
    if not success:
        print("❌ Failed to initialize Azure integration")
        return
    
    print("✅ Azure integration initialized successfully")
    
    # Test 1: Text Generation
    print("\n📝 Testing Text Generation...")
    if azure_integration.openai:
        try:
            text_result = await azure_integration.openai.generate_text(
                "Hello! Please respond with a short greeting and confirm you're working through APIM."
            )
            print(f"✅ Text Generation Result: {text_result}")
        except Exception as e:
            print(f"❌ Text Generation Failed: {e}")
    else:
        print("❌ Azure OpenAI not available")
    
    # Test 2: Image Analysis
    print("\n🖼️  Testing Image Analysis...")
    if azure_integration.cognitive_services:
        try:
            # Test with a sample image URL
            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Check_green_icon.svg/1200px-Check_green_icon.svg.png"
            image_result = await azure_integration.cognitive_services.analyze_image(
                image_url,
                "What do you see in this image? Please describe it briefly."
            )
            print(f"✅ Image Analysis Result: {image_result}")
        except Exception as e:
            print(f"❌ Image Analysis Failed: {e}")
    else:
        print("❌ Azure Cognitive Services not available")
    
    # Test 3: Health Check
    print("\n🏥 Testing Health Check...")
    health = await azure_integration.health_check()
    print(f"Overall Status: {health.get('overall_status', 'unknown')}")
    
    if 'services' in health:
        for service in health['services']:
            if isinstance(service, dict):
                service_name = service.get('service', 'unknown')
                status = service.get('status', 'unknown')
                print(f"  {service_name}: {status}")
    
    print("\n🎉 APIM Setup Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_apim_setup()) 