// CMS Data Viewer and AI Chat Interface

class DataViewerApp {
    constructor() {
        this.currentData = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.pageSize = 50;
        this.searchTerm = '';
        this.ratingFilter = '';
        this.apiKey = null;
        
        this.init();
    }
    
    init() {
        this.loadData();
        this.bindEvents();
        this.setupChat();
        this.loadApiKey();
    }
    
    bindEvents() {
        // Data viewer events
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterData();
        });
        
        document.getElementById('ratingFilter').addEventListener('change', (e) => {
            this.ratingFilter = e.target.value;
            this.filterData();
        });
        
        document.getElementById('refreshDataBtn').addEventListener('click', () => {
            this.loadData();
        });
        
        document.getElementById('downloadCsvBtn').addEventListener('click', () => {
            this.downloadCSV();
        });
        
        document.getElementById('prevPageBtn').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.renderTable();
            }
        });
        
        document.getElementById('nextPageBtn').addEventListener('click', () => {
            const totalPages = Math.ceil(this.filteredData.length / this.pageSize);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.renderTable();
            }
        });
        
        // Chat events
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        document.getElementById('chatInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        document.getElementById('chatInput').addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
        });
    }
    
    async loadData() {
        try {
            this.showLoading('Loading CMS data...');
            
            // Try to load from local CMS data file
            let response = await fetch('../cms_data/cms_full_dataset.json');
            
            if (!response.ok) {
                // Fallback to sample data
                response = await fetch('../cms_data/cms_sample_10_records.json');
            }
            
            if (!response.ok) {
                throw new Error('Could not load data');
            }
            
            this.currentData = await response.json();
            this.filterData();
            this.hideLoading();
            
        } catch (error) {
            console.error('Error loading data:', error);
            this.hideLoading();
            this.showError('Could not load data. Using demo data.');
            this.loadDemoData();
        }
    }
    
    loadDemoData() {
        // Demo data for testing
        this.currentData = Array.from({ length: 100 }, (_, i) => ({
            record_number: (i + 1).toString(),
            cms_certification_number_ccn: `${100000 + i}`,
            hhcahps_survey_summary_star_rating: Math.floor(Math.random() * 5) + 1,
            star_rating_for_health_team_gave_care_in_a_professional_way: Math.floor(Math.random() * 5) + 1,
            percent_of_patients_who_reported_that_their_home_health_tea_c7be: Math.floor(Math.random() * 100),
            star_rating_for_health_team_communicated_well_with_them: Math.floor(Math.random() * 5) + 1,
            number_of_completed_surveys: Math.floor(Math.random() * 1000) + 50,
            survey_response_rate: Math.floor(Math.random() * 50) + 10
        }));
        this.filterData();
    }
    
    filterData() {
        this.filteredData = this.currentData.filter(item => {
            const matchesSearch = !this.searchTerm || 
                Object.values(item).some(value => 
                    value && value.toString().toLowerCase().includes(this.searchTerm)
                );
            
            const matchesRating = !this.ratingFilter || 
                (item.hhcahps_survey_summary_star_rating && 
                 item.hhcahps_survey_summary_star_rating.toString() === this.ratingFilter);
            
            return matchesSearch && matchesRating;
        });
        
        this.currentPage = 1;
        this.renderTable();
    }
    
    renderTable() {
        if (this.filteredData.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        // Render headers
        this.renderHeaders();
        
        // Calculate pagination
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, this.filteredData.length);
        const pageData = this.filteredData.slice(startIndex, endIndex);
        
        // Render table body
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';
        
        pageData.forEach(item => {
            const row = this.createTableRow(item);
            tbody.appendChild(row);
        });
        
        // Update pagination
        this.updatePagination();
    }
    
    renderHeaders() {
        const thead = document.getElementById('tableHeader');
        
        if (this.filteredData.length === 0) {
            thead.innerHTML = '<th>No data available</th>';
            return;
        }
        
        // Get headers from first item
        const headers = Object.keys(this.filteredData[0]);
        const displayHeaders = {
            'record_number': 'Record #',
            'cms_certification_number_ccn': 'CMS ID',
            'hhcahps_survey_summary_star_rating': 'Overall Rating',
            'star_rating_for_health_team_gave_care_in_a_professional_way': 'Care Rating',
            'percent_of_patients_who_reported_that_their_home_health_tea_c7be': 'Patient %',
            'star_rating_for_health_team_communicated_well_with_them': 'Communication',
            'number_of_completed_surveys': 'Surveys',
            'survey_response_rate': 'Response %'
        };
        
        thead.innerHTML = headers.map(header => {
            const displayName = displayHeaders[header] || header.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            return `<th>${displayName}</th>`;
        }).join('');
    }
    
    createTableRow(item) {
        const row = document.createElement('tr');
        
        Object.values(item).forEach(value => {
            const cell = document.createElement('td');
            
            // Special formatting for certain types
            if (typeof value === 'number' || !isNaN(value)) {
                const num = parseFloat(value);
                if (num >= 1 && num <= 5 && Number.isInteger(num)) {
                    // Star rating
                    cell.innerHTML = '★'.repeat(num) + '☆'.repeat(5 - num);
                } else {
                    cell.textContent = value;
                }
            } else {
                cell.textContent = value || '-';
            }
            
            row.appendChild(cell);
        });
        
        return row;
    }
    
    updatePagination() {
        const total = this.filteredData.length;
        const startIndex = (this.currentPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, total);
        const totalPages = Math.ceil(total / this.pageSize);
        
        // Update info
        document.getElementById('paginationInfo').textContent = 
            `Showing ${startIndex + 1} - ${endIndex} of ${total} records`;
        
        // Update buttons
        document.getElementById('prevPageBtn').disabled = this.currentPage <= 1;
        document.getElementById('nextPageBtn').disabled = this.currentPage >= totalPages;
        
        // Update page numbers
        this.renderPageNumbers(totalPages);
    }
    
    renderPageNumbers(totalPages) {
        const container = document.getElementById('pageNumbers');
        container.innerHTML = '';
        
        if (totalPages <= 1) return;
        
        const maxVisible = 5;
        let start = Math.max(1, this.currentPage - 2);
        let end = Math.min(totalPages, start + maxVisible - 1);
        
        if (end - start < maxVisible - 1) {
            start = Math.max(1, end - maxVisible + 1);
        }
        
        for (let i = start; i <= end; i++) {
            const btn = document.createElement('button');
            btn.className = `page-btn ${i === this.currentPage ? 'active' : ''}`;
            btn.textContent = i;
            btn.onclick = () => {
                this.currentPage = i;
                this.renderTable();
            };
            container.appendChild(btn);
        }
    }
    
    renderEmptyState() {
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = `
            <tr>
                <td colspan="100%" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                    No data found matching your criteria
                </td>
            </tr>
        `;
        
        document.getElementById('paginationInfo').textContent = 'No records found';
        document.getElementById('prevPageBtn').disabled = true;
        document.getElementById('nextPageBtn').disabled = true;
        document.getElementById('pageNumbers').innerHTML = '';
    }
    
    downloadCSV() {
        if (this.filteredData.length === 0) {
            this.showError('No data to download');
            return;
        }
        
        const headers = Object.keys(this.filteredData[0]);
        const csv = [
            headers.join(','),
            ...this.filteredData.map(row => 
                headers.map(header => {
                    const value = row[header] || '';
                    return `"${value.toString().replace(/"/g, '""')}"`;
                }).join(',')
            )
        ].join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cms_data_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showSuccess('CSV file downloaded successfully');
    }
    
    // Chat functionality
    setupChat() {
        // Check if running locally or on GitHub Pages
        this.isLocalEnvironment = window.location.hostname === 'localhost' || 
                                 window.location.hostname === '127.0.0.1';
    }
    
    loadApiKey() {
        // Try to load API key from localStorage
        this.apiKey = localStorage.getItem('claude_api_key');
        
        if (!this.apiKey) {
            this.promptForApiKey();
        }
    }
    
    promptForApiKey() {
        const modal = this.createApiKeyModal();
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }
    
    createApiKeyModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); display: flex; align-items: center;
            justify-content: center; z-index: 1000;
        `;
        
        modal.innerHTML = `
            <div style="background: white; padding: 2rem; border-radius: 12px; max-width: 500px; margin: 1rem;">
                <h3 style="margin: 0 0 1rem 0;">
                    <i class="fas fa-key"></i> Configure Claude API
                </h3>
                <p style="color: #666; margin-bottom: 1.5rem;">
                    To use the AI chat feature, please enter your Claude API key from Anthropic.
                    Your key will be stored locally and never sent to our servers.
                </p>
                <div style="margin-bottom: 1rem;">
                    <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">
                        Claude API Key:
                    </label>
                    <input type="password" id="apiKeyInput" 
                           placeholder="sk-ant-api03-..." 
                           style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px;">
                </div>
                <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                    <button id="skipApiKey" style="padding: 0.75rem 1.5rem; border: 1px solid #ddd; background: white; border-radius: 6px; cursor: pointer;">
                        Skip for now
                    </button>
                    <button id="saveApiKey" style="padding: 0.75rem 1.5rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">
                        Save & Continue
                    </button>
                </div>
                <p style="font-size: 0.75rem; color: #888; margin-top: 1rem;">
                    Get your API key at: <a href="https://console.anthropic.com/" target="_blank">console.anthropic.com</a>
                </p>
            </div>
        `;
        
        modal.querySelector('#saveApiKey').onclick = () => {
            const key = modal.querySelector('#apiKeyInput').value.trim();
            if (key) {
                localStorage.setItem('claude_api_key', key);
                this.apiKey = key;
                this.showSuccess('API key saved successfully');
            }
            document.body.removeChild(modal);
        };
        
        modal.querySelector('#skipApiKey').onclick = () => {
            document.body.removeChild(modal);
            this.showInfo('Chat will work in demo mode without Claude API');
        };
        
        return modal;
    }
    
    async sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTyping();
        
        try {
            const response = await this.callClaudeAPI(message);
            this.hideTyping();
            this.addMessage('assistant', response);
        } catch (error) {
            this.hideTyping();
            console.error('Chat error:', error);
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again or check your API key.');
        }
    }
    
    async callClaudeAPI(message) {
        if (!this.apiKey) {
            return "I don't have access to Claude API. Please configure your API key to enable AI responses, or I can provide demo responses about the data.";
        }
        
        // Prepare context about the data
        const dataContext = this.prepareDataContext();
        
        const systemPrompt = `You are an AI assistant helping users analyze CMS healthcare provider data. 
        
Here's information about the dataset:
${dataContext}

Please provide helpful, accurate responses about this healthcare data. Focus on:
- Data analysis and insights
- Statistical summaries
- Trends and patterns
- Comparisons between providers
- Quality metrics interpretation

Always base your responses on the actual data characteristics described above.`;

        try {
            const response = await fetch('https://api.anthropic.com/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: 'claude-3-sonnet-20240229',
                    max_tokens: 1024,
                    system: systemPrompt,
                    messages: [
                        {
                            role: 'user',
                            content: message
                        }
                    ]
                })
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('claude_api_key');
                    this.apiKey = null;
                    throw new Error('Invalid API key. Please check your Claude API key.');
                }
                throw new Error(`API error: ${response.status}`);
            }
            
            const data = await response.json();
            return data.content[0].text;
            
        } catch (error) {
            if (error.message.includes('API key')) {
                throw error;
            }
            
            // Fallback to demo response
            return this.generateDemoResponse(message);
        }
    }
    
    prepareDataContext() {
        if (this.currentData.length === 0) {
            return "No data currently loaded.";
        }
        
        const totalRecords = this.currentData.length;
        const sampleRecord = this.currentData[0];
        const fields = Object.keys(sampleRecord);
        
        // Calculate some basic stats
        const ratings = this.currentData
            .map(r => parseInt(r.hhcahps_survey_summary_star_rating))
            .filter(r => !isNaN(r));
        
        const avgRating = ratings.length > 0 ? 
            (ratings.reduce((a, b) => a + b, 0) / ratings.length).toFixed(2) : 'N/A';
        
        const ratingDistribution = {};
        ratings.forEach(r => {
            ratingDistribution[r] = (ratingDistribution[r] || 0) + 1;
        });
        
        return `
