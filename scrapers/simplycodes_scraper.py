import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class SimplyCodesScraper:
    def __init__(self, headless=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic browser settings
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )
        
        # Add stealth scripts to avoid detection
        self.page = self.context.new_page()
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)

    def close(self):
        """Close all browser resources"""
        try:
            self.page.close()
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except Exception as e:
            print(f"Error closing scraper: {e}")

    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def discover_categories(self, categories_url="https://simplycodes.com/category", timeout=30000):
        """Discover all available categories from the main categories page."""
        try:
            print(f"🔍 Discovering categories from: {categories_url}")
            self.page.goto(categories_url, timeout=timeout, wait_until='networkidle')
            self.random_delay(2, 4)
            
            title = self.page.title()
            print(f"Page title: {title}")
            
            if "403" in title or "forbidden" in title.lower():
                print("⚠️  Detected 403 Forbidden on categories page")
                return []
            
            return self._extract_categories()
            
        except Exception as e:
            print(f"❌ Error discovering categories: {e}")
            return []

    def _extract_categories(self):
        """Extract category URLs and titles from the categories page, including deeper subcategories."""
        categories = []
        try:
            self.page.wait_for_load_state('networkidle')
            
            # First, get the main level 2 categories
            print("🔍 Extracting main categories (level 2)...")
            main_category_links = self.page.query_selector_all('div.flex.flex-row.items-center.justify-between.rounded-16 div.title a')
            
            print(f"Found {len(main_category_links)} main category links")
            
            # Extract all main category data first to avoid context destruction
            main_categories_data = []
            for link in main_category_links:
                try:
                    href = link.get_attribute('href')
                    title = link.inner_text().strip()
                    
                    if href and title:
                        # Convert relative URLs to absolute URLs
                        if href.startswith('/'):
                            full_url = f"https://simplycodes.com{href}"
                        else:
                            full_url = href
                        
                        main_categories_data.append({
                            'title': title,
                            'url': full_url,
                            'category_path': href,
                            'level': 2
                        })
                        print(f"  📁 Level 2: {title}: {full_url}")
                        
                except Exception as e:
                    print(f"❌ Error extracting category link: {e}")
                    continue
            
            # Now add main categories to the result
            categories.extend(main_categories_data)
            
            # Now extract level 3 subcategories directly from the main page
            print(f"\n🔍 Extracting level 3 subcategories from main page...")
            level3_subcategories = self._extract_level3_subcategories_from_main_page()
            categories.extend(level3_subcategories)
            
            print(f"✅ Successfully extracted {len(categories)} total categories (including subcategories)")
            return categories
            
        except Exception as e:
            print(f"❌ Error extracting categories: {e}")
            return []

    def _extract_level3_subcategories_from_main_page(self):
        """Extract level 3 subcategories directly from the main categories page."""
        subcategories = []
        try:
            # Try to expand all collapsible sections so nested UL/LIs are visible
            self._expand_all_subcategory_sections()

            # Look for level 3 subcategory links directly on the main page
            # Based on the HTML structure from the image: li > a[href*="/category/"]
            level3_selectors = [
                'li a[href*="/category/"]',  # Links within li elements (as seen in the image)
                'ul.ml-6 a[href*="/category/"]',  # Links within the nested ul with ml-6 class
                'a.body-2.text-gray-30[href*="/category/"]',  # Specific class from the image
                'div[data-state="open"] ul a[href*="/category/"]',  # Links in expanded sections
            ]
            
            found_links = set()  # To avoid duplicates
            
            for selector in level3_selectors:
                try:
                    links = self.page.query_selector_all(selector)
                    print(f"    🔍 Trying selector '{selector}': found {len(links)} links")
                    
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            title = link.inner_text().strip()
                            
                            if href and title and href not in found_links:
                                # Check if this is a level 3 subcategory (4 parts: /category/level1/level2/level3)
                                path_parts = href.split('/')
                                if len(path_parts) >= 5:  # /category/level1/level2/level3
                                    # Convert relative URLs to absolute URLs
                                    if href.startswith('/'):
                                        full_url = f"https://simplycodes.com{href}"
                                    else:
                                        full_url = href
                                    
                                    # Extract level information from path
                                    level1 = path_parts[2] if len(path_parts) > 2 else ""
                                    level2 = path_parts[3] if len(path_parts) > 3 else ""
                                    level3 = path_parts[4] if len(path_parts) > 4 else ""
                                    
                                    subcategories.append({
                                        'title': title,
                                        'url': full_url,
                                        'category_path': href,
                                        'level': 3,
                                        'parent_category': f"{level1} > {level2}",
                                        'parent_path': f"/category/{level1}/{level2}",
                                        'level1': level1,
                                        'level2': level2,
                                        'level3': level3
                                    })
                                    found_links.add(href)
                                    print(f"      📂 Level 3: {title} ({level1} > {level2} > {level3}): {full_url}")
                                    
                        except Exception as e:
                            print(f"      ⚠️  Error processing link: {e}")
                            continue
                                    
                except Exception as e:
                    print(f"    ⚠️  Error with selector '{selector}': {e}")
                    continue
            
            print(f"  ✅ Found {len(subcategories)} level 3 subcategories from main page")
            return subcategories
            
        except Exception as e:
            print(f"❌ Error extracting level 3 subcategories: {e}")
            return []

    def _expand_all_subcategory_sections(self):
        """Expand all collapsible sections on the categories page so subcategory lists are visible."""
        try:
            # Sometimes content is lazy-rendered; scroll to bottom and back up
            try:
                self.page.mouse.wheel(0, 2000)
                self.random_delay(0.5, 1.0)
                self.page.mouse.wheel(0, -2000)
                self.random_delay(0.5, 1.0)
            except Exception:
                pass

            toggle_selectors = [
                'div[role="button"][aria-controls]',  # Common pattern on this site
                'button[aria-controls]',
                'div[aria-controls][class*="accordion"]',
                '[data-state] [role="button"]',  # Fallback
            ]

            total_clicked = 0
            for selector in toggle_selectors:
                try:
                    toggles = self.page.query_selector_all(selector)
                    for toggle in toggles:
                        try:
                            # Skip if already expanded
                            expanded = toggle.get_attribute('aria-expanded')
                            if expanded and expanded.lower() == 'true':
                                continue

                            toggle.click()
                            total_clicked += 1
                            # Give the animation time to finish and content to render
                            self.random_delay(0.2, 0.5)
                        except Exception:
                            continue
                except Exception:
                    continue

            if total_clicked:
                print(f"    ⬇️ Expanded {total_clicked} collapsible sections")
            else:
                print("    ℹ️ No collapsible toggles detected or already expanded")

            # Wait briefly to ensure DOM is updated
            self.random_delay(0.3, 0.6)

        except Exception as e:
            print(f"    ⚠️  Error while expanding sections: {e}")

    def _extract_subcategories(self, category_url, category_path, category_title):
        """Extract deeper subcategories from a category page."""
        subcategories = []
        try:
            print(f"🔍 Exploring subcategories for: {category_title}")
            
            # Navigate to the category page
            self.page.goto(category_url, timeout=30000, wait_until='networkidle')
            self.random_delay(2, 3)
            
            # Check if page loaded successfully
            title = self.page.title()
            if "403" in title or "forbidden" in title.lower():
                print(f"  ⚠️  Page blocked for {category_title}, skipping subcategories")
                return []
            
            # Look for subcategory links - these might be in different structures
            # Try multiple selectors to find subcategory links
            subcategory_selectors = [
                'li a[href*="/category/"]',  # Links within li elements (as seen in the image)
                'ul.ml-6 a[href*="/category/"]',  # Links within the nested ul with ml-6 class
                'a.body-2.text-gray-30[href*="/category/"]',  # Specific class from the image
                'div[data-state="open"] ul a[href*="/category/"]',  # Links in expanded sections
                'a[href*="/category/"]',  # Any link containing /category/ (fallback)
                'a[href^="/category/"]'  # Links starting with /category/ (fallback)
            ]
            
            found_links = set()  # To avoid duplicates
            
            for selector in subcategory_selectors:
                try:
                    links = self.page.query_selector_all(selector)
                    print(f"    🔍 Trying selector '{selector}': found {len(links)} links")
                    
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            title = link.inner_text().strip()
                            
                            if href and title and href not in found_links:
                                # Check if this is a deeper subcategory (level 3: /category/level1/level2/level3)
                                path_parts = href.split('/')
                                if len(path_parts) >= 5:  # /category/level1/level2/level3
                                    # Convert relative URLs to absolute URLs
                                    if href.startswith('/'):
                                        full_url = f"https://simplycodes.com{href}"
                                    else:
                                        full_url = href
                                    
                                    # Only add if it's a deeper subcategory (not the same as parent)
                                    if href != category_path:
                                        # Extract level information from path
                                        level1 = path_parts[2] if len(path_parts) > 2 else ""
                                        level2 = path_parts[3] if len(path_parts) > 3 else ""
                                        level3 = path_parts[4] if len(path_parts) > 4 else ""
                                        
                                        subcategories.append({
                                            'title': title,
                                            'url': full_url,
                                            'category_path': href,
                                            'level': 3,
                                            'parent_category': category_title,
                                            'parent_path': category_path,
                                            'level1': level1,
                                            'level2': level2,
                                            'level3': level3
                                        })
                                        found_links.add(href)
                                        print(f"      📂 Level 3: {title} ({level1} > {level2} > {level3}): {full_url}")
                                        
                        except Exception as e:
                            print(f"      ⚠️  Error processing link: {e}")
                            continue
                                    
                except Exception as e:
                    print(f"    ⚠️  Error with selector '{selector}': {e}")
                    continue
            
            print(f"  ✅ Found {len(subcategories)} subcategories for {category_title}")
            return subcategories
            
        except Exception as e:
            print(f"❌ Error extracting subcategories for {category_title}: {e}")
            return []

    def scrape_all_categories(self, max_categories=None, delay_between_categories=5):
        """Scrape coupons from all discovered categories."""
        print("🚀 Starting comprehensive category scraping...")
        
        # First, discover all categories
        categories = self.discover_categories()
        
        if not categories:
            print("❌ No categories discovered")
            return []
        
        if max_categories:
            categories = categories[:max_categories]
            print(f"📊 Limiting to first {max_categories} categories")
        
        all_coupons = []
        successful_categories = 0
        
        for idx, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"📂 Processing category {idx}/{len(categories)}: {category['title']} (Level {category.get('level', 2)})")
            print(f"🔗 URL: {category['url']}")
            print(f"{'='*60}")
            
            try:
                # Scrape coupons from this category
                category_coupons = self.scrape(category['url'])
                
                if category_coupons:
                    # Add category information to each coupon
                    for coupon in category_coupons:
                        coupon['category'] = category['title']
                        coupon['category_url'] = category['url']
                        coupon['category_path'] = category['category_path']
                        coupon['category_level'] = category.get('level', 2)
                        if 'parent_category' in category:
                            coupon['parent_category'] = category['parent_category']
                    
                    all_coupons.extend(category_coupons)
                    successful_categories += 1
                    print(f"✅ Found {len(category_coupons)} coupons in {category['title']} (Level {category.get('level', 2)})")
                else:
                    print(f"⚠️  No coupons found in {category['title']}")
                
                # Add delay between categories to be respectful
                if idx < len(categories):
                    print(f"⏳ Waiting {delay_between_categories} seconds before next category...")
                    time.sleep(delay_between_categories)
                    
            except Exception as e:
                print(f"❌ Error scraping category {category['title']}: {e}")
                continue
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Summary:")
        print(f"   • Total categories processed: {len(categories)}")
        print(f"   • Successful categories: {successful_categories}")
        print(f"   • Total coupons collected: {len(all_coupons)}")
        
        return all_coupons

    def scrape(self, url, timeout=30000):
        """Enhanced scraping method with better error handling, returns only coupon list."""
        try:
            print(f"Navigating to: {url}")
            self.page.goto(url, timeout=timeout, wait_until='networkidle')
            self.random_delay(2, 4)
            title = self.page.title()
            print(f"Page title: {title}")
            if "403" in title or "forbidden" in title.lower():
                print("⚠️  Detected 403 Forbidden - trying alternative approach...")
                return self._handle_blocked_page(url)
            return self._extract_data()
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            return []

    def _handle_blocked_page(self, url):
        """Handle blocked pages with alternative strategies, returns only coupon list."""
        print("🔄 Attempting to bypass blocking...")
        try:
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.page.reload(wait_until='networkidle')
            self.random_delay(3, 5)
            title = self.page.title()
            print(f"New page title: {title}")
            if "403" not in title and "forbidden" not in title.lower():
                print("✅ Successfully bypassed blocking!")
                return self._extract_data()
            else:
                print("❌ Still blocked after bypass attempt")
                return []
        except Exception as e:
            print(f"❌ Error during bypass attempt: {e}")
            return []

    def _extract_data(self):
        """Return only the list of coupon dicts (no extra metadata)."""
        try:
            # Only return the coupons list
            return self._extract_coupons()
        except Exception as e:
            print(f"❌ Error extracting data: {e}")
            return []

    def _extract_coupons(self):
        """Extract coupon codes and discount information, saving the index of each coupon block for later validation."""
        coupons = []
        try:
            self.page.wait_for_load_state('networkidle')
            grid_selector = 'div.grid.grid-cols-1'
            grid = self.page.query_selector(grid_selector)
            if not grid:
                print("❌ Coupon grid not found!")
                return []
            coupon_blocks = grid.query_selector_all("div[role='button']")
            print(f"Found {len(coupon_blocks)} coupon blocks in grid.")
            for idx, block in enumerate(coupon_blocks):
                coupon_data = self._extract_single_coupon(block, idx)
                if coupon_data:
                    coupons.append(coupon_data)
            return coupons
        except Exception as e:
            print(f"❌ Error extracting coupons: {e}")
            return []

    def _extract_single_coupon(self, element, button_index):
        """Extract coupon data and save the coupon block's index as button_index for later validation."""
        try:
            # Brand: h3 inside the coupon block
            brand = None
            brand_elem = element.query_selector('h3')
            if brand_elem:
                brand = brand_elem.inner_text().strip()
            # Coupon code: button span.uppercase.truncate
            code = None
            code_elem = element.query_selector('button span.uppercase.truncate')
            if code_elem:
                code = code_elem.inner_text().strip()
            # Description: h4 inside the coupon block
            description = None
            desc_elem = element.query_selector('h4')
            if desc_elem:
                description = desc_elem.inner_text().strip()
            if brand and code and description:
                return {
                    'brand': brand,
                    'code': code,
                    'description': description,
                    'button_index': button_index
                }
            return None
        except Exception as e:
            print(f"❌ Error extracting single coupon: {e}")
            return None

    def scrape_with_retry(self, url, max_retries=3):
        """Scrape with automatic retry logic, returns only coupon list."""
        for attempt in range(max_retries):
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            result = self.scrape(url)
            if result:
                return result
            if attempt < max_retries - 1:
                delay = (attempt + 1) * 5
                print(f"⏳ Waiting {delay} seconds before retry...")
                time.sleep(delay)
        print("❌ All retry attempts failed")
        return []

    def organize_data_tree(self, categories, coupons):
        """Organize categories and coupons into a hierarchical tree structure with support for level 3 subcategories."""
        tree = {}
        
        # First, organize categories by level
        for category in categories:
            path_parts = category['category_path'].split('/')
            level = category.get('level', 2)  # Default to level 2 if not specified
            
            if level == 2 and len(path_parts) >= 3:
                # Level 2 category: /category/level2
                level2 = path_parts[2]
                
                if level2 not in tree:
                    tree[level2] = {
                        'category_name': level2.replace('-', ' ').title(),
                        'category_path': f"/category/{level2}",
                        'subcategories': {}
                    }
                
            elif level == 3 and len(path_parts) >= 4:
                # Level 3 subcategory: /category/level2/level3
                level2 = path_parts[2]
                level3 = path_parts[3]
                
                # Ensure level 2 category exists
                if level2 not in tree:
                    tree[level2] = {
                        'category_name': level2.replace('-', ' ').title(),
                        'category_path': f"/category/{level2}",
                        'subcategories': {}
                    }
                
                # Add level 3 subcategory
                tree[level2]['subcategories'][level3] = {
                    'subcategories_name': category['title'],
                    'subcategories_path': category['category_path'],
                    'url': category['url'],
                    'level': 3,
                    'parent_category': category.get('parent_category', ''),
                    'coupons': []
                }
        
        # Now organize coupons under their respective categories
        for coupon in coupons:
            path_parts = coupon['category_path'].split('/')
            if len(path_parts) >= 4:
                level2 = path_parts[2]
                level3 = path_parts[3]
                
                if level2 in tree and level3 in tree[level2]['subcategories']:
                    # Remove category info from coupon to avoid redundancy
                    coupon_data = {
                        'brand': coupon['brand'],
                        'code': coupon['code'],
                        'description': coupon['description'],
                        'button_index': coupon['button_index']
                    }
                    tree[level2]['subcategories'][level3]['coupons'].append(coupon_data)
        
        return tree

    def save_tree_structure(self, tree, filename="data/category_tree.json"):
        """Save the tree structure to a JSON file."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tree, f, ensure_ascii=False, indent=2)
        print(f"💾 Tree structure saved to {filename}")

    def scrape_all_categories_with_tree(self, max_categories=None, delay_between_categories=5):
        """Scrape coupons from all discovered categories and organize into tree structure."""
        print("🚀 Starting comprehensive category scraping with tree organization...")
        
        # First, discover all categories
        categories = self.discover_categories()
        
        if not categories:
            print("❌ No categories discovered")
            return None
        
        if max_categories:
            categories = categories[:max_categories]
            print(f"📊 Limiting to first {max_categories} categories")
        
        all_coupons = []
        successful_categories = 0
        
        for idx, category in enumerate(categories, 1):
            print(f"\n{'='*60}")
            print(f"📂 Processing category {idx}/{len(categories)}: {category['title']} (Level {category.get('level', 2)})")
            print(f"🔗 URL: {category['url']}")
            print(f"{'='*60}")
            
            try:
                # Scrape coupons from this category
                category_coupons = self.scrape(category['url'])
                
                if category_coupons:
                    # Add category information to each coupon
                    for coupon in category_coupons:
                        coupon['category'] = category['title']
                        coupon['category_url'] = category['url']
                        coupon['category_path'] = category['category_path']
                        coupon['category_level'] = category.get('level', 2)
                        if 'parent_category' in category:
                            coupon['parent_category'] = category['parent_category']
                    
                    all_coupons.extend(category_coupons)
                    successful_categories += 1
                    print(f"✅ Found {len(category_coupons)} coupons in {category['title']} (Level {category.get('level', 2)})")
                else:
                    print(f"⚠️  No coupons found in {category['title']}")
                
                # Add delay between categories to be respectful
                if idx < len(categories):
                    print(f"⏳ Waiting {delay_between_categories} seconds before next category...")
                    time.sleep(delay_between_categories)
                    
            except Exception as e:
                print(f"❌ Error scraping category {category['title']}: {e}")
                continue
        
        print(f"\n🎉 Scraping completed!")
        print(f"📊 Summary:")
        print(f"   • Total categories processed: {len(categories)}")
        print(f"   • Successful categories: {successful_categories}")
        print(f"   • Total coupons collected: {len(all_coupons)}")
        
        # Organize into tree structure
        print(f"\n🌳 Organizing data into tree structure...")
        tree = self.organize_data_tree(categories, all_coupons)
        
        # Save tree structure
        self.save_tree_structure(tree)
        
        # Also save flat structure for backward compatibility
        self.save_comprehensive_coupons(all_coupons)
        
        return {
            'tree': tree,
            'flat_coupons': all_coupons,
            'categories': categories
        }

    def save_comprehensive_coupons(self, coupons, filename="data/comprehensive_coupons.json"):
        """Save comprehensive coupons to JSON file."""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(coupons, f, ensure_ascii=False, indent=2)
        print(f"💾 Comprehensive coupons saved to {filename}")
