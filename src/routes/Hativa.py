from flask import Blueprint, jsonify
from http import HTTPStatus

from src.routes.user_Profile import correct_auth
from src.services import db, red
from src.models.apprentice_model import Apprentice

Hativa_blueprint = Blueprint('Hativa', __name__, url_prefix='/Hativa')


@Hativa_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        if correct_auth()==False:
            return jsonify({'result': f"wrong access token "}), HTTPStatus.OK
        unit_name = db.session.query(Apprentice.unit_name).distinct(Apprentice.unit_name).all()
        if unit_name:
            return [str(row[0]) for row in unit_name]
        return jsonify({'result': []}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
