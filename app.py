from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import datetime

app = Flask(__name__)
geolocator = Nominatim(user_agent="sos_app")

# Simulated emergency data (you can expand this)
emergencies = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    message = data.get("message", "")
    location = data.get("location", "")

    # Get coordinates using Geopy
    try:
        loc = geolocator.geocode(location)
        lat = loc.latitude
        lon = loc.longitude
    except:
        return jsonify({"error": "Invalid location"}), 400

    # Add emergency to list with timestamp
    emergencies.append({
        "message": message,
        "location": location,
        "latitude": lat,
        "longitude": lon,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"status": "Emergency reported successfully!"})

@app.route('/emergencies', methods=['GET'])
def get_emergencies():
    return jsonify(emergencies)

# Only for local testing: CLI-based input
if __name__ == "__main__":
    print("Running locally...")

    message = input("Enter your emergency message: ")
    location = input("Enter your location (e.g., Mumbai, India): ")

    # Simulate HTTP POST to /report
    with app.test_client() as client:
        response = client.post("/report", json={"message": message, "location": location})
        print("Response:", response.get_json())

    # Start Flask server
    app.run(debug=True)
