from http import HTTPStatus

from flask import Blueprint, request, jsonify
from openpyxl.reader.excel import load_workbook

import config
from app import db
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.contact_form_model import ContactForm
from src.models.gift import gift
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')






@master_user_form_blueprint.route('/setSetting_madadim', methods=['post'])
def setSetting_madadim():
    data = request.json
    try:
        config.call_madad_date = data['call_madad_date']
        config.meet_madad_date = data['meet_madad_date']
        config.groupMeet_madad_date = data['groupMeet_madad_date']
        config.callHorim_madad_date = data['callHorim_madad_date']
        config.madadA_date = data['madadA_date']
        config.madadB_date = data['madadB_date']
        config.madadC_date = data['madadC_date']
        config.madadD_date = data['madadD_date']
    except Exception as e:
        return jsonify({'result': "fail-"+str(e)}), HTTPStatus.OK
    return jsonify({'result': 'success'}), HTTPStatus.OK


@master_user_form_blueprint.route('/getAllSetting_madadim', methods=['GET'])
def getNotificationSetting_form():
    try:
        return jsonify({"eshcolMosadMeet_madad_date":config.eshcolMosadMeet_madad_date,
                        "tochnitMeet_madad_date":config.tochnitMeet_madad_date
                        ,"doForBogrim_madad_date":config.doForBogrim_madad_date,
                        "matzbarmeet_madad_date": config.matzbarmeet_madad_date,
                        "professionalMeet_madad_date": config.professionalMeet_madad_date
                           , "callHorim_madad_date": config.callHorim_madad_date,
                        "groupMeet_madad_date": config.groupMeet_madad_date,
                        "meet_madad_date": config.meet_madad_date
                           , "call_madad_date": config.call_madad_date
                           , "cenes_report": config.cenes_report

                        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK



