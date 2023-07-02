from flask import Flask 
from flask_sqlalchemy import SQLAlchemy


def create_app():
     # Database initialize with app.
    db.init_app(app)
    from route.routes import views
     #blueprints for making application components and supporting common patterns within an application
    app.register_blueprint(views)
    return app
