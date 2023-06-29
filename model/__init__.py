from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEM_TRACK_MODIFICATION'] = False
    db.init_app(app)
    from route.views import views
    app.register_blueprint(views)
    return app