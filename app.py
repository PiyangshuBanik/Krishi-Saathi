# import os
# import google.generativeai as genai
# from flask import Flask, render_template, request, jsonify, send_file
# import joblib
# import numpy as np
# import re
# from functools import wraps
# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from io import BytesIO
# import datetime


# # --- Configuration ---
# GEMINI_API_KEY = "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU"
# genai.configure(api_key=GEMINI_API_KEY)

# # Initialize Flask app
# app = Flask(__name__, static_url_path='/static', static_folder='static')
# # --- Load ML Models ---
# model = joblib.load(r'templates\Crop Recommendation\model\rf_model.pkl')
# label_encoder = joblib.load(r'templates\Crop Recommendation\model\label_encoder.pkl')

# # --- Routes for Serving Main HTML Pages ---
# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/about.html')
# def about():
#     return render_template('about.html')

# @app.route('/chat.html')
# def chat():
#     return render_template('chat.html')

# @app.route('/cropCalendar.html')
# def crop_calendar():
#     return render_template('cropCalendar.html')

# @app.route('/feed-back.html')
# def feedback():
#     return render_template('feed-back.html')

# @app.route('/main.html')
# def main():
#     return render_template('main.html')

# @app.route('/organic.html')
# def organic():
#     return render_template('organic.html')

# @app.route('/plantation.html')
# def plantation():
#     return render_template('plantation.html')

# @app.route('/terms-and-service.html')
# def terms_and_service():
#     return render_template('terms-and-service.html')

# @app.route('/weather.html')
# def weather():
#     return render_template('weather.html')

# # --- Routes for Nested Applications ---
# # These routes correctly render templates from your subfolders.
# @app.route('/Crop Recommendation/templates/index.html')
# def crop_recommendation_index():
#     return render_template('Crop Recommendation/templates/index.html')

# @app.route('/Crop Recommendation/templates/result.html')
# def crop_recommendation_result():
#     return render_template('Crop Recommendation/templates/result.html')

# # --- THIS IS THE NEW, WORKING PREDICT FUNCTION ---

# # Helper function for input validation
# def sanitize_numeric_input(value, min_val=None, max_val=None, field_name=""):
#     try:
#         cleaned = re.sub(r'[^0-9.-]', '', str(value))
#         num_value = float(cleaned)
#         if min_val is not None and num_value < min_val:
#             raise ValueError(f"{field_name} must be at least {min_val}")
#         if max_val is not None and num_value > max_val:
#             raise ValueError(f"{field_name} must be at most {max_val}")
#         return num_value
#     except (ValueError, TypeError):
#         raise ValueError(f"Invalid {field_name}")

# @app.route('/predict', methods=['POST'])
# def predict():
#     try:
#         data = [
#             sanitize_numeric_input(request.form['N'], 0, 200, "Nitrogen (N)"),
#             sanitize_numeric_input(request.form['P'], 0, 200, "Phosphorus (P)"),
#             sanitize_numeric_input(request.form['K'], 0, 200, "Potassium (K)"),
#             sanitize_numeric_input(request.form['temperature'], -50, 100, "Temperature"),
#             sanitize_numeric_input(request.form['humidity'], 0, 100, "Humidity"),
#             sanitize_numeric_input(request.form['ph'], 0, 14, "pH"),
#             sanitize_numeric_input(request.form['rainfall'], 0, 1000, "Rainfall")
#         ]
        
#         input_params = { 'N': data[0], 'P': data[1], 'K': data[2], 'temperature': data[3], 'humidity': data[4], 'ph': data[5], 'rainfall': data[6] }
        
#         # Make a real prediction
#         prediction_num = model.predict([data])[0]
#         prediction_label = label_encoder.inverse_transform([prediction_num])[0]
        
#         # Point to the correct nested result.html file
#         return render_template('Crop Recommendation/templates/result.html', crop=prediction_label, params=input_params)
        
#     except ValueError as e:
#         return f"Error: {str(e)}. Please go back and enter valid numbers.", 400
#     except Exception as e:
#         app.logger.error(f"Prediction error: {str(e)}")
#         return "An internal error occurred during prediction.", 500
    
