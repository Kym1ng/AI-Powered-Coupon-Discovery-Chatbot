# Coupon Chatbot - LangChain API

A LangChain-powered chatbot API for finding and recommending coupons from SimplyCodes.com.

## Features

- **Conversational AI**: Chat with an AI assistant about coupons
- **Semantic Search**: Find coupons using natural language queries
- **Category Filtering**: Search within specific categories
- **Brand Filtering**: Find coupons for specific brands
- **REST API**: Easy integration with web applications

## Setup

### 1. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Verify Data
Make sure you have `data/category_tree.json` from running the scraper:
```bash
python ../main.py discover_tree
```

## Usage

### Test the Assistant
```bash
python test_assistant.py
```

### Start the API Server
```bash
python api_openai.py
```

The API will be available at `http://localhost:8000`

### API Documentation
Once the server is running, visit:
- `http://localhost:8000/docs` - Interactive API documentation
- `http://localhost:8000/redoc` - Alternative documentation

## API Endpoints

### Chat with Assistant
```bash
POST /chat
{
  "message": "Show me beauty coupons"
}
```

### Search Coupons
```bash
POST /search
{
  "query": "beauty",
  "category": "Beauty",
  "brand": null
}
```

### Get Categories
```bash
GET /categories
```

### Get Brands
```bash
GET /brands
```

### Get Statistics
```bash
GET /stats
```

## Example Usage

### Python Client
```python
import requests

# Chat with assistant
response = requests.post("http://localhost:8000/chat", json={
    "message": "What beauty coupons do you have?"
})
print(response.json()["answer"])

# Search coupons
response = requests.post("http://localhost:8000/search", json={
    "query": "50% off",
    "category": "Beauty"
})
coupons = response.json()["coupons"]
```

### JavaScript/Node.js Client
```javascript
// Chat with assistant
const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "Show me AI tool coupons" })
});
const result = await response.json();
console.log(result.answer);
```

## Architecture

- **CouponAssistant**: Main class handling LangChain integration
- **Vector Store**: ChromaDB for semantic search
- **LLM**: OpenAI GPT models for natural language understanding
- **FastAPI**: REST API server with automatic documentation

## Next Steps

1. **Test the API**: Run the test script to verify everything works
2. **Build Web Interface**: Create a React/Vue frontend to connect to the API
3. **Deploy**: Host the API on a cloud platform
4. **Enhance**: Add more features like user accounts, favorites, etc.
