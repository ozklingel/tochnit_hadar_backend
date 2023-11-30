import datetime
import time
from datetime import date

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path
from ..models.contact_form_model import ContactForm
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid

from ..models.visit_model import Visit

messegaes_form_blueprint = Blueprint('messegaes_form', __name__, url_prefix='/messegaes_form')

#from chat box
@messegaes_form_blueprint.route('/add', methods=['POST'])
def add_contact_form():
    data = request.json
    print(data)
    subject = data['subject']
    content = data['content']
    attachments=""
    try:
        attachments = data['attachments']
    except:
        print("no attachments")
    created_by_id = str(data['created_by_id'])[4:]
    created_for_id=None
    try:
        created_for_id = str(data['created_for_id'])[4:]
    except:
        print("no created_for_id")
    ContactForm1 = ContactForm(
        id=str(uuid.uuid1().int)[:5],
        created_for_id=created_for_id,
        created_by_id=created_by_id,
        content=content,
        subject=subject,
        created_at=date.today(),
        allreadyread=False,
        attachments=attachments
    )
    print(ContactForm1.created_by_id)

    db.session.add(ContactForm1)
    db.session.commit()
    if ContactForm1:
        print(f'add contact form: subject: [{subject}, content: {content}, created_by_id: {created_by_id}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
    return jsonify({'result': 'error while inserting'}), HTTPStatus.OK

@messegaes_form_blueprint.route('/getAll', methods=['GET'])
def getAll_messegases_form():
    user = request.args.get('userId')[4:]
    print(user)
    messegasesList = db.session.query(ContactForm).filter(ContactForm.created_for_id == user).all()
    print(messegasesList)
    my_dict = []
    for mess in messegasesList:
        my_dict.append(
            {"attachments":mess.attachments,"id": str(mess.id), "from": str(mess.created_by_id), "date": time.mktime(mess.created_at.timetuple()) if mess.created_at is not None else None,
             "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread)})

    if not messegasesList :
        # acount not found
        return jsonify(["Wrong id or no messages"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@messegaes_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    mess_id = request.form.get('report_id')
    mess = Visit.query.get(mess_id)
    mess.allreadyread = 'true'
    db.session.commit()
    if mess_id:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'mess form': request.form}), HTTPStatus.OK