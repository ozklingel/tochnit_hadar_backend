from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY

# register blueprints

db = SQLAlchemy(app)
from src.routes.messegaes_routes import messegaes_form_blueprint
from src.routes.reports_routes import reports_form_blueprint
from src.routes.onboarding_form_routes import onboarding_form_blueprint
from src.routes.notification_form_routes import notification_form_blueprint
from src.routes.setEntityDetails_form_routes import setEntityDetails_form_blueprint

app.register_blueprint(setEntityDetails_form_blueprint)
app.register_blueprint(notification_form_blueprint)

app.register_blueprint(onboarding_form_blueprint)
app.register_blueprint(reports_form_blueprint)
app.register_blueprint(messegaes_form_blueprint)

if __name__ == '__main__':
    app.run(debug=True)