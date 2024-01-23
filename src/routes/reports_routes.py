import datetime
import json
from datetime import datetime,date

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from ..models.ent_group import ent_group

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
    ent_group1=None
    if user:
        List_of_apprentices = data['List_of_apprentices']
        visitId=int(str(uuid.uuid4().int)[:5])
        if len(List_of_apprentices)>1:
            ent_group1=ent_group(
                id=visitId,
                group_name="בהד1",
                table_name="Apprentice",
                ent_id_list=[str(key['id'])[3:] for key in List_of_apprentices],
            )
            db.session.add(ent_group1)

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

    except Exception as e:
        return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': 'success'}), HTTPStatus.OK


@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')[3:]
    print(user)
    reportList = db.session.query(Visit).filter(Visit.user_id == user).all()
    ent_group_list = db.session.query(ent_group.id).filter(ent_group.user_id == user).all()
    ent_group_list_ids= [r[o] for r in ent_group_list]
    my_dict = []
    for noti in reportList:
        daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
        if noti.id in ent_group_list_ids:
            ent_group_item = db.session.query(ent_group.group_name).filter(ent_group.id == noti.id).first()
            my_dict.append(
                {"id": str(noti.id), "from": ent_group_item.group_name,
                 "date": toISO(noti.visit_date),
                 "days_from_now": daysFromNow, "title": str(noti.title), "allreadyread": str(noti.allreadyread),
                 "description": str(noti.note), "attachments": noti.attachments})

        else:
            my_dict.append(
            {"id": str(noti.id), "from":str(noti.apprentice_id), "date":toISO(noti.visit_date),
             "days_from_now": daysFromNow , "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),"attachments": noti.attachments})
    if not reportList :
        # acount not found
        return jsonify([])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_report_form():
    data = request.json
    report_id = data['report_id']
    print(report_id)
    try:
        noti = Visit.query.get(report_id)
        noti.allreadyread = True
        db.session.commit()
        if report_id:
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