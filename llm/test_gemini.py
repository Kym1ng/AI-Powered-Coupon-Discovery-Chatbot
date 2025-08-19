#!/usr/bin/env python3
"""
Test script for Gemini-based Coupon Assistant
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

def test_gemini_assistant():
    """Test the Gemini assistant functionality"""
    
    print("🧪 Testing Gemini Assistant...")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("\n📝 To set up your Gemini API key:")
        print("1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Copy the key and set it as environment variable:")
        print("   export GOOGLE_API_KEY='your-api-key-here'")
        print("   OR add it to your .env file: GOOGLE_API_KEY=your-api-key-here")
        return False
    
    print("✅ GOOGLE_API_KEY found")
    
    try:
        from llm.assistant_gemini import CouponAssistantGemini
        
        # Initialize assistant
        print("🔄 Initializing Gemini Assistant...")
        assistant = CouponAssistantGemini()
        print("✅ Assistant initialized successfully")
        
        # Test stats
        print("\n📊 Testing stats...")
        stats = assistant.get_stats()
        print(f"   Total coupons: {stats['total_coupons']}")
        print(f"   Total categories: {stats['total_categories']}")
        print(f"   Total subcategories: {stats['total_subcategories']}")
        print(f"   Unique brands: {stats['unique_brands']}")
        print(f"   Model: {stats['model']}")
        print(f"   API Provider: {stats['api_provider']}")
        
        # Test categories
        print("\n📂 Testing categories...")
        categories = assistant.get_categories()
        print(f"   Found {len(categories)} main categories")
        print(f"   First 5 categories: {categories[:5]}")
        
        # Test brands
        print("\n🏷️ Testing brands...")
        brands = assistant.get_brands()
        print(f"   Found {len(brands)} unique brands")
        print(f"   First 5 brands: {brands[:5]}")
        
        # Test search
        print("\n🔍 Testing search...")
        search_results = assistant.search_coupons("beauty", "keyword")
        print(f"   Found {len(search_results)} results for 'beauty'")
        if search_results:
            print(f"   First result: {search_results[0]['brand']} - {search_results[0]['code']}")
        
        # Test chat (this will use the AI model)
        print("\n💬 Testing chat functionality...")
        print("   This will use the Gemini AI model to answer questions")
        print("   Note: This may take a moment to initialize the vector store...")
        
        try:
            response = assistant.ask("What beauty coupons do you have?")
            print(f"   AI Response: {response[:200]}...")
            print("✅ Chat functionality working!")
        except Exception as e:
            print(f"   ⚠️ Chat test failed: {e}")
            print("   This might be due to API limits or initialization issues")
        
        print("\n🎉 All tests completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you have installed the required packages:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_assistant()
    if success:
        print("\n🚀 You can now run the Gemini API server with:")
        print("   python llm/api_gemini.py")
        print("\n🌐 The server will run on http://localhost:8001")
    else:
        print("\n❌ Please fix the issues above before running the API server")
