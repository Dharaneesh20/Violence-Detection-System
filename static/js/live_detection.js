// Live Detection JavaScript functionality

let isDetectionActive = false;
let sessionStartTime = null;
let sessionTimer = null;
let confidenceChart = null;
let detectionResultsBuffer = [];
let totalDetections = 0;

// DOM elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const videoFeed = document.getElementById('video-feed');
const videoPlaceholder = document.getElementById('video-placeholder');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const currentStatus = document.getElementById('current-status');
const confidenceValue = document.getElementById('confidence-value');
const totalDetectionsSpan = document.getElementById('total-detections');
const sessionDuration = document.getElementById('session-duration');
const alertLevel = document.getElementById('alert-level');
const detectionLog = document.getElementById('detection-log');
const alertOverlay = document.getElementById('alert-overlay');
const acknowledgeAlert = document.getElementById('acknowledge-alert');

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    setupEventListeners();
    updateUIElements();
});

// Setup event listeners
function setupEventListeners() {
    startBtn.addEventListener('click', startDetection);
    stopBtn.addEventListener('click', stopDetection);
    acknowledgeAlert.addEventListener('click', dismissAlert);
    
    // Handle page visibility change
    document.addEventListener('visibilitychange', function() {
        if (document.hidden && isDetectionActive) {
            console.log('Page hidden, continuing detection in background');
        } else if (!document.hidden && isDetectionActive) {
            console.log('Page visible, resuming UI updates');
        }
    });
}

// Initialize confidence chart
function initializeChart() {
    const canvas = document.getElementById('confidence-chart');
    const ctx = canvas.getContext('2d');
    
    confidenceChart = {
        canvas: canvas,
        ctx: ctx,
        data: [],
        maxDataPoints: 50,
        
        update: function(confidence) {
            this.data.push(confidence);
            if (this.data.length > this.maxDataPoints) {
                this.data.shift();
            }
            this.draw();
        },
        
        draw: function() {
            const width = this.canvas.width;
            const height = this.canvas.height;
            
            // Clear canvas
            this.ctx.clearRect(0, 0, width, height);
            
            if (this.data.length === 0) {
                // Draw empty state
                this.ctx.fillStyle = 'rgba(184, 185, 197, 0.3)';
                this.ctx.font = '16px Arial';
                this.ctx.textAlign = 'center';
                this.ctx.fillText('No data yet', width / 2, height / 2);
                return;
            }
            
            // Draw grid
            this.ctx.strokeStyle = 'rgba(0, 212, 255, 0.1)';
            this.ctx.lineWidth = 1;
            
            // Horizontal lines
            for (let i = 0; i <= 4; i++) {
                const y = (height / 4) * i;
                this.ctx.beginPath();
                this.ctx.moveTo(0, y);
                this.ctx.lineTo(width, y);
                this.ctx.stroke();
            }
            
            // Vertical lines
            for (let i = 0; i <= 10; i++) {
                const x = (width / 10) * i;
                this.ctx.beginPath();
                this.ctx.moveTo(x, 0);
                this.ctx.lineTo(x, height);
                this.ctx.stroke();
            }
            
            // Draw confidence line
            this.ctx.strokeStyle = '#00d4ff';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            
            const pointSpacing = width / (this.maxDataPoints - 1);
            
            this.data.forEach((confidence, index) => {
                const x = index * pointSpacing;
                const y = height - (confidence * height);
                
                if (index === 0) {
                    this.ctx.moveTo(x, y);
                } else {
                    this.ctx.lineTo(x, y);
                }
            });
            
            this.ctx.stroke();
            
            // Draw danger zone
            this.ctx.fillStyle = 'rgba(255, 51, 102, 0.1)';
            this.ctx.fillRect(0, 0, width, height * 0.4);
            
            // Draw safe zone
            this.ctx.fillStyle = 'rgba(0, 255, 136, 0.1)';
            this.ctx.fillRect(0, height * 0.4, width, height * 0.6);
            
            // Draw current value indicator
            if (this.data.length > 0) {
                const lastValue = this.data[this.data.length - 1];
                const x = (this.data.length - 1) * pointSpacing;
                const y = height - (lastValue * height);
                
                this.ctx.fillStyle = lastValue > 0.6 ? '#ff3366' : '#00ff88';
                this.ctx.beginPath();
                this.ctx.arc(x, y, 4, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
    };
    
    // Initial draw
    confidenceChart.draw();
}

// Start detection
async function startDetection() {
    try {
        // Request camera permissions
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop()); // We'll use server-side capture
        
        // Start server-side detection
        const response = await fetch('/start_live_detection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to start detection');
        }
        
        isDetectionActive = true;
        sessionStartTime = Date.now();
        totalDetections = 0;
        detectionResultsBuffer = [];
        
        // Update UI
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
        videoPlaceholder.style.display = 'none';
        videoFeed.style.display = 'block';
        
        // Start video feed
        videoFeed.src = '/video_feed';
        
        // Update status
        updateStatusIndicator(statusIndicator, 'active', 'Active');
        
        // Start session timer
        startSessionTimer();
        
        // Start polling for results
        startResultsPolling();
        
        showNotification('Live detection started successfully!', 'success');
        
    } catch (error) {
        console.error('Error starting detection:', error);
        showNotification('Failed to start detection. Please check camera permissions.', 'error');
    }
}

// Stop detection
async function stopDetection() {
    try {
        const response = await fetch('/stop_live_detection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to stop detection');
        }
        
        isDetectionActive = false;
        
        // Update UI
        startBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'none';
        videoFeed.style.display = 'none';
        videoPlaceholder.style.display = 'flex';
        
        // Stop video feed
        videoFeed.src = '';
        
        // Update status
        updateStatusIndicator(statusIndicator, 'idle', 'Idle');
        
        // Stop session timer
        stopSessionTimer();
        
        // Reset values
        currentStatus.textContent = 'Safe';
        currentStatus.className = 'metric-value safe';
        confidenceValue.textContent = '0%';
        
        showNotification('Live detection stopped', 'info');
        
    } catch (error) {
        console.error('Error stopping detection:', error);
        showNotification('Error stopping detection', 'error');
    }
}

