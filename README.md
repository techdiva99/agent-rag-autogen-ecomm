# CMS.gov Provider Data Downloader

🤖 **Intelligent Agent Module** for downloading and managing healthcare provider data from CMS.gov (Centers for Medicare & Medicaid Services) API. Designed for seamless integration with **Agent-RAG-AutoGen** projects.

## ✨ Key Features

- 🔄 **Automatic Data Updates** - Monitors CMS.gov and downloads new data when available
- 🤖 **Agent Integration** - Ready-to-use agent module for AutoGen workflows  
- 🧠 **RAG-Ready** - Formats data for LLM consumption and vector databases
- 📊 **Complete Dataset** - Successfully tested with all 12,068 healthcare provider records (21MB)
- ⚙️ **Background Service** - Runs continuously with health monitoring and metrics
- 🌐 **Web Dashboard** - Beautiful, real-time monitoring interface for GitHub Pages
- � **Data Viewer** - Browse, search, and export CMS data with interactive table
- 🤖 **AI Chatbot** - Ask questions about your data using Claude API integration
- �🐳 **Production Ready** - Docker, Kubernetes, and cloud deployment configurations

## 🎯 Perfect For Agent-RAG-AutoGen Projects

This module transforms static API data into an **intelligent, self-updating agent** that:
- Automatically keeps your RAG knowledge base fresh
- Provides healthcare data context to AI agents
- Integrates seamlessly with multi-agent systems
- Handles data quality validation and error recovery

---

## 📁 Project Structure

```
├── cms_data/                # Downloaded CMS data files (21MB+ when full)
│   ├── cms_full_dataset.json        # Complete dataset (12,068 records)
│   ├── cms_sample_10_records.json   # Sample data (10 records)
│   ├── cms_record_count.json        # Total record count
│   └── download.log                 # Download activity logs
├── web/                     # Web dashboard for monitoring (GitHub Pages ready)
│   ├── index.html                   # Dashboard interface
│   ├── data-viewer.html             # Data browser and AI chat interface
│   ├── styles.css                   # Professional styling
│   ├── script.js                    # Interactive functionality
│   ├── data-viewer.js               # Data viewer and chatbot logic
│   ├── .nojekyll                    # GitHub Pages config
│   └── data/                        # Generated dashboard data
├── scripts/                 # Utility and automation scripts
│   └── generate_dashboard_data.py   # Dashboard data generator
├── .github/workflows/       # GitHub Actions for automation
│   └── update-dashboard.yml         # Auto-update dashboard data
├── data/                    # Other downloaded data files
├── download_api_data.py     # Main comprehensive downloader script
├── cms_downloader.py        # Specialized CMS data downloader
├── cms_config.py           # CMS API configuration
├── dashboard_api.py         # FastAPI backend for web dashboard
├── simple_download.py       # Simple one-off download script
├── config_template.py       # Configuration template
├── download_cms.sh         # Quick bash script for CMS downloads
├── run_dashboard_api.sh    # Script to start dashboard API
├── requirements.txt         # Python dependencies
├── DASHBOARD_DEPLOYMENT.md  # Dashboard deployment guide
├── WEB_DASHBOARD_GUIDE.md  # Quick start guide for dashboard
└── README.md               # This file
```

## 📊 CMS Dataset Information

### Dataset Overview
- **Total Records:** 12,068 healthcare providers
- **Dataset ID:** `a678955c-467c-5df1-a8bf-c94d22c86247`
- **API Endpoint:** `https://data.cms.gov/provider-data/api/1/datastore/sql`
- **File Size (Full):** ~21MB JSON format
- **Data Type:** Healthcare Home Health Care Provider Survey Results

### Data Fields
Each record contains the following information:
- `cms_certification_number_ccn` - CMS certification number
- `hhcahps_survey_summary_star_rating` - Overall survey star rating (1-5)
- Star ratings for specific care aspects:
  - Professional care delivery
  - Communication quality
  - Medicine and safety discussions
  - Overall care rating
