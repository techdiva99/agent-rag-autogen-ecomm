"""
Enhanced Dashboard API with secure API key management and rate limiting
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import time
from collections import defaultdict, deque
import hashlib
import asyncio
from functools import wraps

# For environment variables
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CMS Data Agent API",
    description="REST API for CMS Healthcare Provider Data Agent Dashboard with secure API key management",
    version="2.0.0"
)

# Security
security = HTTPBearer(auto_error=False)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

# Configuration from environment
class Config:
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    CLAUDE_MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "1024"))
    
    # Rate limiting
    RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "10"))
    RATE_LIMIT_RPH = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "100"))
    RATE_LIMIT_RPD = int(os.getenv("RATE_LIMIT_REQUESTS_PER_DAY", "500"))
    
    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    
    @property
    def has_claude_key(self):
        return self.CLAUDE_API_KEY is not None and self.CLAUDE_API_KEY.startswith("sk-ant-")

config = Config()

# Rate limiting decorator
def rate_limit(requests_per_minute: int = None, requests_per_hour: int = None, requests_per_day: int = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old entries and check limits
            limits = [
                (requests_per_minute or config.RATE_LIMIT_RPM, 60, "minute"),
                (requests_per_hour or config.RATE_LIMIT_RPH, 3600, "hour"),
                (requests_per_day or config.RATE_LIMIT_RPD, 86400, "day")
            ]
            
            for limit, window, period in limits:
                key = f"{client_ip}:{func.__name__}:{period}"
                timestamps = rate_limit_storage[key]
                
                # Remove old timestamps
                while timestamps and current_time - timestamps[0] > window:
                    timestamps.popleft()
                
                # Check if limit exceeded
                if len(timestamps) >= limit:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded: {limit} requests per {period}"
                    )
                
                # Add current timestamp
                timestamps.append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# API Key validation
async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate API key from Authorization header"""
    if not credentials:
        return None
    
    # In production, validate against your API key database
    # For now, we'll use a simple check
    token = credentials.credentials
    
    # You can implement more sophisticated validation here
    if token and len(token) > 10:
        return token
    
    return None

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting CMS Data Agent API v2.0")
    logger.info(f"Claude API available: {config.has_claude_key}")
    logger.info(f"Rate limits: {config.RATE_LIMIT_RPM}/min, {config.RATE_LIMIT_RPH}/hour, {config.RATE_LIMIT_RPD}/day")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CMS Data Agent API",
        "status": "running",
        "version": "2.0.0",
        "claude_available": config.has_claude_key,
        "rate_limits": {
            "requests_per_minute": config.RATE_LIMIT_RPM,
            "requests_per_hour": config.RATE_LIMIT_RPH,
            "requests_per_day": config.RATE_LIMIT_RPD
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/config")
async def get_client_config():
    """Get client configuration (no sensitive data)"""
    return {
        "claude_available": config.has_claude_key,
        "rate_limits": {
            "requests_per_minute": config.RATE_LIMIT_RPM,
            "requests_per_hour": config.RATE_LIMIT_RPH,
            "requests_per_day": config.RATE_LIMIT_RPD
        },
        "features": {
            "chat": config.has_claude_key,
            "data_export": True,
            "real_time_updates": True
        }
    }

@app.post("/api/chat")
@rate_limit(requests_per_minute=5, requests_per_hour=50)  # Lower limits for AI chat
async def chat_with_data(request: Request, chat_request: dict, api_key: str = Depends(get_api_key)):
    """Enhanced chat endpoint with rate limiting and API key management"""
    try:
        message = chat_request.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use server-side Claude API key if available
        if config.has_claude_key:
            response = await call_claude_api_server(message)
        elif api_key and api_key.startswith("sk-ant-"):
            # Use client-provided API key (validate it's a Claude key)
            response = await call_claude_api_with_key(message, api_key)
        else:
            # Fallback to demo response
            response = generate_demo_chat_response(message)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "source": "claude" if (config.has_claude_key or api_key) else "demo"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def call_claude_api_server(message: str) -> str:
    """Call Claude API using server-side API key"""
    import httpx
    
    data_context = await get_data_context()
    
    system_prompt = f"""You are an AI assistant helping users analyze CMS healthcare provider data.

Here's information about the dataset:
{data_context}

Please provide helpful, accurate responses about this healthcare data. Focus on:
- Data analysis and insights
- Statistical summaries  
- Trends and patterns
- Comparisons between providers
- Quality metrics interpretation

Always base your responses on the actual data characteristics described above."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": config.CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": config.CLAUDE_MODEL,
                    "max_tokens": config.CLAUDE_MAX_TOKENS,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
            else:
                logger.error(f"Claude API error: {response.status_code}")
                return generate_demo_chat_response(message)
                
    except Exception as e:
        logger.error(f"Error calling Claude API: {e}")
        return generate_demo_chat_response(message)

async def call_claude_api_with_key(message: str, api_key: str) -> str:
    """Call Claude API using client-provided API key"""
    # This is a placeholder - in production, you might want to proxy the request
    # to avoid exposing the client's API key
    return f"I received your message: '{message}'. Server-side Claude integration would process this with your provided API key."

async def get_data_context() -> str:
    """Get context about the current dataset"""
    try:
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        if cms_data_file.exists():
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
                total_records = len(data) if isinstance(data, list) else 0
                
            if total_records > 0:
                sample_record = data[0] if isinstance(data, list) else {}
                fields = list(sample_record.keys()) if sample_record else []
                
                # Calculate basic stats
                ratings = []
                for record in data[:100]:  # Sample first 100 for performance
                    if isinstance(record, dict) and 'hhcahps_survey_summary_star_rating' in record:
                        try:
                            rating = int(record['hhcahps_survey_summary_star_rating'])
                            if 1 <= rating <= 5:
                                ratings.append(rating)
                        except (ValueError, TypeError):
                            pass
                
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
                
                return f"""
Dataset Summary:
- Total records: {total_records}
- Available fields: {', '.join(fields[:10])}{'...' if len(fields) > 10 else ''}
- Average rating (sample): {avg_rating:.2f}
- Data format: Healthcare provider survey results with star ratings
"""
        
        return "No CMS data currently loaded."
        
    except Exception as e:
        logger.error(f"Error getting data context: {e}")
        return "Error accessing data context."

def generate_demo_chat_response(message: str) -> str:
    """Generate demo response when Claude API is not available"""
    message_lower = message.lower()
    
    if "average" in message_lower and "rating" in message_lower:
        return "Based on the CMS dataset, I can help you calculate average ratings. The dataset includes overall star ratings ranging from 1-5 stars for each healthcare provider."
    
    elif "5 star" in message_lower:
        return "I can identify providers with 5-star ratings. These represent the highest-performing healthcare providers based on patient survey results."
    
    elif "survey" in message_lower and "most" in message_lower:
        return "I'll help you find providers with the most survey responses, which typically indicates larger healthcare facilities."
    
    elif "api key" in message_lower:
        return "To enable full AI capabilities, your administrator can configure a Claude API key in the server environment variables, or you can provide your own API key via the Authorization header."
    
    else:
        return f"""I'm here to help analyze the CMS healthcare provider data! 

**Available with Claude API:**
- Statistical analysis and calculations
- Trend identification and insights
- Data comparisons and correlations
- Detailed explanations of healthcare metrics

**Current mode:** Demo responses (Configure CLAUDE_API_KEY environment variable for full AI capabilities)

What specific aspect of the healthcare data would you like to explore?"""

# Include all previous endpoints from dashboard_api.py
@app.get("/api/status")
async def get_agent_status():
    """Get current agent status"""
    try:
        status_file = Path("cms_data/agent_status.json")
        if status_file.exists():
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        else:
            status_data = {"status": "unknown", "last_seen": None}
        
        return {
            "status": status_data.get("status", "unknown"),
            "last_seen": status_data.get("last_seen"),
            "api_available": config.has_claude_key
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/stats")
async def get_data_stats():
    """Get data statistics"""
    try:
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        record_count_file = Path("cms_data/cms_record_count.json")
        
        stats = {
            "record_count": 0,
            "data_size": 0,
            "last_update": None
        }
        
        if cms_data_file.exists():
            stats["data_size"] = cms_data_file.stat().st_size
            stats["last_update"] = datetime.fromtimestamp(
                cms_data_file.stat().st_mtime
            ).isoformat()
            
            # Count records
            try:
                with open(cms_data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        stats["record_count"] = len(data)
            except:
                pass
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/records")
@rate_limit(requests_per_minute=20)  # Higher limit for data access
async def get_data_records(
    request: Request,
    page: int = 1,
    limit: int = 50,
    search: str = None,
    rating: int = None
):
    """Get paginated data records with optional filtering"""
    try:
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        
        if not cms_data_file.exists():
            cms_data_file = Path("cms_data/cms_sample_10_records.json")
            
        if not cms_data_file.exists():
            return {"records": [], "total": 0, "page": page, "limit": limit}
        
        with open(cms_data_file, 'r') as f:
            all_records = json.load(f)
        
        if not isinstance(all_records, list):
            return {"records": [], "total": 0, "page": page, "limit": limit}
        
        # Apply filters
        filtered_records = all_records
        
        if search:
            search_lower = search.lower()
            filtered_records = [
                record for record in filtered_records
                if any(
                    search_lower in str(value).lower()
                    for value in record.values()
                    if value is not None
                )
            ]
        
        if rating is not None:
            rating_str = str(rating)
            filtered_records = [
                record for record in filtered_records
                if record.get('hhcahps_survey_summary_star_rating') == rating_str
            ]
        
        # Pagination
        total = len(filtered_records)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_records = filtered_records[start_idx:end_idx]
        
        return {
            "records": page_records,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting data records: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
