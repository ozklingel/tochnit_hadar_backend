import csv
import datetime
import uuid

from openpyxl.reader.excel import load_workbook
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.gift import gift
from src.models.system_report import system_report
from src.models.user_model import user1
from src.models.visit_model import Visit
import src.routes.madadim as md

hadar_plan_session_blueprint = Blueprint('hadar_plan_session', __name__, url_prefix='/hadar_plan_session')
@hadar_plan_session_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        hadar_plan_session = db.session.query(Apprentice.hadar_plan_session).distinct(Apprentice.hadar_plan_session).all()
        if hadar_plan_session:
            return  [ str(row[0]) for row in hadar_plan_session]
        return jsonify({'result':[]}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


