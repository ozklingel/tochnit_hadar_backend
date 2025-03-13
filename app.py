from flask import Flask
from src.services import db
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = SECRET_KEY

    db.init_app(app)

    app.config["S3_BUCKET"] = "S3_BUCKET_NAME"
    app.config["S3_KEY"] = "AWS_ACCESS_KEY"
    app.config["S3_SECRET"] = "AWS_ACCESS_SECRET"
    app.config["S3_LOCATION"] = "http://{}.s3.amazonaws.com/"
    app.json.sort_keys = False

    with app.app_context():
        # Import all models here
        from src.models.task_model_v2 import Task, TaskFrequency
        from src.models.user_model import User
        from src.models.task_model_v2 import Task

        # Import other models as needed

        db.create_all()

    # register blueprints
    from src.routes.messages import messages_form_blueprint
    from src.routes.reports import reports_form_blueprint
    from src.routes.onboarding import onboarding_form_blueprint
    from src.routes.notifications import notification_form_blueprint
    from src.routes.users import userProfile_form_blueprint
    from src.routes.homepage import homepage_form_blueprint
    from src.routes.performance_metrics import madadim_form_blueprint
    from src.routes.tasks import tasks_form_blueprint
    from src.routes.master_user import master_user_form_blueprint
    from src.routes.export_import import export_import_blueprint
    from src.routes.institutions import institutionProfile_form_blueprint
    from src.routes.base import base_blueprint
    from src.routes.apprentice import apprentice_profile_form_blueprint
    from src.routes.cluster import eshcol_blueprint
    from src.routes.army_units import Hativa_blueprint
    from src.routes.hadar_plan_session import hadar_plan_session_blueprint
    from src.routes.search_ent import search_bar_form_blueprint
    from src.routes.city import city_blueprint
    from src.routes.gift import gift_blueprint

    app.register_blueprint(userProfile_form_blueprint)
    app.register_blueprint(notification_form_blueprint)
    app.register_blueprint(onboarding_form_blueprint)
    app.register_blueprint(reports_form_blueprint)
    app.register_blueprint(messages_form_blueprint)
    app.register_blueprint(homepage_form_blueprint)
    app.register_blueprint(madadim_form_blueprint)
    app.register_blueprint(tasks_form_blueprint)
    app.register_blueprint(export_import_blueprint)
    app.register_blueprint(master_user_form_blueprint)
    app.register_blueprint(institutionProfile_form_blueprint)
    app.register_blueprint(base_blueprint)
    app.register_blueprint(apprentice_profile_form_blueprint)
    app.register_blueprint(eshcol_blueprint)
    app.register_blueprint(Hativa_blueprint)
    app.register_blueprint(hadar_plan_session_blueprint)
    app.register_blueprint(search_bar_form_blueprint)
    app.register_blueprint(city_blueprint)
    app.register_blueprint(gift_blueprint)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
