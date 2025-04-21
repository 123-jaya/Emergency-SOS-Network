from flask import Flask, request, jsonify, render_template_string
import folium
import matplotlib.pyplot as plt
import io
import base64
from geopy.distance import geodesic

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return jsonify({"status": "Received POST data!"})
    return render_template_string("<h1>Hello from Flask on Vercel!</h1>")

def handler(environ, start_response):
    return app(environ, start_response)