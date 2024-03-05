import datetime
import json
import uuid

from flask import Blueprint, request, jsonify, Response
from http import HTTPStatus


from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

tasks_form_blueprint = Blueprint('tasks_form', __name__, url_prefix='/tasks_form')


@tasks_form_blueprint.route("/getTasks", methods=['GET'])
def getTasks():
    # get tasksAndEvents
    userId = request.args.get("userId")
    res=getAll_notification_form()
    todo_dict = []
    todo_ids=[]
    try:
        for i in range(0,len(res[0].json)):
            ent=res[0].json[i]
            todo_ids.append(ent["id"])
            if ent["numOfLinesDisplay"]==2:#noti not created by user
                del ent["numOfLinesDisplay"]

                #print(ent)
                ent["status"] = "todo"
                ent["id"] = str(ent["id"])
                ent["apprenticeId"] = [ent["apprenticeId"]]

                if ent["event"]== "מפגש_קבוצתי" :
                    ent["apprenticeId"]=[]

                todo_dict.append(ent)

        ApprenticeList = db.session.query( Apprentice.id).filter(
            Apprentice.accompany_id == userId).all()
        all_ApprenticeList_Horim = [r[0] for r in ApprenticeList]

        visitHorim = db.session.query(Visit.ent_reported).filter(Visit.user_id == userId,
                                                    Visit.title == "מפגש_הורים").all()
        for i in visitHorim:
            if i[0] in all_ApprenticeList_Horim:
                all_ApprenticeList_Horim.remove(i[0])
        for ent in all_ApprenticeList_Horim:
            #Apprentice1 = db.session.query(Apprentice.name,Apprentice.last_name).filter(Apprentice.id == ent).first()
            todo_dict.append({"frequency": "never","description": "",'status':'todo',"allreadyread": False, 'apprenticeId': [str(ent)], 'date': '2023-01-01T00:00:00', 'daysfromnow': 373, 'event': 'מפגש_הורים', 'id': str(uuid.uuid4().int)[:5],  'title': 'מפגש הורים'})
        too_old = datetime.datetime.today() - datetime.timedelta(days=60)
        done_visits = db.session.query(Visit.ent_reported,Visit.title,Visit.visit_date,Visit.id,Visit.description).filter(Visit.user_id == userId,
                                                    Visit.id.not_in(todo_ids),Visit.visit_date>too_old).distinct(Visit.id).all()
        done_visits_dict=[{   "frequency": "never",        "allreadyread": False, "event": str(row[1]),
        "description": str(row[4]),'status':'done',"apprenticeId": [str(row[0])], "title": str(row[1])
             ,"daysfromnow": 373, "date": str(row[2]), "id": str(row[3])} for row in [tuple(row) for row in done_visits]] if done_visits is not None else []

        tasks_list = todo_dict+done_visits_dict

        return Response(json.dumps(tasks_list), mimetype='application/json'), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error while get' + str(e)}), HTTPStatus.OK
@tasks_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    try:
        taskId = request.args.get("taskId")
        data = request.json


        updatedEnt = notifications.query.get(taskId)
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

@tasks_form_blueprint.route('/add', methods=['POST'])
def add_task():
    try:
        json_object = request.json
        user = json_object["userId"]
        apprenticeid = json_object["apprenticeid"] if json_object["apprenticeid"] else ""
        event = json_object["event"]
        date = json_object["date"]
        details = json_object["details"]
        frequency = json_object["frequency"] if  json_object["frequency"] is not None else "never"
        notification1 = notifications(
                        userid=user,
                        apprenticeid = apprenticeid,
                        event=event,
                        date=date,
                        allreadyread=False,
                        numoflinesdisplay=2,
                        details=details,
                        frequency=frequency,

            id=int(str(uuid.uuid4().int)[:5]),

        )

        db.session.add(notification1)
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.OK
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
@tasks_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        taskId = data['taskId']
        res = db.session.query(notifications).filter(notifications.id == taskId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
