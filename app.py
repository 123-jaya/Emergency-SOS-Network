from flask import Flask, render_template, request, redirect
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
    return render_template("index.html", emergencies=emergencies, chart=chart, message=message)

@app.route('/map')
def map_view():
    return render_template("map.html")

@app.route('/clear', methods=['POST'])
def clear():
    emergencies.clear()
    save_map()
    return redirect("/")

if __name__ == '__main__':
    save_map()
    print("app ready to serve via gunicorn..")
