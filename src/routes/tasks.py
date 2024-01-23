import datetime
import json
import uuid

from flask import Blueprint, request, jsonify, Response
from http import HTTPStatus

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

tasks_form_blueprint = Blueprint('tasks_form', __name__, url_prefix='/tasks_form')


@tasks_form_blueprint.route("/getTasks", methods=['GET'])
def getTasks():
    # get tasksAndEvents
    userId = request.args.get("userId")[3:]
    res=getAll_notification_form()
    todo_dict = []
    todo_ids=[]
    try:
        for i in range(0,len(res[0].json)):
            ent=res[0].json[i]
            todo_ids.append(ent["id"])
            if ent["numOfLinesDisplay"]==2:#noti not created by user
                ent["status"] = "todo"
                ent["id"] = str(ent["id"])

                todo_dict.append(ent)

        ApprenticeList = db.session.query( Apprentice.id).filter(
            Apprentice.accompany_id == userId).all()
        all_ApprenticeList_Horim = [r[0] for r in ApprenticeList]

        visitHorim = db.session.query(Visit.apprentice_id).filter(Visit.user_id == userId,
                                                    Visit.title == "מפגש_הורים").all()
        for i in visitHorim:
            if i[0] in all_ApprenticeList_Horim:
                all_ApprenticeList_Horim.remove(i[0])
        for ent in all_ApprenticeList_Horim:
            Apprentice1 = db.session.query(Apprentice.name,Apprentice.last_name).filter(
                Apprentice.id == ent).first()
            todo_dict.append({"frequency": "never","description": "",'status':'todo',"allreadyread": False, 'apprenticeId': Apprentice1.name+" "+Apprentice1.last_name, 'date': '01.01.2023', 'daysfromnow': 373, 'event': 'מפגש הורים', 'id': str(uuid.uuid4().int)[:5],  'title': 'מפגש הורים'})
        too_old = datetime.datetime.today() - datetime.timedelta(days=60)
        done_visits = db.session.query(Visit.apprentice_id,Visit.title,Visit.visit_date,Visit.id).filter(Visit.user_id == userId,
                                                    Visit.id.not_in(todo_ids),Visit.visit_date>too_old).all()
        done_visits_dict=[{'status':'done',"apprentice_id": str(row[0]), "title": row[1]
             , "visit_date": row[2], "id": str(row[3])} for row in [tuple(row) for row in done_visits]] if done_visits is not None else []
        tasks_list = todo_dict+done_visits_dict

        return Response(json.dumps(tasks_list), mimetype='application/json'), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error while get' + str(e)}), HTTPStatus.BAD_REQUEST

# @tasks_form_blueprint.route("/getTasks", methods=['GET'])
# def getlists():
#     melaveId = request.args.get("userId")[3:]
#     print(melaveId)
#     too_old = datetime.datetime.today() - datetime.timedelta(days=45)
#     Oldvisitcalls = db.session.query(Visit.title,Visit.apprentice_id,Visit.visit_date).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
#                                                                  Visit.visit_date < too_old).all()
#     print(Oldvisitcalls)
#
#     too_old = datetime.datetime.today() - datetime.timedelta(days=60)
#     Oldvisitmeetings = db.session.query(Visit.title,Visit.apprentice_id,Visit.visit_date).filter(Visit.user_id==melaveId,Visit.title == "מפגש",
#                                                                  Visit.visit_date < too_old).all()
#     print(Oldvisitmeetings)
#
#     too_old = datetime.datetime.today() - datetime.timedelta(days=365)
#     visitHorim = db.session.query(Visit.title,Visit.apprentice_id,Visit.visit_date).filter(Visit.user_id==melaveId,Visit.title == "שיחה_הורים",
#                                                                  Visit.visit_date < too_old).all()
#     print(visitHorim)
#
#     return jsonify({
#         'Oldvisitmeetings': Oldvisitmeetings[0],
#         'Oldvisitcalls': Oldvisitcalls[0],
#         'visitHorim': visitHorim[0],
#
#
#     }), HTTPStatus.OK