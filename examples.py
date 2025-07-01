#!/usr/bin/env python3
"""
Example usage of the API data downloader
"""

from download_api_data import APIDataDownloader
import os


def example_ecommerce_download():
    """Example: Download e-commerce related data"""
    print("🛍️  E-commerce Data Download Example")
    print("=" * 50)
    
    # Example with a free e-commerce API
    downloader = APIDataDownloader("https://fakestoreapi.com", "data/ecommerce")
    
    downloads = [
        ("products", "all_products.json", "Downloading all products"),
        ("products/categories", "categories.json", "Downloading product categories"),
        ("users", "users.json", "Downloading users"),
        ("carts", "carts.json", "Downloading shopping carts")
    ]
    
    for endpoint, filename, description in downloads:
        print(f"\n📥 {description}...")
        success = downloader.download_json_data(endpoint, filename)
        if success:
            print(f"✅ Saved to data/ecommerce/{filename}")
        else:
            print(f"❌ Failed to download {endpoint}")


def example_jsonplaceholder_download():
    """Example: Download data from JSONPlaceholder API"""
    print("\n📄 JSONPlaceholder Data Download Example")
    print("=" * 50)
    
    downloader = APIDataDownloader("https://jsonplaceholder.typicode.com", "data/jsonplaceholder")
    
    # Download different types of data
    downloads = [
        ("posts", "posts.json", "Downloading blog posts"),
        ("users", "users.json", "Downloading users"),
        ("comments", "comments.json", "Downloading comments"),
        ("albums", "albums.json", "Downloading albums"),
        ("photos", "photos.json", "Downloading photos (this might be large!)"),
        ("todos", "todos.json", "Downloading todos")
    ]
    
    for endpoint, filename, description in downloads:
        print(f"\n📥 {description}...")
        success = downloader.download_json_data(endpoint, filename)
        if success:
            print(f"✅ Saved to data/jsonplaceholder/{filename}")
        else:
            print(f"❌ Failed to download {endpoint}")
            
    # Example with parameters
    print(f"\n📥 Downloading posts for user 1...")
    success = downloader.download_json_data("posts", "user_1_posts.json", params={"userId": 1})
    if success:
        print(f"✅ Saved to data/jsonplaceholder/user_1_posts.json")


def example_custom_api():
    """Example: Template for your own API"""
    print("\n🔧 Custom API Example Template")
    print("=" * 50)
    
    # Replace with your actual API details
    API_URL = "https://your-api.com"
    API_KEY = "your_api_key_here"
    
    print(f"API URL: {API_URL}")
    print(f"API Key: {'*' * len(API_KEY) if API_KEY != 'your_api_key_here' else 'Not configured'}")
    
    if API_KEY == "your_api_key_here":
        print("⚠️  Please update the API_URL and API_KEY variables in this function")
        return
    
    downloader = APIDataDownloader(API_URL, "data/custom")
    
    # Set authentication (uncomment and modify as needed)
    # downloader.set_authentication('bearer', token=API_KEY)
    # downloader.set_authentication('api_key', api_key=API_KEY, key_name='X-API-Key')
    
    # Add your endpoints here
    endpoints = [
        # ("endpoint1", "filename1.json"),
        # ("endpoint2", "filename2.json"),
    ]
    
    for endpoint, filename in endpoints:
        print(f"\n📥 Downloading {endpoint}...")
        success = downloader.download_json_data(endpoint, filename)
        if success:
            print(f"✅ Saved to data/custom/{filename}")


def main():
    """Run all examples"""
    print("🚀 API Data Download Examples")
    print("=" * 60)
    
    # Create base data directory
    os.makedirs("data", exist_ok=True)
    
    try:
        # Run examples
        example_jsonplaceholder_download()
        example_ecommerce_download()
        example_custom_api()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed!")
        print("📁 Check the 'data/' folder for downloaded files")
        print("📋 Check the log files for detailed information")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")


if __name__ == "__main__":
    main()
