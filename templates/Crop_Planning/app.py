# app.py
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
from flask_cors import CORS
import re
from functools import wraps
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("API_KEY", "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU")

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
        float(data['Rainfall'])
    except (ValueError, TypeError):
        return False, "pH, Temperature, and Rainfall must be valid numbers."
    
    return True, "Valid"

try:
    if API_KEY == "AIzaSyCh-1osIi4tMAAM0pudn8CpegWKg1wMxMU":
        print("\n--- WARNING: API Key is hardcoded. For production, set it as an environment variable. ---\n")
    if not API_KEY:
        raise ValueError("API Key is not set. Please set the API_KEY environment variable before running the app.")
    genai.configure(api_key=API_KEY)
    genai_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Google AI Model initialized successfully.")
except Exception as e:
    print(f"Error initializing Google AI Model: {e}")
    genai_model = None

def clean_ai_response(text_response):
    try:
        match = re.search(r'```json\s*(\{.*\})\s*```|(\{.*\})', text_response, re.DOTALL)
        if match:
            return match.group(1) or match.group(2)
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
    Your entire response MUST be a single, valid JSON object and nothing else.
    
    Analyze these farming conditions: {conditions}
    
    1. Determine the single best crop that is appropriate for the given conditions.
    2. Generate a detailed farming guide for that crop. For any lists or steps, use the newline character `\n` to separate items.
    
    Return a single JSON object with these exact keys: 
    "predicted_crop", "title", "how_to_plant", "fertilizer", "timeline", "ideal_rainfall", "post_harvest".
    """
    
    try:
        response = genai_model.generate_content(prompt)
        return response.text
    except Exception as e:
        # This print statement is the crucial change
        print(f"Error during genai.generate_content: {e}")
        return json.dumps({"error": "Failed to generate AI guide."})

@app.route('/')
def home():
    return render_template('cropplan.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        user_input_data = request.get_json()
        
        is_valid, message = validate_user_data(user_input_data)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        raw_ai_response = get_ai_prediction_and_guide(user_input_data)
        
        try:
            ai_response_data = json.loads(clean_ai_response(raw_ai_response))
            
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
            return jsonify({'error': 'The AI returned an invalid response. Please try again.'}), 500

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=5003, debug=True)