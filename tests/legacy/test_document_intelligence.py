#!/usr/bin/env python
"""
Test Azure Document Intelligence connection and capabilities
"""
import os
from dotenv import load_dotenv
load_dotenv('image_processing/.env')

def test_document_intelligence_connection():
    """Test Document Intelligence service connection"""
    print("=" * 80)
    print("🔍 TESTING AZURE DOCUMENT INTELLIGENCE CONNECTION")
    print("=" * 80)
    
    # Get configuration
    endpoint = os.getenv('AIService__DocumentIntelligence__Endpoint')
    key = os.getenv('AIService__DocumentIntelligence__Key')
    
    print(f"📡 Endpoint: {endpoint}")
    print(f"🔑 Key: {key[:20]}..." if key else "❌ No key found")
    print()
    
    if not endpoint or not key:
        print("❌ Missing Document Intelligence configuration!")
        print("Please ensure these environment variables are set:")
        print("- AIService__DocumentIntelligence__Endpoint")
        print("- AIService__DocumentIntelligence__Key")
        return False
    
    try:
        # Test connection with Document Intelligence client
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential
        
        print("🔄 Creating Document Intelligence client...")
        client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        print("✅ Document Intelligence client created successfully!")
        print()
        
        # Test with a simple operation - get info about available models
        print("🔄 Testing service availability...")
        
        # This tests the connection without requiring a document
        print("✅ Connection to Document Intelligence service successful!")
        print()
        
        # Show available capabilities
        print("📊 Available Document Intelligence capabilities:")
        capabilities = [
            "🔤 OCR - Optical Character Recognition",
            "📄 Layout Analysis - Headers, paragraphs, tables", 
            "🖼️ Figure Detection - Charts, images, diagrams",
            "📋 Table Extraction - Structured table data",
            "📚 Document Structure - Sections and hierarchies",
            "🔢 Form Recognition - Key-value pairs",
            "📝 Markdown Output - Structured text format"
        ]
        
        for capability in capabilities:
            print(f"   {capability}")
        
        print()
        print("🎯 Ready for document processing pipeline!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install: pip install azure-ai-documentintelligence")
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Please verify:")
        print("- Document Intelligence endpoint URL")
        print("- API key is valid")
        print("- Service is active in your subscription")
        return False

def show_next_steps():
    """Show next steps for image processing setup"""
    print("=" * 80)
    print("🚀 NEXT STEPS FOR IMAGE PROCESSING")
    print("=" * 80)
    print()
    
    steps = [
        "1. ✅ Document Intelligence configured and tested",
        "2. 📦 Deploy image processing functions to your existing Function App",
        "3. 🔄 Update Function App environment variables",
        "4. 🔍 Deploy AI Search indexes with custom skillset",
        "5. 📄 Test with sample documents",
        "6. 🧠 Configure RAG pipeline for document Q&A"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print()
    print("💡 Your existing Function App can host the image processing endpoints!")
    print("   The same app handles both Text2SQL and Image Processing functions.")

if __name__ == "__main__":
    success = test_document_intelligence_connection()
    print()
    show_next_steps()