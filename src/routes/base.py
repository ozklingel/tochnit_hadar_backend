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

base_blueprint = Blueprint('base', __name__, url_prefix='/base')
@base_blueprint.route('/getLocation', methods=['get'])
def getLocation():
    try:
        base1 = request.args.get('base_id')
        print(base1)

        baseEnt = db.session.query(Base).filter(Base.id==base1).first()
        print(baseEnt)
        if baseEnt:
            cordArray=str(baseEnt.cordinatot).split(" ")
            return jsonify({'id': str(baseEnt.id),'LAT': cordArray[0],'LANG':cordArray[1],'name': baseEnt.name}), HTTPStatus.OK
        return jsonify({'result': "error"}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@base_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        baseList = db.session.query(Base).all()
        print(baseList)
        if baseList:
            return  [{"id": str(row.id), "cordinatot": row.cordinatot, "name": row.name} for row in baseList]
        return jsonify({'result': "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK