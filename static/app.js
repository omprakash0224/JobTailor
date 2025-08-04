// Job Application Assistant - Client-side JavaScript

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-resize textareas
    autoResizeTextareas();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize copy functionality
    initializeCopyButtons();
    
    // Character counters for textareas
    initializeCharacterCounters();
}

// Auto-resize textareas based on content
function autoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Initial resize
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    });
}

// Form validation and user experience improvements
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                // Show loading state on submit buttons
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    showLoadingState(submitBtn);
                }
            }
            form.classList.add('was-validated');
        });
    });
}

// Show loading state on buttons
function showLoadingState(button) {
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
    button.disabled = true;
    
    // Store original text for potential restoration
    button.setAttribute('data-original-text', originalText);
}

// Restore button from loading state
function restoreButtonState(button) {
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
        button.removeAttribute('data-original-text');
    }
}

// Initialize copy functionality for code blocks and content
function initializeCopyButtons() {
    // Create copy buttons for pre/code blocks
    const codeBlocks = document.querySelectorAll('pre, .code-block');
    codeBlocks.forEach(block => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary position-absolute top-0 end-0 m-2';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.onclick = () => copyToClipboard(block.textContent, copyBtn);
        
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative';
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);
        wrapper.appendChild(copyBtn);
    });
}

// Enhanced copy to clipboard function
function copyToClipboard(text, button = null) {
    navigator.clipboard.writeText(text).then(function() {
        if (button) {
            showCopySuccess(button);
        }
        showNotification('Content copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Could not copy text: ', err);
        // Fallback for older browsers
        fallbackCopyTextToClipboard(text);
        if (button) {
            showCopySuccess(button);
        }
    });
}

// Fallback copy method for older browsers
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Content copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy content', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Show copy success animation
function showCopySuccess(button) {
    const originalContent = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.classList.remove('btn-outline-secondary');
    button.classList.add('btn-success', 'pulse');
    
    setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove('btn-success', 'pulse');
        button.classList.add('btn-outline-secondary');
    }, 2000);
}

// Character counters for textareas
function initializeCharacterCounters() {
    const textareasWithLimits = document.querySelectorAll('textarea[data-max-length]');
    textareasWithLimits.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.id = textarea.id + '_counter';
        
        const updateCounter = () => {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length}/${maxLength} characters`;
            
            if (remaining < 50) {
                counter.className = 'form-text text-end text-warning';
            } else if (remaining < 0) {
                counter.className = 'form-text text-end text-danger';
            } else {
                counter.className = 'form-text text-end text-muted';
            }
        };
        
        textarea.addEventListener('input', updateCounter);
        textarea.parentNode.appendChild(counter);
        updateCounter();
    });
}

// Show toast notifications
function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast_' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${getIconForType(type)} me-2 text-${type}"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// Get appropriate icon for notification type
function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Smooth scrolling for anchor links
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Enhanced form submission with better UX
function enhanceFormSubmission() {
    const forms = document.querySelectorAll('form[data-enhance="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !form.querySelector(':invalid')) {
                showLoadingState(submitBtn);
                
                // Prevent double submission
                setTimeout(() => {
                    submitBtn.style.pointerEvents = 'none';
                }, 100);
            }
        });
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Auto-save functionality for forms (draft saving)
function initializeAutoSave() {
    const autoSaveForms = document.querySelectorAll('form[data-autosave="true"]');
    autoSaveForms.forEach(form => {
        const formId = form.id || 'form_' + Math.random().toString(36).substr(2, 9);
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`autosave_${formId}_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Save data on input
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                localStorage.setItem(`autosave_${formId}_${input.name}`, input.value);
            }, 1000));
        });
        
        // Clear saved data on successful submission
        form.addEventListener('submit', () => {
            inputs.forEach(input => {
                localStorage.removeItem(`autosave_${formId}_${input.name}`);
            });
        });
    });
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Initialize advanced features
setTimeout(() => {
    initializeSmoothScrolling();
    enhanceFormSubmission();
    initializeAutoSave();
}, 100);

// Export functions for global use
window.JobAssistant = {
    copyToClipboard,
    showNotification,
    showLoadingState,
    restoreButtonState
};
