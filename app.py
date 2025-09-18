import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, redirect, url_for

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')

# --- Routes for Serving Main HTML Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/chat.html')
def chat():
    return render_template('chat.html')

@app.route('/cropCalendar.html')
def crop_calendar():
    return render_template('cropCalendar.html')

@app.route('/feed-back.html')
def feedback():
    return render_template('feed-back.html')

@app.route('/main.html')
def main():
    return render_template('main.html')

@app.route('/organic.html')
def organic():
    return render_template('organic.html')

@app.route('/plantation.html')
def plantation():
    return render_template('plantation.html')

@app.route('/terms-and-service.html')
def terms_and_service():
    return render_template('terms-and-service.html')

@app.route('/weather.html')
def weather():
    return render_template('weather.html')

# --- Routes for Nested Applications ---
# These routes correctly render templates from your subfolders.
@app.route('/Crop Recommendation/templates/index.html')
def crop_recommendation_index():
    return render_template('Crop Recommendation/templates/index.html')

@app.route('/Crop Recommendation/templates/result.html')
def crop_recommendation_result():
    return render_template('Crop Recommendation/templates/result.html')

# This is the new, correct route to handle the form submission.
@app.route('/predict', methods=['POST'])
def predict():
    try:
        N = float(request.form.get('N'))
        P = float(request.form.get('P'))
        K = float(request.form.get('K'))
        temperature = float(request.form.get('temperature'))
        humidity = float(request.form.get('humidity'))
        ph = float(request.form.get('ph'))
        rainfall = float(request.form.get('rainfall'))

        # Here you would call your machine learning model to get a prediction.
        # For now, a placeholder prediction is used.
        prediction_result = "Paddy"

        params = {
            'N': N, 'P': P, 'K': K, 'temperature': temperature,
            'humidity': humidity, 'ph': ph, 'rainfall': rainfall
        }
        
        return render_template('Crop Recommendation/templates/result.html', crop=prediction_result, params=params)

    except (ValueError, TypeError):
        return "Invalid input. Please ensure all fields are filled with numbers.", 400

@app.route('/Crop_Planning/templates/cropplan.html')
def crop_planning():
    return render_template('Crop_Planning/templates/cropplan.html')

# Note: The following routes are based on your previous questions but are not
# visible in the folder structure you provided. They are included here
# for completeness, assuming they follow the same nested pattern.
@app.route('/Crop Yield Prediction/crop_yield_app/templates/index.html')
def yield_prediction_index():
    return render_template('Crop Yield Prediction/crop_yield_app/templates/index.html')

@app.route('/Disease prediction/template/index.html')
def disease_prediction_index():
    return render_template('Disease prediction/template/index.html')

@app.route('/Crop_Prices_Tracker/templates/crop_price_tracker.html')
def crop_price_tracker():
    return render_template('Crop_Prices_Tracker/templates/crop_price_tracker.html')

# --- API Endpoint for Gemini Chatbot ---
@app.route('/api/gemini-chat', methods=['POST'])
def gemini_chat():
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
    app.run(debug=True)