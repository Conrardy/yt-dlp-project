// YouTube Audio Downloader - Frontend JavaScript

// DOM Elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const downloadBtn = document.getElementById('download-btn');
const resetBtn = document.getElementById('reset-btn');
const refreshHistoryBtn = document.getElementById('refresh-history-btn');

const inputSection = document.getElementById('input-section');
const videoInfoSection = document.getElementById('video-info-section');
const progressSection = document.getElementById('progress-section');
const historySection = document.getElementById('history-section');

const urlError = document.getElementById('url-error');
const videoThumbnail = document.getElementById('video-thumbnail');
const videoTitle = document.getElementById('video-title');
const videoUploader = document.getElementById('video-uploader');
const videoDuration = document.getElementById('video-duration');
const videoSize = document.getElementById('video-size');
const sizeSeparator = document.getElementById('size-separator');
const videoDescription = document.getElementById('video-description');

const progressFill = document.getElementById('progress-fill');
const progressPercentage = document.getElementById('progress-percentage');
const progressSpeed = document.getElementById('progress-speed');
const progressMessage = document.getElementById('progress-message');
const downloadComplete = document.getElementById('download-complete');
const downloadLink = document.getElementById('download-link');

const historyTbody = document.getElementById('history-tbody');
const historyStats = document.getElementById('history-stats');
const historyLoading = document.getElementById('history-loading');

// State
let currentTaskId = null;
let currentEventSource = null;
let currentVideoInfo = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    
    // Event listeners
    analyzeBtn.addEventListener('click', handleAnalyze);
    downloadBtn.addEventListener('click', handleDownload);
    resetBtn.addEventListener('click', handleReset);
    refreshHistoryBtn.addEventListener('click', loadHistory);
    
    // Enter key support
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleAnalyze();
        }
    });
});

