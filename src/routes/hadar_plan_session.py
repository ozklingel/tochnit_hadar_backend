from flask import Blueprint, jsonify
from http import HTTPStatus

from src.routes.user_Profile import correct_auth
from src.services import db, red
from src.models.apprentice_model import Apprentice

hadar_plan_session_blueprint = Blueprint('hadar_plan_session', __name__, url_prefix='/hadar_plan_session')


@hadar_plan_session_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        hadar_plan_session = db.session.query(Apprentice.hadar_plan_session).distinct(
            Apprentice.hadar_plan_session).all()
        if hadar_plan_session:
            return [str(row[0]) for row in hadar_plan_session]
        return jsonify({'result': []}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
