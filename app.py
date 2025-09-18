from flask import Flask, request, jsonify
import google.generativeai as genai
import traceback
import os
import re
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# -------------------------------
# Input validation and sanitization
# -------------------------------
def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not text or not isinstance(text, str):
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Escape special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')

    # Limit length
    if len(text) > 1000:
        text = text[:1000]

    return text.strip()


def validate_input(data):
    """Validate input data structure and content"""
    if not data:
        return False, "No data provided"

    # Add more validation rules if needed
    return True, "Valid input"


# -------------------------------
# Initialize Gemini API
# -------------------------------
API_KEY = os.environ.get('GEMINI_API_KEY', 'YOUR-API-KEY')
MODEL_ID = "gemini-2.0-flash"  # ✅ updated to valid Gemini model

# Configure Gemini with API key
genai.configure(api_key=API_KEY)


@app.route('/api/firebase-config')
def get_firebase_config():
    """Secure endpoint to provide Firebase configuration to client"""
    return jsonify({
        'apiKey': os.environ.get('FIREBASE_API_KEY'),
        'authDomain': os.environ.get('FIREBASE_AUTH_DOMAIN'),
        'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
        'storageBucket': os.environ.get('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.environ.get('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.environ.get('FIREBASE_APP_ID'),
        'measurementId': os.environ.get('FIREBASE_MEASUREMENT_ID')
    })


@app.route('/process-loan', methods=['POST'])
def process_loan():
    try:
        json_data = request.get_json(force=True)

        # Validate and sanitize input
        is_valid, validation_message = validate_input(json_data)
        if not is_valid:
            return jsonify({"status": "error", "message": validation_message}), 400

        # Sanitize text fields in JSON
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, str):
                    json_data[key] = sanitize_input(value)

        print(f"Received JSON: {json_data}")

        # -------------------------------
        # Build prompt for Gemini
        # -------------------------------
        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.

You will be given a JSON object that contains information about a farmer's loan application. 
The fields in this JSON will vary depending on the loan type (e.g., Crop Cultivation, Farm Equipment, Water Resources, Land Purchase).

Focus only on loan schemes and eligibility criteria followed by:
1. Indian nationalized banks (SBI, Bank of Baroda, etc.)
2. Private sector Indian banks (ICICI, HDFC, etc.)
3. Regional Rural Banks (RRBs)
4. Cooperative Banks
5. NABARD & government schemes

JSON Data = {json_data}

Your task:
1. Identify the loan type and key fields.
2. Assess eligibility and highlight strengths & challenges.
3. Point out missing critical data.
4. Give actionable suggestions to improve eligibility.
5. Suggest relevant government schemes/subsidies.
6. Respond in **Markdown format** with sections:
   - Loan Type
   - Eligibility Status
   - Loan Range
   - Improvements
   - Schemes
"""

        # -------------------------------
        # Call Gemini model
        # -------------------------------
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(prompt)

        reply = response.text if response and response.text else "No response from model."

        return jsonify({"status": "success", "message": reply}), 200

    except Exception as e:
        print(f"Unexpected Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
