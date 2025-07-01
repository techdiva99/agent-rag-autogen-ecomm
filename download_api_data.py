#!/usr/bin/env python3
"""
API Data Downloader Script

This script downloads data from a source API and saves it to a local folder.
Supports JSON, CSV, and other data formats with error handling and logging.
"""

import requests
import json
import csv
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time


class APIDataDownloader:
    def __init__(self, base_url: str, output_dir: str = "data"):
        """
        Initialize the API Data Downloader
        
        Args:
            base_url: Base URL of the API
            output_dir: Directory to save downloaded data
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.session = requests.Session()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.output_dir, 'download.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def set_authentication(self, auth_type: str, **kwargs):
        """
        Set authentication for API requests
        
        Args:
            auth_type: Type of authentication ('bearer', 'basic', 'api_key')
            **kwargs: Authentication parameters
        """
        if auth_type.lower() == 'bearer':
            token = kwargs.get('token')
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        elif auth_type.lower() == 'basic':
            username = kwargs.get('username')
            password = kwargs.get('password')
            self.session.auth = (username, password)
        elif auth_type.lower() == 'api_key':
            key_name = kwargs.get('key_name', 'X-API-Key')
            api_key = kwargs.get('api_key')
            self.session.headers.update({key_name: api_key})
            
    def download_json_data(self, endpoint: str, filename: str = None, params: Dict = None) -> bool:
        """
        Download JSON data from API endpoint
        
        Args:
            endpoint: API endpoint path
            filename: Output filename (optional)
            params: Query parameters (optional)
            
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            self.logger.info(f"Downloading JSON data from: {url}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{endpoint.replace('/', '_')}_{timestamp}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
                
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Successfully saved JSON data to: {filepath}")
            self.logger.info(f"Records downloaded: {len(data) if isinstance(data, list) else 'N/A'}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False
            
    def download_csv_data(self, endpoint: str, filename: str = None, params: Dict = None) -> bool:
        """
        Download CSV data from API endpoint
        
        Args:
            endpoint: API endpoint path
            filename: Output filename (optional)
            params: Query parameters (optional)
            
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            self.logger.info(f"Downloading CSV data from: {url}")
            
            response = self.session.get(url, params=params, timeout=30, stream=True)
            response.raise_for_status()
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{endpoint.replace('/', '_')}_{timestamp}.csv"
            
            # Ensure .csv extension
            if not filename.endswith('.csv'):
                filename += '.csv'
                
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            self.logger.info(f"Successfully saved CSV data to: {filepath}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False
            
    def download_paginated_data(self, endpoint: str, filename: str = None, 
                              page_param: str = 'page', limit_param: str = 'limit',
                              page_size: int = 100, max_pages: int = None) -> bool:
        """
        Download paginated data from API
        
        Args:
            endpoint: API endpoint path
            filename: Output filename (optional)
            page_param: Parameter name for page number
            limit_param: Parameter name for page size
            page_size: Number of records per page
            max_pages: Maximum number of pages to download
            
        Returns:
            bool: Success status
        """
        try:
            all_data = []
            page = 1
            
            while True:
                if max_pages and page > max_pages:
                    break
                    
                params = {page_param: page, limit_param: page_size}
                url = f"{self.base_url}/{endpoint.lstrip('/')}"
                
                self.logger.info(f"Downloading page {page} from: {url}")
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Handle different response formats
                if isinstance(data, dict):
                    if 'data' in data:
                        page_data = data['data']
                    elif 'results' in data:
                        page_data = data['results']
                    else:
                        page_data = data
                else:
                    page_data = data
                    
                if not page_data or len(page_data) == 0:
                    break
                    
                all_data.extend(page_data if isinstance(page_data, list) else [page_data])
                
                # Check if there are more pages
                if len(page_data) < page_size:
                    break
                    
                page += 1
                time.sleep(0.1)  # Be nice to the API
                
            # Save all collected data
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{endpoint.replace('/', '_')}_paginated_{timestamp}.json"
                
            if not filename.endswith('.json'):
                filename += '.json'
                
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Successfully saved paginated data to: {filepath}")
            self.logger.info(f"Total records downloaded: {len(all_data)}")
            self.logger.info(f"Total pages processed: {page - 1}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return False


def main():
    """Main function with example usage"""
    
    # Configuration - Update these values for your API
    API_BASE_URL = "https://data.cms.gov/provider-data/api/1/datastore"
    OUTPUT_DIR = "data"
    
    # Initialize downloader
    downloader = APIDataDownloader(API_BASE_URL, OUTPUT_DIR)
    
    # Example: Set authentication if needed
    # downloader.set_authentication('bearer', token='your_token_here')
    # downloader.set_authentication('api_key', api_key='your_api_key', key_name='X-API-Key')
    
    print("🚀 Starting CMS.gov API data download...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🌐 API Base URL: {API_BASE_URL}")
    print("-" * 50)
    
    # Example downloads from CMS.gov
    success_count = 0
    total_downloads = 0
    
    # Download first 10 records from the CMS dataset
    total_downloads += 1
    cms_params = {
        'query': '[SELECT * FROM a678955c-467c-5df1-a8bf-c94d22c86247][LIMIT 10]',
        'show_db_columns': ''
    }
    if downloader.download_json_data('sql', 'cms_data_sample.json', params=cms_params):
        success_count += 1
        
    # Download larger dataset (100 records)
    total_downloads += 1
    cms_params_large = {
        'query': '[SELECT * FROM a678955c-467c-5df1-a8bf-c94d22c86247][LIMIT 100]',
        'show_db_columns': ''
    }
    if downloader.download_json_data('sql', 'cms_data_100.json', params=cms_params_large):
        success_count += 1
        
    # Download all data (remove LIMIT for full dataset - be careful with large datasets!)
    total_downloads += 1
    cms_params_all = {
        'query': '[SELECT * FROM a678955c-467c-5df1-a8bf-c94d22c86247]',
        'show_db_columns': ''
    }
    print("⚠️  Downloading full dataset - this may take a while...")
    if downloader.download_json_data('sql', 'cms_data_full.json', params=cms_params_all):
        success_count += 1
    
    print("-" * 50)
    print(f"✅ Download completed: {success_count}/{total_downloads} successful")
    print(f"📊 Check the '{OUTPUT_DIR}' folder for downloaded files")
    print(f"📋 Check '{OUTPUT_DIR}/download.log' for detailed logs")


if __name__ == "__main__":
    main()
