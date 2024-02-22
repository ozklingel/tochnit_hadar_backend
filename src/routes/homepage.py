import datetime
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

import config
from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.madadim import melave_score, mosad_Coordinators_score, eshcol_Coordinators_score
from src.routes.notification_form_routes import getAll_notification_form

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')





def get_melave_score(all_Apprentices):
    # compute score diagram
    counts = dict()
    score_melaveProfile = []
    all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        melave_score1, call_gap_avg, meet_gap_avg = melave_score(melaveId)
        score_melaveProfile.append({"melave_score1":melave_score1,"melaveId":melaveId})
        counts[melave_score1] = counts.get(melave_score1, 0) + 1

    k, v = [], []
    for key, value in counts.items():
        k.append(key)
        v.append(value)
    return (k,v),score_melaveProfile



def get_mosad_Coordinators_score():
    all_Mosad_coord = db.session.query(user1.id, user1.institution_id,user1.name).filter(user1.role_id == "1").all()
    mosad_Cooordinator_score_dict = dict()
    score_MosadCoordProfile=[]
    for mosad_coord in all_Mosad_coord:
        Mosad_coord_score=0
        mosadCoordinator = mosad_coord[0]
        mosad_Coordinators_score1, visitprofessionalMeet_melave_avg, avg_matzbarMeeting_gap, total_avg_call, total_avg_meet = mosad_Coordinators_score(
            mosadCoordinator)
        mosad_Cooordinator_score_dict[mosad_Coordinators_score1] = mosad_Cooordinator_score_dict.get(mosad_Coordinators_score1, 0) + 1
        score_MosadCoordProfile.append({"mosadCoordinator":mosadCoordinator,"mosad_Coordinators_score1":mosad_Coordinators_score1})
    k, v = [], []
    for key, value in mosad_Cooordinator_score_dict.items():
        k.append(key)
        v.append(value)
    return (k,v),score_MosadCoordProfile


def get_Eshcol_corrdintors_score():
    all_Eshcol_coord = db.session.query(user1.id, user1.cluster_id,user1.name,user1.institution_id).filter(user1.role_id == "2").all()
    eshcol_Cooordinator_score = dict()
    score_EshcolCoordProfile=[]
    for Eshcol_coord in all_Eshcol_coord:
        Eshcol_coord_id = Eshcol_coord[0]
        eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = eshcol_Coordinators_score(Eshcol_coord_id)
        eshcol_Cooordinator_score[eshcolCoordinator_score1] = eshcol_Cooordinator_score.get(eshcolCoordinator_score1, 0) + 1
        score_EshcolCoordProfile.append({"eshcol_Cooordinator_score":eshcol_Cooordinator_score,"Eshcol_coord_id":Eshcol_coord_id})
    k, v = [], []
    for key, value in eshcol_Cooordinator_score.items():
        k.append(key)
        v.append(value)
    return (k, v),score_EshcolCoordProfile

def red_green_orange_status(all_Apprentices):
    redvisitcalls = 0
    orangevisitcalls = 0
    greenvisitcalls = 0
    forgotenApprenticCount = 0
    forgotenApprenticeList = []
    # update apprentices call
    visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.ent_reported).filter(Visit.title == "שיחה").all()
    ids = [r[0] for r in visitcalls]
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids:
            redvisitcalls += 1
            forgotenApprenticeList.append(ent.id)
    # handle exist record
    for ent in visitcalls:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        if gap > 100:
            forgotenApprenticeList.append(ent.ent_reported)
        if gap >= 60:
            redvisitcalls += 1
        if 60 > gap > 21:
            orangevisitcalls += 1
        if 21 > gap:
            greenvisitcalls += 1
    # update apprentices meetings
    visitmeetings = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.ent_reported).filter(Visit.title == "מפגש").all()
    redvisitmeetings = 0
    orangevisitmeetings = 0
    greenvisitmeetings = 0
    # handle no record
    ids = [r[0] for r in visitmeetings]
    for ent in all_Apprentices:
        if ent.id not in ids:
            redvisitmeetings += 1
            if ent.id in forgotenApprenticeList:
                forgotenApprenticCount += 1
    # handle exist record
    for ent in visitmeetings:
        gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        if gap > 100:
            if ent.ent_reported in forgotenApprenticeList:
                forgotenApprenticCount += 1
        if gap > 100:
            redvisitmeetings += 1
        if 100 > gap > 90:
            orangevisitmeetings += 1
        if 90 > gap:
            greenvisitmeetings += 1
    return greenvisitmeetings,orangevisitmeetings,redvisitmeetings,greenvisitcalls,orangevisitcalls,redvisitcalls,forgotenApprenticCount

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
    all_Apprentices = db.session.query(Apprentice.id).all()

    counts_melave_score,score_melaveProfile_list=get_melave_score(all_Apprentices)
    mosad_Cooordinator_score,score_MosadCoordProfile_list=get_mosad_Coordinators_score()
    eshcol_Cooordinator_score,score_EshcolCoordProfile_list=get_Eshcol_corrdintors_score()

    greenvisitmeetings,orangevisitmeetings,redvisitmeetings,greenvisitcalls,orangevisitcalls,redvisitcalls,forgotenApprenticCount=red_green_orange_status(all_Apprentices)

    return jsonify({
        'score_melaveProfile_list': score_melaveProfile_list,
        'score_Mosad_Eshcol_CoordProfile_list': score_MosadCoordProfile_list+score_EshcolCoordProfile_list,

        'eshcol_Cooordinator_score': eshcol_Cooordinator_score,
        'Mosad_Cooordinator_score': mosad_Cooordinator_score,
        'melave_score': counts_melave_score ,
        'totalApprentices': len(all_Apprentices),
        'forgotenApprenticCount': forgotenApprenticCount,
        'orangevisitmeetings': orangevisitmeetings,
        'redvisitmeetings': redvisitmeetings,
        'greenvisitmeetings': greenvisitmeetings,
        'greenvisitcalls': greenvisitcalls,
        'orangevisitcalls': orangevisitcalls,
        'redvisitcalls': redvisitcalls,
       # 'user_lastname':record.last_name,
        # 'user_name':record.name,
                   }), HTTPStatus.OK

@homepage_form_blueprint.route("/get_closest_Events", methods=['GET'])
def get_closest_Events():
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
    return jsonify( {"events": tasksAndEvents[0] if tasksAndEvents is not None else []}), HTTPStatus.OK

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
       # print("res1=" ,res[0].json[i])
        ent=res[0].json[i]
        if ent["numOfLinesDisplay"]==3:
            event_dict.append(ent)
        else :
            task_dict.append(ent)

    return event_dict,task_dict

def toISO(d):
    if d:
        Date=d.split(".")
        print(d)
        return datetime(int(Date[2]),int(Date[0]), int(Date[1])).isoformat()
    else:
        return None


    #
    # visitfailors = db.session.query(Visit.ent_reported,func.count(Visit.title)).filter(Visit.title == "נסיון_שכשל").group_by(Visit.ent_reported).all()
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