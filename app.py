from flask import Flask, render_template_string, request, redirect
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import io
import base64
import matplotlib.pyplot as plt
import os
import webbrowser

app = Flask(__name__)
geolocator = Nominatim(user_agent="sos_app")

emergencies = []

html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>SOS Rescue Network</title>
    <style>
        body {
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                        url('/static/bg.jpg') no-repeat center center fixed;
            background-size: cover;
            color: white;
            animation: fadeIn 1.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .container {
            background-color: rgba(0,0,0,0.8);
            padding: 20px;
            margin: 40px auto;
            border-radius: 12px;
            max-width: 900px;
            box-shadow: 0 0 25px rgba(255, 255, 255, 0.1);
        }
        h1, h2 {
            text-align: center;
        }
        iframe {
            width: 100%;
            height: 450px;
            border-radius: 10px;
            border: none;
            box-shadow: 0 0 12px rgba(0,0,0,0.3);
        }
        img {
            display: block;
            margin: 15px auto;
            max-width: 400px;
            border-radius: 10px;
        }
        .form-section, .message, .history, .contacts {
            text-align: center;
            margin-top: 20px;
        }
        input, select, button {
            padding: 10px;
            font-size: 15px;
            margin: 5px;
            border-radius: 6px;
            border: none;
            transition: all 0.3s ease;
        }
        button:hover {
            transform: scale(1.05);
            background-color: #2ecc71;
            color: black;
        }
        .clear-button {
            background-color: crimson;
            color: white;
            margin-top: 10px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            background: rgba(255, 255, 255, 0.1);
            margin: 5px auto;
            padding: 10px;
            border-radius: 6px;
            max-width: 600px;
            transition: background-color 0.2s ease;
        }
        li:hover {
            background: rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🌐 SOS Rescue Network</h1>

    <div class="form-section">
        <form method="POST" action="/">
            <select name="emergency_type">
                <option>Medical</option>
                <option>Fire</option>
                <option>Flood</option>
                <option>Earthquake</option>
                <option>Accident</option>
                <option>Other</option>
            </select>
            <input name="location" placeholder="Enter City or Place" required>
            <button type="submit">🚨 Trigger Emergency</button>
        </form>
    </div>

    {% if message %}
    <div class="message">
        <p><strong>{{ message }}</strong></p>
    </div>
    {% endif %}

    {% if emergencies %}
    <div class="history">
        <h2>📍 Emergency Reports</h2>
        <ul>
        {% for e in emergencies %}
            <li>🔴 {{ e.type }} at {{ e.location }} (Lat: {{ e.lat }}, Lon: {{ e.lon }})</li>
        {% endfor %}
        </ul>
        <form method="POST" action="/clear">
            <button class="clear-button">🧹 Clear Notifications</button>
        </form>
    </div>
    {% endif %}

    <h2>🗺️ Emergency Locations Map</h2>
    <iframe src="/map"></iframe>

    {% if chart %}
    <h2>📊 Emergency Types Distribution</h2>
    <img src="data:image/png;base64,{{ chart }}" alt="Pie Chart"/>
    {% endif %}

    <div class="contacts">
        <h2>📞 Emergency Contacts</h2>
        <p>🚒 Fire: 101</p>
        <p>🚑 Ambulance: 102</p>
        <p>🚓 Police: 100</p>
        <p>🌊 Flood Helpline: 1070</p>
    </div>
</div>
</body>
</html>
'''

def save_map():
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    cluster = MarkerCluster().add_to(m)
    for e in emergencies:
        folium.Marker(
            location=[e["lat"], e["lon"]],
            popup=f"{e['type']} at {e['location']}",
            icon=folium.Icon(color="red" if e["type"] == "Fire" else "blue")
        ).add_to(cluster)
    os.makedirs("templates", exist_ok=True)
    m.save("templates/map.html")

def generate_chart():
    type_count = {}
    for e in emergencies:
        type_count[e["type"]] = type_count.get(e["type"], 0) + 1
    if not type_count:
        return ""
    labels, sizes = zip(*type_count.items())
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        e_type = request.form['emergency_type']
        location = request.form['location']
        loc = geolocator.geocode(location)
        if loc:
            emergencies.append({
                "type": e_type,
                "location": location,
                "lat": loc.latitude,
                "lon": loc.longitude
            })
            save_map()
            message = f"✅ Emergency '{e_type}' triggered at {location}"
        else:
            message = f"❌ Location '{location}' not found. Try again."

    chart = generate_chart()
    return render_template_string(html_template, emergencies=emergencies, chart=chart, message=message)

@app.route('/map')
def map_view():
    return open("templates/map.html").read()

@app.route('/clear', methods=['POST'])
def clear():
    emergencies.clear()
    save_map()
    return redirect("/")

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    save_map()
    print("app ready to serve via gunicorn..")
