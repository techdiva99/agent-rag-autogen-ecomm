#!/usr/bin/env python3
"""
CMS Data Agent

An intelligent agent module for the Agent-RAG-AutoGen project that handles
automated CMS data downloading, monitoring, and updating.
"""

import os
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from download_api_data import APIDataDownloader
from cms_config import CMS_CONFIG, get_query_params, get_filename


@dataclass
class DataUpdateStatus:
    """Status of data update operations"""
    last_check: datetime
    last_update: datetime
    current_record_count: int
    previous_record_count: int
    update_available: bool
    last_error: Optional[str] = None


class CMSDataAgent:
    """
    Intelligent agent for managing CMS data downloads and updates
    
    Features:
    - Automatic data freshness monitoring
    - Scheduled updates when new data is available
    - Error handling and retry logic
    - Integration with Agent-RAG-AutoGen workflows
    - Data validation and quality checks
    """
    
    def __init__(self, 
                 output_dir: str = "cms_data",
                 check_interval_hours: int = 24,
                 auto_update: bool = True,
                 max_retries: int = 3):
        """
        Initialize the CMS Data Agent
        
        Args:
            output_dir: Directory for storing downloaded data
            check_interval_hours: Hours between data freshness checks
            auto_update: Whether to automatically download new data
            max_retries: Maximum retry attempts for failed operations
        """
        self.output_dir = output_dir
        self.check_interval_hours = check_interval_hours
        self.auto_update = auto_update
        self.max_retries = max_retries
        
        # Initialize downloader
        self.downloader = APIDataDownloader(
            base_url=CMS_CONFIG['base_url'],
            output_dir=self.output_dir
        )
        
        # Setup logging
        self._setup_logging()
        
        # Initialize status
        self.status = self._load_status()
        
        # Setup scheduler if auto_update is enabled
        if self.auto_update:
            self._setup_scheduler()
    
    def _setup_logging(self):
        """Setup agent-specific logging"""
        log_file = os.path.join(self.output_dir, 'agent.log')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create agent logger
        self.logger = logging.getLogger('cms_agent')
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _setup_scheduler(self):
        """Setup automatic data checking schedule"""
        schedule.every(self.check_interval_hours).hours.do(self._scheduled_check)
        self.logger.info(f"Scheduled data checks every {self.check_interval_hours} hours")
    
    def _load_status(self) -> DataUpdateStatus:
        """Load previous status or create new one"""
        status_file = os.path.join(self.output_dir, 'agent_status.json')
        
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                return DataUpdateStatus(
                    last_check=datetime.fromisoformat(data['last_check']),
                    last_update=datetime.fromisoformat(data['last_update']),
                    current_record_count=data['current_record_count'],
                    previous_record_count=data['previous_record_count'],
                    update_available=data['update_available'],
                    last_error=data.get('last_error')
                )
            except Exception as e:
                self.logger.warning(f"Could not load status: {e}")
        
        # Create initial status
        return DataUpdateStatus(
            last_check=datetime.now(),
            last_update=datetime.min,
            current_record_count=0,
            previous_record_count=0,
            update_available=True
        )
    
    def _save_status(self):
        """Save current status to file"""
        status_file = os.path.join(self.output_dir, 'agent_status.json')
        
        status_data = {
            'last_check': self.status.last_check.isoformat(),
            'last_update': self.status.last_update.isoformat(),
            'current_record_count': self.status.current_record_count,
            'previous_record_count': self.status.previous_record_count,
            'update_available': self.status.update_available,
            'last_error': self.status.last_error
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    def check_for_updates(self) -> bool:
        """
        Check if new data is available
        
        Returns:
            bool: True if updates are available
        """
        self.logger.info("Checking for data updates...")
        
        try:
            # Get current record count from API
            params = get_query_params('count_records')
            success = self.downloader.download_json_data(
                'sql', 'temp_count.json', params=params
            )
            
            if not success:
                self.status.last_error = "Failed to check record count"
                self._save_status()
                return False
            
            # Read the count
            count_file = os.path.join(self.output_dir, 'temp_count.json')
            with open(count_file, 'r') as f:
                count_data = json.load(f)
            
            new_count = int(count_data[0]['expression'])
            
            # Clean up temp file
            os.remove(count_file)
            
            # Update status
            self.status.previous_record_count = self.status.current_record_count
            self.status.current_record_count = new_count
            self.status.last_check = datetime.now()
            self.status.update_available = new_count > self.status.previous_record_count
            self.status.last_error = None
            
            self._save_status()
            
            if self.status.update_available:
                self.logger.info(f"New data available: {new_count} records (was {self.status.previous_record_count})")
            else:
                self.logger.info(f"No new data: {new_count} records")
            
            return self.status.update_available
            
        except Exception as e:
            error_msg = f"Error checking for updates: {e}"
            self.logger.error(error_msg)
            self.status.last_error = error_msg
            self._save_status()
            return False
    
    def download_latest_data(self, force: bool = False) -> bool:
        """
        Download the latest dataset
        
        Args:
            force: Force download even if no updates detected
            
        Returns:
            bool: Success status
        """
        if not force and not self.status.update_available:
            self.logger.info("No updates available, skipping download")
            return True
        
        self.logger.info("Downloading latest CMS data...")
        
        try:
            # Download full dataset
            params = get_query_params('all_data')
            filename = get_filename('all_data')
            
            success = self.downloader.download_json_data('sql', filename, params=params)
            
            if success:
                self.status.last_update = datetime.now()
                self.status.update_available = False
                self.status.last_error = None
                self._save_status()
                
                self.logger.info(f"Successfully downloaded {self.status.current_record_count} records")
                return True
            else:
                error_msg = "Failed to download data"
                self.logger.error(error_msg)
                self.status.last_error = error_msg
                self._save_status()
                return False
                
        except Exception as e:
            error_msg = f"Error downloading data: {e}"
            self.logger.error(error_msg)
            self.status.last_error = error_msg
            self._save_status()
            return False
    
    def get_latest_data(self, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """
        Get the latest data, downloading if necessary
        
        Args:
            max_age_hours: Maximum age of data before forcing update
            
        Returns:
            List of data records or None if unavailable
        """
        data_file = os.path.join(self.output_dir, get_filename('all_data'))
        
        # Check if we need to update data
        needs_update = False
        
        if not os.path.exists(data_file):
            needs_update = True
            self.logger.info("Data file not found, will download")
        else:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(data_file))
            if file_age > timedelta(hours=max_age_hours):
                needs_update = True
                self.logger.info(f"Data file is {file_age} old, checking for updates")
        
        # Update if needed
        if needs_update:
            if self.check_for_updates() or not os.path.exists(data_file):
                if not self.download_latest_data():
                    return None
        
        # Load and return data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data)} records from local file")
            return data
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return None
    
    def _scheduled_check(self):
        """Scheduled check for updates"""
        self.logger.info("Running scheduled data check...")
        
        if self.check_for_updates() and self.auto_update:
            self.download_latest_data()
    
    def run_scheduler(self):
        """Run the scheduler (blocking call)"""
        self.logger.info("Starting CMS Data Agent scheduler...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'last_check': self.status.last_check.isoformat(),
            'last_update': self.status.last_update.isoformat(),
            'current_record_count': self.status.current_record_count,
            'previous_record_count': self.status.previous_record_count,
            'update_available': self.status.update_available,
            'last_error': self.status.last_error,
            'data_age_hours': (datetime.now() - self.status.last_update).total_seconds() / 3600
        }
    
    def validate_data(self) -> Dict[str, Any]:
        """
        Validate the current dataset
        
        Returns:
            Dict with validation results
        """
        data_file = os.path.join(self.output_dir, get_filename('all_data'))
        
        if not os.path.exists(data_file):
            return {'valid': False, 'error': 'Data file not found'}
        
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation
            record_count = len(data)
            has_required_fields = all(
                'cms_certification_number_ccn' in record and
                'hhcahps_survey_summary_star_rating' in record
                for record in data[:10]  # Check first 10 records
            )
            
            # Star rating validation
            ratings = [r.get('hhcahps_survey_summary_star_rating', '') for r in data if r.get('hhcahps_survey_summary_star_rating')]
            valid_ratings = all(r in ['1', '2', '3', '4', '5', ''] for r in ratings)
            
            return {
                'valid': True,
                'record_count': record_count,
                'has_required_fields': has_required_fields,
                'valid_ratings': valid_ratings,
                'unique_providers': len(set(r.get('cms_certification_number_ccn', '') for r in data)),
                'file_size_mb': os.path.getsize(data_file) / (1024 * 1024)
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}


# Agent factory function for easy integration
def create_cms_agent(**kwargs) -> CMSDataAgent:
    """Create and return a configured CMS Data Agent"""
    return CMSDataAgent(**kwargs)


# CLI interface for the agent
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CMS Data Agent")
    parser.add_argument('--check', action='store_true', help='Check for updates')
    parser.add_argument('--download', action='store_true', help='Download latest data')
    parser.add_argument('--status', action='store_true', help='Show agent status')
    parser.add_argument('--validate', action='store_true', help='Validate current data')
    parser.add_argument('--run-scheduler', action='store_true', help='Run scheduler (blocking)')
    parser.add_argument('--auto-update', action='store_true', help='Enable auto-update')
    
    args = parser.parse_args()
    
    # Create agent
    agent = create_cms_agent(auto_update=args.auto_update)
    
    if args.check:
        has_updates = agent.check_for_updates()
        print(f"Updates available: {has_updates}")
    
    elif args.download:
        success = agent.download_latest_data(force=True)
        print(f"Download successful: {success}")
    
    elif args.status:
        status = agent.get_status()
        print("Agent Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
    
    elif args.validate:
        validation = agent.validate_data()
        print("Data Validation:")
        for key, value in validation.items():
            print(f"  {key}: {value}")
    
    elif args.run_scheduler:
        agent.run_scheduler()
    
    else:
        print("CMS Data Agent - Use --help for options")
        status = agent.get_status()
        print(f"Current record count: {status['current_record_count']}")
        print(f"Data age: {status['data_age_hours']:.1f} hours")
        print(f"Updates available: {status['update_available']}")
