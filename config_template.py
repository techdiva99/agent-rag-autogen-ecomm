# API Configuration Template
# Copy this file to config.py and update with your API details

# API Configuration
API_BASE_URL = "https://your-api-endpoint.com"
API_KEY = "your_api_key_here"
AUTH_TYPE = "bearer"  # Options: 'bearer', 'basic', 'api_key', None

# Authentication settings (choose one)
BEARER_TOKEN = "your_bearer_token_here"

# Basic Auth
BASIC_AUTH_USERNAME = "your_username"
BASIC_AUTH_PASSWORD = "your_password"

# API Key settings
API_KEY_HEADER_NAME = "X-API-Key"  # Common alternatives: "Authorization", "api-key"

# Download settings
OUTPUT_DIRECTORY = "data"
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
DELAY_BETWEEN_REQUESTS = 0.1  # seconds

# Endpoints to download (customize for your API)
ENDPOINTS = [
    {
        "path": "products",
        "filename": "products.json",
        "method": "GET",
        "params": {}
    },
    {
        "path": "categories", 
        "filename": "categories.json",
        "method": "GET",
        "params": {}
    },
    {
        "path": "orders",
        "filename": "orders.json", 
        "method": "GET",
        "params": {"limit": 1000}
    }
]

# Pagination settings
PAGINATION_CONFIG = {
    "page_param": "page",
    "limit_param": "limit", 
    "page_size": 100,
    "max_pages": None  # None for unlimited
}
