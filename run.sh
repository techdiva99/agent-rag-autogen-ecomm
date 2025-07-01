#!/bin/bash

# API Data Downloader Helper Script
# Usage: ./run.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}API Data Downloader Helper${NC}"
    echo ""
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Install dependencies"
    echo "  example   - Run example downloads"
    echo "  simple    - Run simple downloader with URL"
    echo "  download  - Run main downloader script"
    echo "  clean     - Clean downloaded data"
    echo "  logs      - Show download logs"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup"
    echo "  ./run.sh example"
    echo "  ./run.sh simple https://jsonplaceholder.typicode.com/posts"
    echo "  ./run.sh download"
}

setup() {
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
}

run_examples() {
    echo -e "${YELLOW}🚀 Running example downloads...${NC}"
    python examples.py
}

run_simple() {
    if [ -z "$2" ]; then
        echo -e "${RED}❌ Error: URL required for simple download${NC}"
        echo "Usage: ./run.sh simple <url> [filename]"
        echo "Example: ./run.sh simple https://jsonplaceholder.typicode.com/posts posts.json"
        exit 1
    fi
    
    echo -e "${YELLOW}📥 Running simple download...${NC}"
    python simple_download.py "$2" "$3"
}

run_download() {
    echo -e "${YELLOW}🔄 Running main downloader...${NC}"
    python download_api_data.py
}

clean_data() {
    echo -e "${YELLOW}🧹 Cleaning downloaded data...${NC}"
    if [ -d "data" ]; then
        rm -rf data/*
        echo -e "${GREEN}✅ Data directory cleaned!${NC}"
    else
        echo -e "${BLUE}ℹ️  No data directory found${NC}"
    fi
}

show_logs() {
    echo -e "${YELLOW}📋 Showing recent logs...${NC}"
    if [ -f "data/download.log" ]; then
        tail -n 50 data/download.log
    else
        echo -e "${BLUE}ℹ️  No log file found. Run a download first.${NC}"
    fi
}

# Main script logic
case "$1" in
    "setup")
        setup
        ;;
    "example")
        run_examples
        ;;
    "simple")
        run_simple "$@"
        ;;
    "download")
        run_download
        ;;
    "clean")
        clean_data
        ;;
    "logs")
        show_logs
        ;;
    "help"|"")
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
