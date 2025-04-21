
from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

# Dummy emergency data
emergencies = [
    {"id": 1, "type": "Flood", "location": "Mumbai", "priority": "High", "timestamp": "2025-04-21 10:30"},
    {"id": 2, "type": "Earthquake", "location": "Delhi", "priority": "Medium", "timestamp": "2025-04-21 09:45"},
]

@app.route("/")
def index():
    return render_template("index.html", emergencies=emergencies)

@app.route("/report", methods=["POST"])
def report():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    new_id = max(e["id"] for e in emergencies) + 1 if emergencies else 1
    emergencies.append({
        "id": new_id,
        "type": data.get("type", "Unknown"),
        "location": data.get("location", "Unknown"),
        "priority": data.get("priority", "Low"),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return jsonify({"success": True, "emergencies": emergencies})

if __name__ == "__main__":
    app.run(debug=True)
