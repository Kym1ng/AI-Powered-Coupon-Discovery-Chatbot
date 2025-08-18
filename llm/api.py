from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from .assistant import CouponAssistant

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Coupon Chatbot API",
    description="A LangChain-powered API for finding and recommending coupons from SimplyCodes.com",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the coupon assistant
try:
    assistant = CouponAssistant()
    print("✅ Coupon Assistant initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize Coupon Assistant: {e}")
    assistant = None

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    source_documents: List[Dict[str, Any]]

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    brand: Optional[str] = None

class SearchResponse(BaseModel):
    coupons: List[Dict[str, Any]]
    total: int

class StatsResponse(BaseModel):
    total_coupons: int
    total_categories: int
    total_subcategories: int
    categories: List[str]

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Coupon Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/chat": "POST - Chat with the coupon assistant",
            "/search": "POST - Search for specific coupons",
            "/categories": "GET - Get all available categories",
            "/brands": "GET - Get all available brands",
            "/stats": "GET - Get statistics about the data"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the coupon assistant
    
    Ask questions like:
    - "Show me beauty coupons"
    - "What coupons does Taplio have?"
    - "Find AI tool discounts"
    """
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        result = assistant.ask(request.message)
        return ChatResponse(
            answer=result["answer"],
            source_documents=result["source_documents"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_coupons(request: SearchRequest):
    """
    Search for specific coupons
    
    Examples:
    - {"query": "beauty", "category": "Beauty"}
    - {"query": "Taplio", "brand": "Taplio"}
    - {"query": "50% off"}
    """
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        coupons = assistant.search_coupons(
            query=request.query,
            category=request.category,
            brand=request.brand
        )
        
        return SearchResponse(
            coupons=coupons,
            total=len(coupons)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coupons: {str(e)}")

@app.get("/categories", response_model=List[str])
async def get_categories():
    """Get all available categories"""
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        return assistant.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@app.get("/brands", response_model=List[str])
async def get_brands():
    """Get all available brands"""
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        return assistant.get_brands()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting brands: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about the coupon data"""
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        stats = assistant.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "assistant_initialized": assistant is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