- Patient survey response percentages
- `number_of_completed_surveys` - Survey sample size
- `survey_response_rate` - Response rate percentage
- Various footnote fields for data quality indicators

### Sample Data Structure
```json
{
  "record_number": "1",
  "cms_certification_number_ccn": "017000",
  "hhcahps_survey_summary_star_rating": "5",
  "star_rating_for_health_team_gave_care_in_a_professional_way": "4",
  "percent_of_patients_who_reported_that_their_home_health_tea_c7be": "92",
  "star_rating_for_health_team_communicated_well_with_them": "5",
  "number_of_completed_surveys": "665",
  "survey_response_rate": "19"
}
```

## 🏥 CMS Data Download (Quick Start)

### Quick Commands

```bash
# Download 10 sample records (17KB)
./download_cms.sh sample

# Download 100 records (~170KB)
./download_cms.sh medium

# Download 1000 records (~1.7MB)  
./download_cms.sh large

# Download ALL 12,068 records (~21MB)
./download_cms.sh full

# Get total record count
./download_cms.sh count

# Get data structure/schema
./download_cms.sh schema

# Download all sample sizes
./download_cms.sh all
```

### Using Python Directly

```bash
# Interactive mode (recommended for first-time users)
python cms_downloader.py

# Direct command mode
python cms_downloader.py 1    # 10 records
python cms_downloader.py 2    # 100 records
python cms_downloader.py 3    # 1000 records
python cms_downloader.py 4    # ALL 12,068 records (requires confirmation)
python cms_downloader.py 5    # record count only
python cms_downloader.py 6    # data schema sample
python cms_downloader.py 8    # all sample sizes
```

### Download Results Summary

| Option | Records | File Size | Use Case |
|--------|---------|-----------|----------|
| Sample | 10 | 17KB | Quick data exploration |
| Medium | 100 | ~170KB | Development/testing |
| Large | 1,000 | ~1.7MB | Analysis prototyping |
| **Full** | **12,068** | **~21MB** | **Complete analysis** |

## 📈 Data Analysis Examples

### Quick Data Inspection
```bash
# Count total records in downloaded file
python -c "import json; print(f'Records: {len(json.load(open(\"cms_data/cms_full_dataset.json\")))}')"

# Show unique star ratings
python -c "import json; data=json.load(open('cms_data/cms_full_dataset.json')); ratings=set(r['hhcahps_survey_summary_star_rating'] for r in data); print(f'Star ratings: {sorted(ratings)}')"

# Show average survey response rate
python -c "import json; data=json.load(open('cms_data/cms_full_dataset.json')); rates=[int(r['survey_response_rate']) for r in data if r['survey_response_rate'].isdigit()]; print(f'Avg response rate: {sum(rates)/len(rates):.1f}%')"
```

### File Verification
```bash
# Check file sizes
ls -lh cms_data/

# Verify record counts
wc -l cms_data/*.json

# Check download logs
tail cms_data/download.log
```

## 🚀 General API Downloads

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Simple Download

For quick one-off downloads:

```bash
# Download JSON data
python simple_download.py https://jsonplaceholder.typicode.com/posts

# Download with custom filename
python simple_download.py https://api.example.com/data my_data.json

# Download CSV data
python simple_download.py https://example.com/data.csv my_data.csv
```

### 3. Advanced Download

For more complex scenarios with authentication and pagination:

```bash
# Run with default configuration
python download_api_data.py

# Or modify the script for your specific API
# Edit download_api_data.py and change API_BASE_URL
```

## 🔧 Configuration for Other APIs

### For Advanced Downloads

1. Copy the configuration template:
   ```bash
   cp config_template.py config.py
   ```

2. Edit `config.py` with your API details:
   ```python
   API_BASE_URL = "https://your-api.com"
   API_KEY = "your_api_key"
   AUTH_TYPE = "bearer"  # or 'api_key', 'basic', None
   ```

3. Update the endpoints list for your specific API.

### Authentication Options

The scripts support multiple authentication methods:

