# 🎫 Coupon Companion - AI-Powered Coupon Discovery & Chatbot

A comprehensive web scraper and AI chatbot for extracting and querying coupon codes from SimplyCodes.com across all categories with hierarchical tree structure organization.

## 📸 Demo Screenshots

### 🔍 Basic Search Mode (Free)
*No API key required - Fast keyword search and data browsing*

![Basic Search Mode](demo_photo_free.jpg)

**Features:**
- ✅ **Free to use** - No OpenAI API key needed
- 🔍 **Keyword search** - Search by brand, category, or keyword
- 📊 **Statistics** - View data overview and counts
- 📋 **Category listing** - Browse all available categories
- 🏷️ **Brand listing** - See all available brands
- ⚡ **Fast response** - Instant results without AI processing

### 🤖 AI Chat Mode (Gemini)
*Requires Google Gemini API key - Natural language conversations and smart recommendations*

![AI Chat Mode](demo_photo_API.jpg)

**Features:**
- 🤖 **Natural language** - Ask questions in plain English
- 🧠 **Conversational memory** - Maintains context across chat
- 🔍 **Semantic search** - Understands meaning, not just keywords
- 💡 **Smart recommendations** - AI-powered suggestions
- 🎯 **Complex queries** - Handle multi-part questions
- ⚠️ **Requires Google Gemini API key** with sufficient credits

## 🚀 Features

### **Web Scraping**
- **Category Discovery**: Automatically discovers all available categories from SimplyCodes.com
- **3-Level Hierarchy**: Organizes data into hierarchical categories (Level 1 → Level 2 → Level 3 → Coupons)
- **Single Category Scraping**: Scrape coupons from a specific category
- **Comprehensive Scraping**: Load categories + scrape all + enhance with hierarchy
- **Anti-Detection**: Built-in stealth features to avoid blocking
- **Retry Logic**: Automatic retry with exponential backoff
- **Data Export**: Saves results to JSON files with enhanced hierarchy tracking

### **AI Chatbot**
- **Dual Mode Interface**: Basic search (free) and AI chat (OpenAI-powered)
- **Web Interface**: Modern, responsive web UI with mode toggle
- **FastAPI Backend**: RESTful API for both basic and AI functionality
- **Vector Search**: LangChain-powered semantic search for intelligent queries
- **Conversational Memory**: Maintains context across chat sessions

## 📊 Current Data Status

**✅ Successfully Discovered:**
- **19 Main Categories** (Level 1)
- **2510 Total Categories** (including subcategories)
- **1283 Level 2 & 3 Subcategories**
- **Complete AI Categories**: AI Devices, AI Detection, AI Hardware, AI Content Creation, etc.

**Example Categories:**
```
📂 Artificial Intelligence (15 subcategories)
  📄 AI Content Creation
  📄 Business AI Tools
  📄 Conversational Intelligence Software
  📄 Creative AI Tools
  📄 AI Devices
  📄 AI Detection
  📄 AI Hardware
  ... and 8 more

📂 Beauty (8 subcategories)
  📄 Fragrances
  📄 Hair Care
  📄 Makeup
  📄 Nail Care
  📄 Shaving & Hair Removal
  📄 Skin Care
  📄 Tanning
  📄 Tools & Accessories
```

## 🛠️ Usage

### **1. Scraping Commands**

#### Scrape Single Category
```bash
python main.py scrape_single
```
Scrapes the default category (beauty/makeup) and saves results to `data/extracted_coupons.json`.

#### Discover Categories & Create Tree
```bash
python main.py discover_tree
```
Discovers all available categories and creates a tree structure, saving to:
- `data/discovered_categories.json` - All discovered categories (flat list)
- `data/category_tree.json` - Hierarchical tree structure

#### Comprehensive Coupon Scraping
```bash
# Scrape all categories
python main.py comprehensive_coupons

# Scrape only first 10 categories
python main.py comprehensive_coupons 10
```
Performs complete workflow: Load categories → Scrape all → Enhance with hierarchy.

### **2. Chatbot Usage**

#### Start Basic API (Free Mode)
```bash
cd llm
python api_basic.py
```
Provides basic search functionality without OpenAI API requirements.

#### Start AI Chatbot (Requires Google Gemini API)
```bash
cd llm
python api_gemini.py
```
Provides full AI-powered conversational interface.

#### Access Web Interface
1. Start either API server
2. Open `llm/web_interface.html` in your browser
3. Use mode toggle to switch between Basic Search and AI Chat

## 🏗️ Project Structure

```
coupon_companion/
├── main.py                          # Main CLI entry point
├── scrapers/
│   ├── __init__.py                  # Scraper convenience functions
│   └── simplycodes_scraper.py       # Main scraper class
├── validators/
│   └── coupon_validator.py          # Coupon validation logic
├── llm/
│   ├── assistant_gemini.py          # Gemini LangChain AI assistant
│   ├── assistant_openai.py          # OpenAI LangChain AI assistant (alternative)
│   ├── api_gemini.py                # Full AI API (Gemini)
│   ├── api_openai.py                # Full AI API (OpenAI) (alternative)
│   ├── web_interface.html           # Web UI
│   ├── test_assistant.py            # AI assistant tests
│   └── test_basic.py                # Basic API tests
├── data/
│   ├── discovered_categories.json   # Discovered categories (flat)
│   ├── extracted_coupons.json       # Single category results
│   ├── comprehensive_coupons.json   # All categories with hierarchy (flat)
│   └── category_tree.json          # Clean tree structure (no coupons)
├── requirements.txt                 # Python dependencies
├── .env                            # Environment variables (API keys)
└── demo_photo.jpg                  # Project demo screenshot
```

