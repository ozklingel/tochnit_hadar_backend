import uuid

from http import HTTPStatus
from flask import Blueprint, request, jsonify

from src.routes.user_profile import correct_auth
from src.services import db
from src.models.base_model import Base

base_blueprint = Blueprint('base', __name__, url_prefix='/base')


@base_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        baseList = db.session.query(Base).all()
        if baseList:
            return [
                {"id": str(row.id), 'LAT': str(row.cordinatot).split(" ")[0], 'LNG': str(row.cordinatot).split(" ")[1],
                 "name": row.name, "address": row.cordinatot} for row in baseList]
        return jsonify({'result': "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@base_blueprint.route('/add', methods=['POST'])
def add():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        name = data['name']
        cordinatot = data['cordinatot']
        city = Base(
            id=str(uuid.uuid1().int)[:5],  # if ent_group_name!="" else str(uuid.uuid1().int)[:5],
            name=name,
            cordinatot=cordinatot
        )
        db.session.add(city)
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@base_blueprint.route('/upload_baseDB', methods=['PUT'])
def upload_baseDB():
    try:
        import csv
        my_list = []
        # /home/ubuntu/flaskapp/
        with open('data/base_add.csv', 'r', encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                ent = Base(int(str(uuid.uuid4().int)[:5]), row[0].strip(), row[1].strip())
                db.session.add(ent)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
