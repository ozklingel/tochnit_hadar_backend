
import uuid
import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from app import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.visit_model import Visit

apprentice_Profile_form_blueprint = Blueprint('apprentice_Profile_form', __name__, url_prefix='/apprentice_Profile_form')
@apprentice_Profile_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        apprenticetId = data['apprenticetId']
        print(apprenticetId)
        res = db.session.query(notifications).filter(notifications.apprenticeid == apprenticetId, ).delete()
        res = db.session.query(Visit).filter(Visit.ent_reported == apprenticetId, ).delete()
        res = db.session.query(Apprentice).filter(Apprentice.id == apprenticetId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.OK
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@apprentice_Profile_form_blueprint.route("/update", methods=['put'])
def updateTask():
    try:
        # get tasksAndEvents
        apprenticetId = request.args.get("apprenticetId")
        print(apprenticetId)
        data = request.json
        updatedEnt = Apprentice.query.get(apprenticetId)
        for key in data:
            setattr(updatedEnt, key, data[key])
        db.session.commit()
        if updatedEnt:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK



