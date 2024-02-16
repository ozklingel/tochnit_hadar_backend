import json
import pickle
from datetime import datetime
import time
import uuid
import boto3

import werkzeug
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

apprentice_Profile_form_blueprint = Blueprint('apprentice_Profile_form', __name__, url_prefix='/apprentice_Profile_form')
@apprentice_Profile_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        apprenticetId = data['apprenticetId'][3:]
        print(apprenticetId)
        res = db.session.query(notifications).filter(notifications.apprenticeid == apprenticetId, ).delete()
        res = db.session.query(Visit).filter(Visit.ent_reported == apprenticetId, ).delete()
        res = db.session.query(Apprentice).filter(Apprentice.id == apprenticetId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@apprentice_Profile_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    apprenticetId = request.args.get("apprenticetId")[3:]
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
@apprentice_Profile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        apprenticeId = request.args.get('apprenticeId')[3:]
        print(apprenticeId)
        print(request.files)
        imagefile = request.files['image']
        #filename = werkzeug.utils.secure_filename(imagefile.filename)
        #print("\nReceived image File name : " + imagefile.filename)
        #imagefile.save( filename)
        new_filename = uuid.uuid4().hex + '.' + imagefile.filename.rsplit('.', 1)[1].lower()
        bucket_name = "th01-s3"
        session = boto3.Session()
        s3_client = session.client('s3',
                            aws_access_key_id=AWS_access_key_id,
                            aws_secret_access_key=AWS_secret_access_key)
        s3 = boto3.resource('s3',
                            aws_access_key_id=AWS_access_key_id,
                            aws_secret_access_key=AWS_secret_access_key)
        print(new_filename)
        try:
            s3_client.upload_fileobj(imagefile, bucket_name, new_filename)
        except:
            return jsonify({'result': 'faild', 'image path': new_filename}), HTTPStatus.OK
        updatedEnt = Apprentice.query.get(apprenticeId)
        updatedEnt.photo_path="https://th01-s3.s3.eu-north-1.amazonaws.com/"+new_filename
        db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
        return jsonify({'result': 'success', 'image path': new_filename}), HTTPStatus.OK



