# 📊 CMS Data Viewer & AI Chatbot Guide

## 🎯 New Features Added

Your CMS Data Agent now includes two powerful new features:

### 1. **📋 Data Viewer** (`data-viewer.html`)
- Browse and explore all CMS healthcare provider records
- Search and filter by provider ID, ratings, surveys
- Paginated table view with sortable columns  
- Export data to CSV format
- Responsive design for mobile and desktop

### 2. **🤖 AI Chatbot** (Claude Integration)
- Ask natural language questions about your data
- Get intelligent analysis and insights
- Powered by Claude API (Anthropic)
- Contextual responses based on actual data
- Demo mode available without API key

## 🚀 Quick Start

### Access the Data Viewer
```bash
# If running locally
http://localhost:3000/data-viewer.html

# From main dashboard
Click "Browse Data" button in the header

# On GitHub Pages  
https://yourusername.github.io/agent-rag-autogen-ecomm/data-viewer.html
```

### Set Up Claude API (Optional)
1. Get your API key from [console.anthropic.com](https://console.anthropic.com/)
2. Open the data viewer
3. Enter your API key when prompted
4. Start chatting with your data!

## 📋 Data Viewer Features

### **Browse & Search**
- **View All Records**: See your complete CMS dataset in a clean table
- **Search Anything**: Search across all fields (provider ID, ratings, surveys, etc.)
- **Filter by Rating**: Show only providers with specific star ratings (1-5)
- **Pagination**: Navigate through large datasets efficiently

### **Export & Download**
- **CSV Export**: Download filtered data as spreadsheet
- **All Data**: Export complete dataset or just filtered results
- **Formatted Files**: Ready for Excel, Google Sheets, analysis tools

### **Interactive Features**
- **Real-time Search**: Results update as you type
- **Responsive Design**: Works on desktop, tablet, mobile
- **Fast Performance**: Handles 12,000+ records smoothly
- **Visual Ratings**: Star displays for easy rating recognition

## 🤖 AI Chatbot Features

### **Intelligent Analysis**
Ask questions like:
- *"What's the average star rating across all providers?"*
- *"How many providers have 5-star ratings?"*
- *"Which provider has the most survey responses?"*
- *"What percentage of providers have 4+ stars?"*
- *"Tell me about quality trends in the data"*

### **Data Context**
- **Knows Your Data**: AI understands your specific dataset
- **Statistical Analysis**: Calculates averages, totals, distributions
- **Trend Analysis**: Identifies patterns and insights
- **Comparative Analysis**: Compares providers and metrics

### **Smart Responses**
- **Contextual**: Answers based on your actual data
- **Detailed**: Provides specific numbers and analysis
- **Actionable**: Suggests next steps and deeper analysis
- **Educational**: Explains healthcare metrics and significance

## 🔧 Claude API Setup

### Step 1: Get Your API Key
1. Visit [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-api03-...`)

### Step 2: Configure in Data Viewer
1. Open the data viewer
2. You'll see a modal asking for your API key
3. Paste your Claude API key
4. Click "Save & Continue"
5. Your key is stored locally (never sent to our servers)

### Step 3: Start Chatting
- Type questions in natural language
- Get AI-powered insights about your data
- Use sample questions or ask your own

## 💡 Sample Questions to Try

### **Basic Statistics**
- "How many total providers are in the dataset?"
- "What's the average star rating?"
- "Show me the rating distribution"

### **Quality Analysis**  
- "Which providers have perfect 5-star ratings?"
- "What percentage of providers are above average?"
- "Find providers with low response rates"

### **Comparative Analysis**
- "Compare communication vs care ratings"
- "Which metrics correlate with overall ratings?"
- "Show me outliers in the data"

### **Trend Analysis**
- "Are there patterns in high-performing providers?"
- "What makes a provider get 5 stars?"
- "Analyze survey response rate trends"

## 🎨 Customization

### Update Sample Questions
Edit `data-viewer.html` to add your own sample questions:
```html
<button class="query-btn" onclick="askQuestion('Your custom question')">
    Your Button Text
</button>
```

### Modify Search Fields
Update `data-viewer.js` to customize search behavior:
```javascript
// Add custom filters or search logic
filterData() {
    // Your custom filtering code
}
```

### Style Customization
Update the `<style>` section in `data-viewer.html` or add to `styles.css`:
```css
/* Custom styling for data viewer */
.data-table th {
    background: your-brand-color;
}
```

## 🔄 Integration Options

### **GitHub Pages (Static)**
- Data viewer works with static JSON files
- Claude API calls made directly from browser
- No backend server required
- Chat works with your own API key

### **Live API Backend**
- Enhanced chat features through your API
- Server-side Claude integration  
- Additional security and rate limiting
- Shared API key management

### **Hybrid Approach**
- Static data viewer on GitHub Pages
- Optional API backend for advanced features
- Best of both worlds

## 📊 Data Export Options

### **CSV Download**
- Exports current filtered view
- All columns included
- Excel/Google Sheets compatible
- Timestamps in filename

### **Programmatic Access**
```javascript
// Access filtered data programmatically
const viewer = new DataViewerApp();
const filteredData = viewer.filteredData;
```

### **API Endpoints**
```bash
# Get paginated records (if using API backend)
GET /api/data/records?page=1&limit=50&search=term&rating=5

# Chat with data
POST /api/chat
{
  "message": "What's the average rating?"
}
```

## 🛠️ Troubleshooting

### **Data Not Loading**
```bash
# Check if CMS data exists
ls cms_data/cms_full_dataset.json

# Regenerate if missing
python scripts/generate_dashboard_data.py
```

### **Chat Not Working**
1. **Check API Key**: Verify your Claude API key is valid
2. **Check Credits**: Ensure you have API credits available  
3. **Network Issues**: Check browser console for errors
4. **Demo Mode**: Chat works in demo mode without API key

### **Search Issues**
- Try clearing filters and search terms
- Refresh the page to reload data
- Check browser console for JavaScript errors

### **Performance Issues**
- Use pagination for large datasets
- Apply filters to reduce displayed records
- Clear browser cache if needed

## 🔐 Security & Privacy

### **API Key Storage**
- Keys stored in browser localStorage only
- Never transmitted to our servers
- Can be cleared anytime via browser settings

### **Data Privacy**
- Your CMS data stays local or on your servers
- Claude API only receives the questions you ask
- No data mining or storage by third parties

### **Best Practices**
- Don't share API keys
- Use environment variables for production
- Regularly rotate API keys
- Monitor API usage and costs

## 🚀 Deployment

### **GitHub Pages**
```bash
# Data viewer is automatically included
git add web/data-viewer.html web/data-viewer.js
git commit -m "Add data viewer and AI chat"
git push origin main

# Available at:
# https://yourusername.github.io/agent-rag-autogen-ecomm/data-viewer.html
```

### **Custom Domain**
- Configure CNAME file for custom domain
- Update API endpoints if needed
- Ensure HTTPS for Claude API calls

## 📈 Next Steps

### **Enhanced Features**
- Add data visualization charts
- Implement advanced filtering
- Create custom dashboard views
- Add data comparison tools

### **AI Improvements**
- Train on healthcare-specific prompts
- Add domain expertise
- Implement conversation memory
- Create analysis templates

### **Integration Options**
- Connect to BI tools (Tableau, Power BI)
- Export to databases
- API integrations with other systems
- Automated reporting

## 🎉 You Now Have

✅ **Complete Data Explorer** - Browse all 12,000+ provider records  
✅ **AI-Powered Analysis** - Ask questions in natural language  
✅ **Export Capabilities** - Download data as CSV  
✅ **Mobile-Friendly** - Works on any device  
✅ **Search & Filter** - Find exactly what you need  
✅ **No Server Required** - Works on GitHub Pages  
✅ **Secure** - Your API key stays private  
✅ **Extensible** - Easy to customize and enhance  

Your CMS Data Agent is now a complete data exploration and analysis platform! 🚀
