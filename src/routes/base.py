import uuid

from http import HTTPStatus
from flask import Blueprint, request, jsonify

from src.services import db
from src.models.base_model import Base

base_blueprint = Blueprint("base", __name__, url_prefix="/bases")


@base_blueprint.route("", methods=["get"])
def get_all():
    try:

        baseList = db.session.query(Base).all()
        if baseList:
            return [
                {
                    "id": str(row.id),
                    "LAT": str(row.cordinatot).split(",")[0],
                    "LNG": str(row.cordinatot).split(",")[1],
                    "name": row.name,
                    "address": row.cordinatot,
                }
                for row in baseList
            ]
        return jsonify({"result": "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@base_blueprint.route("/add", methods=["POST"])
def add():
    try:

        data = request.json
        name = data["name"]
        cordinatot = data["cordinatot"]
        city = Base(
            id=str(uuid.uuid1().int)[
                :5
            ],  # if ent_group_name!="" else str(uuid.uuid1().int)[:5],
            name=name,
            cordinatot=cordinatot,
        )
        db.session.add(city)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@base_blueprint.route("/upload_baseDB", methods=["PUT"])
def upload_base():
    try:
        import csv

        base_dir = "/home/ubuntu/flaskapp/"

        # /home/ubuntu/flaskapp/
        with open(base_dir + "data/base_add.csv", "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                ent = Base(
                    int(str(uuid.uuid4().int)[:5]),
                    row[0].strip(),
                    row[1].strip() + "," + row[2].strip(),
                )
                db.session.add(ent)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.OK
