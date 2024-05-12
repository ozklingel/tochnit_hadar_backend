import uuid

from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from src.services import db, red
from src.models.base_model import Base
from src.models.city_model import City

city_blueprint = Blueprint('city', __name__, url_prefix='/city')
@city_blueprint.route('/getLocation', methods=['get'])
def getLocation():
    try:
        base1 = request.args.get('base_id')
        print(base1)

        baseEnt = db.session.query(Base).filter(Base.id==base1).first()
        print(baseEnt)
        if baseEnt:
            cordArray=str(baseEnt.cordinatot).split(" ")
            return jsonify({'id': str(baseEnt.id),'LAT': cordArray[0],'LNG':cordArray[1],'name': baseEnt.name,"address":"מישור אדומים"}), HTTPStatus.OK
        return jsonify({'result': "error"}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@city_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        CityList = db.session.query(City).all()
        print(CityList)
        if CityList:
            return  [{"id": str(row.id), "name": row.name,"cluster_id":row.cluster_id} for row in CityList]
        return jsonify({'result': "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@city_blueprint.route('/add', methods=['POST'])
def add():
    try:
        data = request.json
        name = data['name']
        cluster_id = data['cluster']
        city = City(
            id=str(uuid.uuid1().int)[:5],  # if ent_group_name!="" else str(uuid.uuid1().int)[:5],
            name=name,
            cluster_id=cluster_id
        )
        db.session.add(city)
        db.session.commit()
        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST