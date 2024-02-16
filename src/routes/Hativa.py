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

Hativa_blueprint = Blueprint('Hativa', __name__, url_prefix='/Hativa')
@Hativa_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        unit_name = db.session.query(Apprentice.unit_name).distinct(Apprentice.unit_name).all()
        if unit_name:
            return  [str(row[0]) for row in unit_name]
        return jsonify({'result':[]}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


