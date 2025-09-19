document.addEventListener("DOMContentLoaded", function () {
    // --- DATA ---
    const crops = [
        { crop: "Wheat", sowing: 11, harvesting: 3 },
        { crop: "Rice", sowing: 6, harvesting: 10 },
        { crop: "Maize", sowing: 5, harvesting: 9 },
        { crop: "Barley", sowing: 11, harvesting: 4 },
        { crop: "Sugarcane", sowing: 2, harvesting: 12 },
        { crop: "Cotton", sowing: 6, harvesting: 11 },
        { crop: "Groundnut", sowing: 6, harvesting: 10 },
        { crop: "Soybean", sowing: 6, harvesting: 9 },
        { crop: "Pulses", sowing: 10, harvesting: 3 },
        { crop: "Mustard", sowing: 10, harvesting: 2 },
        { crop: "Sunflower", sowing: 1, harvesting: 4 },
        { crop: "Jute", sowing: 3, harvesting: 7 }
    ];
    const months = ["Crop", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

    // --- DOM ELEMENTS ---
    const calendar = document.getElementById("calendar");
    const cropSelect = document.getElementById("cropSelect");
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');

    // --- THEME MANAGEMENT ---
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    };

    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    // --- CALENDAR RENDERING ---
    function renderCalendar(filter = "all") {
        showLoadingState();
        setTimeout(() => renderCalendarContent(filter), 300);
    }

    function showLoadingState() {
        calendar.innerHTML = `
            <div class="calendar-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading crop data...</div>
            </div>
        `;
    }

    function renderCalendarContent(filter) {
        calendar.innerHTML = "";
        
        months.forEach(month => {
            const div = document.createElement("div");
            div.className = "month";
            div.innerText = month;
            calendar.appendChild(div);
        });

        const filteredCrops = crops.filter(c => filter === "all" || c.crop === filter);

        filteredCrops.forEach(crop => {
            const rowData = Array(13).fill("");
            rowData[0] = crop.crop;
            const start = crop.sowing;
            const end = crop.harvesting < start ? crop.harvesting + 12 : crop.harvesting;

            for (let i = start; i <= end; i++) {
                const monthIndex = i > 12 ? i - 12 : i;
                if (i === start) rowData[monthIndex] = "sow";
                else if (i === end) rowData[monthIndex] = "harvest";
                else rowData[monthIndex] = "grow";
            }

            rowData.forEach((cell, idx) => {
                const div = document.createElement("div");
                if (idx === 0) {
                    div.className = "crop-name";
                    div.innerText = cell;
                } else {
                    div.className = `month-cell ${cell}`;
                    if (cell) {
                        const emoji = cell === 'sow' ? '🌱' : cell === 'harvest' ? '🌾' : '🟩';
                        const text = cell.charAt(0).toUpperCase() + cell.slice(1);
                        div.innerHTML = `
                            <span class="emoji" role="img">${emoji}</span>
                            <div class="tooltip">${text}ing for ${crop.crop}</div>
                        `;
                    }
                }
                calendar.appendChild(div);
            });
        });
    }

    // --- EVENT LISTENERS ---
    cropSelect.addEventListener("change", function () {
        calendar.style.opacity = "0.5";
        calendar.style.transform = "translateY(10px)";
        setTimeout(() => {
            renderCalendar(this.value);
            calendar.style.opacity = "1";
            calendar.style.transform = "translateY(0)";
        }, 300);
    });

    // --- INITIALIZATION ---
    renderCalendar();
});
