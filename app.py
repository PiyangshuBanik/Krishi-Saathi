import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file
import joblib
import numpy as np
import re
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')
# --- Load ML Models ---
model = joblib.load(r'templates\Crop Recommendation\model\rf_model.pkl')
label_encoder = joblib.load(r'templates\Crop Recommendation\model\label_encoder.pkl')

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

# --- THIS IS THE NEW, WORKING PREDICT FUNCTION ---

# Helper function for input validation
def sanitize_numeric_input(value, min_val=None, max_val=None, field_name=""):
    try:
        cleaned = re.sub(r'[^0-9.-]', '', str(value))
        num_value = float(cleaned)
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{field_name} must be at least {min_val}")
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{field_name} must be at most {max_val}")
        return num_value
    except (ValueError, TypeError):
        raise ValueError(f"Invalid {field_name}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = [
            sanitize_numeric_input(request.form['N'], 0, 200, "Nitrogen (N)"),
            sanitize_numeric_input(request.form['P'], 0, 200, "Phosphorus (P)"),
            sanitize_numeric_input(request.form['K'], 0, 200, "Potassium (K)"),
            sanitize_numeric_input(request.form['temperature'], -50, 100, "Temperature"),
            sanitize_numeric_input(request.form['humidity'], 0, 100, "Humidity"),
            sanitize_numeric_input(request.form['ph'], 0, 14, "pH"),
            sanitize_numeric_input(request.form['rainfall'], 0, 1000, "Rainfall")
        ]
        
        input_params = { 'N': data[0], 'P': data[1], 'K': data[2], 'temperature': data[3], 'humidity': data[4], 'ph': data[5], 'rainfall': data[6] }
        
        # Make a real prediction
        prediction_num = model.predict([data])[0]
        prediction_label = label_encoder.inverse_transform([prediction_num])[0]
        
        # Point to the correct nested result.html file
        return render_template('Crop Recommendation/templates/result.html', crop=prediction_label, params=input_params)
        
    except ValueError as e:
        return f"Error: {str(e)}. Please go back and enter valid numbers.", 400
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return "An internal error occurred during prediction.", 500
    
# --- ADD THIS NEW FUNCTION FOR PDF DOWNLOADS ---
@app.route('/download_report', methods=['POST'])
def download_report():
    try:
        crop = request.form['crop']
        params = { key: request.form[key] for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'] }
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p.setFont('Helvetica-Bold', 18)
        p.drawString(50, height - 60, "Krishi-Saathi Crop Recommendation Report")
        p.setFont('Helvetica', 10)
        p.drawString(50, height - 80, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, height - 120, "Input Parameters:")
        p.setFont('Helvetica', 11)
        y = height - 140
        for k, v in params.items():
            p.drawString(70, y, f"{k.capitalize()}: {v}")
            y -= 18
            
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, y - 10, "Prediction Result:")
        p.setFont('Helvetica-Bold', 14)
        p.drawString(70, y - 30, f"Recommended Crop: {crop}")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, download_name="crop_recommendation_report.pdf", mimetype='application/pdf')
        
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return "Failed to generate PDF report.", 500
    
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
if __name__ == '_main_':
    app.run(debug=True)