import uuid

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from src.routes.user_profile import correct_auth
from src.services import db
from src.models.base_model import Base
from src.models.city_model import City

city_blueprint = Blueprint('city', __name__, url_prefix='/city')


@city_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        CityList = db.session.query(City).all()
        if CityList:
            return [{"id": str(row.id), "name": row.name, "cluster_id": row.region_id} for row in CityList]
        return jsonify({'result': "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@city_blueprint.route('/add', methods=['POST'])
def add():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        name = data['name']
        region_id = data['cluster']
        city = City(
            id=str(uuid.uuid1().int)[:5],  # if ent_group_name!="" else str(uuid.uuid1().int)[:5],
            name=name,
            region_id=region_id
        )
        db.session.add(city)
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
