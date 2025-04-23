from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import folium
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

# Store emergency reports
emergencies = []

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        emergency_type = request.form.get('emergency_type')
        location = request.form.get('location')
        lat = request.form.get('lat')
        lon = request.form.get('lon')

        if lat and lon:
            lat = float(lat)
            lon = float(lon)
        else:
            # Fallback to default location if lat/lon not provided
            lat = 20.5937  # Default to India
            lon = 78.9629  # Default to India

        emergency = {
            'type': emergency_type,
            'location': location,
            'lat': lat,
            'lon': lon
        }

        emergencies.append(emergency)
        message = f"Emergency '{emergency_type}' reported at {location}!"

    # Create map with reported emergencies
    map_ = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    for e in emergencies:
        folium.Marker(
            [e['lat'], e['lon']], popup=f"<b>{e['type']}</b><br>{e['location']}"
        ).add_to(map_)

    # Save the map to a PNG image
    map_html = map_.get_root().render()

    # Generate emergency chart
    emergency_types = [e['type'] for e in emergencies]
    fig, ax = plt.subplots()
    ax.hist(emergency_types, bins=len(set(emergency_types)), edgecolor='black')
    ax.set_title('Emergency Type Distribution')
    ax.set_xlabel('Emergency Type')
    ax.set_ylabel('Frequency')

    # Save chart to base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return render_template('index.html', message=message, emergencies=emergencies, chart=chart_base64)

@app.route('/clear', methods=['POST'])
def clear_emergencies():
    emergencies.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
