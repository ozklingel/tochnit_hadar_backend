import redis
from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY
db = SQLAlchemy()
db.init_app(app)
red = redis.StrictRedis(host='localhost', port=6379, db=0)

# register blueprints
from src.routes.messegaes_routes import messegaes_form_blueprint
from src.routes.reports_routes import reports_form_blueprint
from src.routes.onboarding_form_routes import onboarding_form_blueprint
from src.routes.notification_form_routes import notification_form_blueprint
from src.routes.setEntityDetails_form_routes import setEntityDetails_form_blueprint
from src.routes.userProfile_routes import userProfile_form_blueprint
from src.routes.homepage import homepage_form_blueprint
from src.routes.madadim import madadim_form_blueprint
from src.routes.tasks import tasks_form_blueprint

app.register_blueprint(userProfile_form_blueprint)
app.register_blueprint(setEntityDetails_form_blueprint)
app.register_blueprint(notification_form_blueprint)
app.register_blueprint(onboarding_form_blueprint)
app.register_blueprint(reports_form_blueprint)
app.register_blueprint(messegaes_form_blueprint)
app.register_blueprint(homepage_form_blueprint)
app.register_blueprint(madadim_form_blueprint)
app.register_blueprint(tasks_form_blueprint)

if __name__ == '__main__':

    app.run(debug=True)