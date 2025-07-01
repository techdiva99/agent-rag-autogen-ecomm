#!/usr/bin/env python3
"""
Agent-RAG-AutoGen Example Usage

Example demonstrating how to use the CMS Data Agent as a module
in the Agent-RAG-AutoGen project for automated data management.
"""

import asyncio
import time
from datetime import datetime
from cms_agent import create_cms_agent
from agent_integration import (
    RAGDataManager, 
    AutoGenCMSAgent, 
    CMSDataService,
    create_rag_integration
)
from agent_config import get_development_config, get_production_config


async def example_basic_agent_usage():
    """Basic agent usage example"""
    print("🤖 Basic CMS Data Agent Example")
    print("=" * 50)
    
    # Create agent with custom configuration
    agent = create_cms_agent(
        output_dir="example_data",
        check_interval_hours=1,
        auto_update=True
    )
    
    # Check current status
    status = agent.get_status()
    print(f"📊 Current Status:")
    print(f"   Records: {status['current_record_count']}")
    print(f"   Data Age: {status['data_age_hours']:.1f} hours")
    print(f"   Updates Available: {status['update_available']}")
    
    # Check for updates
    print(f"\n🔍 Checking for updates...")
    has_updates = agent.check_for_updates()
    print(f"   Updates available: {has_updates}")
    
    # Get latest data
    print(f"\n📥 Getting latest data...")
    data = agent.get_latest_data(max_age_hours=24)
    if data:
        print(f"   ✅ Loaded {len(data)} records")
        # Show sample record
        sample = data[0]
        print(f"   Sample provider: {sample.get('cms_certification_number_ccn')}")
        print(f"   Rating: {sample.get('hhcahps_survey_summary_star_rating')}/5")
    else:
        print(f"   ❌ No data available")
    
    return agent


async def example_rag_integration():
    """RAG integration example"""
    print("\n🧠 RAG Integration Example")
    print("=" * 50)
    
    # Create RAG manager
    rag_manager = RAGDataManager()
    
    # Ensure fresh data
    fresh = await rag_manager.ensure_fresh_data(max_age_hours=24)
    print(f"📊 Fresh data available: {fresh}")
    
    # Get high-rated providers for context
    print(f"\n⭐ Getting high-rated providers...")
    high_rated = rag_manager.get_provider_context(
        rating_threshold=5,
        limit=3
    )
    
    if high_rated:
        context = rag_manager.format_for_llm(high_rated)
        print(f"   Found {len(high_rated)} 5-star providers")
        print(f"   Context preview: {context[:200]}...")
    
    # Get statistics for LLM
    print(f"\n📈 Getting statistics...")
    stats = rag_manager.get_statistics_context()
    print(f"   Stats preview: {stats[:200]}...")
    
    return rag_manager


async def example_autogen_agent():
    """AutoGen agent example"""
    print("\n🔄 AutoGen Agent Example")
    print("=" * 50)
    
    # Create AutoGen-compatible agent
    autogen_agent = AutoGenCMSAgent(name="healthcare_data_agent")
    
    # Simulate different types of requests
    requests = [
        "What's the current data status?",
        "Show me high rated providers",
        "Get statistics about the dataset",
        "Find provider 017000",
        "Update the data"
    ]
    
    for request in requests:
        print(f"\n📨 Request: {request}")
        response = await autogen_agent.handle_data_request(request)
        print(f"🤖 Response: {response[:150]}{'...' if len(response) > 150 else ''}")
    
    return autogen_agent


async def example_background_service():
    """Background service example"""
    print("\n⚙️  Background Service Example")
    print("=" * 50)
    
    # Create background service
    service = CMSDataService(check_interval_hours=0.1)  # Check every 6 minutes for demo
    
    print(f"🚀 Starting background service...")
    print(f"   Check interval: {service.check_interval_hours} hours")
    print(f"   Auto-update enabled: {service.agent.auto_update}")
    
    # Run for a short time (in real usage, this would run indefinitely)
    print(f"\n⏰ Running service for 30 seconds...")
    
    # Start service in background
    service_task = asyncio.create_task(service.start())
    
    # Let it run for a short time
    await asyncio.sleep(30)
    
    # Stop service
    service.stop()
    service_task.cancel()
    
    print(f"⏹️  Service stopped")
    
    return service


