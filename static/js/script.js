document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const scrollBtn = document.getElementById("scrollBtn");
    const scrollIcon = document.getElementById("scrollIcon");
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');
    const htmlEl = document.documentElement;

    // --- Theme Toggle Functionality ---
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlEl.setAttribute('data-theme', savedTheme);
    if (themeText) {
        themeText.textContent = savedTheme.charAt(0).toUpperCase() + savedTheme.slice(1);
    }
    
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlEl.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        htmlEl.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        if (themeText) {
            themeText.textContent = newTheme.charAt(0).toUpperCase() + newTheme.slice(1);
        }
    });

    // --- Scroll Button Functionality ---
    const handleScroll = () => {
        const isNearTop = window.scrollY < 300;
        const isAtBottom = (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 2;

        if (window.scrollY > 100) {
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
    
    window.addEventListener("scroll", handleScroll);

    scrollBtn.addEventListener("click", () => {
        if (scrollIcon.classList.contains("fa-arrow-down")) {
            window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
        } else {
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    });

    // --- Initial Load Animation ---
    window.addEventListener("load", () => {
        document.body.style.animation = "fadeIn 0.8s ease forwards";
    });

    // --- Intersection Observer for Section Animations ---
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                // This assumes your CSS has animations that are paused initially
                entry.target.style.animationPlayState = "running";
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

    document.querySelectorAll("section").forEach((section) => {
        sectionObserver.observe(section);
    });

    // --- Ripple Effect for Cards ---
    document.querySelectorAll(".feature-card").forEach((item) => {
        item.addEventListener("click", function (e) {
            const ripple = document.createElement("div");
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(76, 175, 80, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
                z-index: 1;
            `;
            
            // Add a keyframe animation for the ripple
            const styleSheet = document.styleSheets[0];
            const keyframes = `
                @keyframes ripple {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }`;
            if (styleSheet) {
                 try {
                     styleSheet.insertRule(keyframes, styleSheet.cssRules.length);
                 } catch(e) {
                    console.warn("Could not insert ripple keyframe.", e)
                 }
            }
           
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});
