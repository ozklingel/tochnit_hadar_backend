import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date

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
    meet_dict = []
    call_dict = []
    Horim_dict = []
    try:
        for i in range(0,len(res[0].json)):
            ent=res[0].json[i]
            print(ent)
            if ent["numOfLinesDisplay"]==2:
                if ent["title"]=="שיחה":
                    call_dict.append(ent)
                if ent["title"]=="מפגש" or ent["title"]=="מפגש_קבוצתי" :
                    meet_dict.append(ent)
                if ent["title"]=="מפגש_הורים":
                    Horim_dict.append(ent)
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
            Horim_dict.append({'allreadyread': False, 'apprenticeId': Apprentice1.name+" "+Apprentice1.last_name, 'date': '01.01.2023', 'daysfromnow': 373, 'event': 'מפגש הורים', 'id': 94275, 'numOfLinesDisplay': 2, 'title': 'מפגש הורים'})

        return jsonify({
            'call_dict':call_dict,
            'Horim_dict': Horim_dict,
            "meet_dict": meet_dict,
            }), HTTPStatus.OK
    except:
        return jsonify({'result': 'no Tasks or wrong id'}), HTTPStatus.OK

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