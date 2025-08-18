# Coupon Companion - Enhanced SimplyCodes Scraper

A comprehensive web scraper for extracting coupon codes from SimplyCodes.com across all categories with hierarchical tree structure organization.

## Features

- **Category Discovery**: Automatically discovers all available categories from SimplyCodes.com
- **Tree Structure Organization**: Organizes data into hierarchical categories (Level 2 → Level 3 → Coupons)
- **Single Category Scraping**: Scrape coupons from a specific category
- **Comprehensive Scraping**: Discover categories + scrape all + create tree structure
- **Anti-Detection**: Built-in stealth features to avoid blocking
- **Retry Logic**: Automatic retry with exponential backoff
- **Data Export**: Saves results to JSON files in both flat and tree structures

## Usage

### 1. Scrape Single Category
```bash
python main.py scrape_single
```
This scrapes the default category (beauty/makeup) and saves results to `data/extracted_coupons.json`.

### 2. Discover Categories & Create Tree
```bash
python main.py discover_tree
```
This discovers all available categories and creates a tree structure, saving to:
- `data/discovered_categories.json` - All discovered categories
- `data/category_tree.json` - Hierarchical tree structure

### 3. Comprehensive Tree Scraping
```bash
# Scrape all categories
python main.py comprehensive_tree

# Scrape only first 10 categories
python main.py comprehensive_tree 10
```
This performs a complete workflow:
1. **Discover** all categories
2. **Scrape** coupons from all categories
3. **Create** tree structure

Saves results to:
- `data/discovered_categories.json` - All discovered categories
- `data/comprehensive_coupons.json` - All coupons (flat structure)
- `data/category_tree.json` - All coupons (tree structure)

### 4. Validate Coupons
```bash
python main.py validate
```
This validates the first coupon from the extracted data.

## Output Formats

### Category Discovery Output
```json
[
  {
    "title": "AI Content Creation",
    "url": "https://simplycodes.com/category/artificial-intelligence/ai-content-creation",
    "category_path": "/category/artificial-intelligence/ai-content-creation"
  }
]
```

### Flat Coupon Output
```json
[
  {
    "brand": "Taplio",
    "code": "TAPLIO50",
    "description": "50% off",
    "button_index": 0,
    "category": "AI Content Creation",
    "category_url": "https://simplycodes.com/category/artificial-intelligence/ai-content-creation",
    "category_path": "/category/artificial-intelligence/ai-content-creation"
  }
]
```

### Tree Structure Output
```json
{
  "artificial-intelligence": {
    "category_name": "Artificial Intelligence",
    "category_path": "/category/artificial-intelligence",
    "subcategories": {
      "ai-content-creation": {
        "subcategories_name": "AI Content Creation",
        "subcategories_path": "/category/artificial-intelligence/ai-content-creation",
        "url": "https://simplycodes.com/category/artificial-intelligence/ai-content-creation",
        "coupons": [
          {
            "brand": "Taplio",
            "code": "TAPLIO50",
            "description": "50% off",
            "button_index": 0
          }
        ]
      }
    }
  },
  "beauty": {
    "category_name": "Beauty",
    "category_path": "/category/beauty",
    "subcategories": {
      "makeup": {
        "subcategories_name": "Makeup",
        "subcategories_path": "/category/beauty/makeup",
        "url": "https://simplycodes.com/category/beauty/makeup",
        "coupons": []
      }
    }
  }
}
```

## Tree Structure Organization

The tree structure organizes data hierarchically:

- **Level 2 Categories**: Main categories (e.g., "Artificial Intelligence", "Beauty", "Automotive")
- **Level 3 Categories**: Subcategories under each main category (e.g., "AI Content Creation", "Makeup", "Auto Dealers")
- **Coupons**: Individual coupon codes organized under their respective Level 3 categories

### Example Tree Structure:
```
📂 Artificial Intelligence (5 subcategories)
  📄 AI Content Creation (7 coupons)
  📄 Business AI Tools (9 coupons)
  📄 Conversational Intelligence Software (9 coupons)
  📄 Creative AI Tools (0 coupons)
  📄 Leisure AI Tools (0 coupons)

📂 Beauty (6 subcategories)
  📄 Fragrances (0 coupons)
  📄 Hair Care (0 coupons)
  📄 Makeup (0 coupons)
  📄 Nail Care (0 coupons)
  📄 Shaving & Hair Removal (0 coupons)
  📄 Skin Care (0 coupons)
```

## Configuration

### Scraper Settings
- **Headless Mode**: Default is `True` (runs without browser UI)
- **Delay Between Categories**: Default is 5 seconds
- **Max Categories**: Optional limit for comprehensive scraping
- **Retry Attempts**: Default is 3 attempts with exponential backoff

### Anti-Detection Features
- Realistic browser headers and user agent
- Random delays between requests
- Stealth scripts to hide automation indicators
- 403 error detection and bypass attempts

## Files Structure

```
coupon_companion/
├── main.py                          # Main entry point
├── scrapers/
│   ├── __init__.py                  # Scraper convenience functions
│   └── simplycodes_scraper.py       # Main scraper class
├── validators/
│   └── coupon_validator.py          # Coupon validation logic
├── data/
│   ├── discovered_categories.json   # Discovered categories
│   ├── extracted_coupons.json       # Single category results
│   ├── comprehensive_coupons.json   # All categories (flat structure)
│   └── category_tree.json          # All categories (tree structure)
└── requirements.txt                 # Python dependencies
```

## Requirements

- Python 3.7+
- Playwright
- Other dependencies listed in `requirements.txt`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Notes

- The scraper includes respectful delays between requests to avoid overwhelming the server
- All scraping is done in headless mode by default for better performance
- Results are automatically saved to JSON files in the `data/` directory
- The scraper handles 403 errors and other blocking attempts gracefully
- Tree structure provides better organization for large datasets
- You can create tree structure from existing data without re-scraping
