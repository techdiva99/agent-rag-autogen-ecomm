// CMS Data Agent Dashboard JavaScript

class CMSDashboard {
    constructor() {
        this.apiBaseUrl = this.getApiBaseUrl();
        this.refreshInterval = null;
        this.chart = null;
        
        this.init();
    }
    
    getApiBaseUrl() {
        // Detect deployment environment
        const isLocalhost = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1';
        const isGitHubPages = window.location.hostname.includes('github.io');
        
        if (isLocalhost) {
            // Local development - use local API server
            return 'http://localhost:8000/api';
        } else if (isGitHubPages) {
            // GitHub Pages - use static JSON files
            return './data'; // Relative path to static JSON files
        } else {
            // Production deployment - use deployed API
            return 'https://your-api-domain.com/api'; // Replace with your API URL
        }
    }
    
    isStaticMode() {
        return this.apiBaseUrl === './data';
    }
    
    init() {
        this.bindEvents();
        this.startAutoRefresh();
        this.loadInitialData();
        this.initChart();
    }
    
    bindEvents() {
        // Header buttons
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshData();
        });
        
        document.getElementById('downloadBtn').addEventListener('click', () => {
            this.downloadData();
        });
        
        // Control panel buttons
        document.getElementById('checkUpdatesBtn').addEventListener('click', () => {
            this.checkUpdates();
        });
        
        document.getElementById('validateDataBtn').addEventListener('click', () => {
            this.validateData();
        });
        
        // Auto update toggle
        document.getElementById('autoUpdate').addEventListener('change', (e) => {
            this.toggleAutoUpdate(e.target.checked);
        });
        
        // Update interval change
        document.getElementById('updateInterval').addEventListener('change', (e) => {
            this.setUpdateInterval(parseInt(e.target.value));
        });
        
        // Modal close
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.closeModal();
        });
        
        // Close modal on outside click
        document.getElementById('progressModal').addEventListener('click', (e) => {
            if (e.target.id === 'progressModal') {
                this.closeModal();
            }
        });
    }
    
    async loadInitialData() {
        try {
            await this.refreshData();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to connect to agent. Using demo data.');
            this.loadDemoData();
        }
    }
    
    async refreshData() {
        try {
            this.showLoading();
            
            // Load agent status
            const statusResponse = await this.apiCall('/status');
            if (statusResponse) {
                this.updateAgentStatus(statusResponse);
            }
            
            // Load data statistics
            const statsResponse = await this.apiCall('/data/stats');
            if (statsResponse) {
                this.updateDataStats(statsResponse);
            }
            
            // Load recent activity
            const activityResponse = await this.apiCall('/activity');
            if (activityResponse) {
                this.updateActivity(activityResponse);
            }
            
            // Load data quality metrics
            const qualityResponse = await this.apiCall('/data/quality');
            if (qualityResponse) {
                this.updateDataQuality(qualityResponse);
            }
            
            // Load provider insights
            const insightsResponse = await this.apiCall('/insights');
            if (insightsResponse) {
                this.updateInsights(insightsResponse);
            }
            
            this.hideLoading();
            this.showSuccess('Dashboard updated successfully');
            
        } catch (error) {
            console.error('Failed to refresh data:', error);
            this.hideLoading();
            this.showError('Failed to refresh data from agent');
        }
    }
    
    async apiCall(endpoint) {
        try {
            let url;
            
            if (this.isStaticMode()) {
                // Static mode - map endpoints to JSON files
                const endpointMap = {
                    '/status': '/status.json',
                    '/data/stats': '/stats.json',
                    '/activity': '/activity.json',
                    '/data/quality': '/quality.json',
                    '/insights': '/insights.json'
                };
                
                const jsonFile = endpointMap[endpoint];
                if (!jsonFile) {
                    throw new Error(`Endpoint ${endpoint} not supported in static mode`);
                }
                
                url = `${this.apiBaseUrl}${jsonFile}`;
            } else {
                // API mode - standard endpoint
                url = `${this.apiBaseUrl}${endpoint}`;
            }
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Add timeout
                signal: AbortSignal.timeout(10000)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Handle different data formats
            if (this.isStaticMode() && endpoint === '/activity' && data.activities) {
                return data.activities; // Extract activities array from static JSON
            }
            
            return data;
        } catch (error) {
            if (error.name === 'TimeoutError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    }
    
    updateAgentStatus(data) {
        const statusElement = document.getElementById('agentStatus');
        const statusDot = statusElement.querySelector('.status-dot');
        const statusText = statusElement.querySelector('.status-text');
        
        statusDot.className = `status-dot ${data.status === 'active' ? 'active' : 'inactive'}`;
        statusText.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        
        // Update last seen if available
        if (data.last_seen) {
            const lastSeen = new Date(data.last_seen);
            const timeAgo = this.timeAgo(lastSeen);
            statusText.textContent += ` (${timeAgo})`;
        }
    }
    
    updateDataStats(data) {
        document.getElementById('recordCount').textContent = this.formatNumber(data.record_count || 0);
        document.getElementById('dataSize').textContent = this.formatBytes(data.data_size || 0);
        
        if (data.last_update) {
            const lastUpdate = new Date(data.last_update);
            document.getElementById('lastUpdate').textContent = this.timeAgo(lastUpdate);
        }
    }
    
    updateActivity(activities) {
        const activityList = document.getElementById('activityList');
        activityList.innerHTML = '';
        
        activities.slice(0, 5).forEach(activity => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            
            const iconClass = this.getActivityIcon(activity.type);
            const timeAgo = this.timeAgo(new Date(activity.timestamp));
            
            activityItem.innerHTML = `
                <div class="activity-icon ${activity.type}">
                    <i class="fas ${iconClass}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.message}</div>
                    <div class="activity-time">${timeAgo}</div>
                </div>
            `;
            
            activityList.appendChild(activityItem);
        });
    }
    
    updateDataQuality(quality) {
        const qualityMetrics = ['completeness', 'validity', 'freshness'];
        
        qualityMetrics.forEach(metric => {
            const percentage = quality[metric] || 0;
            const qualityFill = document.querySelector(`.quality-item:nth-child(${qualityMetrics.indexOf(metric) + 1}) .quality-fill`);
            const qualityValue = document.querySelector(`.quality-item:nth-child(${qualityMetrics.indexOf(metric) + 1}) .quality-value`);
            
            if (qualityFill && qualityValue) {
                qualityFill.style.width = `${percentage}%`;
                qualityValue.textContent = `${percentage}%`;
            }
        });
    }
    
    updateInsights(insights) {
        // Update chart data
        if (this.chart && insights.rating_distribution) {
            this.chart.data.datasets[0].data = Object.values(insights.rating_distribution);
            this.chart.update();
        }
        
        // Update top performers
        if (insights.top_performers) {
            const topPerformers = document.getElementById('topPerformers');
            topPerformers.innerHTML = '';
            
            insights.top_performers.slice(0, 3).forEach((provider, index) => {
                const performerItem = document.createElement('div');
                performerItem.className = 'performer-item';
                
                const stars = '⭐'.repeat(Math.round(provider.rating || 5));
                
                performerItem.innerHTML = `
                    <div class="performer-rank">${index + 1}</div>
                    <div class="performer-info">
                        <div class="performer-name">${provider.name || `Provider ${provider.id}`}</div>
                        <div class="performer-rating">
                            <span class="stars">${stars}</span>
                            <span class="surveys">${this.formatNumber(provider.survey_count || 0)} surveys</span>
                        </div>
                    </div>
                `;
                
                topPerformers.appendChild(performerItem);
            });
        }
    }
    
    async downloadData() {
        try {
            if (this.isStaticMode()) {
                // Static mode - simulate download
                this.showProgress('Simulating download...', 0);
                await new Promise(resolve => setTimeout(resolve, 1000));
                this.updateProgress(50, 'Processing...');
                await new Promise(resolve => setTimeout(resolve, 1000));
                this.updateProgress(100, 'Download complete! (Simulated)');
                setTimeout(() => {
                    this.closeModal();
                    this.showInfo('Demo mode: Download simulation completed');
                }, 2000);
                return;
            }
            
            this.showProgress('Downloading data...', 0);
            
            const response = await this.apiCall('/data/download');
            
            if (response.success) {
                this.updateProgress(100, 'Download complete!');
                setTimeout(() => {
                    this.closeModal();
                    this.showSuccess('Data download initiated successfully');
                }, 2000);
            } else {
                throw new Error(response.message || 'Download failed');
            }
            
        } catch (error) {
            console.error('Download failed:', error);
            this.updateProgress(0, 'Download failed');
            setTimeout(() => {
                this.closeModal();
                this.showError('Failed to download data: ' + error.message);
            }, 2000);
        }
    }
    
    async checkUpdates() {
        try {
            if (this.isStaticMode()) {
                // Static mode - simulate update check
                this.showProgress('Checking for updates...', 0);
                await new Promise(resolve => setTimeout(resolve, 1500));
                this.updateProgress(100, 'No updates available (Demo)');
                setTimeout(() => {
                    this.closeModal();
                    this.showInfo('Demo mode: Data is up to date');
                }, 2000);
                return;
            }
            
            this.showProgress('Checking for updates...', 0);
            
            const response = await this.apiCall('/data/check-updates');
            
            if (response.updates_available) {
                this.updateProgress(100, 'Updates available!');
                setTimeout(() => {
                    this.closeModal();
                    this.showSuccess('Updates available. Download will start automatically.');
                }, 2000);
            } else {
                this.updateProgress(100, 'No updates available');
                setTimeout(() => {
                    this.closeModal();
                    this.showInfo('Data is up to date');
                }, 2000);
            }
            
        } catch (error) {
            console.error('Update check failed:', error);
            this.updateProgress(0, 'Update check failed');
            setTimeout(() => {
                this.closeModal();
                this.showError('Failed to check for updates: ' + error.message);
            }, 2000);
        }
    }
    
    async validateData() {
        try {
            if (this.isStaticMode()) {
                // Static mode - simulate validation
                this.showProgress('Validating data...', 0);
                await new Promise(resolve => setTimeout(resolve, 1500));
                this.updateProgress(100, 'Validation successful! (Demo)');
                setTimeout(() => {
                    this.closeModal();
                    this.showSuccess('Demo mode: Data validation passed. 12,068 records validated.');
                }, 2000);
                return;
            }
            
            this.showProgress('Validating data...', 0);
            
            const response = await this.apiCall('/data/validate');
            
            if (response.valid) {
                this.updateProgress(100, 'Validation successful!');
                setTimeout(() => {
                    this.closeModal();
                    this.showSuccess(`Data validation passed. ${response.record_count} records validated.`);
                }, 2000);
            } else {
                this.updateProgress(100, 'Validation issues found');
                setTimeout(() => {
                    this.closeModal();
                    this.showWarning(`Validation found ${response.issues} issues. Check logs for details.`);
                }, 2000);
            }
            
        } catch (error) {
            console.error('Validation failed:', error);
            this.updateProgress(0, 'Validation failed');
            setTimeout(() => {
                this.closeModal();
                this.showError('Failed to validate data: ' + error.message);
            }, 2000);
        }
    }
    
    toggleAutoUpdate(enabled) {
        if (enabled) {
            this.startAutoRefresh();
            this.showSuccess('Auto-update enabled');
        } else {
            this.stopAutoRefresh();
            this.showInfo('Auto-update disabled');
        }
    }
    
    setUpdateInterval(hours) {
        this.stopAutoRefresh();
        this.startAutoRefresh(hours * 60 * 60 * 1000); // Convert hours to milliseconds
        this.showInfo(`Update interval set to ${hours} hour${hours > 1 ? 's' : ''}`);
    }
    
    startAutoRefresh(interval = 5 * 60 * 1000) { // Default 5 minutes
        this.stopAutoRefresh();
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, interval);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    initChart() {
        const ctx = document.getElementById('ratingChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars'],
                datasets: [{
                    data: [156, 425, 1203, 3845, 6439], // Demo data
                    backgroundColor: [
                        '#ef4444', // Red
                        '#f59e0b', // Orange
                        '#eab308', // Yellow
                        '#22c55e', // Green
                        '#10b981'  // Emerald
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Utility functions
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    }
    
    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    timeAgo(date) {
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }
    
    getActivityIcon(type) {
        const icons = {
            'success': 'fa-check-circle',
            'info': 'fa-info-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle',
            'download': 'fa-download',
            'update': 'fa-sync-alt'
        };
        return icons[type] || 'fa-info-circle';
    }
    
    // UI feedback functions
    showProgress(message, progress) {
        const modal = document.getElementById('progressModal');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressText.textContent = message;
        progressFill.style.width = `${progress}%`;
        
        modal.style.display = 'flex';
    }
    
    updateProgress(progress, message) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        progressFill.style.width = `${progress}%`;
        progressText.textContent = message;
    }
    
    closeModal() {
        document.getElementById('progressModal').style.display = 'none';
    }
    
    showLoading() {
        document.getElementById('refreshBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing';
        document.getElementById('refreshBtn').disabled = true;
    }
    
    hideLoading() {
        document.getElementById('refreshBtn').innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
        document.getElementById('refreshBtn').disabled = false;
    }
    
    showNotification(message, type = 'info') {
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
    
    showSuccess(message) { this.showNotification(message, 'success'); }
    showError(message) { this.showNotification(message, 'error'); }
    showWarning(message) { this.showNotification(message, 'warning'); }
    showInfo(message) { this.showNotification(message, 'info'); }
    
    // Demo data for when API is not available
    loadDemoData() {
        this.updateAgentStatus({
            status: 'active',
            last_seen: new Date().toISOString()
        });
        
        this.updateDataStats({
            record_count: 12068,
            data_size: 22548578, // ~21.5MB
            last_update: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 hours ago
        });
        
        this.updateActivity([
            {
                type: 'success',
                message: 'Data Download Complete',
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
            },
            {
                type: 'info',
                message: 'Checking for Updates',
                timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString()
            },
            {
                type: 'warning',
                message: 'Validation Warning',
                timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
            }
        ]);
        
        this.updateDataQuality({
            completeness: 98,
            validity: 96,
            freshness: 92
        });
        
        this.updateInsights({
            rating_distribution: {
                '1': 156,
                '2': 425,
                '3': 1203,
                '4': 3845,
                '5': 6439
            },
            top_performers: [
                { id: '257085', name: 'Provider 257085', rating: 5, survey_count: 1553 },
                { id: '557061', name: 'Provider 557061', rating: 5, survey_count: 1546 },
                { id: '397012', name: 'Provider 397012', rating: 5, survey_count: 1240 }
            ]
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new CMSDashboard();
});
