#!/usr/bin/env python3
"""
Agent-RAG-AutoGen Integration Module

This module provides integration between the CMS Data Agent and the 
Agent-RAG-AutoGen framework for seamless data management in AI workflows.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from cms_agent import CMSDataAgent, create_cms_agent


class RAGDataManager:
    """
    Data manager for RAG (Retrieval-Augmented Generation) workflows
    Integrates CMS data with vector databases and AI agents
    """
    
    def __init__(self, 
                 cms_agent: CMSDataAgent = None,
                 vector_db_config: Dict = None,
                 embedding_model: str = "text-embedding-ada-002"):
        """
        Initialize RAG Data Manager
        
        Args:
            cms_agent: CMS Data Agent instance
            vector_db_config: Vector database configuration
            embedding_model: Embedding model for vectorization
        """
        self.cms_agent = cms_agent or create_cms_agent()
        self.vector_db_config = vector_db_config or {}
        self.embedding_model = embedding_model
        
    async def ensure_fresh_data(self, max_age_hours: int = 24) -> bool:
        """
        Ensure we have fresh CMS data for RAG operations
        
        Args:
            max_age_hours: Maximum acceptable data age
            
        Returns:
            bool: True if fresh data is available
        """
        try:
            data = self.cms_agent.get_latest_data(max_age_hours=max_age_hours)
            return data is not None
        except Exception as e:
            print(f"Error ensuring fresh data: {e}")
            return False
    
    def get_provider_context(self, 
                           provider_id: str = None,
                           rating_threshold: int = 4,
                           limit: int = 100) -> List[Dict]:
        """
        Get provider data for RAG context
        
        Args:
            provider_id: Specific provider CCN
            rating_threshold: Minimum star rating
            limit: Maximum number of providers
            
        Returns:
            List of provider records for context
        """
        data = self.cms_agent.get_latest_data()
        if not data:
            return []
        
        # Filter data based on criteria
        filtered_data = data
        
        if provider_id:
            filtered_data = [
                r for r in filtered_data 
                if r.get('cms_certification_number_ccn') == provider_id
            ]
        
        if rating_threshold:
            filtered_data = [
                r for r in filtered_data 
                if (r.get('hhcahps_survey_summary_star_rating', '0').isdigit() and
                    int(r.get('hhcahps_survey_summary_star_rating', '0')) >= rating_threshold)
            ]
        
        return filtered_data[:limit]
    
    def format_for_llm(self, providers: List[Dict]) -> str:
        """
        Format provider data for LLM consumption
        
        Args:
            providers: List of provider records
            
        Returns:
            Formatted string for LLM context
        """
        if not providers:
            return "No provider data available."
        
        formatted_text = "Healthcare Provider Information:\n\n"
        
        for i, provider in enumerate(providers, 1):
            ccn = provider.get('cms_certification_number_ccn', 'Unknown')
            rating = provider.get('hhcahps_survey_summary_star_rating', 'Not rated')
            surveys = provider.get('number_of_completed_surveys', 'Unknown')
            response_rate = provider.get('survey_response_rate', 'Unknown')
            
            formatted_text += f"{i}. Provider {ccn}:\n"
            formatted_text += f"   - Overall Rating: {rating}/5 stars\n"
            formatted_text += f"   - Survey Responses: {surveys} completed\n"
            formatted_text += f"   - Response Rate: {response_rate}%\n"
            
            # Add specific care ratings
            prof_care = provider.get('star_rating_for_health_team_gave_care_in_a_professional_way', 'N/A')
            communication = provider.get('star_rating_for_health_team_communicated_well_with_them', 'N/A')
            
            formatted_text += f"   - Professional Care: {prof_care}/5 stars\n"
            formatted_text += f"   - Communication: {communication}/5 stars\n\n"
        
        return formatted_text
    
    def get_statistics_context(self) -> str:
        """
        Get statistical summary for LLM context
        
        Returns:
            Statistical summary string
        """
        data = self.cms_agent.get_latest_data()
        if not data:
            return "No statistical data available."
        
        # Calculate statistics
        total_providers = len(data)
        
        # Rating distribution
        ratings = [
            int(r.get('hhcahps_survey_summary_star_rating', '0'))
            for r in data 
            if r.get('hhcahps_survey_summary_star_rating', '').isdigit()
        ]
        
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Response rates
        response_rates = [
            int(r.get('survey_response_rate', '0'))
            for r in data 
            if r.get('survey_response_rate', '').isdigit()
        ]
        
        avg_response_rate = sum(response_rates) / len(response_rates) if response_rates else 0
        
        context = f"""Healthcare Provider Statistics:
- Total Providers: {total_providers:,}
- Average Rating: {avg_rating:.1f}/5 stars
- Average Survey Response Rate: {avg_response_rate:.1f}%
- Data Last Updated: {self.cms_agent.status.last_update.strftime('%Y-%m-%d %H:%M')}

