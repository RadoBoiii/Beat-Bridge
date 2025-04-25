/**
 * BeatBridge - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle platform selection UI enhancements
    setupPlatformSelectors();
    
    // Setup copy to clipboard functionality
    setupClipboardCopy();
    
    // Add smooth scrolling for anchor links
    setupSmoothScrolling();
});

/**
 * Set up platform selection enhancements
 */
function setupPlatformSelectors() {
    const sourcePlatform = document.getElementById('source_platform');
    const destPlatform = document.getElementById('destination_platform');
    
    if (sourcePlatform && destPlatform) {
        // Update URL input placeholder based on selected source platform
        sourcePlatform.addEventListener('change', function() {
            const urlInput = document.getElementById('playlist_url');
            if (!urlInput) return;
            
            const platform = this.value;
            if (platform === 'spotify') {
                urlInput.placeholder = 'https://open.spotify.com/playlist/...';
            } else if (platform === 'apple_music') {
                urlInput.placeholder = 'https://music.apple.com/us/playlist/...';
            } else if (platform === 'youtube_music') {
                urlInput.placeholder = 'https://music.youtube.com/playlist?list=...';
            }
        });
        
        // Prevent selecting the same platform for source and destination
        const form = document.getElementById('playlistForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (sourcePlatform.value === destPlatform.value) {
                    e.preventDefault();
                    
                    // Show error message
                    const errorEl = document.createElement('div');
                    errorEl.className = 'alert alert-danger mt-3 mb-0';
                    errorEl.innerHTML = '<strong>Error:</strong> Source and destination platforms cannot be the same.';
                    
                    // Check if error already exists
                    const existingError = form.querySelector('.alert-danger');
                    if (existingError) {
                        existingError.remove();
                    }
                    
                    form.appendChild(errorEl);
                    
                    // Scroll to error
                    errorEl.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
    }
}

/**
 * Set up clipboard copy functionality
 */
function setupClipboardCopy() {
    // Global clipboard copy function
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text)
            .then(() => {
                showToast('Success', 'Link copied to clipboard!', 'success');
            })
            .catch(err => {
                console.error('Error copying text: ', err);
                showToast('Error', 'Failed to copy link. Please try again.', 'danger');
            });
    };
}

/**
 * Show a toast notification
 */
function showToast(title, message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '11';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastEl = document.createElement('div');
    toastEl.id = toastId;
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}:</strong> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize and show the toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 3000
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Set up smooth scrolling for anchor links
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                
                const targetEl = document.querySelector(this.getAttribute('href'));
                if (targetEl) {
                    targetEl.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

/**
 * Update URL parameter without page refresh
 */
function updateUrlParam(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, '', url);
}

/**
 * Get URL parameter by name
 */
function getUrlParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}