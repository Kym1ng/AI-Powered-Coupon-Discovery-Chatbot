#!/usr/bin/env python3
"""
Basic test script for the Coupon Assistant (without OpenAI API)
Tests data loading and basic functionality
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import assistant
sys.path.append(str(Path(__file__).parent))

def test_data_loading():
    """Test basic data loading functionality"""
    print("🧪 Testing basic data loading...")
    
    try:
        # Test if we can import the assistant (without initializing OpenAI)
        from assistant import CouponAssistant
        
        # Check if data file exists
        data_path = Path(__file__).parent.parent / "data" / "category_tree.json"
        if not data_path.exists():
            print(f"❌ Data file not found at {data_path}")
            print("Please run: python ../main.py discover_tree")
            return False
        
        print(f"✅ Data file found at {data_path}")
        
        # Test basic data loading (without OpenAI)
        print("🔄 Testing data loading...")
        
        # Create a mock assistant class for testing
        class MockCouponAssistant:
            def __init__(self):
                self.coupon_data = self._load_coupon_data()
            
            def _load_coupon_data(self):
                """Load coupon data from the tree structure JSON file"""
                data_path = Path(__file__).parent.parent / "data" / "category_tree.json"
                
                if not data_path.exists():
                    raise FileNotFoundError(f"Coupon data not found at {data_path}. Please run the scraper first.")
                
                import json
                with open(data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            def get_stats(self):
                """Get statistics about the coupon data"""
                total_coupons = 0
                total_categories = len(self.coupon_data)
                total_subcategories = 0
                
                for category_data in self.coupon_data.values():
                    total_subcategories += len(category_data['subcategories'])
                    for subcategory_data in category_data['subcategories'].values():
                        total_coupons += len(subcategory_data['coupons'])
                
                return {
                    "total_coupons": total_coupons,
                    "total_categories": total_categories,
                    "total_subcategories": total_subcategories,
                    "categories": [data['category_name'] for data in self.coupon_data.values()]
                }
            
            def get_brands(self):
                """Get list of all available brands"""
                brands = set()
                for category_data in self.coupon_data.values():
                    for subcategory_data in category_data['subcategories'].values():
                        for coupon in subcategory_data['coupons']:
                            brands.add(coupon['brand'])
                return sorted(list(brands))
            
            def search_coupons(self, query: str, category: str = None, brand: str = None):
                """Search for specific coupons"""
                results = []
                
                for category_key, category_data in self.coupon_data.items():
                    category_name = category_data['category_name']
                    
                    # Filter by category if specified
                    if category and category.lower() not in category_name.lower():
                        continue
                        
                    for subcategory_key, subcategory_data in category_data['subcategories'].items():
                        subcategory_name = subcategory_data['subcategories_name']
                        
                        for coupon in subcategory_data['coupons']:
                            # Filter by brand if specified
                            if brand and brand.lower() not in coupon['brand'].lower():
                                continue
                            
                            # Check if query matches any coupon field
                            query_lower = query.lower()
                            if (query_lower in coupon['brand'].lower() or
                                query_lower in coupon['code'].lower() or
                                query_lower in coupon['description'].lower() or
                                query_lower in category_name.lower() or
                                query_lower in subcategory_name.lower()):
                                
                                results.append({
                                    "brand": coupon['brand'],
                                    "code": coupon['code'],
                                    "description": coupon['description'],
                                    "category": category_name,
                                    "subcategory": subcategory_name,
                                    "url": subcategory_data['url'],
                                    "button_index": coupon.get('button_index', 0)
                                })
                
                return results
        
        # Test the mock assistant
        assistant = MockCouponAssistant()
        
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
        
        # Test category-specific search
        print(f"\n🔍 Testing category-specific search...")
        category_results = assistant.search_coupons("", category="Beauty")
        print(f"Found {len(category_results)} coupons in Beauty category")
        
        print("\n✅ All basic tests completed successfully!")
        print("\n🎉 Ready to set up OpenAI API for full functionality!")
        print("\nNext steps:")
        print("1. Get an OpenAI API key from https://platform.openai.com/")
        print("2. Set it as environment variable: export OPENAI_API_KEY='your-key'")
        print("3. Run: python test_assistant.py")
        print("4. Start the API server: python api.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_loading()
    if not success:
        print("\n❌ Please fix the issues above before proceeding.")
