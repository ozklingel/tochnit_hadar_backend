import csv
import datetime
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

export_import_blueprint = Blueprint('export_import', __name__, url_prefix='/export_import')
@export_import_blueprint.route("/export_apprentice_score", methods=['GET'])
def export_apprentice_score():
    my_dict = {"test": 1, "testing": 2}

    with open('mycsvfile.csv', 'w') as f:  # You will need 'wb' mode in Python 2.x
        w = csv.DictWriter(f, my_dict.keys())
        w.writeheader()
        w.writerow(my_dict)