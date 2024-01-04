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

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')


@homepage_form_blueprint.route("/initMaster", methods=['GET'])
def homepageMaster():
    accessToken =request.headers.get('Authorization')
    print("accessToken:",accessToken)
    userId = request.args.get("userId")[3:]
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
    redvisitcalls=0
    orangevisitcalls=0
    greenvisitcalls=0
    forgotenApprenticCount=0
    forgotenApprenticeList=[]
    all_Apprentices = db.session.query(Apprentice.id).all()
    # update apprentices call
    visitcalls = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(Visit.apprentice_id).filter(Visit.title == "שיחה").all()
    ids=[r[0] for r in visitcalls]
    #handle no record
    for ent in all_Apprentices:
        if ent.id not in ids:
            redvisitcalls+=1
            forgotenApprenticeList.append(ent.id)
    #handle exist record
    for ent in visitcalls:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        print("call gap:", gap)
        if gap>100:
            forgotenApprenticeList.append(ent.apprentice_id)
        if gap >= 60:
            redvisitcalls+=1
        if 60> gap > 21:
            orangevisitcalls+=1
        if 21>gap:
            greenvisitcalls+=1
    # update apprentices meetings
    visitmeetings = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(Visit.apprentice_id).filter(Visit.title == "מפגש").all()
    redvisitmeetings=0
    orangevisitmeetings=0
    greenvisitmeetings=0
    #handle no record
    ids=[r[0] for r in visitmeetings]
    for ent in all_Apprentices:
        if ent.id not in ids:
            redvisitmeetings+=1
            if ent.id in forgotenApprenticeList:
                forgotenApprenticCount+=1
    #handle exist record
    for ent in visitmeetings:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        print("meeting gap:", gap)
        if gap>100:
            if ent.apprentice_id in forgotenApprenticeList:
                forgotenApprenticCount+=1
        if gap > 100:
            redvisitmeetings+=1
        if 100> gap > 90:
            orangevisitmeetings+=1
        if 90>gap:
            greenvisitmeetings+=1

    call_score=greenvisitcalls/len(all_Apprentices)*12
    meeting_score=greenvisitmeetings/len(all_Apprentices)*12
    group_meeting = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(Visit.apprentice_id).filter(Visit.title == "מפגש_קבוצתי").all()
    gap = (date.today() - group_meeting.visit_date).days if group_meeting is not None else 100
    group_meeting_score=0
    if gap>60:
        group_meeting_score+=12
    cenes_yearly = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(Visit.apprentice_id).filter(Visit.title == "כנס_שנתי").all()
    gap = (date.today() - cenes_yearly.visit_date).days if group_meeting is not None else 100
    cenes_yearly_score=0
    if gap<365:
        cenes_yearly_score+=6.6
    yeshiva_monthly = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date")).group_by(Visit.apprentice_id).filter(Visit.title == "ישיבת_מלוים").all()
    gap = (date.today() - yeshiva_monthly.visit_date).days if group_meeting is not None else 100
    yeshiva_monthly_score=0
    if gap<30:
        yeshiva_monthly_score+=6.6
    Horim_meeting = db.session.query(Visit.apprentice_id).filter(Visit.title == "מפגש_הורים").all()
    Horim_meeting_score=0
    if len(Horim_meeting)==len(all_Apprentices):
        Horim_meeting_score+=10

    return jsonify({
        'totalApprentices': len(all_Apprentices),
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

@homepage_form_blueprint.route("/get_closest_Events", methods=['GET'])
def homepage():
    accessToken =request.headers.get('Authorization')
    print("accessToken:",accessToken)
    userId = request.args.get("userId")[3:]
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
    return jsonify(tasksAndEvents[0] if tasksAndEvents is not None else None), HTTPStatus.OK

def getlists(userId):
    # get tasksAndEvents
    res=getAll_notification_form()
    if res is None:
        return None,None
    if str(type(res))!="<class 'tuple'>":
        return [],[]
    event_dict = []
    task_dict = []
    for i in range(len(res[0].json)):
        print("res1=" ,res[0].json[i])
        ent=res[0].json[i]
        if ent["numOfLinesDisplay"]==3:
            ent["date"]=toISO(ent["date"])
            event_dict.append(ent)
        else :
            task_dict.append(ent)

    return event_dict,task_dict

def toISO(d):
    if d:
        Date=d.split(".")
        print("Date:" ,d)
        return datetime(int(Date[2]),int(Date[0]), int(Date[1])).isoformat()
    else:
        return None


    #
    # visitfailors = db.session.query(Visit.apprentice_id,func.count(Visit.title)).filter(Visit.title == "נסיון_שכשל").group_by(Visit.apprentice_id).all()
    # print(visitfailors)
    # count_1t5 = 0
    # count_6t10 = 0
    # count_11t15 = 0
    # count_15 = 0
    # multiply=5
    # for ent in visitfailors:
    #     if ent[1] > 15*multiply:
    #         count_15 += 1
    #     elif 15*multiply >= ent[1] >= 11*multiply:
    #         count_11t15 += 1
    #     elif 10*multiply >= ent[1] >= 6*multiply:
    #         count_6t10 += 1
    #     elif 5*multiply >= ent[1] >= 1*multiply:
    #         count_1t5 += 1