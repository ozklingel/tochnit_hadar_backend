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

eshcol_blueprint = Blueprint('eshcol', __name__, url_prefix='/eshcol')
@eshcol_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        eshcols_user = db.session.query(user1.eshcol).distinct(user1.eshcol).all()
        eshcols_appren = db.session.query(Apprentice.eshcol).distinct(Apprentice.eshcol).all()
        eshcols_user_ids=[str(row[0]) for row in eshcols_user]
        eshcols_appren_ids=[str(row[0])for row in eshcols_appren]
        result = eshcols_user_ids + list(set(eshcols_appren_ids) - set(eshcols_user_ids))
        return  result
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