- **Bearer Token**: `AUTH_TYPE = "bearer"`
- **API Key**: `AUTH_TYPE = "api_key"`
- **Basic Auth**: `AUTH_TYPE = "basic"`
- **No Auth**: `AUTH_TYPE = None`

## 📊 Features

### Main Script (`download_api_data.py`)
- ✅ Multiple authentication methods
- ✅ JSON and CSV support
- ✅ Paginated data download
- ✅ Error handling and logging
- ✅ Configurable retry logic
- ✅ Rate limiting
- ✅ Detailed logging

### CMS-Specific Script (`cms_downloader.py`)
- ✅ Pre-configured for CMS.gov API
- ✅ SQL query support
- ✅ Multiple dataset size options
- ✅ Interactive and command-line modes
- ✅ Data validation and verification
- ✅ Custom query support

### Simple Script (`simple_download.py`)
- ✅ Quick one-off downloads
- ✅ Command line interface
- ✅ Auto file type detection
- ✅ Basic error handling

## 📝 Usage Examples

### Download E-commerce Data

```python
from download_api_data import APIDataDownloader

# Initialize
downloader = APIDataDownloader("https://api.ecommerce.com")

# Set authentication
downloader.set_authentication('bearer', token='your_token')

# Download products
downloader.download_json_data('products', 'products.json')

# Download with pagination
downloader.download_paginated_data('orders', 'all_orders.json', page_size=100)

# Download with filters
downloader.download_json_data('products', 'electronics.json', 
                              params={'category': 'electronics'})
```

### Command Line Examples

```bash
# Download user data
python simple_download.py https://jsonplaceholder.typicode.com/users users.json

# Download product catalog
python simple_download.py https://api.store.com/products products.json

# Download orders (will auto-detect JSON format)
python simple_download.py https://api.store.com/orders
```

## 📂 Output

All downloaded data is saved with:
- Timestamped filenames
- Detailed logs in respective directories
- Error handling and retry logs
- File size and record count information

### CMS Data Output
- **Location**: `cms_data/` folder
- **Main file**: `cms_full_dataset.json` (21MB, 12,068 records)
- **Logs**: `cms_data/download.log`

### General API Data Output
- **Location**: `data/` folder
- **Logs**: `data/download.log`

## 🎯 Getting Started Checklist

### For CMS Data
1. ✅ Clone/download this repository
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Test with sample: `./download_cms.sh sample`
4. ✅ Download full dataset: `./download_cms.sh full`
5. ✅ Verify data: Check `cms_data/` folder (should have 21MB file)

### For Other APIs
1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Test simple download: `python simple_download.py <your_api_url>`
3. ✅ For complex APIs: Copy and modify `config_template.py`
4. ✅ Update `download_api_data.py` with your API details

## 📈 Next Steps

### Data Analysis
With your CMS data downloaded, you can now:
- Analyze healthcare provider ratings across regions
- Study survey response patterns
- Identify high-performing providers
- Create visualizations of care quality metrics
- Build machine learning models for quality prediction

### Integration
- Import data into databases (PostgreSQL, MySQL, SQLite)
- Load into analytics tools (Pandas, R, Tableau)
- Create dashboards and reports
- Build APIs on top of the data

### Automation
- Set up scheduled downloads for updated data
- Create data pipelines for continuous analysis
- Implement alerts for data quality issues
- Build monitoring for new CMS datasets

## 📋 Support and Maintenance

### Regular Updates
```bash
# Check for new data periodically
./download_cms.sh count

# Re-download if record count changes
./download_cms.sh full

# Keep logs clean
truncate -s 0 cms_data/download.log
```

### Monitoring
```bash
# Check system health
./download_cms.sh sample && echo "✅ System healthy" || echo "❌ System issues"

# Verify file integrity
python -c "import json; json.load(open('cms_data/cms_full_dataset.json')); print('✅ JSON valid')"
```

---

## 📞 Quick Reference