// Handle URL analysis
async function handleAnalyze() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Veuillez entrer une URL YouTube');
        return;
    }
    
    // Hide error
    hideError();
    
    // Disable button
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Analyse en cours...';
    
    try {
        const response = await fetch(`/api/info?url=${encodeURIComponent(url)}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors de l\'analyse de l\'URL');
        }
        
        const videoInfo = await response.json();
        currentVideoInfo = videoInfo;
        displayVideoInfo(videoInfo);
        
    } catch (error) {
        showError(error.message);
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyser';
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyser';
    }
}

// Display video information
function displayVideoInfo(info) {
    videoTitle.textContent = info.title || 'Titre inconnu';
    videoUploader.textContent = info.uploader || 'Auteur inconnu';
    videoDuration.textContent = info.duration_formatted || info.duration || 'Durée inconnue';
    
    if (info.estimated_file_size) {
        videoSize.textContent = `~${info.estimated_file_size}`;
        videoSize.style.display = 'inline';
        sizeSeparator.style.display = 'inline';
    } else {
        videoSize.style.display = 'none';
        sizeSeparator.style.display = 'none';
    }
    
    if (info.thumbnail) {
        videoThumbnail.src = info.thumbnail;
        videoThumbnail.style.display = 'block';
    } else {
        videoThumbnail.style.display = 'none';
    }
    
    if (info.description) {
        videoDescription.textContent = info.description.substring(0, 200) + (info.description.length > 200 ? '...' : '');
        videoDescription.style.display = 'block';
    } else {
        videoDescription.style.display = 'none';
    }
    
    // Show video info section
    videoInfoSection.style.display = 'block';
    
    // Scroll to video info
    videoInfoSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle download
async function handleDownload() {
    if (!currentVideoInfo) {
        showError('Veuillez d\'abord analyser une vidéo');
        return;
    }
    
    const url = urlInput.value.trim();
    
    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Démarrage...';
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur lors du démarrage du téléchargement');
        }
        
        const data = await response.json();
        currentTaskId = data.task_id;
        
        // Show progress section
        progressSection.style.display = 'block';
        downloadComplete.style.display = 'none';
        progressFill.style.width = '0%';
        progressPercentage.textContent = '0%';
        progressSpeed.textContent = '';
        progressMessage.textContent = 'Initialisation...';
        
        // Scroll to progress
        progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Start listening to progress
        startProgressListener(currentTaskId);
        
    } catch (error) {
        showError(error.message);
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Télécharger';
    }
}

// Start progress listener via SSE
function startProgressListener(taskId) {
    // Close existing connection if any
    if (currentEventSource) {
        currentEventSource.close();
    }
    
    const eventSource = new EventSource(`/api/progress/${taskId}`);
    currentEventSource = eventSource;
    
    eventSource.addEventListener('progress', (event) => {
        const progress = JSON.parse(event.data);
        updateProgress(progress);
    });
    
    eventSource.addEventListener('error', (event) => {
        const error = JSON.parse(event.data);
        showError(error.error || 'Erreur lors du téléchargement');
        eventSource.close();
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Télécharger';
    });
    
    eventSource.onerror = () => {
        eventSource.close();
        // Don't show error immediately, might be temporary
    };
}

// Update progress display
function updateProgress(progress) {
    const percentage = progress.percentage || 0;
    progressFill.style.width = `${percentage}%`;
    progressPercentage.textContent = `${percentage.toFixed(1)}%`;
    
    if (progress.speed) {
        progressSpeed.textContent = progress.speed;
    }
    
    if (progress.message) {
        progressMessage.textContent = progress.message;
    }
    
    if (progress.status === 'finished') {
        // Download complete
        progressFill.style.width = '100%';
        progressPercentage.textContent = '100%';
        progressMessage.textContent = 'Téléchargement terminé !';
        
        if (progress.filename) {
            downloadLink.href = `/api/downloads/${encodeURIComponent(progress.filename)}`;
            downloadComplete.style.display = 'block';
        }
        
        // Reload history
        loadHistory();
        
        // Close event source
        if (currentEventSource) {
            currentEventSource.close();
            currentEventSource = null;
        }
        
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Télécharger';
        
    } else if (progress.status === 'error') {
        showError(progress.message || 'Erreur lors du téléchargement');
        
        if (currentEventSource) {
            currentEventSource.close();
            currentEventSource = null;
        }
        
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Télécharger';
    }
}

// Handle reset
function handleReset() {
    urlInput.value = '';
    currentVideoInfo = null;
    videoInfoSection.style.display = 'none';
    progressSection.style.display = 'none';
    hideError();
    
    if (currentEventSource) {
        currentEventSource.close();
        currentEventSource = null;
    }
    
    urlInput.focus();
}

// Load download history
async function loadHistory() {
    historyLoading.style.display = 'block';
    
    try {
        // Load stats
        const statsResponse = await fetch('/api/stats');
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            historyStats.innerHTML = `
                <span><strong>${stats.total_downloads}</strong> téléchargements</span>
                <span><strong>${stats.total_size_mb} MB</strong> au total</span>
            `;
        }
        
        // Load history
        const response = await fetch('/api/history?limit=50');
        
        if (!response.ok) {
            throw new Error('Erreur lors du chargement de l\'historique');
        }
        
        const history = await response.json();
        displayHistory(history);
        
    } catch (error) {
        console.error('Error loading history:', error);
        historyTbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">Erreur lors du chargement de l'historique</td>
            </tr>
        `;
    } finally {
        historyLoading.style.display = 'none';
    }
}

// Display history
function displayHistory(history) {
    if (history.length === 0) {
        historyTbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">Aucun téléchargement pour le moment</td>
            </tr>
        `;
        return;
    }
    
    historyTbody.innerHTML = history.map(item => {
        const date = new Date(item.download_date);
        const formattedDate = date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <tr>
                <td>${formattedDate}</td>
                <td>${escapeHtml(item.title)}</td>
                <td>${item.duration || '-'}</td>
                <td>${escapeHtml(item.uploader || '-')}</td>
                <td class="history-actions">
                    <a href="/api/downloads/${encodeURIComponent(item.filename)}" 
                       class="btn btn-download" 
                       download>
                        📥 Télécharger
                    </a>
                </td>
            </tr>
        `;
    }).join('');
}

// Show error message
function showError(message) {
    urlError.textContent = message;
    urlError.style.display = 'block';
}

// Hide error message
function hideError() {
    urlError.style.display = 'none';
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
