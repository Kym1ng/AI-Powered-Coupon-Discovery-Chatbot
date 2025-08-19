import json
import sys
from pathlib import Path
from scrapers import run_scraper, discover_categories
from validators import validate_first_coupon

def save_coupons_to_json(coupons, filename="data/extracted_coupons.json"):
    """Save extracted coupons to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(coupons, f, ensure_ascii=False, indent=2)
    print(f"💾 Coupons saved to {filename}")

def save_categories_to_json(categories, filename="data/discovered_categories.json"):
    """Save discovered categories to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"💾 Categories saved to {filename}")

def scrape_single_main():
    """Scrape a single category (default: beauty/makeup)"""
    url = "https://simplycodes.com/category/beauty/makeup"    
    print("=== Single Category Scraper ===\n")
    print(f"🔗 Scraping: {url}")
    
    result = run_scraper(url, headless=True, use_retry=True)
    if result:
        print(f"\n📋 Results:")
        print(f"Successfully extracted {len(result)} coupons")
        save_coupons_to_json(result)
    else:
        print("❌ No coupons found or scraping failed")

def discover_tree_main():
    """Discover all categories and create tree structure"""
    print("=== Category Discovery & Tree Creation ===\n")
    
    # Discover categories
    categories = discover_categories(headless=True)
    if not categories:
        print("❌ No categories discovered")
        return
    
    print(f"✅ Successfully discovered {len(categories)} categories")
    save_categories_to_json(categories)
    
    # Create tree structure directly from discovered categories
    print(f"\n🌳 Creating tree structure...")
    from scrapers import SimplyCodesScraper
    
    scraper = SimplyCodesScraper(headless=True)
    try:
        # Create empty coupons list since we're just discovering categories
        empty_coupons = []
        tree = scraper.organize_data_tree(categories, empty_coupons)
        scraper.save_tree_structure(tree)
        
        print(f"✅ Successfully created tree structure with {len(tree)} main categories")
        
        # Show tree structure preview
        print(f"\n📁 Tree Structure Preview:")
        for level2_key, level2_data in tree.items():
            print(f"  📂 {level2_data['category_name']} ({len(level2_data['subcategories'])} subcategories)")
            for level3_key, level3_data in list(level2_data['subcategories'].items())[:3]:  # Show first 3
                print(f"    📄 {level3_data['subcategories_name']}")
            if len(level2_data['subcategories']) > 3:
                print(f"    ... and {len(level2_data['subcategories']) - 3} more subcategories")
    except Exception as e:
        print(f"❌ Failed to create tree structure: {e}")
    finally:
        scraper.close()

