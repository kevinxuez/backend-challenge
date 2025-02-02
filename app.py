from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"

@app.route("/api")
def api():
    return jsonify("hi")


if __name__ == "__main__":
    app.run()

