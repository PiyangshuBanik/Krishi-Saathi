from flask import Flask, request, jsonify
import google.generativeai as genai
import traceback
import os
import re
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
# Allow requests from a specific origin for development
# This prevents CORS errors when the client-side code is on a different server (like a local file server).
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})

# ------------------------------------
# Input validation and sanitization
# ------------------------------------
def sanitize_value(value):
    """
    Sanitize a single string value to prevent prompt injection attacks.
    Removes newline and carriage return characters which can be used to
    manipulate the prompt's structure.
    """
    if not isinstance(value, str):
        return value
    return re.sub(r'[\n\r\t]', ' ', value)

def validate_input(data):
    """
    Validate the input data structure.
    Ensures the data is a non-empty dictionary.
    """
    if not data or not isinstance(data, dict):
        return False, "Invalid or no data provided. Expected a JSON object."
    return True, "Valid input"

# ------------------------------------
# Initialize Gemini API
# ------------------------------------
# Retrieve API key from environment variables.
# This is a critical security practice to avoid hardcoding secrets.
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    # Raise a clear error if the key is not found, preventing the app from running
    # in an insecure state.
    raise ValueError("GEMINI_API_KEY not found in environment variables. "
                     "Please create a .env file and add it.")

# Use a valid Gemini model ID.
MODEL_ID = "gemini-1.5-flash"

# Configure the Gemini API with the retrieved key.
genai.configure(api_key=API_KEY)

# ------------------------------------
# API Endpoints
# ------------------------------------

@app.route('/api/firebase-config')
def get_firebase_config():
    """
    Secure endpoint to provide Firebase configuration to the client.
    This is useful for passing credentials without exposing them in the
    client-side source code.
    """
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
    """
    Main endpoint for processing loan applications.
    It takes a JSON payload, sanitizes it, and sends it to the Gemini API
    to get an eligibility assessment.
    """
    try:
        # Get JSON data from the request body.
        json_data = request.get_json()
        
        # Validate the received data structure.
        is_valid, validation_message = validate_input(json_data)
        if not is_valid:
            return jsonify({"status": "error", "message": validation_message}), 400

        # Sanitize each string value in the input dictionary to prevent injection.
        sanitized_data = {key: sanitize_value(value) for key, value in json_data.items()}

        # Construct the prompt for the Gemini model.
        # The prompt is a clear instruction set for the AI, with the sanitized
        # user data embedded safely within it.
        prompt = f"""
You are a financial loan eligibility advisor specializing in agricultural loans for farmers in India.
You will be provided with a JSON object that contains information about a farmer's loan application.
The fields in this JSON will vary depending on the loan type (e.g., Crop Cultivation, Farm Equipment, Water Resources, Land Purchase).

Focus only on loan schemes and eligibility criteria followed by:
1. Indian nationalized banks (SBI, Bank of Baroda, etc.)
2. Private sector Indian banks (ICICI, HDFC, etc.)
3. Regional Rural Banks (RRBs)
4. Cooperative Banks
5. NABARD & government schemes

JSON Data:
{sanitized_data}

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

        # Initialize the Gemini model and generate content based on the prompt.
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(prompt)

        # Extract the text response.
        reply = response.text if response and response.text else "No response from model."

        # Return the AI's response to the client.
        return jsonify({"status": "success", "message": reply}), 200

    except Exception as e:
        # Log the detailed error for debugging purposes on the server.
        print(f"Unexpected Error: {e}")
        traceback.print_exc()
        # Return a generic, secure error message to the client.
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

# ------------------------------------
# Run the Flask App
# ------------------------------------
if __name__ == '__main__':
    # Run the app.
    # host='0.0.0.0' makes the server accessible from any machine on the network.
    # debug=True enables live-reloading and helpful error pages for development.
    app.run(host='0.0.0.0', port=5000, debug=True)