# # --- ADD THIS NEW FUNCTION FOR PDF DOWNLOADS ---
# @app.route('/download_report', methods=['POST'])
# def download_report():
#     try:
#         crop = request.form['crop']
#         params = { key: request.form[key] for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'] }
        
#         buffer = BytesIO()
#         p = canvas.Canvas(buffer, pagesize=A4)
#         width, height = A4
        
#         p.setFont('Helvetica-Bold', 18)
#         p.drawString(50, height - 60, "Krishi-Saathi Crop Recommendation Report")
#         p.setFont('Helvetica', 10)
#         p.drawString(50, height - 80, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
#         p.setFont('Helvetica-Bold', 12)
#         p.drawString(50, height - 120, "Input Parameters:")
#         p.setFont('Helvetica', 11)
#         y = height - 140
#         for k, v in params.items():
#             p.drawString(70, y, f"{k.capitalize()}: {v}")
#             y -= 18
            
#         p.setFont('Helvetica-Bold', 12)
#         p.drawString(50, y - 10, "Prediction Result:")
#         p.setFont('Helvetica-Bold', 14)
#         p.drawString(70, y - 30, f"Recommended Crop: {crop}")
        
#         p.showPage()
#         p.save()
#         buffer.seek(0)
        
#         return send_file(buffer, as_attachment=True, download_name="crop_recommendation_report.pdf", mimetype='application/pdf')
        
#     except Exception as e:
#         app.logger.error(f"PDF generation error: {str(e)}")
#         return "Failed to generate PDF report.", 500
    
# @app.route('/Crop_Planning/templates/cropplan.html')
# def crop_planning():
#     return render_template('Crop_Planning/templates/cropplan.html')

# # Note: The following routes are based on your previous questions but are not
# # visible in the folder structure you provided. They are included here
# # for completeness, assuming they follow the same nested pattern.
# @app.route('/Crop Yield Prediction/crop_yield_app/templates/index.html')
# def yield_prediction_index():
#     return render_template('Crop Yield Prediction/crop_yield_app/templates/index.html')

# @app.route('/Disease prediction/template/index.html')
# def disease_prediction_index():
#     return render_template('Disease prediction/template/index.html')

# @app.route('/Crop_Prices_Tracker/templates/crop_price_tracker.html')
# def crop_price_tracker():
#     return render_template('Crop_Prices_Tracker/templates/crop_price_tracker.html')

# # --- API Endpoint for Gemini Chatbot ---
# @app.route('/api/gemini-chat', methods=['POST'])
# def gemini_chat():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400

#     try:
#         model = genai.GenerativeModel('gemini-pro')
#         response = model.generate_content(user_message)
#         return jsonify({'response': response.text})
#     except Exception as e:
#         print(f"Error calling Gemini API: {e}")
#         return jsonify({'error': 'Failed to get a response from the AI. Please try again.'}), 500

# # Run the app
# if __name__ == '__main__':
#     app.run(debug=True)



#change code from gemini below
import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, send_file, redirect
import joblib
import json
import re
from functools import wraps
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime
import requests
import logging

# ==============================================================================
# --- APP CONFIGURATION & INITIALIZATION ---
# ==============================================================================

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static')

# Basic logging setup
logging.basicConfig(level=logging.INFO)

# --- Gemini AI API Configuration ---
try:
    API_KEY = os.environ.get("API_KEY", "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU") # Replace with your key
    if "AIzaSy" in API_KEY:
         print("\n--- WARNING: API Key appears to be hardcoded. For production, set it as an environment variable. ---\n")
    if not API_KEY:
        raise ValueError("API Key is not set. Please set the API_KEY environment variable.")
    genai.configure(api_key=API_KEY)
    planner_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Google AI Models initialized successfully.")
except Exception as e:
    print(f"Error initializing Google AI Model: {e}")
    planner_model = None

# --- Load Local Machine Learning Models ---
try:
    model = joblib.load(r'templates\Crop Recommendation\model\rf_model.pkl')
    label_encoder = joblib.load(r'templates\Crop Recommendation\model\label_encoder.pkl')
    app.logger.info("Crop recommendation ML model loaded successfully.")