## 🔧 API Endpoints

### **Basic API (Free)**
- `GET /health` - Health check
- `GET /search?query=beauty` - Search coupons by keyword
- `GET /categories` - List all categories
- `GET /brands` - List all brands
- `GET /stats` - Get statistics

### **AI API (Gemini)**
- `POST /chat` - AI-powered conversational chat
- `GET /search?query=beauty` - Semantic search
- `GET /categories` - List all categories
- `GET /brands` - List all brands
- `GET /stats` - Get statistics

## 📋 Output Formats

### **Category Discovery Output**
```json
[
  {
    "title": "AI Content Creation",
    "url": "https://simplycodes.com/category/artificial-intelligence/ai-content-creation",
    "category_path": "/category/artificial-intelligence/ai-content-creation",
    "level": 2,
    "parent_category": "artificial-intelligence"
  }
]
```

### **Enhanced Coupon Output**
```json
{
  "brand": "Taplio",
  "code": "TAPLIO50",
  "description": "50% off",
  "button_index": 0,
  "category": "AI Content Creation",
  "category_url": "https://simplycodes.com/category/artificial-intelligence/ai-content-creation",
  "category_path": "/category/artificial-intelligence/ai-content-creation",
  "level1": "artificial-intelligence",
  "level2": "ai-content-creation",
  "level3": null
}
```

## 🚀 Quick Start

### **1. Environment Setup**
```bash
# Clone repository
git clone https://github.com/Kym1ng/AI-Powered-Coupon-Discovery-Chatbot.git
cd AI-Powered-Coupon-Discovery-Chatbot/coupon_companion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

### **2. Discover Categories**
```bash
python main.py discover_tree
```

### **3. Start Chatbot**
```bash
# Basic mode (free)
cd llm
python api_basic.py

# AI mode (requires OpenAI API key)
# First, set your Google Gemini API key in .env file
echo "GOOGLE_API_KEY=your-gemini-api-key-here" > .env
python llm/api_gemini.py
```

### **4. Access Web Interface**
Open `llm/web_interface.html` in your browser and start chatting!

## 🔑 Configuration

### **Environment Variables**
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your-gemini-api-key-here
```

### **Scraper Settings**
- **Headless Mode**: Default is `True` (runs without browser UI)
- **Delay Between Categories**: Default is 5 seconds
- **Max Categories**: Optional limit for comprehensive scraping
- **Retry Attempts**: Default is 3 attempts with exponential backoff

### **Anti-Detection Features**
- Realistic browser headers and user agent
- Random delays between requests
- Stealth scripts to hide automation indicators
- 403 error detection and bypass attempts

## 📈 Performance

**Current Data Coverage:**
- ✅ **2,510 Total Categories** discovered
- ✅ **1,283 Level 2 & 3 Subcategories** found
- ✅ **19 Main Categories** with complete hierarchy
- ✅ **All AI Categories** including previously missing ones

**Scraping Speed:**
- ~5 seconds per category (with anti-detection delays)
- ~2-3 hours for comprehensive scraping of all categories
- Real-time category discovery in ~30 seconds

## 🤖 Chatbot Modes

### **Basic Search Mode (Free)** - See demo above ↑
- ✅ No API key required
- ✅ Fast keyword search
- ✅ Category and brand listings
- ✅ Statistics and data overview
- ✅ Perfect for quick coupon lookups
- ⚡ Instant response time

### **AI Chat Mode (Gemini)** - See demo above ↑
- 🤖 Natural language queries
- 🧠 Conversational memory
- 🔍 Semantic search capabilities
- 💡 Smart recommendations
- 🎯 Complex multi-part questions
- ⚠️ Requires Google Gemini API key with credits
- 💰 Incurs Google Gemini usage costs

## 🐛 Troubleshooting

### **Common Issues**

**1. 403 Forbidden Errors**
- The scraper includes automatic retry logic
- If persistent, try running with longer delays

**2. Google Gemini API Errors**
- Check your API key in `.env` file
- Ensure you have sufficient credits
- Try using `gemini-1.5-flash` for cheaper usage

**3. Web Interface Not Working**
- Ensure API server is running (`python llm/api_gemini.py`)
- Check browser console for CORS errors
- Verify API URL in `web_interface.html`

**4. Missing Categories**
- Run `python main.py discover_tree` to refresh category data
- Check `data/discovered_categories.json` for current data

## 📝 Notes

- The scraper includes respectful delays between requests to avoid overwhelming the server
- All scraping is done in headless mode by default for better performance
- Results are automatically saved to JSON files in the `data/` directory
- The scraper handles 403 errors and other blocking attempts gracefully
- Enhanced coupon data provides complete hierarchy tracking
- Clean tree structure for navigation, enhanced coupons for search
- The chatbot supports both free basic search and paid AI chat modes (Gemini-powered)

## 🔄 Recent Updates

**Latest Improvements:**
- ✅ Fixed level 3 category discovery
- ✅ Enhanced selectors to find all level 2 categories (with and without level 3)
- ✅ Improved tree organization with proper 3-level hierarchy
- ✅ Renamed `comprehensive_tree` to `comprehensive_coupons` for clarity
- ✅ Enhanced coupon data with clean hierarchy tracking (`level1`, `level2`, `level3`)
- ✅ Separated clean tree structure from coupon data
- ✅ Added dual-mode chatbot (basic + AI)
- ✅ Created web interface with mode toggle
- ✅ Implemented FastAPI backend for both modes
- ✅ Added comprehensive error handling and retry logic

---

**🎯 Ready to discover the best coupons? Start with `python main.py discover_tree` and then launch your chatbot!**
