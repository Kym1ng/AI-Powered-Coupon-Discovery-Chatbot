#!/usr/bin/env python3
"""
Test script for the OpenAI Coupon Assistant
Run this to verify everything is working correctly
"""

import os
from dotenv import load_dotenv
from assistant_openai import CouponAssistant

# Load environment variables
load_dotenv()

def test_assistant():
    """Test the coupon assistant functionality"""
    print("🧪 Testing OpenAI Coupon Assistant...")
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Initialize assistant
        print("🔄 Initializing OpenAI Coupon Assistant...")
        assistant = CouponAssistant()
        print("✅ OpenAI Assistant initialized successfully!")
        
        # Get stats
        print("\n📊 Getting statistics...")
        stats = assistant.get_stats()
        print(f"Total coupons: {stats['total_coupons']}")
        print(f"Total categories: {stats['total_categories']}")
        print(f"Total subcategories: {stats['total_subcategories']}")
        
        # Get categories
        print(f"\n📁 Available categories: {len(stats['categories'])}")
        for i, category in enumerate(stats['categories'][:5]):
            print(f"  {i+1}. {category}")
        if len(stats['categories']) > 5:
            print(f"  ... and {len(stats['categories']) - 5} more")
        
        # Get brands
        print(f"\n🏷️  Available brands: {len(assistant.get_brands())}")
        brands = assistant.get_brands()[:5]
        for i, brand in enumerate(brands):
            print(f"  {i+1}. {brand}")
        if len(assistant.get_brands()) > 5:
            print(f"  ... and {len(assistant.get_brands()) - 5} more")
        
        # Test search functionality
        print(f"\n🔍 Testing search functionality...")
        search_results = assistant.search_coupons("beauty")
        print(f"Found {len(search_results)} beauty-related coupons")
        
        if search_results:
            print("Sample results:")
            for i, coupon in enumerate(search_results[:3]):
                print(f"  {i+1}. {coupon['brand']} - {coupon['code']} ({coupon['description']})")
        
        # Test chat functionality (only if you want to use OpenAI credits)
        print(f"\n💬 Testing chat functionality...")
        print("Note: This will use OpenAI API credits")
        
        response = input("Do you want to test the chat functionality? (y/n): ")
        if response.lower() == 'y':
            print("🔄 Setting up QA chain (this may take a moment)...")
            assistant.setup_qa_chain()
            
            test_questions = [
                "What beauty coupons do you have?",
                "Show me AI tool coupons",
                "What's the best discount for Taplio?"
            ]
            
            for question in test_questions:
                print(f"\n❓ Question: {question}")
                try:
                    result = assistant.ask(question)
                    print(f"🤖 Answer: {result['answer']}")
                    print(f"📄 Sources: {len(result['source_documents'])} documents")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_assistant()
    if success:
        print("\n🎉 Ready to start the OpenAI API server!")
        print("Run: python llm/api_openai.py")
    else:
        print("\n❌ Please fix the issues above before proceeding.")
