from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

# Create a flask app.
app = Flask(__name__)
# Set database url and passward.
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY
#create an object of class SQLAlchemy
db = SQLAlchemy(app)


import route.routes, model.models

if __name__ == '__main__':
    #create the tables and database
    db.create_all()
    # Database initialize with app.
    db.init_app(app)
    from route.routes import views
    #blueprints for making application components and supporting common patterns
    app.register_blueprint(views)
    #now app is running and route.routes.py you need to create the APIs
