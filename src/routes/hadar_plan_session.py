
from flask import Blueprint, jsonify
from http import HTTPStatus

from src.services import db, red
from src.models.apprentice_model import Apprentice


hadar_plan_session_blueprint = Blueprint('hadar_plan_session', __name__, url_prefix='/hadar_plan_session')
@hadar_plan_session_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        hadar_plan_session = db.session.query(Apprentice.hadar_plan_session).distinct(Apprentice.hadar_plan_session).all()
        if hadar_plan_session:
            return  [ str(row[0]) for row in hadar_plan_session]
        return jsonify({'result':[]}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


