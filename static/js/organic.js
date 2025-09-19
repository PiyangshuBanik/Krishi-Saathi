document.addEventListener("DOMContentLoaded", function () {
    // --- PARTICLES.JS INITIALIZATION ---
    // This is a placeholder configuration. You can customize it.
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            "particles": {
                "number": { "value": 80, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#4caf50" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.5, "random": true },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#66bb6a", "opacity": 0.4, "width": 1 },
                "move": { "enable": true, "speed": 1, "direction": "none", "straight": false }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": { "onhover": { "enable": true, "mode": "repulse" } },
                "modes": { "repulse": { "distance": 60, "duration": 0.4 } }
            },
            "retina_detect": true
        });
    }

    // --- SCROLL PROGRESS INDICATOR ---
    const scrollProgress = document.getElementById("scrollProgress");
    if (scrollProgress) {
        window.addEventListener("scroll", () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            scrollProgress.style.width = scrollPercent + "%";
        });
    }

    // --- INTERSECTION OBSERVER FOR ANIMATIONS ---
    const animatedElements = document.querySelectorAll(".animate-in");
    if (animatedElements.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    // Stagger the animation delay
                    entry.target.style.animationDelay = `${index * 100}ms`;
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedElements.forEach(el => observer.observe(el));
    }
    
    // --- THEME TOGGLE FUNCTIONALITY ---
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');

    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if (themeText) {
            themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
        }
    };

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

});