def example_configuration():
    """Configuration example"""
    print("\n⚙️  Configuration Example")
    print("=" * 50)
    
    # Get different environment configs
    dev_config = get_development_config()
    prod_config = get_production_config()
    
    print(f"🔧 Development Config:")
    print(f"   Output Dir: {dev_config.output_dir}")
    print(f"   Check Interval: {dev_config.check_interval_hours}h")
    print(f"   Auto Update: {dev_config.auto_update}")
    print(f"   Log Level: {dev_config.log_level}")
    
    print(f"\n🏭 Production Config:")
    print(f"   Output Dir: {prod_config.output_dir}")
    print(f"   Check Interval: {prod_config.check_interval_hours}h")
    print(f"   Metrics: {prod_config.enable_metrics}")
    print(f"   Notifications: {prod_config.enable_notifications}")
    
    # Save configs
    dev_config.save_config("example_dev_config.json")
    prod_config.save_config("example_prod_config.json")
    print(f"\n💾 Configs saved to JSON files")


async def example_data_analysis():
    """Data analysis example"""
    print("\n📊 Data Analysis Example")
    print("=" * 50)
    
    # Get agent and data
    agent = create_cms_agent()
    data = agent.get_latest_data()
    
    if not data:
        print("❌ No data available for analysis")
        return
    
    print(f"📈 Analyzing {len(data)} provider records...")
    
    # Rating distribution
    ratings = [
        int(r.get('hhcahps_survey_summary_star_rating', '0'))
        for r in data 
        if r.get('hhcahps_survey_summary_star_rating', '').isdigit()
    ]
    
    if ratings:
        from collections import Counter
        rating_dist = Counter(ratings)
        print(f"\n⭐ Rating Distribution:")
        for rating in sorted(rating_dist.keys()):
            count = rating_dist[rating]
            pct = (count / len(ratings)) * 100
            print(f"   {rating} stars: {count:,} providers ({pct:.1f}%)")
    
    # Response rate analysis
    response_rates = [
        int(r.get('survey_response_rate', '0'))
        for r in data 
        if r.get('survey_response_rate', '').isdigit()
    ]
    
    if response_rates:
        avg_rate = sum(response_rates) / len(response_rates)
        min_rate = min(response_rates)
        max_rate = max(response_rates)
        print(f"\n📋 Survey Response Rates:")
        print(f"   Average: {avg_rate:.1f}%")
        print(f"   Range: {min_rate}% - {max_rate}%")
    
    # Top providers
    five_star = [
        r for r in data 
        if r.get('hhcahps_survey_summary_star_rating') == '5'
    ]
    
    print(f"\n🏆 Top Performers:")
    print(f"   5-star providers: {len(five_star)}")
    
    if five_star:
        # Sort by survey count
        top_by_surveys = sorted(
            five_star,
            key=lambda x: int(x.get('number_of_completed_surveys', '0')) if x.get('number_of_completed_surveys', '').isdigit() else 0,
            reverse=True
        )[:5]
        
        print(f"   Top 5 by survey volume:")
        for i, provider in enumerate(top_by_surveys, 1):
            ccn = provider.get('cms_certification_number_ccn', 'Unknown')
            surveys = provider.get('number_of_completed_surveys', 'Unknown')
            print(f"     {i}. Provider {ccn}: {surveys} surveys")


async def main():
    """Run all examples"""
    print("🎯 CMS Data Agent - Agent-RAG-AutoGen Integration Examples")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run examples
        await example_basic_agent_usage()
        await example_rag_integration()
        await example_autogen_agent()
        example_configuration()
        await example_data_analysis()
        
        # Note: Skipping background service example to avoid long runtime
        print("\n⚠️  Skipping background service example (would run continuously)")
        
        print("\n" + "=" * 80)
        print("🎉 All examples completed successfully!")
        print("\n💡 Integration Tips:")
        print("   1. Use create_cms_agent() to get a configured agent")
        print("   2. Use RAGDataManager for LLM context preparation")
        print("   3. Use AutoGenCMSAgent for AutoGen framework integration")
        print("   4. Use CMSDataService for background monitoring")
        print("   5. Configure with environment-specific settings")
        
        print("\n🚀 Ready for Agent-RAG-AutoGen integration!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())
