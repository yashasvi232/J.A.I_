// Authentication functions
function isUserLoggedIn() {
    // Check if user is logged in and has valid token
    const token = localStorage.getItem('access_token');
    const userLoggedIn = localStorage.getItem('userLoggedIn') === 'true';
    return token && userLoggedIn;
}

function redirectToLogin(intendedPage = '') {
    // Store the intended page for redirect after login
    if (intendedPage) {
        localStorage.setItem('redirectAfterLogin', intendedPage);
    }
    window.location.href = 'client-login.html';
}

function checkAuthAndRedirect(targetPage) {
    if (!isUserLoggedIn()) {
        redirectToLogin(targetPage);
        return false;
    }
    return true;
}

function logout() {
    // Clear all authentication data
    localStorage.removeItem('access_token');
    localStorage.removeItem('userLoggedIn');
    localStorage.removeItem('userType');
    localStorage.removeItem('redirectAfterLogin');
    
    // Call logout endpoint
    const token = localStorage.getItem('access_token');
    if (token) {
        fetch('http://localhost:8000/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        }).catch(error => console.log('Logout API call failed:', error));
    }
    
    // Redirect to homepage
    window.location.href = 'index.html';
}

function updateNavigation() {
    const loginLink = document.querySelector('.login-link');
    const navAuth = document.querySelector('.nav-auth');
    
    if (isUserLoggedIn() && loginLink) {
        const userType = localStorage.getItem('userType');
        
        // Update login link to show user type and logout option
        if (userType === 'client') {
            loginLink.innerHTML = '<i class="fas fa-user"></i> Client Dashboard';
            loginLink.href = 'client-dashboard.html';
        } else if (userType === 'lawyer') {
            loginLink.innerHTML = '<i class="fas fa-gavel"></i> Lawyer Dashboard';
            loginLink.href = 'lawyer-dashboard.html';
        }
        
        // Add logout button
        const logoutBtn = document.createElement('a');
        logoutBtn.href = '#';
        logoutBtn.className = 'login-link';
        logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Logout';
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                logout();
            }
        });
        
        // Insert logout button after login link
        if (loginLink.parentNode) {
            loginLink.parentNode.insertBefore(logoutBtn, loginLink.nextSibling);
        }
    }
}

// Add click event listeners for protected navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Update navigation based on login status
    updateNavigation();
    
    // Find Lawyers link protection
    const findLawyersLinks = document.querySelectorAll('a[href="lawyers.html"], a[href*="lawyers.html"]');
    findLawyersLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!isUserLoggedIn()) {
                e.preventDefault();
                redirectToLogin('lawyers.html');
            }
        });
    });

    // Terms link protection
    const termsLinks = document.querySelectorAll('a[href="terms.html"], a[href*="terms.html"]');
    termsLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!isUserLoggedIn()) {
                e.preventDefault();
                redirectToLogin('terms.html');
            }
        });
    });

    // Post a Case button protection
    const postCaseButtons = document.querySelectorAll('a[href="#"]:contains("Post a Case"), .btn:contains("Post a Case")');
    postCaseButtons.forEach(button => {
        if (button.textContent.includes('Post a Case')) {
            button.addEventListener('click', function(e) {
                if (!isUserLoggedIn()) {
                    e.preventDefault();
                    redirectToLogin('post-case.html');
                }
            });
        }
    });
});

// Search form functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default page reload

            // Check if user is logged in before searching
            if (!isUserLoggedIn()) {
                redirectToLogin('lawyers.html');
                return;
            }

            // Get the selected category
            const selectedCategory = document.getElementById('categorySelect').value;
            const searchBtn = document.querySelector('.search-btn');
            const originalText = searchBtn.innerHTML;

            if (selectedCategory) {
                // Add loading state
                searchBtn.innerHTML = '<span class="loading-spinner"></span>Finding Lawyers...';
                searchBtn.classList.add('btn-loading');
                searchBtn.disabled = true;

                // Simulate search delay
                setTimeout(() => {
                    searchBtn.innerHTML = '<i class="fas fa-search"></i> Redirecting...';
                    
                    setTimeout(() => {
                        // Redirect to lawyers.html with the category as a URL parameter
                        window.location.href = `lawyers.html?category=${encodeURIComponent(selectedCategory)}`;
                    }, 500);
                }, 1500);
            } else {
                // Add error animation
                searchBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
                searchBtn.innerHTML = '<i class="fas fa-exclamation"></i> Select Category';
                
                setTimeout(() => {
                    searchBtn.innerHTML = originalText;
                    searchBtn.style.background = '';
                }, 2000);
            }
        });
    }
});