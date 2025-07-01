#!/usr/bin/env python3
"""
Simple API Data Downloader

A simplified version for quick data downloads from APIs.
Usage: python simple_download.py <api_url> [output_filename]
"""

import requests
import json
import sys
import os
from datetime import datetime


def download_data(api_url, output_file=None, headers=None):
    """
    Download data from API and save to file
    
    Args:
        api_url: URL to fetch data from
        output_file: Output filename (optional)
        headers: HTTP headers dict (optional)
    """
    try:
        print(f"🔄 Downloading data from: {api_url}")
        
        # Make request
        response = requests.get(api_url, headers=headers or {}, timeout=30)
        response.raise_for_status()
        
        # Determine content type
        content_type = response.headers.get('content-type', '').lower()
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if 'json' in content_type:
                output_file = f"api_data_{timestamp}.json"
            elif 'csv' in content_type:
                output_file = f"api_data_{timestamp}.csv"
            else:
                output_file = f"api_data_{timestamp}.txt"
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        output_path = os.path.join("data", output_file)
        
        # Save data based on content type
        if 'json' in content_type:
            data = response.json()
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📊 Records: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            with open(output_path, 'wb') as f:
                f.write(response.content)
        
        print(f"✅ Data saved to: {output_path}")
        print(f"📁 File size: {os.path.getsize(output_path)} bytes")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python simple_download.py <api_url> [output_filename]")
        print("\nExamples:")
        print("  python simple_download.py https://jsonplaceholder.typicode.com/posts")
        print("  python simple_download.py https://api.example.com/data my_data.json")
        sys.exit(1)
    
    api_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Example headers (customize as needed)
    headers = {
        'User-Agent': 'API Data Downloader',
        'Accept': 'application/json'
        # Add authentication headers here if needed:
        # 'Authorization': 'Bearer your_token_here',
        # 'X-API-Key': 'your_api_key_here',
    }
    
    success = download_data(api_url, output_file, headers)
    
    if success:
        print("🎉 Download completed successfully!")
    else:
        print("💥 Download failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
