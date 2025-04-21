# api/index.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask on Vercel!"

# Required for Vercel's WSGI interface
from flask import Request, Response
def handler(request: Request) -> Response:
    return app.wsgi_app(request.environ, lambda status, headers: None)