Rating Distribution:
"""
        
        if ratings:
            from collections import Counter
            rating_dist = Counter(ratings)
            for rating in sorted(rating_dist.keys()):
                count = rating_dist[rating]
                percentage = (count / len(ratings)) * 100
                context += f"- {rating} stars: {count} providers ({percentage:.1f}%)\n"
        
        return context


class AutoGenCMSAgent:
    """
    AutoGen-compatible agent wrapper for CMS data operations
    """
    
    def __init__(self, name: str = "cms_data_agent"):
        self.name = name
        self.cms_agent = create_cms_agent()
        self.rag_manager = RAGDataManager(self.cms_agent)
        
    async def handle_data_request(self, message: str) -> str:
        """
        Handle data requests from other AutoGen agents
        
        Args:
            message: Request message
            
        Returns:
            Response with requested data
        """
        message_lower = message.lower()
        
        if "update" in message_lower or "refresh" in message_lower:
            success = self.cms_agent.download_latest_data()
            return f"Data update {'successful' if success else 'failed'}"
        
        elif "status" in message_lower:
            status = self.cms_agent.get_status()
            return f"CMS Data Status: {status['current_record_count']} records, " \
                   f"last updated {status['data_age_hours']:.1f} hours ago"
        
        elif "provider" in message_lower:
            # Extract provider ID if mentioned
            import re
            provider_match = re.search(r'\b\d{6}\b', message)
            provider_id = provider_match.group() if provider_match else None
            
            providers = self.rag_manager.get_provider_context(
                provider_id=provider_id,
                limit=5
            )
            return self.rag_manager.format_for_llm(providers)
        
        elif "statistics" in message_lower or "stats" in message_lower:
            return self.rag_manager.get_statistics_context()
        
        elif "high rated" in message_lower or "best" in message_lower:
            providers = self.rag_manager.get_provider_context(
                rating_threshold=5,
                limit=10
            )
            return self.rag_manager.format_for_llm(providers)
        
        else:
            return """I can help with CMS healthcare provider data. Available commands:
- 'update data' - Refresh the dataset
- 'status' - Check data status
- 'provider [ID]' - Get specific provider info
- 'statistics' - Get data summary
- 'high rated providers' - Get top-rated providers"""


# Integration functions for different RAG frameworks
def integrate_with_langchain():
    """Integration with LangChain framework"""
    try:
        from langchain.tools import BaseTool
        from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
        
        class CMSDataTool(BaseTool):
            name = "cms_data_tool"
            description = "Tool for accessing CMS healthcare provider data"
            
            def __init__(self):
                super().__init__()
                self.rag_manager = RAGDataManager()
            
            def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
                if "provider" in query.lower():
                    providers = self.rag_manager.get_provider_context(limit=5)
                    return self.rag_manager.format_for_llm(providers)
                elif "stats" in query.lower():
                    return self.rag_manager.get_statistics_context()
                else:
                    return "Available: provider data, statistics"
            
            async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
                return self._run(query)
        
        return CMSDataTool()
    
    except ImportError:
        print("LangChain not available")
        return None


def integrate_with_autogen():
    """Integration with AutoGen framework"""
    try:
        # AutoGen integration
        return AutoGenCMSAgent()
    except ImportError:
        print("AutoGen not available")
        return None


# Background service for continuous data monitoring
class CMSDataService:
    """
    Background service for continuous CMS data monitoring
    Suitable for deployment in Agent-RAG-AutoGen systems
    """
    
    def __init__(self, check_interval_hours: int = 6):
        self.check_interval_hours = check_interval_hours
        self.agent = create_cms_agent(
            auto_update=True,
            check_interval_hours=check_interval_hours
        )
        self.running = False
    
    async def start(self):
        """Start the background service"""
        self.running = True
        print(f"Starting CMS Data Service (check interval: {self.check_interval_hours}h)")
        
        while self.running:
            try:
                # Check for updates
                has_updates = self.agent.check_for_updates()
                
                if has_updates:
                    print("New CMS data detected, downloading...")
                    success = self.agent.download_latest_data()
                    if success:
                        print("✅ CMS data updated successfully")
                    else:
                        print("❌ Failed to update CMS data")
                
                # Wait for next check
                await asyncio.sleep(self.check_interval_hours * 3600)
                
            except Exception as e:
                print(f"Error in CMS data service: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def stop(self):
        """Stop the background service"""
        self.running = False
        print("Stopping CMS Data Service")


# Factory function for easy integration
def create_rag_integration(framework: str = "autogen") -> Any:
    """
    Create framework-specific integration
    
    Args:
        framework: Target framework ('autogen', 'langchain')
        
    Returns:
        Framework-specific integration object
    """
    if framework.lower() == "autogen":
        return integrate_with_autogen()
    elif framework.lower() == "langchain":
        return integrate_with_langchain()
    else:
        return RAGDataManager()


# Example usage for Agent-RAG-AutoGen
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        # Create AutoGen agent
        autogen_agent = create_rag_integration("autogen")
        
        # Example interactions
        response1 = await autogen_agent.handle_data_request("Show me high rated providers")
        print("High rated providers:", response1[:200] + "...")
        
        response2 = await autogen_agent.handle_data_request("What's the data status?")
        print("Status:", response2)
        
        # Start background service
        service = CMSDataService(check_interval_hours=1)  # Check every hour for demo
        print("Background service ready")
    
    asyncio.run(demo())
