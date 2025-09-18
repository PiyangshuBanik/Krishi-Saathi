// script.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("crop-form");
    const submitBtn = document.getElementById("submit-btn");
    const progressBar = document.getElementById("progress-bar");
    const resultContainer = document.getElementById("result-container");
    const resultText = document.getElementById("result-text");
    const guideContainer = document.getElementById("guide-container");
    const guideTitle = document.getElementById("guide-title");
    const guideTimeline = document.getElementById("guide-timeline");
    const guideHowToPlant = document.getElementById("guide-how-to-plant");
    const guideFertilizer = document.getElementById("guide-fertilizer");
    const guideIdealRainfall = document.getElementById("guide-ideal-rainfall");
    const guidePostHarvest = document.getElementById("guide-post-harvest");

    // --- Form and Progress Bar Logic ---
    function updateProgress() {
        const inputs = form.querySelectorAll("input[required], select[required]");
        const filled = Array.from(inputs).filter(
            (input) => input.value.trim() !== ""
        ).length;
        const progress = (filled / inputs.length) * 100;
        progressBar.style.width = progress + "%";
    }

    function validateField(field) {
        const formGroup = field.closest(".form-group");
        const isValid = field.value.trim() !== "" && field.checkValidity();

        formGroup.classList.remove("error", "success");
        if (field.value.trim() !== "") {
            formGroup.classList.add(isValid ? "success" : "error");
        }

        return isValid;
    }

    form.querySelectorAll("input, select").forEach((field) => {
        field.addEventListener("blur", () => validateField(field));
        field.addEventListener("input", () => {
            if (field.closest(".form-group").classList.contains("error")) {
                validateField(field);
            }
        });
    });

    form.addEventListener("input", updateProgress);
    form.addEventListener("change", updateProgress);
    updateProgress();

    // --- API Call and Response Handling ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fields = form.querySelectorAll("input[required], select[required]");
        let isValid = true;
        fields.forEach((field) => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        if (!isValid) {
            const firstError = form.querySelector(".form-group.error");
            if (firstError) {
                firstError.scrollIntoView({ behavior: "smooth", block: "center" });
            }
            return;
        }

        submitBtn.innerHTML = '<span class="loading"></span> Analyzing Your Farm...';
        submitBtn.disabled = true;

        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            const el = document.getElementsByName(key)[0];
            data[key] = el.type === "number" ? parseFloat(value) : value;
        });

        displayLoading();

        try {
            const response = await fetch("http://localhost:5003/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || "Prediction failed.");
            }

            const result = await response.json();
            
            if (result && result.crop && result.guide) {
                displayResultAndGuide(result.crop, result.guide);
            } else {
                displayError("Failed to get a valid response from the server.");
            }

        } catch (error) {
            console.error("Error connecting to server:", error);
            displayError("Could not connect to the AI service. Please check your network connection.");
        } finally {
            submitBtn.innerHTML = "Get Full Farming Plan";
            submitBtn.disabled = false;
        }
    });

    function displayLoading() {
        resultContainer.classList.remove("hidden");
        resultText.textContent = "Curating your personalized crop guide...";
        guideContainer.classList.add("hidden");
    }

    function displayError(message) {
        resultContainer.classList.remove("hidden");
        resultText.textContent = message;
        guideContainer.classList.add("hidden");
    }

    function formatAIResponse(text) {
        if (!text) return "";
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        formattedText = formattedText.replace(/\n/g, "<br>");
        return formattedText;
    }

    function displayResultAndGuide(cropName, guide) {
        resultContainer.classList.remove("hidden");
        resultText.textContent = cropName;

        guideTitle.textContent = guide.title;
        guideTimeline.innerHTML = formatAIResponse(guide.timeline);
        guideHowToPlant.innerHTML = formatAIResponse(guide.how_to_plant);
        guideFertilizer.innerHTML = formatAIResponse(guide.fertilizer);
        guideIdealRainfall.innerHTML = formatAIResponse(guide.ideal_rainfall);
        guidePostHarvest.innerHTML = formatAIResponse(guide.post_harvest);

        guideContainer.classList.remove("hidden");
        resultContainer.scrollIntoView({ behavior: "smooth" });
    }

    // --- THREE.js Animation ---
    let scene, camera, renderer, particles;
    function initThreeJS() {
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.z = 50;

        renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById("three-canvas"),
            alpha: true,
            antialias: true,
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 0);

        createParticles();
        animate();
        window.addEventListener("resize", onWindowResize);
    }

    function createParticles() {
        const geometry = new THREE.BufferGeometry();
        const particleCount = 100;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const greenColor = new THREE.Color(0x2e7d32);
        const lightGreenColor = new THREE.Color(0x4caf50);

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 200;
            positions[i3 + 1] = (Math.random() - 0.5) * 200;
            positions[i3 + 2] = (Math.random() - 0.5) * 100;
            const color = Math.random() > 0.5 ? greenColor : lightGreenColor;
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }

        geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        const material = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending,
        });
        particles = new THREE.Points(geometry, material);
        scene.add(particles);
    }

    function animate() {
        requestAnimationFrame(animate);
        if (particles) {
            particles.rotation.x += 0.001;
            particles.rotation.y += 0.002;
        }
        renderer.render(scene, camera);
    }

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    initThreeJS();

    // --- Navbar Scroll Logic ---
    let lastScrollTop = 0;
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            navbar.style.transform = "translateY(-100%)";
        } else {
            navbar.style.transform = "translateY(0)";
        }
        lastScrollTop = scrollTop;
    });
});