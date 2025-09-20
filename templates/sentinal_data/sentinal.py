# app.py
from flask import Flask, render_template, request, jsonify
import requests
import datetime
import os
from dotenv import load_dotenv
import base64
from concurrent.futures import ThreadPoolExecutor

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("SENTINELHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINELHUB_CLIENT_SECRET")
# Global variable to cache the token for efficiency
access_token_cache = {"token": None, "expiry_time": datetime.datetime.now()}


def get_access_token():
    """Authenticate with Sentinel Hub and cache the token."""
    global access_token_cache
    # If token exists and is not expired (with a 5-minute buffer), return it
    if access_token_cache["token"] and access_token_cache["expiry_time"] > datetime.datetime.now() + datetime.timedelta(minutes=5):
        return access_token_cache["token"]

    url = "https://services.sentinel-hub.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        res = requests.post(url, data=payload, timeout=10)
        res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = res.json()
        
        # Cache the new token and set its expiry time
        access_token_cache["token"] = data.get("access_token")
        expires_in = data.get("expires_in", 3600)  # Default to 1 hour
        access_token_cache["expiry_time"] = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        
        print("Successfully obtained new Sentinel Hub access token.")
        return access_token_cache["token"]
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        return None

def fetch_image_from_sentinel(lat, lon, date_str, token, evalscript):
    """
    Generic function to fetch an image from Sentinel Hub using a specific evalscript.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Bounding box [minLon, minLat, maxLon, maxLat] - approx. 2.2km x 2.2km
    min_lon, max_lon = float(lon) - 0.01, float(lon) + 0.01
    min_lat, max_lat = float(lat) - 0.01, float(lat) + 0.01

    # Create a ±5 day window to increase chances of finding a cloud-free image
    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    date_from = (date_obj - datetime.timedelta(days=5)).strftime("%Y-%m-%dT00:00:00Z")
    date_to = (date_obj + datetime.timedelta(days=5)).strftime("%Y-%m-%dT23:59:59Z")

    request_payload = {
        "input": {
            "bounds": {
                "bbox": [min_lon, min_lat, max_lon, max_lat],
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a", # Using high-quality L2A data
                "dataFilter": {
                    "timeRange": {"from": date_from, "to": date_to},
                    "mosaickingOrder": "leastCC" # Prioritize least cloudy scenes
                }
            }]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": evalscript  # This tells Sentinel Hub how to render the image
    }

    img_url = "https://services.sentinel-hub.com/api/v1/process"
    try:
        img_res = requests.post(img_url, headers=headers, json=request_payload, timeout=30)
        img_res.raise_for_status() # Check for HTTP errors
        return img_res.content
    except requests.exceptions.RequestException as e:
        # Return the detailed error message from Sentinel Hub if available
        error_details = e.response.text if e.response else str(e)
        print(f"Sentinel Hub API Error: {error_details}")
        return {"error": error_details}


@app.route('/')
def index():
    return render_template("satellite.html")


@app.route('/get_image', methods=['POST'])
def get_image():
    data = request.get_json()
    lat, lon, date = data.get("lat"), data.get("lon"), data.get("date")

    if not all([lat, lon, date]):
        return jsonify({"error": "Missing required parameters (lat, lon, date)"}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Authentication failed. Check Sentinel Hub credentials in .env file."}), 500

    # --- Evalscript for True Color Image ---
    evalscript_true_color = """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B03", "B02"],
                output: { bands: 3 }
            };
        }
        function evaluatePixel(sample) {
            return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
        }
    """

    # --- Evalscript for NDVI Analysis ---
    evalscript_ndvi = """
        //VERSION=3
        function setup() {
            return {
                input: [{ bands: ["B04", "B08"] }],
                output: { id: "default", bands: 3, sampleType: "AUTO" }
            };
        }
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            if (ndvi < -0.2) return [0.0, 0.0, 0.0];
            else if (ndvi < 0.0) return [0.6, 0.4, 0.2];
            else if (ndvi < 0.2) return [0.9, 0.9, 0.2];
            else if (ndvi < 0.5) return [0.2, 0.8, 0.2];
            else return [0.0, 0.6, 0.0];
        }
    """
    
    results = {}
    # Use a thread pool to make both API requests concurrently for faster response
    with ThreadPoolExecutor() as executor:
        future_true_color = executor.submit(fetch_image_from_sentinel, lat, lon, date, token, evalscript_true_color)
        future_ndvi = executor.submit(fetch_image_from_sentinel, lat, lon, date, token, evalscript_ndvi)
        
        results['true_color'] = future_true_color.result()
        results['ndvi'] = future_ndvi.result()

    # Check for errors in the results
    if isinstance(results['true_color'], dict):
        return jsonify({"error": f"Failed to fetch True Color image. Reason: {results['true_color']['error']}"}), 500
    if isinstance(results['ndvi'], dict):
        return jsonify({"error": f"Failed to fetch NDVI image. Reason: {results['ndvi']['error']}"}), 500

    # If successful, encode images to Base64 and send to frontend
    true_color_b64 = base64.b64encode(results['true_color']).decode("utf-8")
    ndvi_b64 = base64.b64encode(results['ndvi']).decode("utf-8")
    
    return jsonify({
        "true_color_b64": true_color_b64,
        "ndvi_b64": ndvi_b64
    })


if __name__ == "__main__":
    app.run(port=5004, debug=True)