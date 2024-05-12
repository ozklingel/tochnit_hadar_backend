from flask import Flask, app
from flask_cors import CORS
from src.services import db
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY
db.init_app(app)


app.config['S3_BUCKET'] = "S3_BUCKET_NAME"
app.config['S3_KEY'] = "AWS_ACCESS_KEY"
app.config['S3_SECRET'] = "AWS_ACCESS_SECRET"
app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'


# register blueprints
from src.routes.messegaes_routes import messegaes_form_blueprint
from src.routes.reports_routes import reports_form_blueprint
from src.routes.onboarding_form_routes import onboarding_form_blueprint
from src.routes.notification_form_routes import notification_form_blueprint
from src.routes.setEntityDetails_form_routes import setEntityDetails_form_blueprint
from src.routes.user_Profile import userProfile_form_blueprint
from src.routes.homepage import homepage_form_blueprint
from src.routes.madadim import madadim_form_blueprint
from src.routes.tasks import tasks_form_blueprint
from src.routes.masterUser import master_user_form_blueprint
from src.routes.export_import import export_import_blueprint
from src.routes.institutionProfile_routes import institutionProfile_form_blueprint
from src.routes.base import base_blueprint
from src.routes.apprentice_Profile import apprentice_Profile_form_blueprint
from src.routes.eshcol import eshcol_blueprint
from src.routes.Hativa import Hativa_blueprint
from src.routes.hadar_plan_session import hadar_plan_session_blueprint
from src.routes.search_ent import search_bar_form_blueprint
from src.routes.city import city_blueprint
from src.routes.gift import gift_blueprint

app.register_blueprint(userProfile_form_blueprint)
app.register_blueprint(setEntityDetails_form_blueprint)
app.register_blueprint(notification_form_blueprint)
app.register_blueprint(onboarding_form_blueprint)
app.register_blueprint(reports_form_blueprint)
app.register_blueprint(messegaes_form_blueprint)
app.register_blueprint(homepage_form_blueprint)
app.register_blueprint(madadim_form_blueprint)
app.register_blueprint(tasks_form_blueprint)
app.register_blueprint(export_import_blueprint)
app.register_blueprint(master_user_form_blueprint)
app.register_blueprint(institutionProfile_form_blueprint)
app.register_blueprint(base_blueprint)
app.register_blueprint(apprentice_Profile_form_blueprint)
app.register_blueprint(eshcol_blueprint)
app.register_blueprint(Hativa_blueprint)
app.register_blueprint(hadar_plan_session_blueprint)
app.register_blueprint(search_bar_form_blueprint)
app.register_blueprint(city_blueprint)
app.register_blueprint(gift_blueprint)

if __name__ == '__main__':

    app.run(debug=True)