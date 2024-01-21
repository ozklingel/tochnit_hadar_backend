import datetime
import json
from datetime import datetime,date

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
    user = str(data['userId'])[3:]
    updatedEnt = None
    if user:
        List_of_apprentices = data['List_of_apprentices']
        visitId=int(str(uuid.uuid4().int)[:5])
        for key in List_of_apprentices:
            Visit1 = Visit(
                user_id=user,
                apprentice_id=str(key['id'])[3:],
                note=data['event_details'],
                visit_in_army=bool(data['event_type']),
                visit_date=data['date'],
                allreadyread=False,
                id=visitId,
                title=data['event_type'],
                attachments=data['attachments'],
                description=data['description']

            )

            db.session.add(Visit1)

    try:
        db.session.commit()

    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': 'success'}), HTTPStatus.OK


@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')[3:]
    print(user)
    reportList = db.session.query(Visit).filter(Visit.user_id == user).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
        apprenticeList = db.session.query(Visit.apprentice_id).filter(Visit.id == noti.id ).all()
        my_dict.append(
            {"id": str(noti.id), "from":[str(i[0]) for i in [tuple(row) for row in apprenticeList]], "date":toISO(noti.visit_date),
             "days_from_now": daysFromNow , "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),"attachments": str(noti.attachments)})
    if not reportList :
        # acount not found
        return jsonify(["Wrong id or empty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_report_form():
    report_id = request.form.get('report_id')
    Visit1 = Visit.query.get(report_id)
    Visit1.allreadyread = 'true'
    db.session.commit()
    if report_id:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK
def toISO(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None