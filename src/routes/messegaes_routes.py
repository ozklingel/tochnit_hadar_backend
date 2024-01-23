import datetime
import json
import time
from datetime import datetime,date

import boto3
import flask
from twilio.rest import Client

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from config import AWS_access_key_id, AWS_secret_access_key
from ..models.contact_form_model import ContactForm
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid

from ..models.visit_model import Visit

messegaes_form_blueprint = Blueprint('messegaes_form', __name__, url_prefix='/messegaes_form')
@messegaes_form_blueprint.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    data = request.json
    print(data)
    subject = data['subject']
    content = data['content']
    account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
    auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body='Hello there!',
        to='whatsapp:+972549247616'
    )

    print(message.sid)
#from chat box
@messegaes_form_blueprint.route('/add', methods=['POST'])
def add_contact_form():
    data = request.json
    print(data)
    subject = data['subject']
    content = data['content']
    attachments=[]
    icon=""
    try:
        icon = data['icon']
    except:
        print("no icon")
    created_by_id = str(data['created_by_id'])[3:]
    created_for_id = str(data['created_for_id'])[3:]

    files = request.files.getlist('file[]')
    for file in files:
        print(file)
        new_filename = uuid.uuid4().hex + '.' + file.filename.rsplit('.', 1)[1].lower()
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
            s3_client.upload_fileobj(file, bucket_name, new_filename)
            attachments.append(new_filename)
        except:
            return jsonify({'result': 'faild', 'image path': new_filename}), HTTPStatus.OK

    try:
        ContactForm1 = ContactForm(
            id=str(uuid.uuid1().int)[:5],
            created_for_id=created_for_id,
            created_by_id=created_by_id,
            content=content,
            subject=subject,
            created_at=date.today(),
            allreadyread=False,
            attachments=attachments,
            icon=icon
        )
        db.session.add(ContactForm1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if ContactForm1:
        print(f'add contact form: subject: [{subject}, content: {content}, created_by_id: {created_by_id}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
@messegaes_form_blueprint.route('/getAll', methods=['GET'])
def getAll_messegases_form():
    user = request.args.get('userId')[3:]
    print(user)
    messegasesList = db.session.query(ContactForm).filter(ContactForm.created_for_id == user).all()
    print(messegasesList)
    my_dict = []
    for mess in messegasesList:
        print(mess.attachments)
        my_dict.append(
            {"attachments":mess.attachments,"id": str(mess.id), "from": str(mess.created_by_id), "date":toISO(mess.created_at),
             "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),"icon":mess.icon})

    if not messegasesList:
        # acount not found
        return jsonify([])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@messegaes_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_message_form():
    data = request.json
    message_id = data['message_id']
    print(message_id)
    try:
        noti = ContactForm.query.get(message_id)
        noti.allreadyread = True
        db.session.commit()
        if message_id:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK
def toISO(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None

