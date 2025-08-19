from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from assistant_gemini import CouponAssistantGemini

# Initialize FastAPI app
app = FastAPI(title="Coupon Assistant Gemini API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the assistant
try:
    assistant = CouponAssistantGemini()
    print("✅ Gemini Assistant initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Gemini Assistant: {e}")
    assistant = None

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    model: str
    api_provider: str

class SearchRequest(BaseModel):
    query: str
    search_type: str = "keyword"  # keyword, category, brand

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    query: str
    search_type: str

class StatsResponse(BaseModel):
    total_coupons: int
    total_categories: int
    total_subcategories: int
    unique_brands: int
    model: str
    api_provider: str

@app.get("/")
async def root():
    return {"message": "Coupon Assistant Gemini API", "status": "running"}

@app.get("/health")
async def health_check():
    if assistant:
        return {"status": "healthy", "model": assistant.model_name, "api_provider": "Google Gemini"}
    else:
        raise HTTPException(status_code=500, detail="Assistant not initialized")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        response = assistant.ask(request.message)
        return ChatResponse(
            response=response,
            model=assistant.model_name,
            api_provider="Google Gemini"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_coupons(request: SearchRequest):
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        results = assistant.search_coupons(request.query, request.search_type)
        return SearchResponse(
            results=results,
            count=len(results),
            query=request.query,
            search_type=request.search_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coupons: {str(e)}")

@app.get("/categories", response_model=List[str])
async def get_categories():
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        return assistant.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@app.get("/brands", response_model=List[str])
async def get_brands():
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        return assistant.get_brands()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting brands: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    if not assistant:
        raise HTTPException(status_code=500, detail="Assistant not initialized")
    
    try:
        stats = assistant.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
