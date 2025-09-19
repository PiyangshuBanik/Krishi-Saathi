Krishi-Saathi 🌱 कृषि-साथी
An intelligent, AI-powered smart farming platform designed to empower Indian farmers with data-driven insights, community support, and modern agricultural tools.

🌾 About The Project
Krishi-Saathi (Agriculture Companion) is a comprehensive digital ecosystem built to address the core challenges faced by farmers in India. From unpredictable weather to market price volatility and crop diseases, farming involves numerous uncertainties. Our platform leverages the power of Artificial Intelligence, Machine Learning, and real-time data to provide actionable advice, helping farmers increase their yield, reduce waste, and improve their profitability.

This project integrates a suite of powerful tools into a user-friendly mobile and web interface, making advanced agricultural technology accessible to every farmer.

✨ Key Features
Our platform is packed with features to assist at every stage of the farming lifecycle:

🌱 Crop Recommendation: AI model that suggests the most suitable crops based on soil type, pH, temperature, rainfall, and location.

📈 Yield Prediction: Forecasts potential crop yield using machine learning algorithms and historical data.

🦠 Plant Disease Detection: Upload an image of a plant leaf to instantly identify diseases and receive suggestions for remedies.

💬 AI Chat Assistant: A 24/7 AI-powered chatbot (using Google Gemini) to answer any farming-related questions, from pest control to organic farming techniques.

💸 Live Crop Price Tracker: Fetches real-time market prices for various crops from different states and markets using the Government of India's public data API.

📅 Smart Crop Planner: An intelligent tool that helps farmers plan their crop cycles and activities for optimal results.

☀️ Weather Forecast: Provides localized and accurate weather predictions to help farmers plan their activities.

🛠️ Tech Stack
This project is built using a modern and robust set of technologies:

Frontend (Mobile App):

Flutter

Dart

Backend & ML Models:

Python

Flask (for serving the API and models)

Pandas & Scikit-learn (for ML models)

AI & Cloud Services:

Google Gemini API: Powers the intelligent Chat Assistant.

Database & APIs:

Govt. of India Data Portal: Used for the Crop Price Tracker.

📸 Screenshots
Dashboard	Crop Recommendation	AI Chat Assistant

Export to Sheets
🚀 Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Make sure you have the following installed on your system:

Git

Python 3.10+ and Pip

Flutter SDK

Installation
Clone the repository

Bash

git clone https://github.com/PiyangshuBanik/Krishi-Saathi.git
cd Krishi-Saathi
Setup the Backend (Flask & ML)

Navigate to the backend directory (e.g., cd Crop_Planning/ or wherever your app.py is).

Create and activate a virtual environment:

Bash

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
Install the required Python packages:

Bash

pip install -r requirements.txt
Create a .env file in the backend directory and add your Google Gemini API key:

GEMINI_API_KEY="YOUR_API_KEY_HERE"
Run the Flask server:

Bash

flask run --port 5003
Setup the Frontend (Flutter App)

Navigate to the Flutter app's root directory.

Get the dependencies:

Bash

flutter pub get
Run the app on an emulator or a connected device:

Bash

flutter run
👨‍💻 Meet the Team - Tech Busters
This project was brought to life by a dedicated team of developers and innovators.

Name	Role
Piyangshu Banik	Team Leader • AI & ML • Web Development
Pranshu Bhutani	Backend Developer
Gaganpreet Singh	AI & ML Developer
Advitiya Sharma	Web Developer
Lakshay Goel	Flutter Developer
Ramandeep Kaur	Python & Documentation Specialist

Export to Sheets
🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
Distributed under the MIT License. See LICENSE for more information.

🙏 Acknowledgments
Government of India Data Portal for providing the market price API.

The Flutter and Python communities for their incredible open-source libraries.
