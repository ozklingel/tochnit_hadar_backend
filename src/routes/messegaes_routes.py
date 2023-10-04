import datetime

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


@messegaes_form_blueprint.route('/add', methods=['POST'])
def add_contact_form():
    data = request.json
    subject = data['subject']
    content = data['content']
    created_by_id = data['created_by_id']
    created_for_id = data['created_for_id']
    print(type(created_by_id))
    newToner = ContactForm(
        id=str(uuid.uuid1().int)[:5],
        created_for_id=created_for_id,
        created_by_id=created_by_id,
        content=content,
        subject=subject,
        created_at=None,
        allreadyread=False
    )
    print(newToner.created_by_id)

    db.session.add(newToner)
    db.session.commit()
    if newToner:
        print(f'add contact form: subject: [{subject}, content: {content}, created_by_id: {created_by_id}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'contact_form': request.form}), HTTPStatus.OK
    return jsonify({'result': 'error', 'contact_form': request.form}), HTTPStatus.OK

@messegaes_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')
    print(user)
    reportList = db.session.query(ContactForm).filter(ContactForm.created_for_id == user).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        my_dict.append(
            {"id": str(noti.id), "from": str(noti.created_by_id), "date": str(noti.created_at),
             "content": noti.content, "title": str(noti.subject), "allreadyread": str(noti.allreadyread)})

    if not reportList :
        # acount not found
        return jsonify(["Wrong id or no messages"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@messegaes_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    report_id = request.form.get('report_id')
    noti = Visit.query.get(report_id)
    noti.allreadyread = 'true'
    db.session.commit()
    if report_id:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK