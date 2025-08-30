// Upload Detection JavaScript functionality

let selectedFile = null;
let analysisResults = null;
let isAnalyzing = false;

// Utility functions (fallback if main.js not loaded)
function showNotification(message, type = 'info', duration = 3000) {
    console.log(`${type.toUpperCase()}: ${message}`);
    // Try to use the main app notification if available
    if (window.violenceDetectionApp && window.violenceDetectionApp.showNotification) {
        window.violenceDetectionApp.showNotification(message, type, duration);
    } else {
        alert(message);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// DOM elements
const uploadArea = document.getElementById('upload-area');
const videoInput = document.getElementById('video-input');
const browseBtn = document.getElementById('browse-btn');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const removeFileBtn = document.getElementById('remove-file');
const analyzeBtn = document.getElementById('analyze-btn');
const progressSection = document.getElementById('progress-section');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const analysisResultsSection = document.getElementById('analysis-results');
const errorSection = document.getElementById('error-section');
const errorMessage = document.getElementById('error-message');
const retryBtn = document.getElementById('retry-btn');

// Result elements
const overallVerdict = document.getElementById('overall-verdict');
const verdictStatus = document.getElementById('verdict-status');
const verdictConfidence = document.getElementById('verdict-confidence');
const totalFrames = document.getElementById('total-frames');
const analyzedFrames = document.getElementById('analyzed-frames');
const violentFrames = document.getElementById('violent-frames');
const violencePercentage = document.getElementById('violence-percentage');
const detectionTimeline = document.getElementById('detection-timeline');

// Export buttons
const exportJson = document.getElementById('export-json');
const exportCsv = document.getElementById('export-csv');
const exportPdf = document.getElementById('export-pdf');

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Upload detection page loaded');
    console.log('Elements found:', {
        uploadArea: !!uploadArea,
        videoInput: !!videoInput,
        browseBtn: !!browseBtn,
        analyzeBtn: !!analyzeBtn
    });
    
    setupEventListeners();
    setupDragAndDrop();
    resetUI();
});

// Setup event listeners
function setupEventListeners() {
    browseBtn.addEventListener('click', () => videoInput.click());
    videoInput.addEventListener('change', handleFileSelect);
    removeFileBtn.addEventListener('click', removeFile);
    analyzeBtn.addEventListener('click', analyzeVideo);
    retryBtn.addEventListener('click', retryAnalysis);
    
    // Export handlers
    exportJson.addEventListener('click', () => exportReport('json'));
    exportCsv.addEventListener('click', () => exportReport('csv'));
    exportPdf.addEventListener('click', () => exportReport('pdf'));
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => videoInput.click());
}

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

// Handle drag leave
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

// Handle drop
function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect({ target: { files } });
    }
}

// Handle file selection
function handleFileSelect(e) {
    console.log('File selection triggered', e);
    const file = e.target.files[0];
    
    if (!file) {
        console.log('No file selected');
        return;
    }
    
    console.log('File selected:', file.name, 'Type:', file.type, 'Size:', file.size);
    
    // Validate file type
    const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/quicktime'];
    if (!allowedTypes.some(type => file.type.includes(type.split('/')[1]) || file.name.toLowerCase().includes(type.split('/')[1]))) {
        console.log('Invalid file type:', file.type);
        showNotification('Please select a valid video file (MP4, AVI, MOV, WMV)', 'error');
        return;
    }
    
    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
        console.log('File too large:', file.size);
        showNotification('File size must be less than 100MB', 'error');
        return;
    }
    
    console.log('File validation passed, showing file info');
    selectedFile = file;
    showFileInfo(file);
}

// Show file information
function showFileInfo(file) {
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadArea.style.display = 'none';
    fileInfo.classList.remove('hidden');
    
    // Reset results
    hideAllSections();
}

// Remove file
function removeFile() {
    selectedFile = null;
    videoInput.value = '';
    
    uploadArea.style.display = 'block';
    fileInfo.classList.add('hidden');
    
    hideAllSections();
}

// Analyze video
async function analyzeVideo() {
    console.log('Analyze video called', { selectedFile, isAnalyzing });
    
    if (!selectedFile || isAnalyzing) {
        console.log('Cannot analyze - no file or already analyzing');
        return;
    }
    
    console.log('Starting video analysis for:', selectedFile.name);
    isAnalyzing = true;
    
    // Show progress section
    progressSection.classList.remove('hidden');
    hideAllSections();
    
    // Disable analyze button
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-cog fa-spin"></i> Analyzing...';
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('video', selectedFile);
        
        console.log('Sending video to server...');
        
        // Start progress animation
        animateProgress();
        
        // Upload and analyze
        const response = await fetch('/upload_video', {
            method: 'POST',
            body: formData
        });
        
        console.log('Server response status:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Server error:', errorData);
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const result = await response.json();
        console.log('Analysis result:', result);
        
        if (result.success) {
            analysisResults = result.results;
            showAnalysisResults(result.results);
            showNotification('Video analysis completed successfully!', 'success');
        } else {
            throw new Error(result.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showAnalysisError(error.message);
        showNotification('Analysis failed: ' + error.message, 'error');
    } finally {
        isAnalyzing = false;
        progressSection.classList.add('hidden');
        
        // Re-enable analyze button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-play"></i> Start Analysis';
    }
}

// Animate progress
function animateProgress() {
    let progress = 0;
    const messages = [
        'Uploading video...',
        'Extracting frames...',
        'Analyzing motion patterns...',
        'Detecting violence indicators...',
        'Processing results...',
        'Finalizing analysis...'
    ];
    
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 95) progress = 95;
        
        progressFill.style.width = `${progress}%`;
        
        const messageIndex = Math.floor((progress / 100) * messages.length);
        if (messageIndex < messages.length) {
            progressText.textContent = messages[messageIndex];
        }
        
        if (!isAnalyzing) {
            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = 'Analysis complete';
        }
    }, 500);
}

// Show analysis results
function showAnalysisResults(results) {
    hideAllSections();
    analysisResultsSection.classList.remove('hidden');
    
    // Update overall verdict
    const isViolent = results.is_violent_video;
    const confidence = Math.round((results.violence_percentage || 0));
    
    verdictStatus.textContent = isViolent ? 'Violence Detected' : 'Safe';
    verdictStatus.className = `verdict-status ${isViolent ? 'danger' : 'safe'}`;
    verdictConfidence.textContent = `Confidence: ${confidence}%`;
    
    // Update verdict icon
    const verdictIcon = overallVerdict.querySelector('.verdict-icon');
    verdictIcon.className = `verdict-icon ${isViolent ? 'danger' : 'safe'}`;
    verdictIcon.innerHTML = `<i class="fas fa-${isViolent ? 'exclamation-triangle' : 'shield-alt'}"></i>`;
    
    // Update metrics
    totalFrames.textContent = results.total_frames.toLocaleString();
    analyzedFrames.textContent = results.analyzed_frames.toLocaleString();
    violentFrames.textContent = results.violent_frames.toLocaleString();
    violencePercentage.textContent = `${Math.round(results.violence_percentage)}%`;
    
    // Update timeline
    updateDetectionTimeline(results.frame_results || []);
}

// Update detection timeline
function updateDetectionTimeline(frameResults) {
    detectionTimeline.innerHTML = '';
    
    if (frameResults.length === 0) {
        detectionTimeline.innerHTML = `
            <div class="timeline-empty">
                <i class="fas fa-info-circle"></i>
                <p>No detailed frame data available</p>
            </div>
        `;
        return;
    }
    
    frameResults.forEach(frame => {
        const timelineItem = document.createElement('div');
        timelineItem.className = `timeline-item ${frame.is_violent ? 'danger' : 'safe'}`;
        
        const timestamp = formatTime(Math.floor(frame.timestamp));
        const confidence = Math.round(frame.confidence * 100);
        
        timelineItem.innerHTML = `
            <div class="timeline-item-time">${timestamp}</div>
            <div class="timeline-item-status">${frame.is_violent ? 'Violence' : 'Safe'}</div>
            <div class="timeline-item-confidence">${confidence}% confidence</div>
        `;
        
        detectionTimeline.appendChild(timelineItem);
    });
}

// Show analysis error
function showAnalysisError(message) {
    hideAllSections();
    errorSection.classList.remove('hidden');
    errorMessage.textContent = message;
}

// Retry analysis
function retryAnalysis() {
    if (selectedFile) {
        analyzeVideo();
    }
}

// Hide all result sections
function hideAllSections() {
    progressSection.classList.add('hidden');
    analysisResultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
}

// Reset UI
function resetUI() {
    hideAllSections();
    fileInfo.classList.add('hidden');
    uploadArea.style.display = 'block';
    
    // Reset form
    videoInput.value = '';
    selectedFile = null;
    analysisResults = null;
}

// Export report
function exportReport(format) {
    if (!analysisResults) {
        showNotification('No analysis results to export', 'error');
        return;
    }
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `violence_detection_report_${timestamp}`;
    
    switch (format) {
        case 'json':
            exportAsJson(filename);
            break;
        case 'csv':
            exportAsCsv(filename);
            break;
        case 'pdf':
            exportAsPdf(filename);
            break;
    }
}

// Export as JSON
function exportAsJson(filename) {
    const reportData = {
        analysis_info: {
            file_name: selectedFile?.name || 'unknown',
            file_size: selectedFile?.size || 0,
            analysis_date: new Date().toISOString(),
            total_frames: analysisResults.total_frames,
            analyzed_frames: analysisResults.analyzed_frames,
            violent_frames: analysisResults.violent_frames,
            violence_percentage: analysisResults.violence_percentage,
            is_violent_video: analysisResults.is_violent_video
        },
        frame_results: analysisResults.frame_results || []
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    downloadFile(blob, `${filename}.json`);
    
    showNotification('JSON report exported successfully', 'success');
}

// Export as CSV
function exportAsCsv(filename) {
    let csvContent = 'Frame,Timestamp,Is_Violent,Confidence\n';
    
    if (analysisResults.frame_results) {
        analysisResults.frame_results.forEach(frame => {
            csvContent += `${frame.frame},${frame.timestamp},${frame.is_violent},${frame.confidence}\n`;
        });
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadFile(blob, `${filename}.csv`);
    
    showNotification('CSV report exported successfully', 'success');
}

// Export as PDF (simplified text-based)
function exportAsPdf(filename) {
    let pdfContent = `Violence Detection Report\n`;
    pdfContent += `Generated: ${new Date().toLocaleString()}\n\n`;
    pdfContent += `File Information:\n`;
    pdfContent += `- Name: ${selectedFile?.name || 'unknown'}\n`;
    pdfContent += `- Size: ${selectedFile ? formatFileSize(selectedFile.size) : 'unknown'}\n\n`;
    pdfContent += `Analysis Results:\n`;
    pdfContent += `- Total Frames: ${analysisResults.total_frames}\n`;
    pdfContent += `- Analyzed Frames: ${analysisResults.analyzed_frames}\n`;
    pdfContent += `- Violent Frames: ${analysisResults.violent_frames}\n`;
    pdfContent += `- Violence Percentage: ${Math.round(analysisResults.violence_percentage)}%\n`;
    pdfContent += `- Overall Verdict: ${analysisResults.is_violent_video ? 'Violence Detected' : 'Safe'}\n\n`;
    
    if (analysisResults.frame_results && analysisResults.frame_results.length > 0) {
        pdfContent += `Frame-by-Frame Results:\n`;
        analysisResults.frame_results.forEach(frame => {
            const timestamp = formatTime(Math.floor(frame.timestamp));
            const confidence = Math.round(frame.confidence * 100);
            pdfContent += `${timestamp}: ${frame.is_violent ? 'Violence' : 'Safe'} (${confidence}%)\n`;
        });
    }
    
    const blob = new Blob([pdfContent], { type: 'text/plain' });
    downloadFile(blob, `${filename}.txt`);
    
    showNotification('Text report exported successfully', 'success');
}

// Download file helper
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Export for debugging
window.uploadDetection = {
    selectedFile,
    analysisResults,
    analyzeVideo,
    exportReport
};
