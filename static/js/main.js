/**
 * Main JavaScript file for the Library Management System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Initialize date picker fields if any
    initializeDatePickers();

    // Add listener for book search form
    setupSearchForms();

    // Setup confirmation dialogs
    setupConfirmationDialogs();

    // Setup dynamic form for loan creation
    setupLoanForm();
});

/**
 * Initialize date picker fields
 */
function initializeDatePickers() {
    // We're using the built-in date input, not a JavaScript library
    // This is just a placeholder function for future enhancements
}

/**
 * Setup search forms with instant filtering
 */
function setupSearchForms() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            // If we want to implement client-side filtering later,
            // we can add it here
        });
    }

    // Add event listener to category filter if exists
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    }

    // Add event listener to loan status filter if exists
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    }
}

/**
 * Setup confirmation dialogs for delete actions
 */
function setupConfirmationDialogs() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    const returnButtons = document.querySelectorAll('.btn-return');
    returnButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to mark this book as returned?')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Setup loan form with dynamic book and member selection
 */
function setupLoanForm() {
    const bookSelect = document.getElementById('book_id');
    const memberSelect = document.getElementById('member_id');
    
    if (bookSelect && memberSelect) {
        // We could add AJAX book search functionality here in the future
        // For now, we're using the select dropdown populated from the server
    }
}

/**
 * Format a date to a readable string
 * @param {Date} date - The date to format
 * @return {string} - Formatted date string
 */
function formatDate(date) {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }
    
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric'
    };
    
    return date.toLocaleDateString(undefined, options);
}

/**
 * Calculate days between two dates
 * @param {Date} startDate - The start date
 * @param {Date} endDate - The end date
 * @return {number} - Number of days
 */
function daysBetween(startDate, endDate) {
    if (!(startDate instanceof Date)) {
        startDate = new Date(startDate);
    }
    if (!(endDate instanceof Date)) {
        endDate = new Date(endDate);
    }
    
    // Convert both dates to milliseconds
    const startMs = startDate.getTime();
    const endMs = endDate.getTime();
    
    // Calculate the difference in milliseconds
    const differenceMs = endMs - startMs;
    
    // Convert back to days and return
    return Math.round(differenceMs / (1000 * 60 * 60 * 24));
}

/**
 * Check if a string is a valid email
 * @param {string} email - The email to validate
 * @return {boolean} - True if valid email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Display a temporary notification
 * @param {string} message - The message to display
 * @param {string} type - The type of message (success, danger, warning, info)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.setAttribute('role', 'alert');
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to the page
    const container = document.querySelector('.notification-container');
    if (container) {
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 5000);
    }
}
