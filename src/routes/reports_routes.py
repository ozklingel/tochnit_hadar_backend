import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path
pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid
from ..models.visit_model import Visit

reports_form_blueprint = Blueprint('reports_form', __name__, url_prefix='/reports_form')

@reports_form_blueprint.route('/add', methods=['post'])
def add_reports_form():
    data = request.json
    user = data['userId']
    print(user)
    updatedEnt = None
    if user:
        List_of_apprentices = data['List_of_apprentices']
        print(data['event_details'])
        for key in List_of_apprentices:
            newToner = Visit(
                user_id=user,
                apprentice_id=key['id'],
                note=data['event_details'],
                visit_in_army=bool(data['event_type']),
                visit_date=data['date'],
                allreadyread=False,
                id=int(str(uuid.uuid4().int)[:5]),
                title=data['event_type']
            )
            print(newToner)
            db.session.add(newToner)
    db.session.commit()
    if user is None  :
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')
    print(user)
    reportList = db.session.query(Visit).filter(Visit.user_id == user).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        daysFromNow = str(datetime.date.today() - noti.visit_date) if noti.visit_date is not None else None
        my_dict.append(
            {"id": str(noti.id), "from": str(noti.apprentice_id), "date": str(noti.visit_date),
             "days_from_now": daysFromNow , "title": str(noti.title), "allreadyread": str(noti.allreadyread)})

    if not reportList :
        # acount not found
        return jsonify(["Wrong id or empty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    report_id = request.form.get('report_id')
    noti = Visit.query.get(report_id)
    noti.allreadyread = 'true'
    db.session.commit()
    if report_id:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK
