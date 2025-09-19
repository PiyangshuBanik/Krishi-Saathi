document.addEventListener('DOMContentLoaded', function() {
    // --- ELEMENT SELECTORS ---
    const themeToggle = document.querySelector('.theme-toggle');
    const themeIcon = document.querySelector('.theme-icon');
    const themeText = document.querySelector('.theme-text');
    const feedbackForm = document.getElementById('feedbackForm');
    const thankYouMessage = document.getElementById('thankYouMessage');
    const allFeedbacksSection = document.getElementById('allFeedbacks');
    const viewFeedbacksBtn = document.getElementById('viewFeedbacksBtn');
    const feedbacksList = document.getElementById('feedbacksList');
    const feedbackTextarea = document.getElementById('feedback');
    const charCountElement = document.getElementById('charCount');
    const feedbackMain = document.getElementById('feedback-main');

    // --- THEME MANAGEMENT ---
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (theme === 'dark') {
            themeIcon.classList.replace('fa-sun', 'fa-moon');
            themeText.textContent = 'Dark';
        } else {
            themeIcon.classList.replace('fa-moon', 'fa-sun');
            themeText.textContent = 'Light';
        }
    };
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });
    
    // Apply saved theme on initial load
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // --- CHARACTER COUNT ---
    if (feedbackTextarea && charCountElement) {
        feedbackTextarea.addEventListener('input', function() {
            const charCount = this.value.length;
            charCountElement.textContent = charCount;
            if (charCount > 500) {
                charCountElement.style.color = '#ff7043';
            } else if (charCount > 300) {
                charCountElement.style.color = '#ff9800';
            } else {
                charCountElement.style.color = 'var(--text-muted)';
            }
        });
    }

    // --- FORM SUBMISSION ---
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const feedbackText = feedbackTextarea.value.trim();
        
        if (!name || !feedbackText) {
            Swal.fire({
                title: 'Missing Information',
                text: 'Please fill in all required fields.',
                icon: 'warning',
                confirmButtonColor: '#4caf50'
            });
            return;
        }
        
        const submitButton = this.querySelector('.submit-button');
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Sending...</span>';
        submitButton.disabled = true;
        
        setTimeout(() => {
            const feedbackData = {
                name,
                email: email || 'Not provided',
                feedback: feedbackText,
                date: new Date().toISOString(),
            };
            
            // Save feedback to Local Storage
            const feedbacks = JSON.parse(localStorage.getItem('Krishi-SaathiFeedbacks')) || [];
            feedbacks.push(feedbackData);
            localStorage.setItem('Krishi-SaathiFeedbacks', JSON.stringify(feedbacks));

            // Show success UI
            feedbackMain.classList.add('hidden');
            thankYouMessage.classList.remove('hidden');
            feedbackForm.reset();
            if (charCountElement) charCountElement.textContent = '0';
            
            submitButton.innerHTML = '<i class="fas fa-paper-plane"></i><span>Share Feedback</span>';
            submitButton.disabled = false;
        }, 1500);
    });
    
    // --- VIEW ALL FEEDBACKS ---
    function showAllFeedbacks() {
        feedbackMain.classList.add('hidden');
        thankYouMessage.classList.add('hidden');
        allFeedbacksSection.classList.remove('hidden');
        
        const allFeedbacks = JSON.parse(localStorage.getItem('Krishi-SaathiFeedbacks')) || [];
        
        if (allFeedbacks.length === 0) {
            feedbacksList.innerHTML = `<div class="no-feedback"><p>No feedback submissions yet.</p></div>`;
            return;
        }

        allFeedbacks.sort((a, b) => new Date(b.date) - new Date(a.date));

        feedbacksList.innerHTML = allFeedbacks.map(fb => `
            <div class="feedback-item">
                <h4><i class="fas fa-user-circle"></i> ${escapeHtml(fb.name)}</h4>
                <p>${escapeHtml(fb.feedback)}</p>
                <div class="feedback-meta">
                    <span>${new Date(fb.date).toLocaleString()}</span>
                </div>
            </div>
        `).join('');
    }

    if (viewFeedbacksBtn) {
        viewFeedbacksBtn.addEventListener('click', showAllFeedbacks);
    }
    
    // --- UTILITY ---
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
