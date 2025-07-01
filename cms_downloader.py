#!/usr/bin/env python3
"""
CMS.gov Data Downloader

Specialized script for downloading data from CMS.gov Provider Data API
"""

import os
import sys
from download_api_data import APIDataDownloader
from cms_config import CMS_CONFIG, get_query_params, get_filename, QUERIES

def download_cms_data(query_types=None, custom_queries=None):
    """
    Download data from CMS.gov API
    
    Args:
        query_types: List of predefined query types to download
        custom_queries: Dict of custom queries {filename: query_string}
    """
    
    # Initialize downloader
    downloader = APIDataDownloader(
        base_url=CMS_CONFIG['base_url'],
        output_dir=CMS_CONFIG['output_dir']
    )
    
    print("🏥 Starting CMS.gov Provider Data download...")
    print(f"📁 Output directory: {CMS_CONFIG['output_dir']}")
    print(f"🆔 Dataset ID: {CMS_CONFIG['dataset_id']}")
    print("-" * 60)
    
    success_count = 0
    total_downloads = 0
    
    # Download predefined query types
    if query_types:
        for query_type in query_types:
            if query_type not in QUERIES:
                print(f"❌ Unknown query type: {query_type}")
                continue
                
            total_downloads += 1
            print(f"📥 Downloading {query_type}...")
            
            try:
                params = get_query_params(query_type)
                filename = get_filename(query_type)
                
                if downloader.download_json_data('sql', filename, params=params):
                    success_count += 1
                    print(f"✅ Successfully downloaded: {filename}")
                else:
                    print(f"❌ Failed to download: {filename}")
                    
            except Exception as e:
                print(f"❌ Error downloading {query_type}: {e}")
    
    # Download custom queries
    if custom_queries:
        for filename, query in custom_queries.items():
            total_downloads += 1
            print(f"📥 Downloading custom query to {filename}...")
            
            try:
                params = {
                    'query': query,
                    **CMS_CONFIG['default_params']
                }
                
                if downloader.download_json_data('sql', filename, params=params):
                    success_count += 1
                    print(f"✅ Successfully downloaded: {filename}")
                else:
                    print(f"❌ Failed to download: {filename}")
                    
            except Exception as e:
                print(f"❌ Error downloading custom query: {e}")
    
    print("-" * 60)
    print(f"✅ Download completed: {success_count}/{total_downloads} successful")
    print(f"📊 Check the '{CMS_CONFIG['output_dir']}' folder for downloaded files")
    print(f"📋 Check '{CMS_CONFIG['output_dir']}/download.log' for detailed logs")
    
    return success_count, total_downloads

def main():
    """Main function with different download options"""
    
    print("CMS.gov Data Downloader")
    print("=" * 40)
    print("Available options:")
    print("1. Quick sample (10 records)")
    print("2. Medium sample (100 records)")
    print("3. Large sample (1000 records)")
    print("4. Full dataset (all records)")
    print("5. Get record count")
    print("6. Get data schema")
    print("7. Custom download")
    print("8. Download all samples")
    
    if len(sys.argv) > 1:
        option = sys.argv[1]
    else:
        option = input("\nEnter your choice (1-8): ").strip()
    
    try:
        if option == '1':
            download_cms_data(['sample_10'])
        elif option == '2':
            download_cms_data(['sample_100'])
        elif option == '3':
            download_cms_data(['sample_1000'])
        elif option == '4':
            print("⚠️  Warning: This will download the entire dataset!")
            confirm = input("Are you sure? (y/N): ").strip().lower()
            if confirm == 'y':
                download_cms_data(['all_data'])
            else:
                print("Download cancelled.")
        elif option == '5':
            download_cms_data(['count_records'])
        elif option == '6':
            download_cms_data(['schema_info'])
        elif option == '7':
            print("Enter your custom SQL query:")
            query = input("Query: ").strip()
            filename = input("Output filename: ").strip()
            if not filename.endswith('.json'):
                filename += '.json'
            download_cms_data(custom_queries={filename: query})
        elif option == '8':
            download_cms_data(['sample_10', 'sample_100', 'count_records', 'schema_info'])
        else:
            print("Invalid option. Please choose 1-8.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Download interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
