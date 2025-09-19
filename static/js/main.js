document.addEventListener('DOMContentLoaded', function () {
    // --- ELEMENT SELECTORS ---
    const wrapper = document.querySelector('.header-nav-wrapper');
    const themeToggle = document.querySelector('.theme-toggle');
    const logoutBtn = document.getElementById('logoutBtn');
    const scrollBtn = document.getElementById("scrollBtn");
    const scrollIcon = document.getElementById("scrollIcon");

    // --- THEME MANAGEMENT ---
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    };

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    // Apply saved theme on initial load
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
    
    // --- STICKY HEADER & NAVBAR ---
    let lastScrollTop = 0;
    window.addEventListener('scroll', () => {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollTop > lastScrollTop && scrollTop > 150) {
            // Scroll Down
            wrapper.style.transform = 'translateY(-100%)';
        } else {
            // Scroll Up
            wrapper.style.transform = 'translateY(0)';
        }
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; 
    }, false);

    // --- SCROLL TO TOP/BOTTOM BUTTON ---
    const handleScrollButton = () => {
        const isAtBottom = (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 5;
        
        if (window.scrollY > 200) {
            scrollBtn.classList.add("visible");
        } else {
            scrollBtn.classList.remove("visible");
        }

        if (isAtBottom) {
            scrollIcon.classList.replace("fa-arrow-down", "fa-arrow-up");
        } else {
            scrollIcon.classList.replace("fa-arrow-up", "fa-arrow-down");
        }
    };
    
    window.addEventListener("scroll", handleScrollButton);
    
    scrollBtn.addEventListener("click", () => {
        const isScrollingDown = scrollIcon.classList.contains("fa-arrow-down");
        window.scrollTo({
            top: isScrollingDown ? document.body.scrollHeight : 0,
            behavior: "smooth",
        });
    });

    // --- AUTHENTICATION MANAGER (DISABLED) ---
    /*
    class AuthManager {
        constructor() {
            this.currentUser = this.getCurrentUser();
        }

        getCurrentUser() {
            try {
                const user = localStorage.getItem('Krishi-Saathi_current_user');
                return user ? JSON.parse(user) : null;
            } catch (error) {
                console.error('Error getting current user:', error);
                return null;
            }
        }

        isLoggedIn() {
            return this.currentUser !== null;
        }

        logout() {
            try {
                localStorage.removeItem('Krishi-Saathi_current_user');
                this.currentUser = null;
                return { success: true, message: 'Logged out successfully' };
            } catch (error) {
                console.error('Error during logout:', error);
                return { success: false, message: 'Error during logout' };
            }
        }
    }

    window.authManager = new AuthManager();
    */

    // --- UI MESSAGES ---
    function showAuthMessage(message, type = 'info') {
        const existingMessage = document.querySelector('.auth-message');
        if (existingMessage) existingMessage.remove();

        const messageDiv = document.createElement('div');
        messageDiv.className = `auth-message auth-message-${type}`;
        const iconClass = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';
        messageDiv.innerHTML = `<div class="auth-message-content"><i class="fas ${iconClass}"></i><span>${message}</span></div>`;
        
        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.style.animation = 'slideOutRight 0.3s ease-out forwards';
            messageDiv.addEventListener('animationend', () => messageDiv.remove());
        }, 5000);
    }

    // --- PAGE AUTHENTICATION & UI UPDATES (DISABLED) ---
    /*
    function requireAuth() {
        if (!window.authManager.isLoggedIn()) {
            showAuthMessage('Please log in to access your dashboard.', 'error');
            setTimeout(() => { window.location.href = 'index.html'; }, 2000);
            return false;
        }
        return true;
    }

    // Check auth on page load and update UI
    if (requireAuth()) {
        const currentUser = window.authManager.getCurrentUser();
        if (currentUser && currentUser.fullname) {
            const headerTitle = document.querySelector('header h2');
            if (headerTitle) {
                headerTitle.textContent = `Welcome, ${currentUser.fullname}!`;
            }
        }
    }
    */
    
    // --- LOGOUT FUNCTIONALITY (DISABLED) ---
    /*
    if(logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            Swal.fire({
                title: 'Confirm Logout',
                text: 'Are you sure you want to logout?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Yes, logout',
                background: document.documentElement.getAttribute('data-theme') === 'dark' ? '#2F5249' : '#fff',
                color: document.documentElement.getAttribute('data-theme') === 'dark' ? '#f0f2f5' : '#1e293b'
            }).then((result) => {
                if (result.isConfirmed) {
                    const logoutResult = window.authManager.logout();
                    if (logoutResult.success) {
                        showAuthMessage(logoutResult.message, 'success');
                        setTimeout(() => { window.location.href = 'index.html'; }, 1500);
                    } else {
                        showAuthMessage(logoutResult.message, 'error');
                    }
                }
            });
        });
    }
    */
});