except Exception as e:
    app.logger.error(f"Failed to load ML model: {e}")
    model = None
    label_encoder = None

# --- Load Crop Price Tracker Data at Startup ---
CROP_PRICE_API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
CROP_PRICE_API_PARAMS = {
    "api-key": "579b464db66ec23bdd000001c43ef34767ce496343897dfb1893102b",
    "format": "json",
    "limit": "10000"
}

def load_price_data():
    """Loads data from the data.gov.in API when the application starts."""
    try:
        app.logger.info("Fetching crop price data from API...")
        response = requests.get(CROP_PRICE_API_URL, params=CROP_PRICE_API_PARAMS, timeout=20)
        response.raise_for_status()
        app.logger.info("Crop price data fetched successfully.")
        return response.json().get("records", [])
    except requests.RequestException as e:
        app.logger.error(f"Crop price API request failed: {e}")
        return []

CROP_PRICE_DATA = load_price_data()


# ==============================================================================
# --- HELPER & SANITIZATION FUNCTIONS ---
# ==============================================================================

# --- Helpers for Crop Recommendation ---
def validate_required_fields(required_fields):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for field in required_fields:
                if field not in request.form or not request.form[field].strip():
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_numeric_input(value, min_val=None, max_val=None, field_name=""):
    try:
        cleaned = re.sub(r'[^0-9.-]', '', str(value))
        num_value = float(cleaned)
        if min_val is not None and num_value < min_val:
            raise ValueError(f"{field_name} must be at least {min_val}")
        if max_val is not None and num_value > max_val:
            raise ValueError(f"{field_name} must be at most {max_val}")
        return num_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {field_name}: {str(e)}")

def sanitize_text_input(text, max_length=255):
    if not isinstance(text, str):
        return ""
    return re.sub(r'[<>"\'&]', '', text.strip())[:max_length]

# --- Helpers for Crop Planner ---
def validate_user_data_planner(data):
    # This function is specific to the planner's JSON structure
    required_fields = ['pH', 'Temperature', 'Rainfall', 'Soil_Type', 'Season', 'Market_Demand', 'Fertilizer_Used', 'Pest_Issue', 'Irrigation_Method']
    for field in required_fields:
        if field not in data or (isinstance(data[field], str) and not data[field].strip()):
            return False, f"Missing required field: {field}"
    try:
        float(data['pH']); float(data['Temperature']); float(data['Rainfall'])
    except (ValueError, TypeError):
        return False, "pH, Temperature, and Rainfall must be valid numbers."
    return True, "Valid"

def clean_ai_response(text_response):
    try:
        match = re.search(r'```json\s*(\{.*?\})\s*```', text_response, re.DOTALL)
        if match: return match.group(1)
        match = re.search(r'(\{.*\})', text_response, re.DOTALL)
        if match: return match.group(1)
    except Exception as e:
        app.logger.error(f"Error cleaning AI response: {e}")
    return text_response

def get_ai_prediction_and_guide(user_data):
    if not planner_model: return json.dumps({"error": "AI model is not configured."})
    sanitized_data = {k: sanitize_text_input(str(v), 100) for k, v in user_data.items()}
    conditions = ", ".join([f"{key.replace('_', ' ')}: {value}" for key, value in sanitized_data.items()])
    prompt = f"""
    You are a JSON API providing agricultural advice. Respond ONLY with a single valid JSON object.
    Conditions: {conditions}
    Return JSON with keys: "predicted_crop", "title", "how_to_plant", "fertilizer", "timeline", "ideal_rainfall", "post_harvest".
    Separate list items or steps with "\\n".
    """
    try:
        response = planner_model.generate_content(prompt)
        return response.candidates[0].content.parts[0].text if response.candidates else json.dumps({"error": "Empty response from AI"})
    except Exception as e:
        app.logger.error(f"Error during genai.generate_content: {e}")
        return json.dumps({"error": "Failed to generate AI guide."})


# ==============================================================================
# --- MAIN PAGE RENDERING ROUTES ---
# ==============================================================================

