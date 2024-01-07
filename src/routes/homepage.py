import datetime
from pyluach import dates, hebrewcal, parshios
#sudo pip install pyluach
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date,timedelta

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')


def melave_score(all_Apprentices):
    # compute score diagram
    counts = dict()
    all_melave = db.session.query(user1.id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        melave_Apprentices_count = db.session.query(func.count(Apprentice.id)).filter(
            Apprentice.accompany_id == melaveId).group_by(Apprentice.id).first()
        if melave_Apprentices_count is None:
            continue
        print("melaveId", melaveId)
        good_call_melave_count = 0
        visitcalls = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date")).filter(
            Visit.title == "שיחה", Visit.user_id == melaveId).group_by(
            Visit.apprentice_id).all()
        for ent in visitcalls:
            gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 22
            print("call gap:", gap)
            if gap <= 21:
                good_call_melave_count += 1
        call_score = good_call_melave_count / melave_Apprentices_count[0] * 12
        good_meeting_melave_count = 0
        visitMeeting = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date")).filter(
            Visit.title == "מפגש", Visit.user_id == melaveId).group_by(
            Visit.apprentice_id).all()
        for ent in visitMeeting:
            gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
            print("call gap:", gap)
            if gap <= 60:
                good_meeting_melave_count += 1
        meeting_score = good_meeting_melave_count / melave_Apprentices_count[0] * 12
        group_meeting = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.apprentice_id).filter(Visit.title == "מפגש_קבוצתי", Visit.user_id == melaveId).first()
        gap = (date.today() - group_meeting.visit_date).days if group_meeting is not None else 100
        group_meeting_score = 0
        if gap <= 60:
            group_meeting_score += 12
        cenes_yearly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "כנס_שנתי", Visit.user_id == melaveId).all()
        gap = (date.today() - cenes_yearly.visit_date).days if group_meeting is not None else 400
        cenes_yearly_score = 0
        if gap < 365:
            cenes_yearly_score += 6.6
        yeshiva_monthly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == melaveId).first()
        gap = (date.today() - yeshiva_monthly.visit_date).days if group_meeting is not None else 100
        yeshiva_monthly_score = 0
        if gap < 30:
            yeshiva_monthly_score += 6.6
        professional_2monthly = db.session.query(Visit.user_id,
                                                 func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "מפגש_מקצועי", Visit.user_id == melaveId).first()
        gap = (date.today() - professional_2monthly.visit_date).days if group_meeting is not None else 100
        professional_2monthly_score = 0
        if gap < 60:
            professional_2monthly_score += 6.6
        Horim_meeting = db.session.query(Visit.apprentice_id).filter(Visit.title == "מפגש_הורים",
                                                                     Visit.user_id == melaveId).all()
        Horim_meeting_score = 0
        if len(Horim_meeting) == len(all_Apprentices):
            Horim_meeting_score += 10
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.title == "ביקור_בסיס",
                                                                                            Visit.visit_date > too_old,
                                                                                            Visit.user_id == melaveId).group_by(
            Visit.visit_date).count()
        base_meeting_score = 0
        if base_meeting > 2:
            base_meeting_score += 10
        melave_score = base_meeting_score + Horim_meeting_score + professional_2monthly_score + yeshiva_monthly_score + \
                       cenes_yearly_score + \
                       group_meeting_score + meeting_score + call_score
        counts[melave_score] = counts.get(melave_score, 0) + 1
    return counts


def Eshcol_corrdintors_score():
    all_Eshcol_coord = db.session.query(user1.id, user1.cluster_id).filter(user1.role_id == "2").all()
    eshcol_Cooordinator_score = dict()
    for Eshcol_coord in all_Eshcol_coord:
        Eshcol_coord_id = Eshcol_coord[0]
        cluster_id = Eshcol_coord[1]
        all_Mosad_Cordinators = db.session.query(user1.id).filter(user1.role_id == "1",
                                                                  user1.cluster_id == cluster_id).all()
        if len(all_Mosad_Cordinators) == 0:
            continue
        all_Mosad_Cordinators_list = [r[0] for r in all_Mosad_Cordinators]
        visit_Mosad_monthly_meetings_personal = db.session.query(Visit.user_id, func.max(Visit.visit_date).label(
            "visit_date")).group_by(Visit.user_id).filter(Visit.title == "ישיבה_חודשית_אשכול_מוסד").filter(
            Visit.user_id.in_(list(all_Mosad_Cordinators_list))).all()
        success_visit_Mosad_monthly_meetings_personal = 0
        for ent in visit_Mosad_monthly_meetings_personal:
            all_Mosad_Cordinators_list.remove(ent.user_id)
            gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
            if gap < 31:
                success_visit_Mosad_monthly_meetings_personal += 1
        Eshcol_coord_score = success_visit_Mosad_monthly_meetings_personal / len(all_Mosad_Cordinators) * 60
        too_old = datetime.today() - timedelta(days=31)
        visit_Tohnit_monthly_meetings = db.session.query(Visit.user_id,
                                                         func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבה_חודשית_כלל_תוכנית", Visit.user_id == Eshcol_coord_id,
                                  Visit.visit_date > too_old).all()
        if visit_Tohnit_monthly_meetings:
            Eshcol_coord_score += 40
        eshcol_Cooordinator_score[Eshcol_coord_score] = eshcol_Cooordinator_score.get(Eshcol_coord_score, 0) + 1
    return eshcol_Cooordinator_score