def comprehensive_coupons_main():
    """Comprehensive scraping: load categories + scrape all + enhance with hierarchy"""
    print("=== Comprehensive Coupon Scraper ===\n")
    
    # Get optional parameters
    max_categories = None
    if len(sys.argv) > 2:
        try:
            max_categories = int(sys.argv[2])
            print(f"📊 Limiting to {max_categories} categories")
        except ValueError:
            print("⚠️  Invalid max_categories parameter, using all categories")
    
    # Step 1: Load discovered categories and tree structure
    print("🔍 Step 1: Loading discovered categories and tree structure...")
    
    # Load discovered categories for URLs
    discovered_path = Path("data/discovered_categories.json")
    if not discovered_path.exists():
        print("❌ discovered_categories.json not found. Please run 'discover_tree' first.")
        return
    
    with open(discovered_path, 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    if not categories:
        print("❌ No categories found in discovered_categories.json")
        return
    
    # Load tree structure for hierarchy mapping
    tree_path = Path("data/category_tree.json")
    if not tree_path.exists():
        print("❌ category_tree.json not found. Please run 'discover_tree' first.")
        return
    
    with open(tree_path, 'r', encoding='utf-8') as f:
        tree_structure = json.load(f)
    
    print(f"✅ Loaded {len(categories)} categories and tree structure")
    
    if max_categories:
        categories = categories[:max_categories]
        print(f"📊 Limiting to first {max_categories} categories")
    
    # Step 2: Create URL to hierarchy mapping
    print(f"\n🗺️  Step 2: Creating URL to hierarchy mapping...")
    url_to_hierarchy = {}
    
    # Build mapping from tree structure
    for level1_key, level1_data in tree_structure.items():
        level1_name = level1_data['category_name']
        level1_path = level1_data['category_path']
        
        for level2_key, level2_data in level1_data['subcategories'].items():
            level2_name = level2_data['subcategories_name']
            level2_path = level2_data['subcategories_path']
            
            # Add level 2 mapping
            url_to_hierarchy[level2_path] = {
                'level1': level1_key,
                'level2': level2_key,
                'level3': None
            }
            
            # Add level 3 mappings if they exist
            if 'subcategories' in level2_data:
                for level3_key, level3_data in level2_data['subcategories'].items():
                    level3_path = level3_data['subcategories_path']
                    
                    url_to_hierarchy[level3_path] = {
                        'level1': level1_key,
                        'level2': level2_key,
                        'level3': level3_key
                    }
    
    print(f"✅ Created hierarchy mapping for {len(url_to_hierarchy)} URLs")
    
    # Step 3: Scrape all categories
    print(f"\n🚀 Step 3: Scraping coupons from all categories...")
    from scrapers import SimplyCodesScraper
    
    scraper = SimplyCodesScraper(headless=True)
    try:
        all_coupons = []
        successful_categories = 0
        
        for idx, category in enumerate(categories, 1):
            print(f"\n📂 Processing {idx}/{len(categories)}: {category['title']}")
            
            try:
                category_coupons = scraper.scrape(category['url'])
                
                if category_coupons:
                    # Add category information and hierarchy to each coupon
                    for coupon in category_coupons:
                        coupon['category'] = category['title']
                        coupon['category_url'] = category['url']
                        coupon['category_path'] = category['category_path']
                        
                        # Add hierarchy information
                        hierarchy = url_to_hierarchy.get(category['category_path'], {})
                        coupon['level1'] = hierarchy.get('level1')
                        coupon['level2'] = hierarchy.get('level2')
                        coupon['level3'] = hierarchy.get('level3')
                    
                    all_coupons.extend(category_coupons)
                    successful_categories += 1
                    print(f"✅ Found {len(category_coupons)} coupons")
                else:
                    print(f"⚠️  No coupons found")
                
                # Add delay between categories
                if idx < len(categories):
                    print(f"⏳ Waiting 5 seconds...")
                    import time
                    time.sleep(5)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Summary: {successful_categories}/{len(categories)} categories successful, {len(all_coupons)} total coupons")
        
        # Save comprehensive coupons with hierarchy
        save_coupons_to_json(all_coupons, "data/comprehensive_coupons.json")
        
        print(f"✅ Comprehensive coupon scraping completed successfully!")
        print(f"📁 Enhanced coupons saved to data/comprehensive_coupons.json")
        
    finally:
        scraper.close()

def validator_main():
    print("=== Coupon Validator ===\n")
    validate_first_coupon()

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [scrape_single|discover_tree|comprehensive_coupons|validate] [max_categories]")
        print("\nCommands:")
        print("  scrape_single      - Scrape single category (beauty/makeup)")
        print("  discover_tree      - Discover categories and create tree structure")
        print("  comprehensive_coupons - Load categories + scrape all + enhance with hierarchy")
        print("  validate           - Validate first coupon")
        print("\nOptional parameters:")
        print("  max_categories     - Limit number of categories (for comprehensive_coupons)")
        return
    
    cmd = sys.argv[1].lower()
    if cmd == "scrape_single":
        scrape_single_main()
    elif cmd == "discover_tree":
        discover_tree_main()
    elif cmd == "comprehensive_coupons":
        comprehensive_coupons_main()
    elif cmd == "validate":
        validator_main()
    else:
        print("Unknown command. Use 'scrape_single', 'discover_tree', 'comprehensive_coupons', or 'validate'.")

if __name__ == "__main__":
    main()
