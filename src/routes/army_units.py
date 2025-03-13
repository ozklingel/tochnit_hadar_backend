from flask import Blueprint, jsonify
from http import HTTPStatus

from src.services import db
from src.models.apprentice_model import Apprentice

Hativa_blueprint = Blueprint("army_units", __name__, url_prefix="/army_units")


@Hativa_blueprint.route("", methods=["get"])
def get_all():
    try:

        unit_name = (
            db.session.query(Apprentice.unit_name).distinct(Apprentice.unit_name).all()
        )
        if unit_name:
            return [str(row[0]) for row in unit_name]
        return jsonify({"result": []}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