// Start session timer
function startSessionTimer() {
    sessionTimer = setInterval(() => {
        if (sessionStartTime) {
            const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
            sessionDuration.textContent = formatTime(elapsed);
        }
    }, 1000);
}

// Stop session timer
function stopSessionTimer() {
    if (sessionTimer) {
        clearInterval(sessionTimer);
        sessionTimer = null;
    }
}

// Start polling for results
function startResultsPolling() {
    if (!isDetectionActive) return;
    
    fetch('/get_live_results')
        .then(response => response.json())
        .then(data => {
            updateDetectionResults(data);
            
            // Continue polling if detection is active
            if (isDetectionActive) {
                setTimeout(startResultsPolling, 500); // Poll every 500ms
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
            
            // Retry after delay if detection is still active
            if (isDetectionActive) {
                setTimeout(startResultsPolling, 2000);
            }
        });
}

// Update detection results
function updateDetectionResults(data) {
    if (!data.results || data.results.length === 0) return;
    
    const latestResult = data.results[data.results.length - 1];
    
    // Update confidence chart
    confidenceChart.update(latestResult.confidence);
    
    // Update current status
    const isViolent = latestResult.is_violent;
    const confidence = Math.round(latestResult.confidence * 100);
    
    currentStatus.textContent = isViolent ? 'Violence Detected' : 'Safe';
    currentStatus.className = `metric-value ${isViolent ? 'danger' : 'safe'}`;
    confidenceValue.textContent = `${confidence}%`;
    
    // Update total detections
    totalDetections = data.total_detections || 0;
    totalDetectionsSpan.textContent = totalDetections;
    
    // Update alert level
    updateAlertLevel(confidence, isViolent);
    
    // Add to detection log
    addToDetectionLog(latestResult);
    
    // Show alert if violence detected with high confidence
    if (isViolent && latestResult.confidence > 0.8) {
        showViolenceAlert();
    }
}

// Update alert level
function updateAlertLevel(confidence, isViolent) {
    let level, className;
    
    if (isViolent && confidence > 80) {
        level = 'Critical';
        className = 'danger';
    } else if (isViolent && confidence > 60) {
        level = 'High';
        className = 'danger';
    } else if (confidence > 40) {
        level = 'Medium';
        className = 'warning';
    } else {
        level = 'Low';
        className = 'safe';
    }
    
    alertLevel.textContent = level;
    alertLevel.className = `stat-value ${className}`;
}

// Add to detection log
function addToDetectionLog(result) {
    // Remove empty message if it exists
    const emptyMessage = detectionLog.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }
    
    // Create log item
    const logItem = document.createElement('div');
    logItem.className = `log-item ${result.is_violent ? 'danger' : 'safe'}`;
    
    const confidence = Math.round(result.confidence * 100);
    const timestamp = formatTimestamp(result.timestamp);
    
    logItem.innerHTML = `
        <div class="log-item-icon">
            <i class="fas fa-${result.is_violent ? 'exclamation-triangle' : 'check-circle'}"></i>
        </div>
        <div class="log-item-content">
            <div class="log-item-status">${result.is_violent ? 'Violence Detected' : 'Safe'}</div>
            <div class="log-item-details">Confidence: ${confidence}%</div>
        </div>
        <div class="log-item-time">${timestamp}</div>
    `;
    
    // Add to top of log
    detectionLog.insertBefore(logItem, detectionLog.firstChild);
    
    // Keep only last 20 items
    const items = detectionLog.querySelectorAll('.log-item');
    if (items.length > 20) {
        items[items.length - 1].remove();
    }
}

// Show violence alert
function showViolenceAlert() {
    alertOverlay.style.display = 'flex';
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (alertOverlay.style.display === 'flex') {
            dismissAlert();
        }
    }, 10000);
}

// Dismiss alert
function dismissAlert() {
    alertOverlay.style.display = 'none';
}

// Update UI elements
function updateUIElements() {
    // Set initial states
    stopBtn.style.display = 'none';
    videoFeed.style.display = 'none';
    alertOverlay.style.display = 'none';
    
    // Update status indicator
    updateStatusIndicator(statusIndicator, 'idle', 'Idle');
}

// Utility function imports
const { formatTime, formatTimestamp, updateStatusIndicator, showNotification } = window.violenceDetectionApp;

// Handle page unload
window.addEventListener('beforeunload', function(e) {
    if (isDetectionActive) {
        e.preventDefault();
        e.returnValue = 'Detection is currently active. Are you sure you want to leave?';
        return 'Detection is currently active. Are you sure you want to leave?';
    }
});

// Export for debugging
window.liveDetection = {
    isDetectionActive,
    startDetection,
    stopDetection,
    updateDetectionResults
};
