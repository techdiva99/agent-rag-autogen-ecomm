#!/usr/bin/env python3
"""
Generate static dashboard data files for GitHub Pages deployment
This script reads the current agent status and data, then generates
JSON files that the static dashboard can use.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_data_directory():
    """Create web/data directory if it doesn't exist"""
    data_dir = Path("web/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def generate_status_data():
    """Generate agent status data"""
    status_file = Path("cms_data/agent_status.json")
    
    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            status_data = {}
    else:
        status_data = {}
    
    # Generate status with current timestamp
    status = {
        "status": status_data.get("status", "unknown"),
        "last_seen": status_data.get("last_seen", datetime.now().isoformat()),
        "generated_at": datetime.now().isoformat(),
        "demo_mode": False
    }
    
    return status

def generate_stats_data():
    """Generate data statistics"""
    cms_data_file = Path("cms_data/cms_full_dataset.json")
    record_count_file = Path("cms_data/cms_record_count.json")
    
    stats = {
        "record_count": 0,
        "data_size": 0,
        "last_update": None,
        "generated_at": datetime.now().isoformat()
    }
    
    if cms_data_file.exists():
        stats["data_size"] = cms_data_file.stat().st_size
        stats["last_update"] = datetime.fromtimestamp(
            cms_data_file.stat().st_mtime
        ).isoformat()
        
        # Try to count records directly from the file
        try:
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    stats["record_count"] = len(data)
                elif isinstance(data, dict) and 'records' in data:
                    stats["record_count"] = len(data['records'])
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    if record_count_file.exists():
        try:
            with open(record_count_file, 'r') as f:
                count_data = json.load(f)
                if isinstance(count_data, dict):
                    stats["record_count"] = count_data.get("total_records", stats["record_count"])
                elif isinstance(count_data, int):
                    stats["record_count"] = count_data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    return stats

def generate_activity_data():
    """Generate recent activity data from logs"""
    log_file = Path("cms_data/agent.log")
    activities = []
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Parse last 10 log entries
            for line in lines[-10:]:
                if line.strip():
                    # Simple log parsing
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
                        elif "download" in message.lower() and "complete" in message.lower():
                            activity_type = "success"
                        elif "download" in message.lower():
                            activity_type = "info"
                        
                        activities.append({
                            "type": activity_type,
                            "message": message,
                            "timestamp": timestamp_str
                        })
        except Exception as e:
            logger.warning(f"Could not parse log file: {e}")
    
    # Add generation timestamp
    result = {
        "activities": activities[-5:],  # Last 5 activities
        "generated_at": datetime.now().isoformat()
    }
    
    return result

def generate_quality_data():
    """Generate data quality metrics"""
    cms_data_file = Path("cms_data/cms_full_dataset.json")
    
    quality = {
        "completeness": 100,
        "validity": 100,
        "freshness": 100,
        "generated_at": datetime.now().isoformat()
    }
    
    if cms_data_file.exists():
        # Check freshness based on file age
        file_age = datetime.now() - datetime.fromtimestamp(cms_data_file.stat().st_mtime)
        if file_age > timedelta(days=7):
            quality["freshness"] = max(0, 100 - (file_age.days - 7) * 10)
        
        # Basic completeness check
        try:
            with open(cms_data_file, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                # Sample some records for completeness
                sample_size = min(100, len(data))
                complete_records = 0
                
                for i in range(0, len(data), len(data) // sample_size):
                    record = data[i]
                # Check if key fields are present
                if isinstance(record, dict):
                    key_fields = ['cms_certification_number_ccn']
                    if all(field in record and record[field] for field in key_fields):
                        complete_records += 1
                
                quality["completeness"] = (complete_records / sample_size) * 100
                
        except Exception as e:
            logger.warning(f"Could not analyze data for quality: {e}")
            quality["validity"] = 80  # Reduced if we can't parse
    else:
        # No data file
        quality["completeness"] = 0
        quality["validity"] = 0
        quality["freshness"] = 0
    
    return quality

def generate_insights_data():
    """Generate insights and analytics data"""
    cms_data_file = Path("cms_data/cms_full_dataset.json")
    
    # Default insights
    insights = {
        "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        "top_performers": [],
        "generated_at": datetime.now().isoformat()
    }
    
    if not cms_data_file.exists():
        # Use demo data if no real data available
        insights["rating_distribution"] = {"1": 156, "2": 425, "3": 1203, "4": 3845, "5": 6439}
        insights["top_performers"] = [
            {"id": "257085", "name": "Provider 257085", "rating": 5, "survey_count": 1553},
            {"id": "557061", "name": "Provider 557061", "rating": 5, "survey_count": 1546},
            {"id": "397012", "name": "Provider 397012", "rating": 5, "survey_count": 1240}
        ]
        return insights
    
    try:
        with open(cms_data_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            # Analyze rating distribution
            rating_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
            top_providers = []
            
            for provider in data:
                if not isinstance(provider, dict):
                    continue
                    
                # Look for rating fields - adapt based on your data structure
                rating_field = None
                for field in ['hhcahps_survey_summary_star_rating', 'overall_rating', 'rating', 'star_rating']:
                    if field in provider and provider[field]:
                        rating_field = field
                        break
                
                if rating_field:
                    try:
                        rating = int(float(provider[rating_field]))
                        if 1 <= rating <= 5:
                            rating_counts[str(rating)] += 1
                    except (ValueError, TypeError):
                        pass
                
                # Collect potential top performers
                if rating_field and provider.get(rating_field):
                    try:
                        rating_val = float(provider[rating_field])
                        if rating_val >= 4.5:  # High rating threshold
                            provider_id = provider.get("cms_certification_number_ccn", "unknown")
                            survey_count = 0
                            
                            # Try to get survey count from various fields
                            for count_field in ['number_of_completed_surveys', 'survey_count', 'surveys']:
                                if count_field in provider and provider[count_field]:
                                    try:
                                        survey_count = int(provider[count_field])
                                        break
                                    except (ValueError, TypeError):
                                        pass
                            
                            top_providers.append({
                                "id": str(provider_id),
                                "name": f"Provider {provider_id}",
                                "rating": rating_val,
                                "survey_count": survey_count
                            })
                    except (ValueError, TypeError):
                        pass
            
            insights["rating_distribution"] = rating_counts
            
            # Sort top performers by survey count and rating
            top_providers.sort(key=lambda x: (x["rating"], x["survey_count"]), reverse=True)
            insights["top_performers"] = top_providers[:10]
            
            logger.info(f"Generated insights: {len(top_providers)} top performers, rating distribution: {rating_counts}")
            
    except Exception as e:
        logger.warning(f"Could not analyze data file for insights: {e}")
        # Keep default/demo data
    
    return insights

def main():
    """Main function to generate all dashboard data"""
    logger.info("Starting dashboard data generation...")
    
    # Ensure output directory exists
    data_dir = ensure_data_directory()
    
    # Generate all data files
    try:
        # Agent status
        status_data = generate_status_data()
        with open(data_dir / "status.json", "w") as f:
            json.dump(status_data, f, indent=2)
        logger.info("Generated status.json")
        
        # Data statistics
        stats_data = generate_stats_data()
        with open(data_dir / "stats.json", "w") as f:
            json.dump(stats_data, f, indent=2)
        logger.info("Generated stats.json")
        
        # Recent activity
        activity_data = generate_activity_data()
        with open(data_dir / "activity.json", "w") as f:
            json.dump(activity_data, f, indent=2)
        logger.info("Generated activity.json")
        
        # Data quality
        quality_data = generate_quality_data()
        with open(data_dir / "quality.json", "w") as f:
            json.dump(quality_data, f, indent=2)
        logger.info("Generated quality.json")
        
        # Insights and analytics
        insights_data = generate_insights_data()
        with open(data_dir / "insights.json", "w") as f:
            json.dump(insights_data, f, indent=2)
        logger.info("Generated insights.json")
        
        # Create a manifest file
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "files": ["status.json", "stats.json", "activity.json", "quality.json", "insights.json"],
            "generator_version": "1.0.0"
        }
        with open(data_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        logger.info("Generated manifest.json")
        
        logger.info("Dashboard data generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error generating dashboard data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
