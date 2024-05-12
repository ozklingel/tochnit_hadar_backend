import uuid

from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from src.services import db, red
from src.models.base_model import Base

base_blueprint = Blueprint('base', __name__, url_prefix='/base')
@base_blueprint.route('/getLocation', methods=['get'])
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
        return jsonify({'result': str(e)}), HTTPStatus.OK


@base_blueprint.route('/getAll', methods=['get'])
def getAll():
    try:
        baseList = db.session.query(Base).all()
        print(baseList)
        if baseList:
            return  [{"id": str(row.id), 'LAT': str(row.cordinatot).split(" ")[0],'LNG':str(row.cordinatot).split(" ")[1], "name": row.name,"address":row.cordinatot} for row in baseList]
        return jsonify({'result': "error"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@base_blueprint.route('/add', methods=['POST'])
def add():
    try:
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