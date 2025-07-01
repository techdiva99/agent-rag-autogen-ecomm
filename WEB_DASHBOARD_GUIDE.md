# 🌐 Web Dashboard Quick Start Guide

## What You Get

A beautiful, real-time web dashboard for monitoring your CMS Data Agent with:

- ✅ **Live Agent Status** - See if your agent is running and when it last checked for updates
- ✅ **Data Statistics** - Record count, file size, last update time
- ✅ **Data Quality Metrics** - Completeness, validity, and freshness indicators
- ✅ **Recent Activity** - Latest agent actions and logs
- ✅ **Provider Insights** - Rating distribution charts and top performers
- ✅ **Interactive Controls** - Download data, check updates, validate data
- ✅ **Responsive Design** - Works perfectly on desktop, tablet, and mobile

## 🚀 Quick Deployment (3 Steps)

### Step 1: Test Locally (1 minute)
```bash
# Generate dashboard data
python scripts/generate_dashboard_data.py

# Start the web server
cd web && python -m http.server 3000

# Open http://localhost:3000 in your browser
```

### Step 2: Deploy to GitHub Pages (2 minutes)
```bash
# 1. Enable GitHub Pages in your repository settings
#    - Go to Settings > Pages
#    - Source: "Deploy from a branch" 
#    - Branch: main
#    - Folder: /web

# 2. Commit and push the web files
git add web/ .github/
git commit -m "Deploy CMS Agent Dashboard to GitHub Pages"
git push origin main

# 3. Your dashboard will be live at:
# https://yourusername.github.io/agent-rag-autogen-ecomm/
```

### Step 3: Automatic Updates (GitHub Actions)
The included GitHub Action automatically:
- Updates dashboard data every 6 hours
- Generates fresh statistics and insights
- Commits updates to keep your dashboard current

## 🎯 Dashboard Features

### 📊 Status Overview
- **Agent Health**: Real-time status indicator
- **Data Metrics**: Total records (12,068+), file size (~21MB), last update
- **Quick Actions**: Refresh, download, validate buttons

### 📈 Analytics
- **Rating Distribution**: Visual chart of provider star ratings
- **Top Performers**: Highest-rated providers with survey counts
- **Quality Metrics**: Data completeness, validity, and freshness scores

### ⚙️ Interactive Controls
- **Update Interval**: Configure how often to check for new data
- **Auto-Update Toggle**: Enable/disable automatic updates
- **Manual Actions**: Force updates, validate data integrity

### 📱 Responsive Design
- Fully responsive layout works on all devices
- Modern, professional styling
- Real-time updates and notifications

## 🔧 Advanced Setup (Optional)

### Deploy with Live API Backend

For real-time data updates (instead of GitHub Actions), deploy the FastAPI backend:

1. **Deploy API** (choose one):
   ```bash
   # Railway (recommended)
   npm install -g @railway/cli
   railway login && railway init && railway up
   
   # Heroku
   echo "web: python -m uvicorn dashboard_api:app --host 0.0.0.0 --port \$PORT" > Procfile
   heroku create your-cms-api && git push heroku main
   ```

2. **Update Frontend**:
   ```javascript
   // In web/script.js, update the API URL:
   getApiBaseUrl() {
       return 'https://your-deployed-api.com/api';
   }
   ```

### Local Development with Live API

```bash
# Terminal 1: Start API
./run_dashboard_api.sh

# Terminal 2: Start frontend
cd web && python -m http.server 3000

# Dashboard: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

## 📊 Demo vs Live Modes

### GitHub Pages (Demo Mode)
- ✅ Uses static JSON files updated by GitHub Actions
- ✅ No server costs - completely free hosting
- ✅ Fast, reliable, works everywhere
- ✅ Perfect for monitoring and reports
- ⚠️ Data updates every 6 hours via GitHub Actions

### Live API Mode  
- ✅ Real-time data updates
- ✅ Interactive controls (download, validate)
- ✅ Live agent communication
- ⚠️ Requires backend server deployment
- ⚠️ Hosting costs for API server

## 🎨 Customization

### Update Styling
Edit `web/styles.css` to customize:
- Colors and branding
- Layout and spacing  
- Component styles
- Responsive breakpoints

### Add New Metrics
1. Update `scripts/generate_dashboard_data.py` to generate new data
2. Modify `web/script.js` to display the data
3. Add UI components in `web/index.html`

### Change Update Frequency
Edit `.github/workflows/update-dashboard.yml`:
```yaml
on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours instead of 6
```

## 🔍 Troubleshooting

### Dashboard Shows "Demo Mode"
- ✅ Expected on GitHub Pages - this is normal!
- Data comes from static JSON files
- Updates every 6 hours via GitHub Actions

### No Data Showing
```bash
# Regenerate dashboard data
python scripts/generate_dashboard_data.py

# Check generated files
ls -la web/data/
```

### GitHub Pages Not Updating
- Check repository Settings > Pages is enabled
- Verify branch and folder settings (/web)
- Clear browser cache
- Check GitHub Actions tab for any errors

### API Connection Errors  
```bash
# Check API health
curl http://localhost:8000/

# Restart API server
./run_dashboard_api.sh
```

## 📈 Next Steps

1. **Customize Your Dashboard**: Update colors, add your branding
2. **Set Up Monitoring**: Add alerts for data issues
3. **Integrate with Tools**: Connect to Slack, email notifications
4. **Extend Functionality**: Add new charts, metrics, or controls
5. **Share with Team**: Your GitHub Pages URL works for everyone

## 🎉 You're All Set!

Your CMS Data Agent now has a professional web dashboard that:
- Automatically updates with fresh data
- Provides beautiful visualizations
- Works on any device
- Costs nothing to host
- Integrates perfectly with your existing Agent-RAG-AutoGen workflow

Visit your dashboard at: `https://yourusername.github.io/agent-rag-autogen-ecomm/`