@app.route('/')
def index(): return render_template('index.html')
@app.route('/about.html')
def about(): return render_template('about.html')
@app.route('/chat.html')
def chat(): return render_template('chat.html')
@app.route('/cropCalendar.html')
def crop_calendar(): return render_template('cropCalendar.html')
@app.route('/feed-back.html')
def feedback(): return render_template('feed-back.html')
@app.route('/main.html')
def main(): return render_template('main.html')
@app.route('/organic.html')
def organic(): return render_template('organic.html')
@app.route('/plantation.html')
def plantation(): return render_template('plantation.html')
@app.route('/terms-and-service.html')
def terms_and_service(): return render_template('terms-and-service.html')
@app.route('/weather.html')
def weather(): return render_template('weather.html')

# --- Routes for Nested Applications ---
@app.route('/Crop Recommendation/templates/index.html')
def crop_recommendation_index(): return render_template('Crop Recommendation/templates/index.html')
@app.route('/Crop_Planning/templates/cropplan.html')
def crop_planning(): return render_template('Crop_Planning/templates/cropplan.html')
@app.route('/Crop Yield Prediction/crop_yield_app/templates/index.html')
def yield_prediction_index(): return render_template('Crop Yield Prediction/crop_yield_app/templates/index.html')
@app.route('/Disease prediction/template/index.html')
def disease_prediction_index(): return render_template('Disease prediction/template/index.html')
@app.route('/Crop_Prices_Tracker/templates/crop_price_tracker.html')
def price_tracker_page(): return render_template('Crop_Prices_Tracker/templates/crop_price_tracker.html')


# ==============================================================================
# --- FUNCTIONAL ENDPOINTS & API ROUTES ---
# ==============================================================================

