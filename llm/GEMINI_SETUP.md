# 🆓 Google Gemini API Setup (FREE Alternative)

## 🎯 **Why Gemini?**
- **FREE tier**: 60 requests/minute, 15M characters/month
- **No credit card required** for free tier
- **No expiration** on free usage
- **Same functionality** as OpenAI version

## 🔑 **Get Your Gemini API Key:**

### **Step 1: Visit Google AI Studio**
Go to: https://makersuite.google.com/app/apikey

### **Step 2: Sign In**
- Use your Google account (same as Google Drive)
- No additional signup needed

### **Step 3: Create API Key**
- Click **"Create API Key"**
- Choose **"Create API Key in new project"** or existing project
- Copy the generated API key

### **Step 4: No Billing Setup Required**
- Free tier works without adding payment method
- You can add billing later if you need more usage

## 🔧 **Setup in Your Project:**

### **Option 1: Environment Variable**
```bash
export GOOGLE_API_KEY="your-gemini-api-key-here"
```

### **Option 2: .env File**
Create or edit `.env` file in your project root:
```bash
# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your-openai-api-key-here

# Google Gemini API Key (FREE tier available)
GOOGLE_API_KEY=your-gemini-api-key-here
```

### **Option 3: Direct in Terminal**
```bash
# Set for current session
export GOOGLE_API_KEY="your-gemini-api-key-here"

# Then run your Gemini chatbot
python llm/api_gemini.py
```

## 📦 **Install Dependencies:**
```bash
pip install -r requirements.txt
```

## 🧪 **Test Gemini Assistant:**
```bash
python llm/test_gemini.py
```

## 🚀 **Run Gemini API Server:**
```bash
python llm/api_gemini.py
```
The server will run on: http://localhost:8001

## 🌐 **Use in Web Interface:**
Update your web interface to use the Gemini API:
- Change API_BASE_URL to `http://localhost:8001`
- Or create a toggle between OpenAI and Gemini

## 📊 **Free Tier Limits:**
- **60 requests per minute** (1 request/second)
- **15 million characters per month**
- **No credit card required**
- **No expiration**

## 🔄 **API Endpoints (Same as OpenAI):**
- `POST /chat` - AI chat with Gemini
- `POST /search` - Search coupons
- `GET /categories` - Get all categories
- `GET /brands` - Get all brands
- `GET /stats` - Get database statistics
- `GET /health` - Health check

## 💡 **Benefits:**
1. **Completely FREE** for reasonable usage
2. **No credit card required**
3. **Same functionality** as OpenAI version
4. **Google's reliable infrastructure**
5. **Good performance** and accuracy

## ⚠️ **Notes:**
- Gemini models: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`
- Default model: `gemini-1.5-flash` (fast and efficient)
- Embeddings model: `models/embedding-001`

## 🆚 **Comparison:**
| Feature | OpenAI (GPT) | Google Gemini |
|---------|-------------|---------------|
| Free Tier | $0 for 3 months | $0 forever |
| Credit Card | Required | Not required |
| Requests/min | Varies | 60 |
| Characters/month | Varies | 15M |
| Model Quality | Excellent | Very Good |
| Cost | Pay per use | Free tier generous |

**Recommendation**: Start with Gemini for free, upgrade to OpenAI if you need more features or higher limits.
