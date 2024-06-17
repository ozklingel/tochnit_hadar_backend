from flask import Blueprint, jsonify
from http import HTTPStatus

from src.routes.user_profile import correct_auth
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.user_model import User

eshcol_blueprint = Blueprint('eshcol', __name__, url_prefix='/eshcol')


@eshcol_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        eshcols_user = db.session.query(User.eshcol).distinct(User.eshcol).all()
        eshcols_appren = db.session.query(Apprentice.eshcol).distinct(Apprentice.eshcol).all()
        eshcols_user_ids = [str(row[0]) for row in eshcols_user]
        eshcols_appren_ids = [str(row[0]) for row in eshcols_appren]
        result = eshcols_user_ids + list(set(eshcols_appren_ids) - set(eshcols_user_ids))
        return result
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
