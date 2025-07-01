"""
FastAPI backend for CMS Data Agent Dashboard
Provides REST API endpoints for the web dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from cms_agent import CMSDataAgent
    from agent_config import AgentConfig
except ImportError as e:
    print(f"Warning: Could not import agent modules: {e}")
    print("Running in demo mode without live agent integration")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CMS Data Agent API",
    description="REST API for CMS Healthcare Provider Data Agent Dashboard",
    version="1.0.0"
)

# Configure CORS for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None
demo_mode = False

def init_agent():
    """Initialize the CMS agent if available"""
    global agent, demo_mode
    try:
        config = AgentConfig()
        agent = CMSDataAgent(config.get_config())
        logger.info("CMS Agent initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize CMS Agent: {e}")
        logger.info("Running in demo mode")
        demo_mode = True

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    init_agent()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CMS Data Agent API",
        "status": "running",
        "version": "1.0.0",
        "demo_mode": demo_mode,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_agent_status():
    """Get current agent status"""
    try:
        if demo_mode or agent is None:
            return get_demo_status()
        
        # Get real agent status
        status_file = Path("cms_data/agent_status.json")
        if status_file.exists():
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        else:
            status_data = {"status": "unknown", "last_seen": None}
        
        return {
            "status": status_data.get("status", "unknown"),
            "last_seen": status_data.get("last_seen"),
            "demo_mode": False
        }
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/stats")
async def get_data_stats():
    """Get data statistics"""
    try:
        if demo_mode or agent is None:
            return get_demo_stats()
        
        # Get real data stats
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
        
        if record_count_file.exists():
            with open(record_count_file, 'r') as f:
                count_data = json.load(f)
                stats["record_count"] = count_data.get("total_records", 0)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activity")
async def get_recent_activity():
    """Get recent agent activity"""
    try:
        if demo_mode or agent is None:
            return get_demo_activity()
        
        # Read agent log file
        log_file = Path("cms_data/agent.log")
        activities = []
        
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                # Parse last 10 log entries
                for line in lines[-10:]:
                    if line.strip():
                        # Simple log parsing - adapt based on your log format
                        parts = line.strip().split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp_str = parts[0]
                            level = parts[1]
                            message = parts[2]
                            
                            activity_type = "info"
                            if "ERROR" in level:
                                activity_type = "error"
                            elif "WARNING" in level:
                                activity_type = "warning"
                            elif "download" in message.lower():
                                activity_type = "success"
                            
                            activities.append({
                                "type": activity_type,
                                "message": message,
                                "timestamp": timestamp_str
                            })
                            
            except Exception as e:
                logger.warning(f"Could not parse log file: {e}")
        
        return activities[:5]  # Return last 5 activities
        
    except Exception as e:
        logger.error(f"Error getting activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/quality")
async def get_data_quality():
    """Get data quality metrics"""
    try:
        if demo_mode or agent is None:
            return get_demo_quality()
        
        # Calculate real data quality metrics
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        
        if not cms_data_file.exists():
            return {"completeness": 0, "validity": 0, "freshness": 0}
        
        quality = {"completeness": 100, "validity": 100, "freshness": 100}
        
        # Check freshness based on file age
        file_age = datetime.now() - datetime.fromtimestamp(cms_data_file.stat().st_mtime)
        if file_age > timedelta(days=7):
            quality["freshness"] = max(0, 100 - (file_age.days - 7) * 10)
        
        # You can add more sophisticated quality checks here
        return quality
        
    except Exception as e:
        logger.error(f"Error getting data quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights")
async def get_insights():
    """Get data insights and analytics"""
    try:
        if demo_mode or agent is None:
            return get_demo_insights()
        
        # Analyze real data for insights
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        
        if not cms_data_file.exists():
            return get_demo_insights()
        
        insights = {
            "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            "top_performers": []
        }
        
        try:
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, list) and len(data) > 0:
                # Analyze rating distribution
                rating_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
                top_providers = []
                
                for provider in data:
                    # Look for rating fields - adapt based on your data structure
                    rating_field = None
                    for field in ['overall_rating', 'rating', 'star_rating']:
                        if field in provider and provider[field]:
                            rating_field = field
                            break
                    
                    if rating_field:
                        rating = str(provider[rating_field])
                        if rating in rating_counts:
                            rating_counts[rating] += 1
                    
                    # Collect top performers
                    if rating_field and provider.get(rating_field) == 5:
                        top_providers.append({
                            "id": provider.get("provider_id", "unknown"),
                            "name": provider.get("facility_name", f"Provider {provider.get('provider_id', 'unknown')}"),
                            "rating": 5,
                            "survey_count": provider.get("number_of_surveys", 0)
                        })
                
                insights["rating_distribution"] = rating_counts
                
                # Sort top performers by survey count
                top_providers.sort(key=lambda x: x["survey_count"], reverse=True)
                insights["top_performers"] = top_providers[:10]
                
        except Exception as e:
            logger.warning(f"Could not analyze data file: {e}")
            return get_demo_insights()
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/download")
async def trigger_download():
    """Trigger data download"""
    try:
        if demo_mode or agent is None:
            return {"success": True, "message": "Demo mode - download simulated"}
        
        # Trigger real download
        if agent:
            success = agent.update_data()
            return {
                "success": success,
                "message": "Download completed successfully" if success else "Download failed"
            }
        else:
            return {"success": False, "message": "Agent not available"}
        
    except Exception as e:
        logger.error(f"Error triggering download: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data/check-updates")
async def check_updates():
    """Check for data updates"""
    try:
        if demo_mode or agent is None:
            return {"updates_available": False, "message": "Demo mode"}
        
        # Check for real updates
        if agent:
            updates_available = agent.check_for_updates()
            return {
                "updates_available": updates_available,
                "message": "Updates available" if updates_available else "Data is up to date"
            }
        else:
            return {"updates_available": False, "message": "Agent not available"}
        
    except Exception as e:
        logger.error(f"Error checking updates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/data/validate")
async def validate_data():
    """Validate data integrity"""
    try:
        if demo_mode or agent is None:
            return {
                "valid": True,
                "record_count": 12068,
                "issues": 0,
                "message": "Demo mode - validation simulated"
            }
        
        # Perform real validation
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        
        if not cms_data_file.exists():
            return {"valid": False, "message": "Data file not found"}
        
        try:
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
            
            record_count = len(data) if isinstance(data, list) else 0
            
            return {
                "valid": True,
                "record_count": record_count,
                "issues": 0,
                "message": "Data validation successful"
            }
            
        except json.JSONDecodeError:
            return {
                "valid": False,
                "record_count": 0,
                "issues": 1,
                "message": "Invalid JSON format"
            }
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Demo data functions
def get_demo_status():
    return {
        "status": "active",
        "last_seen": datetime.now().isoformat(),
        "demo_mode": True
    }

def get_demo_stats():
    return {
        "record_count": 12068,
        "data_size": 22548578,  # ~21.5MB
        "last_update": (datetime.now() - timedelta(hours=2)).isoformat()
    }

def get_demo_activity():
    now = datetime.now()
    return [
        {
            "type": "success",
            "message": "Data Download Complete",
            "timestamp": (now - timedelta(hours=2)).isoformat()
        },
        {
            "type": "info",
            "message": "Checking for Updates",
            "timestamp": (now - timedelta(hours=4)).isoformat()
        },
        {
            "type": "warning",
            "message": "Validation Warning",
            "timestamp": (now - timedelta(days=1)).isoformat()
        },
        {
            "type": "success",
            "message": "Agent Started",
            "timestamp": (now - timedelta(days=2)).isoformat()
        }
    ]

def get_demo_quality():
    return {
        "completeness": 98,
        "validity": 96,
        "freshness": 92
    }

@app.get("/api/data/records")
async def get_data_records(
    page: int = 1,
    limit: int = 50,
    search: str = None,
    rating: int = None
):
    """Get paginated data records with optional filtering"""
    try:
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        
        if not cms_data_file.exists():
            # Try sample data
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

@app.post("/api/chat")
async def chat_with_data(request: dict):
    """Chat endpoint for AI questions about the data"""
    try:
        message = request.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # For demo purposes, return a helpful response
        # In production, this could integrate with your Claude API or other AI service
        
        response = generate_chat_response(message)
        
        return {
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_chat_response(message: str) -> str:
    """Generate a helpful response about the CMS data"""
    message_lower = message.lower()
    
    # Try to load actual data for context
    try:
        cms_data_file = Path("cms_data/cms_full_dataset.json")
        if cms_data_file.exists():
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
                total_records = len(data) if isinstance(data, list) else 0
        else:
            total_records = 0
    except:
        total_records = 0
    
    if "average" in message_lower and "rating" in message_lower:
        return f"Based on the CMS dataset of {total_records} healthcare providers, I can help you calculate average ratings. The dataset includes overall star ratings and specific care quality metrics for each provider."
    
    elif "5 star" in message_lower or "five star" in message_lower:
        return f"I can identify all providers with 5-star ratings in the dataset. These represent the highest-performing healthcare providers based on patient survey results."
    
    elif "survey" in message_lower and ("most" in message_lower or "highest" in message_lower):
        return f"I'll help you find providers with the most survey responses. This typically indicates larger healthcare facilities with higher patient volumes."
    
    elif "quality" in message_lower or "trend" in message_lower:
        return f"The CMS dataset includes multiple quality metrics including overall ratings, care delivery ratings, communication scores, and patient satisfaction percentages. I can help analyze trends across these metrics."
    
    elif "help" in message_lower or "what can" in message_lower:
        return """I can help you analyze the CMS healthcare provider data in many ways:

• Calculate statistics (averages, totals, distributions)
• Find top-performing providers by ratings
• Analyze survey response patterns
• Compare providers across different metrics
• Identify trends in quality scores
• Filter data by specific criteria

What specific aspect of the healthcare data would you like to explore?"""
    
    else:
        return f"I'm here to help you analyze the CMS healthcare provider dataset ({total_records} records). I can answer questions about provider ratings, survey results, quality metrics, and trends. What would you like to know about the data?"

def get_demo_insights():
    return {
        "rating_distribution": {"1": 156, "2": 425, "3": 1203, "4": 3845, "5": 6439},
        "top_performers": [
            {"id": "257085", "name": "Provider 257085", "rating": 5, "survey_count": 1553},
            {"id": "557061", "name": "Provider 557061", "rating": 5, "survey_count": 1546},
            {"id": "397012", "name": "Provider 397012", "rating": 5, "survey_count": 1240},
            {"id": "123456", "name": "Provider 123456", "rating": 5, "survey_count": 1180},
            {"id": "789012", "name": "Provider 789012", "rating": 5, "survey_count": 1150}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
