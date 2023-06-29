from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

# Create a flask app.
app = Flask(__name__)
# Set database url and passward.
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)
import route.routes, model.models

if __name__ == '__main__':
    db.create_all()
    app.run()
