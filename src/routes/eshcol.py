from flask import Blueprint, jsonify
from http import HTTPStatus

from src.models.cluster_model import Cluster
from src.routes.user_profile import correct_auth
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.user_model import User

eshcol_blueprint = Blueprint('eshcol', __name__, url_prefix='/eshcol')


@eshcol_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        eshcols_user = db.session.query(Cluster).all()
        return jsonify([{"id":r.id,"name":r.name} for r in eshcols_user])
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
