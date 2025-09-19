document.addEventListener("DOMContentLoaded", () => {
    // WeatherAPI Configuration
    const key = "005186776a4c4589a6e90608250407"; // IMPORTANT: Add your WeatherAPI key here
    const url = "https://api.weatherapi.com/v1";

    // DOM Element Selections
    const locationInput = document.getElementById('cityInput');
    const searchButton = document.getElementById('search');
    const getCity = document.getElementById('city');
    const getRegion = document.getElementById('region');
    const getCountry = document.getElementById('country');
    const getTemperature = document.getElementById('temperature');
    const getDescription = document.getElementById('description');
    const hourlyForecastContainer = document.getElementById('hour');
    const dayWiseForecastContainer = document.getElementById('day');
    const errorMessageDiv = document.getElementById('error-message');

    // --- THEME TOGGLE ---
    const themeToggle = document.querySelector('.theme-toggle');
    const themeText = document.querySelector('.theme-text');
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        if(themeText) themeText.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
    };
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);


    // --- GEOLOCATION ---
    function getLocation() {
        return new Promise((resolve, reject) => {
            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    (position) => resolve({ lat: position.coords.latitude, lon: position.coords.longitude }),
                    (error) => reject(error)
                );
            } else {
                reject(new Error("Geolocation is not supported."));
            }
        });
    }

    // --- DYNAMIC BACKGROUND ---
    function updateBackground(conditionText) {
        const body = document.body;
        let imageUrl = '';
        const lowerCaseCondition = conditionText.toLowerCase();

        if (lowerCaseCondition.includes('sunny') || lowerCaseCondition.includes('clear')) {
            imageUrl = 'https://i.pinimg.com/originals/30/11/3e/30113e3b3303667c4b31a5f6d2f32386.jpg';
        } else if (lowerCaseCondition.includes('cloudy') || lowerCaseCondition.includes('overcast') || lowerCaseCondition.includes('mist')) {
            imageUrl = 'https://s.itl.cat/pngfile/s/29-298354_dark-clouds-wallpaper-hd-dark-clouds-background.jpg';
        } else if (lowerCaseCondition.includes('rain') || lowerCaseCondition.includes('drizzle')) {
            imageUrl = 'https://i.pinimg.com/originals/e6/94/16/e69416a2b1b5935a8400c4060824b232.jpg';
        } else if (lowerCaseCondition.includes('snow') || lowerCaseCondition.includes('sleet')) {
            imageUrl = 'https://wallpapercave.com/wp/wp7932243.jpg';
        } else if (lowerCaseCondition.includes('thunder') || lowerCaseCondition.includes('storm')) {
            imageUrl = 'https://i.ytimg.com/vi/jJzSU_c-2d4/maxresdefault.jpg';
        } else {
            imageUrl = 'https://www.publicdomainpictures.net/pictures/130000/velka/plain-blue-background.jpg'; // Default
        }
        body.style.backgroundImage = `url('${imageUrl}')`;
    }

    // --- EVENT LISTENERS ---
    searchButton.addEventListener('click', () => {
        const location = locationInput.value.trim();
        if (location) fetchWeather(location);
    });
    locationInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') searchButton.click();
    });

    // --- MAIN FETCH FUNCTION ---
    async function fetchWeather(location) {
        if (!key) {
            Swal.fire('API Key Missing', 'Please add your WeatherAPI key in weather.js', 'error');
            return;
        }
        let query = (typeof location === 'object' && location.lat) ? `${location.lat},${location.lon}` : location;
        const forecastURL = `${url}/forecast.json?key=${key}&q=${query}&days=10&aqi=no&alerts=no`;

        try {
            const response = await fetch(forecastURL);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error.message);
            }
            const data = await response.json();
            displayWeather(data);
            displayHourlyForecast(data);
            displayDaywiseForecast(data);
            updateBackground(data.current.condition.text);
            if (errorMessageDiv) errorMessageDiv.textContent = '';
        } catch (error) {
            console.error("Error fetching data:", error);
            if (errorMessageDiv) errorMessageDiv.textContent = `Error: ${error.message}`;
            Swal.fire('Error', `Could not fetch weather data for "${location}". Please try another city.`, 'error');
        }
    }

    // --- DISPLAY FUNCTIONS ---
    function displayWeather(data) {
        getCity.textContent = data.location.name;
        getRegion.textContent = data.location.region;
        getCountry.textContent = data.location.country;
        getDescription.textContent = data.current.condition.text;

        const tempContent = getTemperature;
        tempContent.innerHTML = `${data.current.temp_c}°C <img src="https:${data.current.condition.icon}" alt="${data.current.condition.text}">`;
    }

    function displayHourlyForecast(data) {
        hourlyForecastContainer.innerHTML = '';
        const allHours = data.forecast.forecastday[0].hour;
        const currentHour = new Date(data.location.localtime).getHours();
        const remainingHours = allHours.filter(hourData => new Date(hourData.time).getHours() >= currentHour);

        remainingHours.forEach(hourData => {
            const hourCard = document.createElement('div');
            hourCard.className = 'hData-card';
            const hour = new Date(hourData.time).getHours();
            const formattedHour = hour === 0 ? '12 AM' : hour > 12 ? `${hour - 12} PM` : `${hour} AM`;
            hourCard.innerHTML = `
                <p class="time">${formattedHour}</p>
                <img src="https:${hourData.condition.icon}" alt="${hourData.condition.text}" />
                <p class="temp">${hourData.temp_c}°C</p>
            `;
            hourlyForecastContainer.appendChild(hourCard);
        });
    }

    function displayDaywiseForecast(data) {
        dayWiseForecastContainer.innerHTML = '';
        data.forecast.forecastday.forEach(forecastData => {
            const forecastCard = document.createElement('div');
            forecastCard.className = 'dayData-card';
            const dayName = new Date(forecastData.date).toLocaleDateString('en-US', { weekday: 'short' });
            forecastCard.innerHTML = `
                <p class="date">${dayName}</p>
                <img src="https:${forecastData.day.condition.icon}" alt="${forecastData.day.condition.text}" />
                <p class="temp">${forecastData.day.maxtemp_c}°C / ${forecastData.day.mintemp_c}°C</p>
            `;
            dayWiseForecastContainer.appendChild(forecastCard);
        });
    }

    // --- INITIAL LOAD ---
    (async () => {
        try {
            const location = await getLocation();
            fetchWeather(location);
        } catch (error) {
            console.warn("Geolocation failed, falling back to New Delhi:", error.message);
            fetchWeather("New Delhi");
        }
    })();
});
