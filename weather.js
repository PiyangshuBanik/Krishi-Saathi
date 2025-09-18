// WeatherAPI Configuration
const key = "005186776a4c4589a6e90608250407";
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
const errorMessageDiv = document.getElementById('error-message'); // Assuming you have an error message div in your HTML

// Function to handle fetching the user's current location
async function getLocation() {
    return new Promise((resolve, reject) => {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    resolve({ lat, lon });
                },
                (error) => {
                    reject(error);
                }
            );
        } else {
            reject(new Error("Geolocation is not supported by this browser."));
        }
    });
}

// Initial fetch on page load - checks for current location first
window.onload = async () => {
    try {
        const location = await getLocation();
        fetchWeather(location);
    } catch (error) {
        console.warn("Geolocation failed, falling back to default city:", error.message);
        fetchWeather("New Delhi");
    }
};

// Dynamic background based on weather condition
function updateBackground(conditionText) {
    const body = document.body;
    let imageUrl = '';
    const lowerCaseCondition = conditionText.toLowerCase();

    if (lowerCaseCondition.includes('sunny') || lowerCaseCondition.includes('clear') || lowerCaseCondition.includes('sun')) {
        imageUrl = 'https://wallpapers.com/images/hd/sunny-day-wallpaper-f21ok5dhnkco3i5n.jpg';
    } else if (lowerCaseCondition.includes('cloudy') || lowerCaseCondition.includes('overcast') || lowerCaseCondition.includes('mist') || lowerCaseCondition.includes('cloud')) {
        imageUrl = 'https://pics.freeartbackgrounds.com/midle/Cloudy_Sky_Background-1520.jpg';
    } else if (lowerCaseCondition.includes('rain') || lowerCaseCondition.includes('drizzle') || lowerCaseCondition.includes('shower') || lowerCaseCondition.includes('rainy')) {
        imageUrl = 'https://static.vecteezy.com/system/resources/previews/046/982/857/non_2x/monsoon-season-rainy-season-illustration-of-heavy-rain-illustration-of-rain-cloud-vector.jpg';
    } else if (lowerCaseCondition.includes('snow') || lowerCaseCondition.includes('sleet') || lowerCaseCondition.includes('ice') || lowerCaseCondition.includes('snowy')) {
        imageUrl = 'https://images.unsplash.com/photo-1542382441-2a6237890635?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    } else if (lowerCaseCondition.includes('thunder') || lowerCaseCondition.includes('storm') || lowerCaseCondition.includes('thundery') || lowerCaseCondition.includes('stormy')) {
        imageUrl = 'https://images.unsplash.com/photo-1507663249114-1e523a502626?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    } else if (lowerCaseCondition.includes('fog') || lowerCaseCondition.includes('foggy') || lowerCaseCondition.includes('dew') || lowerCaseCondition.includes('dewy')) {
        // Correcting the URL as the original was a link to Unsplash, not an image.
        imageUrl = 'https://images.unsplash.com/photo-1510280455071-876646872589?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D';
    } else {
        imageUrl = 'https://www.transparenttextures.com/patterns/clean-textile.png';
    }

    body.style.backgroundImage = `url('${imageUrl}')`;
    body.style.backgroundSize = 'cover';
    body.style.backgroundPosition = 'center';
    body.style.backgroundRepeat = 'no-repeat';
    body.style.backgroundAttachment = 'fixed';
}

// Event listeners for search functionality
searchButton.addEventListener('click', () => {
    const location = locationInput.value.trim();
    if (location) {
        fetchWeather(location);
    }
});

locationInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchButton.click();
    }
});

// Main function to fetch all weather data
async function fetchWeather(location) {
    let query;
    if (typeof location === 'object' && location !== null) {
        // Use coordinates
        query = `${location.lat},${location.lon}`;
    } else {
        // Use location name
        query = location;
    }

    // A single API call to get current, hourly, and 10-day forecast
    const forecastURL = `${url}/forecast.json?key=${key}&q=${query}&days=10&aqi=no&alerts=no`;

    try {
        const response = await fetch(forecastURL);
        if (!response.ok) {
            // Handle HTTP errors
            const errorData = await response.json();
            throw new Error(`Weather data not found for ${query}. Error: ${errorData.error.message}`);
        }
        const data = await response.json();

        // Call display functions with the fetched data
        displayWeather(data);
        displayHourlyForecast(data);
        displayDaywiseForecast(data);

        // Update background based on current weather condition
        updateBackground(data.current.condition.text);
        
        // Clear any previous error messages
        if (errorMessageDiv) errorMessageDiv.textContent = '';
    } catch (error) {
        console.error("Error fetching data:", error);
        if (errorMessageDiv) {
             errorMessageDiv.textContent = error.message;
        } else {
            alert(error.message);
        }
    }
}

// Display current weather
function displayWeather(data) {
    getCity.textContent = data.location.name;
    getRegion.textContent = data.location.region;
    getCountry.textContent = data.location.country;
    getTemperature.textContent = `${data.current.temp_c}°C`;
    getDescription.textContent = data.current.condition.text;

    // Remove existing icon before adding a new one
    const existingIcon = getTemperature.querySelector('img');
    if (existingIcon) {
        existingIcon.remove();
    }
    
    const imageAdd = document.createElement("img");
    imageAdd.src = `https:${data.current.condition.icon}`;
    imageAdd.alt = data.current.condition.text;
    getTemperature.appendChild(imageAdd);
}

// Display hourly forecast for the rest of the current day
function displayHourlyForecast(data) {
    if (!hourlyForecastContainer) return;
    hourlyForecastContainer.innerHTML = '';
    
    const allHours = data.forecast.forecastday[0].hour;
    const currentHour = new Date(data.location.localtime).getHours();

    // Filter hours from now until midnight
    const remainingHours = allHours.filter(hourData => {
        const hour = new Date(hourData.time).getHours();
        return hour >= currentHour;
    });
    
    remainingHours.forEach(hourData => {
        const hourCard = document.createElement('div');
        hourCard.classList.add('hData-card');
        
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

// Display day-wise forecast (10 days)
function displayDaywiseForecast(data) {
    if (!dayWiseForecastContainer) return;
    dayWiseForecastContainer.innerHTML = '';

    const forecastCollection = data.forecast.forecastday;

    forecastCollection.forEach(forecastData => {
        const forecastCard = document.createElement('div');
        forecastCard.classList.add('dayData-card');
        
        const date = new Date(forecastData.date);
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });

        forecastCard.innerHTML = `
            <p class="date">${dayName}</p>
            <img src="https:${forecastData.day.condition.icon}" alt="${forecastData.day.condition.text}" />
            <p class="temp">${forecastData.day.maxtemp_c}°C / ${forecastData.day.mintemp_c}°C </p>
        `;
        dayWiseForecastContainer.appendChild(forecastCard);
    });
}