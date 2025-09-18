import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, redirect, url_for

# --- Configuration ---
# Your Gemini API key
# Note: In a real application, you should use environment variables for keys.
GEMINI_API_KEY = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')

# --- Routes for Serving HTML Pages ---
# Render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Render the about.html page
@app.route('/about.html')
def about():
    return render_template('about.html')

# Render the chat.html page
@app.route('/chat.html')
def chat():
    return render_template('chat.html')

# Render the cropCalendar.html page
@app.route('/cropCalendar.html')
def crop_calendar():
    return render_template('cropCalendar.html')

# Render the feed-back.html page
@app.route('/feed-back.html')
def feedback():
    return render_template('feed-back.html')

# Render the main.html (Dashboard) page
@app.route('/main.html')
def main():
    return render_template('main.html')

# Render the organic.html page
@app.route('/organic.html')
def organic():
    return render_template('organic.html')

# Render the plantation.html page
@app.route('/plantation.html')
def plantation():
    return render_template('plantation.html')

# Render the terms-and-service.html page
@app.route('/terms-and-service.html')
def terms_and_service():
    return render_template('terms-and-service.html')

# Render the weather.html page
@app.route('/weather.html')
def weather():
    return render_template('weather.html')

# Redirects for sub-directories to the main app
# These routes assume that the referenced tools are also part of this Flask app
@app.route('/Crop Recommendation/templates/index.html')
def crop_recommendation_index():
    # Placeholder: In a real scenario, you'd render this template
    return "This route is a placeholder. You need to provide the actual template content."

@app.route('/Crop Yield Prediction/crop_yield_app/templates/index.html')
def yield_prediction_index():
    return "This route is a placeholder."

@app.route('/Disease prediction/template/index.html')
def disease_prediction_index():
    return "This route is a placeholder."

@app.route('/Crop_Planning/templates/cropplan.html')
def crop_planning():
    return "This route is a placeholder."
    
@app.route('/Crop_Prices_Tracker/templates/crop_price_tracker.html')
def crop_price_tracker():
    return "This route is a placeholder."


# --- API Endpoint for Gemini Chatbot ---
@app.route('/api/gemini-chat', methods=['POST'])
def gemini_chat():
    """Handles chat requests by sending a message to the Gemini API."""
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(user_message)
        return jsonify({'response': response.text})
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return jsonify({'error': 'Failed to get a response from the AI. Please try again.'}), 500


# Run the app
if __name__ == '__main__':
    # Set debug=True for development to see errors.
    # Set to False for production environments.
    app.run(debug=True)