# --- Endpoint for CROP RECOMMENDATION (ML Model) ---
@app.route('/predict', methods=['POST'])
@validate_required_fields(['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
def predict():
    print("-----Received prediction request with form data from the crop recommendation---->:", request.form)
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
        input_params = {k: str(v) for k, v in zip(['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'], data)}
        prediction_num = model.predict([data])[0]
        prediction_label = label_encoder.inverse_transform([prediction_num])[0]
        return render_template('Crop Recommendation/templates/result.html', crop=prediction_label, params=input_params)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed due to an internal server error.'}), 500

# --- Endpoint for CROP PLANNER (AI Model) ---
@app.route('/predict_plan', methods=['POST'])
def predict_plan():
    print("-----Received prediction plan request with JSON data from the crop planner:->>", request.json)
    try:
        if not request.is_json: return jsonify({'error': 'Content-Type must be application/json'}), 400
        user_input_data = request.get_json()
        is_valid, message = validate_user_data_planner(user_input_data)
        if not is_valid: return jsonify({'error': message}), 400
        raw_ai_response = get_ai_prediction_and_guide(user_input_data)
        cleaned_response = clean_ai_response(raw_ai_response)
        try:
            ai_response_data = json.loads(cleaned_response)
            response_payload = { "crop": ai_response_data.get('predicted_crop'), "guide": ai_response_data }
            return jsonify(response_payload)
        except json.JSONDecodeError:
            app.logger.error(f"Failed to parse AI response: {raw_ai_response}")
            return jsonify({'error': 'The AI returned an invalid response. Please try again.'}), 500
    except Exception as e:
        app.logger.error(f"Prediction plan error: {str(e)}")
        return jsonify({'error': 'Prediction failed due to an internal server error.'}), 500

# --- Endpoints for CROP PRICE TRACKER ---
@app.route('/crop_price_tracker', methods=['GET', 'POST'])
def crop_price_tracker():
    print("-----Received crop price tracker request with form data:->>", request.form)
    try:
        crops = sorted({record['commodity'] for record in CROP_PRICE_DATA if record.get('commodity')})
        result, error, form_data = [], None, {}
        if request.method == 'POST':
            crop = sanitize_text_input(request.form.get('crop'))
            state = sanitize_text_input(request.form.get('state'))
            market = sanitize_text_input(request.form.get('market'))
            form_data = {'crop': crop, 'state': state, 'market': market}
            print("<--- Sanitized form data is ---> :", form_data)
            if not all([crop, state, market]):
                error = "All fields (crop, state, market) are required."
            else:
                result = [r for r in CROP_PRICE_DATA if r.get('commodity','').lower()==crop.lower() and r.get('state','').lower()==state.lower() and r.get('market','').lower()==market.lower()]
                result.sort(key=lambda x: x.get('arrival_date', ''), reverse=True)
                if not result: error = f"No price data found for {crop} in {market}, {state}."
        return render_template('Crop_Prices_Tracker/templates/crop_price_tracker.html', crops=crops, result=result, error=error, form_data=form_data)
    except Exception as e:
        app.logger.error(f"Error in crop_price_tracker route: {e}")
        return render_template('Crop_Prices_Tracker/templates/crop_price_tracker.html', crops=[], error="An unexpected server error occurred.")

@app.route('/get_states')
def get_states():
    print("-----Received get_states request with args from price tracker:->>", request.args)
    try:
        crop = sanitize_text_input(request.args.get('crop')).lower()
        if not crop: return jsonify([])
        states = sorted({r['state'] for r in CROP_PRICE_DATA if r.get('commodity', '').lower() == crop and r.get('state')})
        return jsonify(states)
    except Exception as e:
        app.logger.error(f"Error in get_states: {e}")
        return jsonify({"error": "Could not fetch states"}), 500

@app.route('/get_markets')
def get_markets():
    print("-----Received get_markets request with args from price tracker:->>", request.args)
    try:
        crop = sanitize_text_input(request.args.get('crop')).lower()
        state = sanitize_text_input(request.args.get('state')).lower()
        if not crop or not state: return jsonify([])
        markets = sorted({r['market'] for r in CROP_PRICE_DATA if r.get('commodity','').lower()==crop and r.get('state','').lower()==state and r.get('market')})
        return jsonify(markets)
    except Exception as e:
        app.logger.error(f"Error in get_markets: {e}")
        return jsonify({"error": "Could not fetch markets"}), 500

# --- Endpoint for PDF Report DOWNLOAD ---
@app.route('/download_report', methods=['POST'])
@validate_required_fields(['crop', 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
def download_report():
    print("---------Received PDF report request with form data:->>", request.form)
    try:
        crop = sanitize_text_input(request.form['crop'], 100)
        params = {k: sanitize_text_input(v) for k, v in request.form.items() if k != 'crop'}
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        p.setFont('Helvetica-Bold', 18); p.drawString(50, height - 60, "Krishi-Saathi Crop Recommendation Report")
        p.setFont('Helvetica', 10); p.drawString(50, height - 80, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        p.setFont('Helvetica-Bold', 12); p.drawString(50, height - 120, "Input Parameters:")
        p.setFont('Helvetica', 11)
        y = height - 140
        for k, v in params.items():
            p.drawString(70, y, f"{k.capitalize()}: {v}"); y -= 18
        p.setFont('Helvetica-Bold', 12); p.drawString(50, y - 10, "Prediction Result:")
        p.setFont('Helvetica-Bold', 14); p.drawString(70, y - 30, f"Recommended Crop: {crop}")
        p.showPage(); p.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="crop_recommendation_report.pdf", mimetype='application/pdf')
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate PDF report.'}), 500

# --- API Endpoint for General Gemini CHATBOT ---
@app.route('/api/gemini-chat', methods=['POST'])
def gemini_chat():
    user_message = request.json.get('message')
    if not user_message: return jsonify({'error': 'No message provided'}), 400
    try:
        chat_model = genai.GenerativeModel('gemini-pro')
        response = chat_model.generate_content(user_message)
        return jsonify({'response': response.text})
    except Exception as e:
        app.logger.error(f"Error calling Gemini API: {e}")
        return jsonify({'error': 'Failed to get a response from the AI.'}), 500

# ==============================================================================
# --- GLOBAL ERROR HANDLERS & APP RUN ---
# ==============================================================================
@app.errorhandler(400)
def bad_request(error): return jsonify({'error': 'Bad request'}), 400
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal Server Error: {str(error)}")
    return jsonify({'error': 'An internal server error occurred.'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)