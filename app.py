import os
import re
import json
import datetime
import joblib
import numpy as np
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# --------------------
# Flask setup
# --------------------
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# --------------------
# Google Gemini Config
# --------------------
GEMINI_API_KEY = os.environ.get("API_KEY", "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU")
genai.configure(api_key=GEMINI_API_KEY)
try:
    genai_model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Google AI Model initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing Google AI Model: {e}")
    genai_model = None

# --------------------
# ML Model for Crop Recommendation
# --------------------
model = joblib.load(r'templates\Crop Recommendation\model\rf_model.pkl')
label_encoder = joblib.load(r'templates\Crop Recommendation\model\label_encoder.pkl')

# --------------------
# Middleware for Logging
# --------------------

# @app.before_request
# def log_request_info():
#     print("\n--- Incoming Request ---")
#     print("Path:", request.path)
#     print("Method:", request.method)
#     print("Headers:", dict(request.headers))
#     print("Body:", request.get_data())
#     print("------------------------")

# --------------------
# Helper functions
# --------------------
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

def sanitize_input(text, max_length=255):
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r'[<>"\']', '', text.strip())
    return cleaned[:max_length]

def validate_user_data(data):
    required_fields = [
        'pH', 'Temperature', 'Rainfall', 'Soil_Type', 'Season',
        'Market_Demand', 'Fertilizer_Used', 'Pest_Issue', 'Irrigation_Method'
    ]
    for field in required_fields:
        if field not in data or (isinstance(data[field], str) and not data[field].strip()):
            return False, f"Missing required field: {field}"
    try:
        float(data['pH'])
        float(data['Temperature'])
        int(data['Rainfall'])
    except (ValueError, TypeError):
        return False, "pH, Temperature, and Rainfall must be valid numbers."
    return True, "Valid"

def clean_ai_response(text_response):
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text_response, re.DOTALL)
        if match:
            return match.group(1)
        match = re.search(r'(\{.*\})', text_response, re.DOTALL)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error cleaning AI response: {e}")
    return text_response

def get_ai_prediction_and_guide(user_data):
    if not genai_model:
        return json.dumps({"error": "AI model is not configured."})

    sanitized_data = {k: sanitize_input(str(v), 100) for k, v in user_data.items()}
    conditions = ", ".join([f"{key.replace('_', ' ')}: {value}" for key, value in sanitized_data.items()])

    prompt = f"""
You are a JSON API that provides agricultural advice.
STRICT RULE: Respond ONLY with a single valid JSON object, no extra text.

Conditions: {conditions}

Return JSON with these keys:
- "predicted_crop"
- "title"
- "how_to_plant"
- "fertilizer"
- "timeline"
- "ideal_rainfall"
- "post_harvest"

If you provide lists or steps, separate them with "\\n".
"""
    try:
        response = genai_model.generate_content(prompt)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        return json.dumps({"error": "Empty response from AI"})
    except Exception as e:
        print(f"Error during genai.generate_content: {e}")
        return json.dumps({"error": "Failed to generate AI guide."})

# --------------------
# Routes - Main Pages
# --------------------
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

@app.route('/Crop_Planning/templates/cropplan.html')
def crop_planning():
    return render_template('/Crop_Planning/templates/cropplan.html')

# --------------------
# Crop Recommendation (ML)
# --------------------
@app.route('/predict_crop_planning', methods=['POST'])
def predict_crop_recommendation():
    #print("HELLO CONDUCTOR 1")
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
        input_params = dict(zip(['N','P','K','temperature','humidity','ph','rainfall'], data))
        prediction_num = model.predict([data])[0]
        prediction_label = label_encoder.inverse_transform([prediction_num])[0]
        return render_template('Crop Recommendation/templates/result.html', crop=prediction_label, params=input_params)
    except ValueError as e:
        return f"Error: {str(e)}", 400
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return "An internal error occurred during prediction.", 500

# --------------------
# Crop Planning (AI JSON)
# --------------------
@app.route('/predict', methods=['POST'])
def predict_crop_planning():
    #print("HELLO CONDUCTOR 2 predict cop planning")
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        user_input_data = request.get_json()
        is_valid, message = validate_user_data(user_input_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        raw_ai_response = get_ai_prediction_and_guide(user_input_data)
        cleaned_response = clean_ai_response(raw_ai_response)
        ai_response_data = json.loads(cleaned_response)
        response_payload = {
            "crop": ai_response_data.get('predicted_crop'),
            "guide": {
                "title": ai_response_data.get('title'),
                "timeline": ai_response_data.get('timeline'),
                "how_to_plant": ai_response_data.get('how_to_plant'),
                "fertilizer": ai_response_data.get('fertilizer'),
                "ideal_rainfall": ai_response_data.get('ideal_rainfall'),
                "post_harvest": ai_response_data.get('post_harvest')
            }
        }
        return jsonify(response_payload)
    except json.JSONDecodeError:
        return jsonify({'error': 'The AI returned an invalid response'}), 500
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

# --------------------
# PDF Download
# --------------------
@app.route('/download_report', methods=['POST'])
def download_report():
    try:
        crop = request.form['crop']
        params = {key: request.form[key] for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']}
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        p.setFont('Helvetica-Bold', 18)
        p.drawString(50, height - 60, "Krishi-Saathi Crop Recommendation Report")
        p.setFont('Helvetica', 10)
        p.drawString(50, height - 80, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        p.setFont('Helvetica-Bold', 12)
        p.drawString(50, height - 120, "Input Parameters:")
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

# --------------------
# Gemini Chatbot API
# --------------------
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
        return jsonify({'error': 'Failed to get a response from the AI'}), 500

# --------------------
# Run
# --------------------
if __name__ == '__main__':
    print("🚀 Unified Flask app starting...")
    app.run(port=5000, debug=True)
