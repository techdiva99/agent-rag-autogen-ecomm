#!/bin/bash
# Quick script to download CMS data

echo "🏥 CMS Data Downloader - Quick Commands"
echo "========================================"

case "$1" in
    "sample")
        echo "📥 Downloading 10 sample records..."
        python cms_downloader.py 1
        ;;
    "medium")
        echo "📥 Downloading 100 sample records..."
        python cms_downloader.py 2
        ;;
    "large")
        echo "📥 Downloading 1000 sample records..."
        python cms_downloader.py 3
        ;;
    "count")
        echo "📊 Getting record count..."
        python cms_downloader.py 5
        ;;
    "schema")
        echo "📋 Getting data schema..."
        python cms_downloader.py 6
        ;;
    "all")
        echo "📥 Downloading all sample sizes..."
        python cms_downloader.py 8
        ;;
    "full")
        echo "⚠️  WARNING: This will download the ENTIRE dataset!"
        python cms_downloader.py 4
        ;;
    *)
        echo "Usage: $0 {sample|medium|large|count|schema|all|full}"
        echo ""
        echo "Commands:"
        echo "  sample  - Download 10 records"
        echo "  medium  - Download 100 records"
        echo "  large   - Download 1000 records"
        echo "  count   - Get total record count"
        echo "  schema  - Get data structure"
        echo "  all     - Download all sample sizes"
        echo "  full    - Download entire dataset (use with caution!)"
        echo ""
        echo "Example: $0 sample"
        ;;
esac
