# app.py
from flask import Flask, render_template, request, jsonify, redirect
import requests
import re
from functools import wraps
import logging

app = Flask(__name__)

# --- Basic logging setup ---
logging.basicConfig(level=logging.INFO)

# --- Global API config ---
API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_PARAMS = {
    "api-key": "579b464db66ec23bdd000001c43ef34767ce496343897dfb1893102b",
    "format": "json",
    "limit": "10000"  # Increased limit to get more comprehensive data
}

# --- Input validation helper ---
def sanitize_input(text, max_length=100):
    """Sanitizes text input to prevent basic injection issues."""
    if not isinstance(text, str):
        return ""
    cleaned = re.sub(r'[<>"\'&]', '', text.strip())
    return cleaned[:max_length]

# --- Load data once at startup ---
def load_data():
    """Loads data from the API when the application starts."""
    try:
        app.logger.info("Fetching data from API...")
        response = requests.get(API_URL, params=API_PARAMS, timeout=20)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        app.logger.info("Data fetched successfully.")
        return response.json().get("records", [])
    except requests.RequestException as e:
        app.logger.error(f"API request failed: {e}")
        return []

DATA = load_data()

# --- Routes ---
@app.route('/')
def home():
    """Redirects the root URL to the main tracker page."""
    return redirect('/crop_price_tracker')

@app.route('/crop_price_tracker', methods=['GET', 'POST'])
def crop_price_tracker():
    """Handles the main page logic for displaying crops and results."""
    try:
        crops = sorted({record['commodity'] for record in DATA if record.get('commodity')})
        result = []
        error = None
        form_data = {}

        if request.method == 'POST':
            crop = sanitize_input(request.form.get('crop'))
            state = sanitize_input(request.form.get('state'))
            market = sanitize_input(request.form.get('market'))
            form_data = {'crop': crop, 'state': state, 'market': market}

            if not all([crop, state, market]):
                error = "All fields (crop, state, market) are required."
            else:
                result = [
                    r for r in DATA
                    if r.get('commodity', '').lower() == crop.lower()
                    and r.get('state', '').lower() == state.lower()
                    and r.get('market', '').lower() == market.lower()
                ]
                # Sort results by date, most recent first
                result.sort(key=lambda x: x.get('arrival_date', ''), reverse=True)

                if not result:
                    error = f"No price data found for {crop} in {market}, {state}."

        return render_template('crop_price_tracker.html', crops=crops, result=result, error=error, form_data=form_data)
    
    except Exception as e:
        app.logger.error(f"Error in crop_price_tracker route: {e}")
        return render_template('crop_price_tracker.html', crops=[], error="An unexpected server error occurred.")

@app.route('/get_states')
def get_states():
    """API endpoint to get states for a selected crop."""
    try:
        crop = sanitize_input(request.args.get('crop')).lower()
        if not crop:
            return jsonify([])
        
        states = sorted({r['state'] for r in DATA if r.get('commodity', '').lower() == crop and r.get('state')})
        return jsonify(states)
    except Exception as e:
        app.logger.error(f"Error in get_states: {e}")
        return jsonify({"error": "Could not fetch states"}), 500

@app.route('/get_markets')
def get_markets():
    """API endpoint to get markets for a selected crop and state."""
    try:
        crop = sanitize_input(request.args.get('crop')).lower()
        state = sanitize_input(request.args.get('state')).lower()
        
        if not crop or not state:
            return jsonify([])
        
        markets = sorted({
            r['market'] for r in DATA
            if r.get('commodity', '').lower() == crop and r.get('state', '').lower() == state and r.get('market')
        })
        return jsonify(markets)
    except Exception as e:
        app.logger.error(f"Error in get_markets: {e}")
        return jsonify({"error": "Could not fetch markets"}), 500

# --- Global error handlers ---
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    return render_template('crop_price_tracker.html', error="An internal server error occurred."), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)