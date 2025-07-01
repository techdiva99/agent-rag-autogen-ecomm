# CMS Data Agent - Web Dashboard Deployment Guide

This guide explains how to deploy the CMS Data Agent web dashboard to GitHub Pages and set up the backend API.

## Dashboard Components

The web dashboard consists of:

1. **Frontend** (`web/` folder):
   - `index.html` - Main dashboard interface
   - `styles.css` - Styling and responsive design
   - `script.js` - JavaScript for API communication and interactivity

2. **Backend API** (`dashboard_api.py`):
   - FastAPI-based REST API
   - Serves live agent data and status
   - Provides endpoints for dashboard functionality

## Deployment Options

### Option 1: GitHub Pages (Static) + External API

#### Step 1: Deploy Frontend to GitHub Pages

1. **Enable GitHub Pages:**
   ```bash
   # In your repository settings, enable GitHub Pages
   # Set source to "Deploy from a branch"
   # Select branch: main
   # Folder: /web
   ```

2. **Create GitHub Pages Configuration:**
   ```bash
   # Create .nojekyll file to prevent Jekyll processing
   touch web/.nojekyll
   ```

3. **Update API URL in script.js:**
   ```javascript
   // In web/script.js, update the getApiBaseUrl() function:
   getApiBaseUrl() {
       return 'https://your-api-domain.com/api'; // Your deployed API URL
   }
   ```

4. **Commit and push:**
   ```bash
   git add web/
   git commit -m "Deploy dashboard to GitHub Pages"
   git push origin main
   ```

#### Step 2: Deploy Backend API

**Option A: Railway (Recommended)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Option B: Heroku**
```bash
# Create Procfile
echo "web: python -m uvicorn dashboard_api:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-cms-agent-api
git push heroku main
```

**Option C: DigitalOcean App Platform**
```yaml
# Create .do/app.yaml
name: cms-agent-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/agent-rag-autogen-ecomm
    branch: main
  run_command: python -m uvicorn dashboard_api:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
```

### Option 2: GitHub Pages + GitHub Actions API

For a more integrated solution, use GitHub Actions to update static JSON files:

1. **Create GitHub Action** (`.github/workflows/update-dashboard.yml`):
```yaml
name: Update Dashboard Data
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Update dashboard data
      run: python scripts/generate_dashboard_data.py
    - name: Commit updates
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add web/data/
        git commit -m "Update dashboard data" || exit 0
        git push
```

2. **Create data generation script** (`scripts/generate_dashboard_data.py`):
```python
#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def generate_dashboard_data():
    # Create web/data directory
    data_dir = Path("web/data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate status.json
    status = {
        "status": "active",
        "last_seen": datetime.now().isoformat(),
        "generated_at": datetime.now().isoformat()
    }
    
    with open(data_dir / "status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    # Add more data generation as needed
    
if __name__ == "__main__":
    generate_dashboard_data()
```

### Option 3: Full Static (Demo Mode)

For development or demo purposes, the dashboard works entirely in static mode:

1. Simply open `web/index.html` in a browser
2. The dashboard will automatically switch to demo mode
3. All functionality works with simulated data

## Configuration

### Environment Variables (for API deployment)

```bash
# Production settings
export PYTHONPATH="/app"
export LOG_LEVEL="INFO"

# Optional: Database connections
export DATABASE_URL="your-database-url"
export REDIS_URL="your-redis-url"
```

### CORS Configuration

Update `dashboard_api.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourusername.github.io"],  # Your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Local Development

### Start Both Frontend and Backend

1. **Start the API server:**
   ```bash
   ./run_dashboard_api.sh
   ```

2. **Serve the frontend locally:**
   ```bash
   cd web
   python -m http.server 3000
   ```

3. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Update API URL for Local Development

In `web/script.js`, modify the `getApiBaseUrl()` function:

```javascript
getApiBaseUrl() {
    const isDevelopment = window.location.hostname === 'localhost' || 
                        window.location.hostname === '127.0.0.1';
    
    if (isDevelopment) {
        return 'http://localhost:8000/api';  // Local API
    }
    return 'https://your-deployed-api.com/api';  // Production API
}
```

## Testing the Deployment

### Test API Endpoints

```bash
# Health check
curl https://your-api-domain.com/

# Agent status
curl https://your-api-domain.com/api/status

# Data stats
curl https://your-api-domain.com/api/data/stats
```

### Test Dashboard

1. Open your GitHub Pages URL
2. Check browser console for any errors
3. Verify all dashboard sections load properly
4. Test refresh and control buttons

## Monitoring and Maintenance

### API Monitoring

- Set up health checks for your API endpoint
- Monitor API response times and availability
- Set up alerts for failures

### Dashboard Updates

- The dashboard auto-refreshes every 5 minutes by default
- Manual refresh button always available
- Real-time status indicators show connection health

### Data Updates

- Agent continues to run independently
- API serves the latest data from agent files
- Dashboard reflects changes automatically

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Update CORS settings in `dashboard_api.py`
   - Ensure API URL is correct in `script.js`

2. **API Connection Failed:**
   - Dashboard switches to demo mode automatically
   - Check API server status and logs
   - Verify network connectivity

3. **GitHub Pages Not Updating:**
   - Check repository settings
   - Ensure `.nojekyll` file exists
   - Clear browser cache

4. **API Deployment Issues:**
   - Check application logs
   - Verify environment variables
   - Ensure requirements.txt is complete

### Debug Mode

Enable debug logging in the API:

```python
# In dashboard_api.py
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

1. **API Authentication:**
   - Add API keys for production use
   - Implement rate limiting
   - Use HTTPS only

2. **Data Privacy:**
   - Ensure no sensitive data in frontend
   - Implement proper data sanitization
   - Follow healthcare data regulations

3. **Infrastructure:**
   - Use secure hosting platforms
   - Regular security updates
   - Monitor for vulnerabilities

## Next Steps

1. Deploy the API to your preferred platform
2. Update the API URL in the frontend
3. Deploy to GitHub Pages
4. Set up monitoring and alerts
5. Customize the dashboard for your needs

The dashboard provides a powerful, real-time interface for monitoring your CMS Data Agent with professional styling and responsive design suitable for production use.