def mosad_Cooordinator_score():
    all_Mosad_coord = db.session.query(user1.id, user1.institution_id).filter(user1.role_id == "1").all()
    mosad_Cooordinator_score_dict = dict()
    for mosad_coord in all_Mosad_coord:
        Mosad_coord_score=0
        mosad_coord = 0
        mosad_coord_id = mosad_coord[0]
        institution_id = mosad_coord[1]
        all_Mosad_Melave = db.session.query(user1.id).filter(user1.role_id == "0",
                                                             user1.institution_id == institution_id).all()
        if len(all_Mosad_Melave) == 0:
            continue
        all_Mosad_Melaves_list = [r[0] for r in all_Mosad_Melave]
        visit_racaz_mosad_monthly_meetings = db.session.query(Visit.user_id, func.max(Visit.visit_date).label(
            "visit_date")).group_by(Visit.user_id).filter(Visit.title == "ישיבה_רכז_מלוה").filter(
            Visit.user_id.in_(list(all_Mosad_Melaves_list))).all()
        visit_Mosad_melave_meetings_personal = 0
        for ent in visit_racaz_mosad_monthly_meetings:
            all_Mosad_Melaves_list.remove(ent.user_id)
            gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
            if gap < 90:
                visit_Mosad_melave_meetings_personal += 1
        Mosad_coord_score+=visit_Mosad_melave_meetings_personal/len(all_Mosad_Melave)*30
        # visit_racaz_mosad_monthly_meetings = db.session.query(Visit.user_id, func.max(Visit.visit_date).label(
        #     "visit_date")).group_by(Visit.user_id).filter(Visit.title == "מפגש_מקצועי").filter(
        #     Visit.user_id.in_(list(all_Mosad_Melaves_list))).all()
        # visit_Mosad_melave_meetings_personal = 0
        # for ent in visit_racaz_mosad_monthly_meetings:
        #     all_Mosad_Melaves_list.remove(ent.user_id)
        #     gap = (date.today() - ent.visit_date).days if ent.visit_date is not None else 0
        #     if gap < 90:
        #         visit_Mosad_melave_meetings_personal += 1
        # Mosad_coord_score+=visit_Mosad_melave_meetings_personal/len(all_Mosad_Melave)*30
        todays_Month = dates.HebrewDate.today().month
        if todays_Month==2 or todays_Month==6 or todays_Month==8:
            continue #nisan ,Av and Tishrey dont compute
        too_old = datetime.today() - timedelta(days=31)
        visit_allMelavim_monthly_meetings = db.session.query(Visit.user_id,
                                                         func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == mosad_coord_id,
                                  Visit.visit_date > too_old).all()
        if visit_allMelavim_monthly_meetings:
            Mosad_coord_score += 10
        too_old = datetime.today() - timedelta(days=365)
        visit_did_for_apprentice = db.session.query(Visit.user_id,
                                                         ).filter(Visit.title == "עשייה_לבוגרים", Visit.user_id == mosad_coord_id,
                                  Visit.visit_date > too_old).all()
        if len(visit_did_for_apprentice)>=3:
            Mosad_coord_score += 5
        too_old = datetime.today() - timedelta(days=365)
        visit_Hazana_new_THsession = db.session.query(Visit.user_id,
                                                         func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "הזנת_מחזור_חדש", Visit.user_id == mosad_coord_id,
                                  Visit.visit_date > too_old).all()
        if len(visit_Hazana_new_THsession)>=1:
            Mosad_coord_score += 5
    return "hi"



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
        if gap>100:
            if ent.apprentice_id in forgotenApprenticeList:
                forgotenApprenticCount+=1
        if gap > 100:
            redvisitmeetings+=1
        if 100> gap > 90:
            orangevisitmeetings+=1
        if 90>gap:
            greenvisitmeetings+=1
    counts_melave_score=melave_score(all_Apprentices)
    eshcol_Cooordinator_score=Eshcol_corrdintors_score()
    #mosad_Cooordinator_score=mosad_Cooordinator_score()

    return jsonify({
        'eshcol_Cooordinator_score': eshcol_Cooordinator_score,
        'Mosad_Cooordinator_score': counts_melave_score,
        'melave_score': counts_melave_score ,
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