| Task | Command | Result |
|------|---------|---------|
| Test system | `./download_cms.sh sample` | 10 records (17KB) |
| Full download | `./download_cms.sh full` | 12,068 records (21MB) |
| Check count | `./download_cms.sh count` | Verify 12,068 total |
| Get schema | `./download_cms.sh schema` | See data structure |
| Custom query | `python cms_downloader.py 7` | Interactive mode |
| Other APIs | `python simple_download.py <url>` | Any API download |

**🎉 You now have a complete CMS healthcare provider dataset ready for analysis!**

## 🤖 Agent Module Integration

### Agent-RAG-AutoGen Integration

This CMS data downloader has been designed as a complete **intelligent agent module** for integration with Agent-RAG-AutoGen projects. The agent provides:

- **Automated data monitoring** - Continuously checks for new CMS data
- **Intelligent updates** - Downloads new data only when available
- **RAG integration** - Formats data for LLM consumption
- **AutoGen compatibility** - Works seamlessly with multi-agent workflows
- **Background services** - Runs autonomously in production environments

### Agent Components

```
├── cms_agent.py              # Core intelligent agent
├── agent_integration.py      # RAG and AutoGen integration
├── agent_config.py          # Environment configurations
├── agent_examples.py        # Usage examples
├── health_check.py          # Health monitoring
└── deploy/                  # Deployment configurations
```

### Quick Agent Setup

```python
from cms_agent import create_cms_agent
from agent_integration import AutoGenCMSAgent, RAGDataManager

# 1. Basic agent
agent = create_cms_agent(
    output_dir="cms_data",
    check_interval_hours=6,    # Check every 6 hours
    auto_update=True           # Auto-download new data
)

# 2. AutoGen integration
autogen_agent = AutoGenCMSAgent(name="healthcare_data_agent")

# 3. RAG integration
rag_manager = RAGDataManager(agent)
```

## 🔄 Automatic Data Updates

The agent automatically monitors CMS.gov for new data and updates your dataset when changes are detected.

### How It Works

1. **Scheduled Monitoring**: Agent checks CMS API every N hours (configurable)
2. **Change Detection**: Compares current record count with previous count
3. **Automatic Download**: Downloads full dataset when new records are available
4. **Validation**: Verifies data integrity after download
5. **Notification**: Optional alerts when data is updated

### Update Configuration

```python
# Development: Check every hour
dev_agent = create_cms_agent(check_interval_hours=1, auto_update=True)

# Production: Check every 6 hours
prod_agent = create_cms_agent(check_interval_hours=6, auto_update=True)

# Manual control: Disable auto-updates
manual_agent = create_cms_agent(auto_update=False)
```

### Manual Update Control

```python
# Check for updates manually
has_updates = agent.check_for_updates()
print(f"New data available: {has_updates}")

# Force download latest data
success = agent.download_latest_data(force=True)

# Get data with automatic freshness check
data = agent.get_latest_data(max_age_hours=24)
```

## 🧠 RAG Integration Features

### LLM Context Preparation

```python
from agent_integration import RAGDataManager

rag = RAGDataManager()

# Get high-rated providers for context
providers = rag.get_provider_context(rating_threshold=5, limit=10)
context = rag.format_for_llm(providers)

# Get statistical overview
stats = rag.get_statistics_context()

# Ensure data freshness
fresh = await rag.ensure_fresh_data(max_age_hours=24)
```

### AutoGen Agent Integration

```python
from agent_integration import AutoGenCMSAgent

# Create AutoGen-compatible agent
cms_agent = AutoGenCMSAgent(name="healthcare_expert")

# Handle natural language requests
response = await cms_agent.handle_data_request("Show me top-rated providers")
response = await cms_agent.handle_data_request("What's the data status?")
response = await cms_agent.handle_data_request("Update the dataset")
```

### Supported Agent Requests

| Request Type | Example | Response |
|-------------|---------|----------|
| Data Status | "What's the data status?" | Record count, age, update status |
| Provider Info | "Show me provider 017000" | Detailed provider information |
| High Performers | "Get top-rated providers" | List of 5-star providers |
| Statistics | "Give me dataset statistics" | Rating distribution, averages |
| Data Updates | "Update the data" | Download confirmation |

