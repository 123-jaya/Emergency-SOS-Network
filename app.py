from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Vercel using Python and Flask!"

# No need for if __name__ == "__main__" because Vercel handles execution