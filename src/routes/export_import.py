import csv
import datetime
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify, send_file
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
@export_import_blueprint.route("/export_dict", methods=['post'])
def export_apprentice_score():
    data = request.json
    print(data)
    my_dict = data['dict']
    print(my_dict)
    with open('/home/ubuntu/flaskapp/dict2.csv', 'w') as f:
        w = csv.DictWriter(f, my_dict.keys())
        w.writeheader()
        w.writerow(my_dict)
    return send_file("/home/ubuntu/flaskapp/dict2.csv", as_attachment=True, download_name="/home/ubuntu/flaskapp/dict2.csv")
