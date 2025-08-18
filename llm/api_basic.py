from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

app = FastAPI(
    title="Coupon Search API (Basic)",
    description="A basic API for searching coupons without OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load coupon data
def load_coupon_data():
    data_path = Path(__file__).parent.parent / "data" / "category_tree.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Coupon data not found at {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    coupon_data = load_coupon_data()
    print("✅ Coupon data loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load coupon data: {e}")
    coupon_data = {}

# Pydantic models
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
        "message": "Coupon Search API (Basic)",
        "version": "1.0.0",
        "status": "running",
        "note": "This is a basic version without AI chat functionality",
        "endpoints": {
            "/search": "POST - Search for specific coupons",
            "/categories": "GET - Get all available categories",
            "/brands": "GET - Get all available brands",
            "/stats": "GET - Get statistics about the data"
        }
    }

@app.post("/search", response_model=SearchResponse)
async def search_coupons(request: SearchRequest):
    """
    Search for specific coupons
    
    Examples:
    - {"query": "beauty", "category": "Beauty"}
    - {"query": "Taplio", "brand": "Taplio"}
    - {"query": "50% off"}
    """
    if not coupon_data:
        raise HTTPException(status_code=500, detail="Coupon data not loaded")
    
    try:
        results = []
        
        for category_key, category_data in coupon_data.items():
            category_name = category_data['category_name']
            
            # Filter by category if specified
            if request.category and request.category.lower() not in category_name.lower():
                continue
                
            for subcategory_key, subcategory_data in category_data['subcategories'].items():
                subcategory_name = subcategory_data['subcategories_name']
                
                for coupon in subcategory_data['coupons']:
                    # Filter by brand if specified
                    if request.brand and request.brand.lower() not in coupon['brand'].lower():
                        continue
                    
                    # Check if query matches any coupon field
                    query_lower = request.query.lower()
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
        
        return SearchResponse(
            coupons=results,
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coupons: {str(e)}")

@app.get("/categories", response_model=List[str])
async def get_categories():
    """Get all available categories"""
    if not coupon_data:
        raise HTTPException(status_code=500, detail="Coupon data not loaded")
    
    try:
        return [data['category_name'] for data in coupon_data.values()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting categories: {str(e)}")

@app.get("/brands", response_model=List[str])
async def get_brands():
    """Get all available brands"""
    if not coupon_data:
        raise HTTPException(status_code=500, detail="Coupon data not loaded")
    
    try:
        brands = set()
        for category_data in coupon_data.values():
            for subcategory_data in category_data['subcategories'].values():
                for coupon in subcategory_data['coupons']:
                    brands.add(coupon['brand'])
        return sorted(list(brands))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting brands: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about the coupon data"""
    if not coupon_data:
        raise HTTPException(status_code=500, detail="Coupon data not loaded")
    
    try:
        total_coupons = 0
        total_categories = len(coupon_data)
        total_subcategories = 0
        
        for category_data in coupon_data.values():
            total_subcategories += len(category_data['subcategories'])
            for subcategory_data in category_data['subcategories'].values():
                total_coupons += len(subcategory_data['coupons'])
        
        return StatsResponse(
            total_coupons=total_coupons,
            total_categories=total_categories,
            total_subcategories=total_subcategories,
            categories=[data['category_name'] for data in coupon_data.values()]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "data_loaded": len(coupon_data) > 0,
        "total_categories": len(coupon_data) if coupon_data else 0
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Basic Coupon Search API...")
    print("📊 This version works without OpenAI API key")
    print("🌐 API will be available at: http://localhost:8000")
    print("📖 Documentation at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
