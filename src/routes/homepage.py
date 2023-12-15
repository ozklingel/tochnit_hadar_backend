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

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')


@homepage_form_blueprint.route("/initMaster", methods=['GET'])
def homepageMaster():
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
    # update apprentices call
    visitcalls = db.session.query(Visit).filter(Visit.title == "שיחה").all()
    redvisitcalls=0
    orangevisitcalls=0
    greenvisitcalls=0
    forgotenApprenticCount=0
    forgotenApprenticeList=[]

    for ent in visitcalls:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        print("call gap:", gap)
        if gap>100:
            forgotenApprenticeList.append(ent.apprentice_id)
        if 60> gap > 30:
            orangevisitcalls+=1
        if gap >= 60:
            redvisitcalls+=1
        if 30>gap:
            greenvisitcalls+=1
    # update apprentices meetings
    visitmeetings = db.session.query(Visit).filter(Visit.title == "מפגש").all()
    redvisitmeetings=0
    orangevisitmeetings=0
    greenvisitmeetings=0
    for ent in visitmeetings:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        print("meeting gap:", gap)
        if gap>100:
            if ent.apprentice_id in forgotenApprenticeList:
                forgotenApprenticCount+=1
        if 60> gap > 30:
            orangevisitmeetings+=1
        if gap > 60:
            redvisitmeetings+=1
        if 30>gap:
            greenvisitmeetings+=1

    visitfailors = db.session.query(Visit.apprentice_id,func.count(Visit.title)).filter(Visit.title == "נסיון_שכשל").group_by(Visit.apprentice_id).all()
    print(visitfailors)
    count_1t5 = 0
    count_6t10 = 0
    count_11t15 = 0
    count_15 = 0
    multiply=5
    for ent in visitfailors:
        if ent[1] > 15*multiply:
            count_15 += 1
        elif 15*multiply >= ent[1] >= 11*multiply:
            count_11t15 += 1
        elif 10*multiply >= ent[1] >= 6*multiply:
            count_6t10 += 1
        elif 5*multiply >= ent[1] >= 1*multiply:
            count_1t5 += 1
    return jsonify({
        'count_1t5': count_1t5,
        'count_6t10': count_6t10,
        'count_11t15': count_11t15,
        'count_15': count_15,
        'forgotenApprenticCount': forgotenApprenticCount,
        'orangevisitmeetings': orangevisitmeetings,
        'redvisitmeetings': redvisitmeetings,
        'greenvisitmeetings': greenvisitmeetings,
        'greenvisitcalls': greenvisitcalls,
        'orangevisitcalls': orangevisitcalls,
        'redvisitcalls': redvisitcalls,
        'user_lastname':record.last_name,
         'user_name':record.name,
                   }), HTTPStatus.OK

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
                    "tasks":tasksAndEvents[1] if tasksAndEvents is not None else None ,
                    "closeEvents":tasksAndEvents[0] if tasksAndEvents is not None else None}), HTTPStatus.OK

def getlists(userId):
    # get tasksAndEvents
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