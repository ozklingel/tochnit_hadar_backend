import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')

@homepage_form_blueprint.route("/init", methods=['GET'])
def homepage():
    accessToken =request.headers.get('Authorization')
    print("accessToken:",accessToken)
    userId = request.args.get("userId")[4:]
    print("Userid:", str(userId))
    redisaccessToken = red.hget(userId, "accessToken").decode("utf-8")
    print("redisaccessToken:",redisaccessToken)


    if not redisaccessToken==accessToken:
        return jsonify({'result': f"wrong access token r {userId}"}), HTTPStatus.OK

    record = user1.query.filter_by(id=userId).first()
    red.hset(userId, "id", record.id)
    red.hset(userId, "name", record.name)
    red.hset(userId, "lastname", record.last_name)
    red.hset(userId, "email", record.email)
    red.hset(userId, "role", record.role_id)


    return jsonify({
                    'user_lastname':record.last_name,
                    'user_name':record.name,
                    "tasks":getMytasks(record.id),
                    "closeEvents":getcloseEvents(record.id)}), HTTPStatus.OK

def getcloseEvents(userId):
    too_old = datetime.datetime.today() - datetime.timedelta(days=3)
    reportList = db.session.query(notifications.apprenticeid,notifications.event).\
        filter(notifications.userid == userId,notifications.date>= too_old).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        my_dict.append(
            {"apprenticeid": str(noti.apprenticeid),
             "event": str(noti.event),
             "daysfromnow": str(datetime.date.today() - noti.date)})

    if reportList is None:
        # acount not found
        return "Wrong id"
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return my_dict
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

def getMytasks(userId):
    reportList = db.session.query(Visit.apprentice_id, Visit.title,Visit.visit_date). \
        filter(Visit.user_id == userId).limit(3).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        daysfromnow="0"
        if noti.visit_date:
            daysfromnow=str(datetime.date.today() - noti.visit_date)
        my_dict.append(
            {"apprenticeid": str(noti.apprentice_id),
             "title": str(noti.title),
             "daysfromnow": daysfromnow})

    if reportList is None:
        # acount not found
        return "Wrong id"
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return my_dict