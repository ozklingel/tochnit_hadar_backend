from flask import Blueprint, jsonify
from http import HTTPStatus
from src.models.cluster_model import Cluster
from src.services import db


eshcol_blueprint = Blueprint("cluster", __name__, url_prefix="/cluster")


@eshcol_blueprint.route("", methods=["get"])
def get_all():
    try:
        eshcols_user = db.session.query(Cluster).all()
        return jsonify([{"id": r.id, "name": r.name} for r in eshcols_user])
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