## ⚙️ Background Service

For production environments, run the agent as a background service that continuously monitors for updates.

### Background Service Features

- **Continuous Monitoring**: Runs 24/7 checking for data updates
- **Error Recovery**: Automatic retry on failures
- **Health Monitoring**: HTTP endpoints for status checks
- **Metrics Export**: Prometheus-compatible metrics
- **Logging**: Comprehensive activity logs

### Running as Service

```python
from agent_integration import CMSDataService

# Create background service
service = CMSDataService(check_interval_hours=6)

# Start service (runs continuously)
await service.start()
```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t cms-data-agent .
docker run -d \
  -v $(pwd)/data:/data/cms_data \
  -p 8080:8080 \
  cms-data-agent

# Check health
curl http://localhost:8080/health
```

### Health Monitoring

```bash
# Health check
curl http://localhost:8080/health
# Returns: {"status": "healthy", "records": 12068}

# Detailed status
curl http://localhost:8080/status
# Returns: Full agent and data status

# Prometheus metrics
curl http://localhost:8080/metrics
# Returns: Metrics in Prometheus format
```

## 🔧 Environment Configuration

### Development Environment

```python
from agent_config import get_development_config

config = get_development_config()
# - Check every hour
# - Debug logging enabled
# - Local data directory
# - No notifications
```

### Production Environment

```python
from agent_config import get_production_config

config = get_production_config()
# - Check every 6 hours
# - Metrics enabled
# - Persistent storage
# - Email/Slack notifications
# - Health monitoring
```

### Custom Configuration

```python
from agent_config import AgentConfig

custom_config = AgentConfig(
    output_dir="/data/healthcare",
    check_interval_hours=12,
    auto_update=True,
    enable_notifications=True,
    notification_config={
        "email": {
            "enabled": True,
            "recipients": ["admin@company.com"]
        }
    }
)
```

## 📊 Data Quality & Validation

The agent includes comprehensive data validation:

```python
# Validate current dataset
validation = agent.validate_data()
print(f"Valid: {validation['valid']}")
print(f"Records: {validation['record_count']}")
print(f"File size: {validation['file_size_mb']:.1f} MB")

# Built-in validation checks:
# ✅ Record count verification (expect ~12,068)
# ✅ Required field presence
# ✅ Star rating validity (1-5)
# ✅ File integrity
# ✅ Data completeness
```

## 🚀 Integration Examples

### Example 1: AutoGen Multi-Agent System

```python
import autogen

# Create CMS data agent
cms_agent = AutoGenCMSAgent(name="healthcare_data")

# Create other agents
analyst_agent = autogen.AssistantAgent(name="analyst")
planner_agent = autogen.AssistantAgent(name="planner")

# Use in group chat
group_chat = autogen.GroupChat(
    agents=[cms_agent, analyst_agent, planner_agent],
    messages=[],
    max_round=10
)
```

### Example 2: LangChain Integration

```python
from langchain.agents import initialize_agent
from agent_integration import integrate_with_langchain

# Create CMS tool for LangChain
cms_tool = integrate_with_langchain()

# Initialize agent with CMS tool
agent = initialize_agent(
    tools=[cms_tool],
    llm=llm,
    agent="zero-shot-react-description"
)
```

### Example 3: Background Data Pipeline

```python
import asyncio
from agent_integration import CMSDataService

async def main():
    # Start background monitoring
    service = CMSDataService(check_interval_hours=6)
    
    # Run other application logic
    while True:
        # Your application code here
        await asyncio.sleep(60)

