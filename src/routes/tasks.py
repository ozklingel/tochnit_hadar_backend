import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date

from sqlalchemy import func

from app import db, red
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
    meet_dict = []
    call_dict = []
    Horim_dict = []

    for i in range(len(res[0].json)):
        ent=res[0].json[i]
        if ent["numOfLinesDisplay"]==2:
            if ent["title"]=="שיחה":
                call_dict.append(ent)
            if ent["title"]=="מפגש":
                meet_dict.append(ent)
            if ent["title"]=="מפגש_הורים":
                Horim_dict.append(ent)
            return jsonify({
                'call_dict':call_dict,
                'Horim_dict': Horim_dict,
                "meet_dict": meet_dict,
                }), HTTPStatus.OK

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