Dataset Summary:
- Total records: ${totalRecords}
- Average star rating: ${avgRating}
- Rating distribution: ${JSON.stringify(ratingDistribution)}
- Available fields: ${fields.join(', ')}
- Record example: ${JSON.stringify(sampleRecord, null, 2)}
        `;
    }
    
    generateDemoResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('average') && lowerMessage.includes('rating')) {
            return `Based on the current dataset of ${this.currentData.length} providers, I can help you calculate the average rating. Let me analyze the star ratings for you.`;
        }
        
        if (lowerMessage.includes('5 star') || lowerMessage.includes('five star')) {
            return `I can help you find providers with 5-star ratings. Let me search through the data to identify the top-performing healthcare providers.`;
        }
        
        if (lowerMessage.includes('survey') && lowerMessage.includes('most')) {
            return `I'll help you find which provider has the most survey responses. This is often a good indicator of provider size and patient volume.`;
        }
        
        if (lowerMessage.includes('trend') || lowerMessage.includes('pattern')) {
            return `I can analyze trends in the healthcare provider data, including rating distributions, response rates, and quality patterns across different providers.`;
        }
        
        return `I'd be happy to help you analyze the CMS healthcare provider data! I can help with statistics, trends, comparisons, and insights about provider ratings and survey results. Please configure your Claude API key for more detailed AI responses, or ask me specific questions about the data.`;
    }
    
    addMessage(sender, content) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString();
        const avatar = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${avatar}
            </div>
            <div>
                <div class="message-content">${content}</div>
                <div class="message-timestamp">${timestamp}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTyping() {
        const messagesContainer = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-indicator-message';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTyping() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Utility functions
    showLoading(message) {
        const tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = `
            <tr>
                <td colspan="100%" class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    ${message}
                </td>
            </tr>
        `;
    }
    
    hideLoading() {
        // Loading will be replaced by actual table content
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showInfo(message) {
        this.showNotification(message, 'info');
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-remove after 5 seconds
        setTimeout(() => this.removeNotification(notification), 5000);
        
        // Add close event
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification);
        });
    }
    
    removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'error': 'fa-times-circle',
            'warning': 'fa-exclamation-triangle',
            'info': 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }
}

// Global function for sample query buttons
function askQuestion(question) {
    document.getElementById('chatInput').value = question;
    document.getElementById('sendBtn').click();
}

// Initialize the app when page loads
document.addEventListener('DOMContentLoaded', () => {
    new DataViewerApp();
});
