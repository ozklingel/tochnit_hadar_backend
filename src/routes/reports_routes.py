import datetime
from datetime import datetime,date
from flask import Blueprint, request, jsonify
from http import HTTPStatus
import config
from .search_ent import filter_by_request
from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.cluster_model import Cluster
from ..models.institution_model import Institution
from ..models.user_model import user1
from app import  db
import uuid
from ..models.visit_model import Visit

reports_form_blueprint = Blueprint('reports_form', __name__, url_prefix='/reports_form')

@reports_form_blueprint.route('/add', methods=['post'])
def add_reports_form():
    data = request.json
    user = str(data['userId'])
    ent_group_name = ""
    attachments=[]
    try:
        ent_group_name = str(data['ent_group'])
    except:
        print("no ent_group ")
    try:
        attachments = data['attachments']
    except:
        print("no  attachments")
    if user:
        List_of_repored = data['List_of_repored']
        vis_id = int(str(uuid.uuid4().int)[:5])
        print(List_of_repored)
        for key in List_of_repored:
            Visit1 = Visit(
                user_id=user,
                ent_reported=str(key),
                visit_in_army=True if data['event_type']==config.basis_report else False,
                visit_date=data['date'],
                allreadyread=False,
                id=vis_id,
                title=data['event_type'],
                attachments=attachments,
                ent_group=ent_group_name,
                description=data['description']
            )

            db.session.add(Visit1)

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': "success"}), HTTPStatus.OK

@reports_form_blueprint.route('/getById', methods=['GET'])
def getById():
    try:
        report_id = request.args.get('report_id')
        user = request.args.get('userId')
        print(report_id)
        reportList = db.session.query(Visit.id,Visit.ent_reported, Visit.ent_group, Visit.note, Visit.visit_date,
                                      Visit.title, Visit.description, Visit.attachments, Visit.allreadyread).filter(
            Visit.id==report_id,Visit.user_id == user).all()
        print(reportList)
        if reportList:
            reportIDs=[str(r[0]) for r in reportList ]
            noti=reportList[0]
            return jsonify(
                {"id": str(noti.id), "reported_on": [str(noti.ent_reported)], "date": toISO(noti.visit_date),
                 "ent_group": "",
                 "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),
                 "attachments": noti.attachments}), HTTPStatus.OK
                # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
        return jsonify([])
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    try:
        user = request.args.get('userId')
        print(user)
        reportList = db.session.query(Visit.ent_reported,Visit.ent_group,Visit.note,Visit.visit_date,Visit.id,Visit.title,Visit.description,Visit.attachments,Visit.allreadyread).filter(Visit.user_id == user).all()
        group_report_dict=dict()
        my_dict = []
        groped_rep=[]
        for noti in reportList:
            daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
            if noti.ent_group !="":
                if noti.ent_group+str(noti.id) in  group_report_dict:
                    group_report_dict[noti.ent_group+str(noti.id)].append(str(noti.ent_reported))
                else:
                    print("created_for_id",noti.ent_reported)
                    group_report_dict[noti.ent_group+str(noti.id)] = [str(noti.ent_reported)]
                groped_rep.append(noti)
            else:
                my_dict.append(
                {"id": str(noti.id), "reported_on":[str(noti.ent_reported)], "date":toISO(noti.visit_date),        "ent_group": "",
                  "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),"attachments": noti.attachments})
        for noti in groped_rep:
            daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
            if group_report_dict[noti.ent_group+str(noti.id)]!=None:
                my_dict.append(
                    {"id": str(noti.id), "reported_on": group_report_dict[noti.ent_group+str(noti.id)], "date": toISO(noti.visit_date),
                     "ent_group": noti.ent_group,
                      "title": str(noti.title), "allreadyread": str(noti.allreadyread),
                     "description": str(noti.note), "attachments": noti.attachments})
                group_report_dict[noti.ent_group+str(noti.id)]=None

        else:
            # print(f' notifications: {my_dict}]')
            # TODO: get Noti form to DB
            return jsonify(my_dict), HTTPStatus.OK
            # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_report_form():
    data = request.json
    report_id = data['report_id']
    print(report_id)
    try:
        num_rows_updated = Visit.query.filter_by(id=report_id).update(dict(allreadyread=True))
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



@reports_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        reportId = data['reportId']
        res = db.session.query(Visit).filter(Visit.id == reportId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@reports_form_blueprint.route("/update", methods=['put'])
def update():
    try:
        # get tasksAndEvents
        reportId = request.args.get("reportId")
        data = request.json
        updatedEnt = Visit.query.get(reportId)
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



@reports_form_blueprint.route("/filter_report", methods=['GET'])
def filter_report():
    try:
        users,apprentice,ent_group_dict=filter_by_request(request)
        reports_user=db.session.query(Visit.id).filter(Visit.user_id.in_(users)).all()
        reports_apprentice=db.session.query(Visit.id).filter(Visit.ent_reported.in_(apprentice)).all()
        ent_group_concat=", ".join(ent_group_dict.values())
        print(ent_group_concat)
        #reports_ent_group=db.session.query(Visit.id).filter(Visit.ent_group==ent_group.id,ent_group.group_name==ent_group_concat).all()
        users_mess=[str(i[0]) for i in [tuple(row) for row in reports_user]]
        apprentice_mess=[str(i[0]) for i in [tuple(row) for row in reports_apprentice]]
        #ent_group_mess=[str(i[0]) for i in [tuple(row) for row in reports_ent_group]]
        result=set(users_mess+apprentice_mess)
        print(result)
        return jsonify( [str(row) for row in result]
            ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@reports_form_blueprint.route("/filter_to", methods=['GET'])
def filter_to():
    try:
        users,apprentice,ent_group_dict=filter_by_request(request)

        ent_group_concat=""
        if apprentice!=[] or users!=[]:
            ent_group_concat=", ".join(ent_group_dict.values())
        result = set(users + apprentice)

        return jsonify({"filtered":    [str(row) for row in result]

                          ,
                        "ent_group":ent_group_concat
                        }
            ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

