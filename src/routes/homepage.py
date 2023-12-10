import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')

@homepage_form_blueprint.route("/init", methods=['GET'])
def homepage():
    accessToken =request.headers.get('Authorization')
    print("accessToken:",accessToken)
    userId = request.args.get("userId")[4:]
    print("Userid:", str(userId))
    '''
    redisaccessToken = red.hget(userId, "accessToken").decode("utf-8")
    print("redisaccessToken:",redisaccessToken)
    if not redisaccessToken==accessToken:
        return jsonify({'result': f"wrong access token r {userId}"}), HTTPStatus.OK
        '''
    record = user1.query.filter_by(id=userId).first()
    '''
    red.hset(userId, "id", record.id)
    red.hset(userId, "name", record.name)
    red.hset(userId, "lastname", record.last_name)
    red.hset(userId, "email", record.email)
    red.hset(userId, "role", record.role_id)
'''
    tasksAndEvents=getlists(record.id)
    print(tasksAndEvents)
    return jsonify({
                    'user_lastname':record.last_name,
                    'user_name':record.name,
                    "tasks":tasksAndEvents[1],
                    "closeEvents":tasksAndEvents[0]}), HTTPStatus.OK

def getlists(userId):
    res=getAll_notification_form()
    event_dict = []
    task_dict = []

    for i in range(len(res[0].json)):
        print(res[0].json[i]["numOfLinesDisplay"])
        if res[0].json[i]["numOfLinesDisplay"]==3:
            event_dict.append(res[0].json[i])
        else :
            task_dict.append(res[0].json[i])

            return event_dict,task_dict