asyncio.run(main())
```

## 📋 Agent Status Monitoring

### Status Information

```python
status = agent.get_status()
# Returns:
{
    'last_check': '2025-07-01T13:42:35',
    'last_update': '2025-07-01T13:31:20', 
    'current_record_count': 12068,
    'previous_record_count': 12068,
    'update_available': False,
    'last_error': None,
    'data_age_hours': 0.2
}
```

### Metrics for Monitoring Systems

The agent exposes metrics compatible with Prometheus, Grafana, and other monitoring systems:

```
cms_data_records{} 12068
cms_data_age_hours{} 0.2
cms_data_valid{} 1
cms_data_file_size_mb{} 21.5
```

## 🌐 Web Dashboard

### Beautiful Real-Time Monitoring Interface

A professional web dashboard provides real-time monitoring of your CMS Data Agent with:

- **📊 Live Status** - Agent health, data statistics, and activity logs
- **📈 Analytics** - Provider rating distribution and top performers  
- **⚙️ Interactive Controls** - Download data, check updates, validate integrity
- **📱 Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **🆓 Free Hosting** - Deploy to GitHub Pages at no cost

### Quick Start (2 minutes to deploy)

```bash
# 1. Generate dashboard data
python scripts/generate_dashboard_data.py

# 2. Test locally
cd web && python -m http.server 3000
# Open http://localhost:3000

# 3. Deploy to GitHub Pages
# - Enable GitHub Pages in repository settings
# - Set source to: Branch "main", Folder "/web"  
# - Your dashboard will be live at:
# https://yourusername.github.io/agent-rag-autogen-ecomm/
```

### Dashboard Features

| Feature | Description |
|---------|-------------|
| **Agent Status** | Real-time health indicator and last-seen timestamp |
| **Data Metrics** | Record count (12,068+), file size (~21MB), last update |
| **Quality Scores** | Completeness, validity, and freshness percentages |
| **Activity Feed** | Recent downloads, updates, and validation results |
| **Rating Analytics** | Visual chart of provider star rating distribution |
| **Top Performers** | Highest-rated providers with survey counts |
| **Interactive Controls** | Download, validate, and update data buttons |
| **Data Browser** | Browse, search, and export all CMS records |
| **AI Chat Assistant** | Ask questions about data using Claude API |
| **Auto-Updates** | GitHub Actions update dashboard data every 6 hours |

### Deployment Options

**Option 1: GitHub Pages (Recommended)**
- ✅ Completely free hosting
- ✅ Automatic updates via GitHub Actions
- ✅ Professional appearance
- ✅ No server management required

**Option 2: Live API Backend**  
- ✅ Real-time data updates
- ✅ Interactive agent control
- ⚠️ Requires server deployment

See [WEB_DASHBOARD_GUIDE.md](WEB_DASHBOARD_GUIDE.md) for detailed instructions.

## 📋 Data Viewer & AI Chat

### Browse Your Data Interactively

Access a powerful data explorer at `/data-viewer.html` with:

- **📋 Interactive Table** - Browse all 12,068+ provider records with search and filtering
- **🔍 Smart Search** - Search across all fields (provider ID, ratings, surveys, locations)
- **⭐ Rating Filters** - Filter by 1-5 star ratings to find top performers
- **📊 Export Options** - Download filtered data as CSV for further analysis
- **📱 Mobile-Friendly** - Responsive design works on any device

### AI-Powered Data Analysis

Chat with your data using Claude API integration:

```
🤖 Ask questions like:
• "What's the average star rating across all providers?"
• "How many providers have 5-star ratings?"  
• "Which provider has the most survey responses?"
• "What percentage of providers have 4+ stars?"
• "Tell me about quality trends in the data"
```

**Features:**
- **🧠 Intelligent Analysis** - Get statistical insights and trend analysis
- **💬 Natural Language** - Ask questions in plain English
- **📊 Data Context** - AI understands your specific CMS dataset
- **🔐 Secure** - Your Claude API key stays private in your browser
- **⚡ Fast** - Instant responses with detailed explanations

### Quick Setup

```bash
# 1. Access the data viewer
# From dashboard: Click "Browse Data" button
# Direct URL: /data-viewer.html

# 2. Set up Claude API (optional)
# Get API key from: https://console.anthropic.com/
# Enter when prompted in the chat interface
# Works in demo mode without API key

# 3. Start exploring!
# Browse data, ask questions, export results
```

See [DATA_VIEWER_GUIDE.md](DATA_VIEWER_GUIDE.md) for complete setup and usage instructions.

---