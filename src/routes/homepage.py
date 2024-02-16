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
from src.routes.notification_form_routes import getAll_notification_form

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')





def melave_score(all_Apprentices):
    # compute score diagram
    counts = dict()
    score_melaveProfile = []
    all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_id == "0").all()
    for melave in all_melave:
        melaveId = melave[0]
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices)==0:
            counts[100] = counts.get(100, 0) + 1
            score_melaveProfile.append({"id":melave.id, "name":melave.name,"institution_id": melave.institution_id, "score":100})
            continue
        visitcalls = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "שיחה", Visit.user_id == melaveId,Visit.visit_date>config.call_madad_date).order_by(Visit.visit_date).all()
        call_score=compute_visit_score(all_melave_Apprentices,visitcalls,12,21)
        visitmeetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "מפגש", Visit.user_id == melaveId,Visit.visit_date>config.meet_madad_date).order_by(Visit.visit_date).all()
        personal_meet_score=compute_visit_score(all_melave_Apprentices,visitmeetings,12,90)
        group_meeting = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.ent_reported).filter(Visit.title == "מפגש_קבוצתי", Visit.user_id == melaveId).first()
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
        Horim_meeting = db.session.query(Visit.ent_reported).filter(Visit.title == "מפגש_הורים",
                                                                     Visit.user_id == melaveId).all()
        Horim_meeting_score = 0
        if len(Horim_meeting) == len(all_melave_Apprentices):
            Horim_meeting_score += 10
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.title == "מפגש",Visit.visit_in_army==True,
                                                                                            Visit.visit_date > too_old,
                                                                                            Visit.user_id == melaveId).group_by(
            Visit.visit_date).count()
        base_meeting_score = 0
        if base_meeting > 2:
            base_meeting_score += 10
        melave_score = base_meeting_score + Horim_meeting_score + professional_2monthly_score + yeshiva_monthly_score + \
                       cenes_yearly_score + \
                       group_meeting_score + personal_meet_score + call_score
        counts[melave_score] = counts.get(melave_score, 0) + 1
        score_melaveProfile.append(
            {"id": melave.id, "name": melave.name, "institution_id": melave.institution_id, "score": 100})

    k, v = [], []
    for key, value in counts.items():
        k.append(key)
        v.append(value)
    return (k,v),score_melaveProfile



def mosad_Coordinators_score():
    all_Mosad_coord = db.session.query(user1.id, user1.institution_id,user1.name).filter(user1.role_id == "1").all()
    mosad_Cooordinator_score_dict = dict()
    score_MosadCoordProfile=[]
    for mosad_coord in all_Mosad_coord:
        Mosad_coord_score=0
        mosad_coord_id = mosad_coord[0]
        institution_id = mosad_coord[1]
        all_Mosad_Melave = db.session.query(user1.id).filter(user1.role_id == "0",
                                                             user1.institution_id == institution_id).all()
        if len(all_Mosad_Melave) == 0:
            mosad_Cooordinator_score_dict[100] = mosad_Cooordinator_score_dict.get(100, 0) + 1
            score_MosadCoordProfile.append({"id":mosad_coord.id, "name":mosad_coord.name,"institution_id": mosad_coord.institution_id, "score":100})
            continue
        all_Mosad_Melaves_list = [r[0] for r in all_Mosad_Melave]
        #מצבר=30
        visit_matzbar_meetings = db.session.query(Visit.user_id, Visit.visit_date).filter(Visit.title == "מצבר").filter(
            Visit.user_id.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
        visit_matzbar_meetings_score=compute_visit_score(all_Mosad_Melave, visit_matzbar_meetings, 30, 90)
        Mosad_coord_score+=visit_matzbar_meetings_score
        #מפגש_מקצועי=10
        visit_mosad_professional_meetings = db.session.query(Visit.user_id, Visit.visit_date).filter(Visit.title == "מפגש_מקצועי").filter(
            Visit.user_id.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
        visit_mosad_professional_meetings_score=compute_visit_score(all_Mosad_Melave, visit_mosad_professional_meetings, 30, 90)
        Mosad_coord_score+=visit_mosad_professional_meetings_score

        #ישיבת_מלוים=15
        todays_Month = dates.HebrewDate.today().month
        if todays_Month==2 or todays_Month==6 or todays_Month==8:
            Mosad_coord_score += 10 #nisan ,Av and Tishrey dont compute
            Mosad_coord_score += 5 #precence of melavim
        else:
            too_old = datetime.today() - timedelta(days=31)
            visit_allMelavim_monthly_meetings = db.session.query(Visit.user_id,
                                                             func.max(Visit.visit_date).label("visit_date")).group_by(
                Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == mosad_coord_id,
                                      Visit.visit_date > too_old).all()
            if visit_allMelavim_monthly_meetings:
                Mosad_coord_score += 10
                Mosad_coord_score+=5*len(visit_allMelavim_monthly_meetings)/len(all_Mosad_Melave) if len(all_Mosad_Melave)!=0 else 0
        #עשייה_לבוגרים=5
        too_old = datetime.today() - timedelta(days=365)
        visit_did_for_apprentice = db.session.query(Visit.user_id,
                                                         ).filter(Visit.title == "עשייה_לבוגרים", Visit.user_id == mosad_coord_id,
                                  Visit.visit_date > too_old).all()
        if len(visit_did_for_apprentice)>=3:
            Mosad_coord_score += 5
        #הזנת_מחזור_חדש=10
        too_old = datetime.today() - timedelta(days=365)
        visit_Hazana_new_THsession = db.session.query(Visit.user_id,
                                                         func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "הזנת_מחזור_חדש", Visit.user_id == mosad_coord_id,
                                  Visit.visit_date > too_old).all()
        if len(visit_Hazana_new_THsession)>=1:
            Mosad_coord_score += 10
        mosad_Cooordinator_score_dict[Mosad_coord_score] = mosad_Cooordinator_score_dict.get(Mosad_coord_score, 0) + 1
        score_MosadCoordProfile.append(
            {"id": mosad_coord.id, "name": mosad_coord.name, "institution_id": mosad_coord.institution_id,
             "score": Mosad_coord_score})

    k, v = [], []
    for key, value in mosad_Cooordinator_score_dict.items():
        k.append(key)
        v.append(value)
    return (k,v),score_MosadCoordProfile

def compute_visit_score(all_children,visits,maxScore,expected_gap):
    all_children_ids = [r[0] for r in all_children]

    from collections import defaultdict
    visitcalls_melave_list = defaultdict(list)
    # key is apprenticeId and value is list of  gaps visits date
    for index in range(1, len(visits)):
        gap = (visits[index][1] - visits[index - 1][1]).days if visits[index] is not None else 21
        visitcalls_melave_list[visits[index][0]].append(gap)
    visitcalls_melave_avg = 0
    for k, v in visitcalls_melave_list.items():
        if k in all_children_ids:
            all_children_ids.remove(k)
        visitcalls_melave_avg += (sum(v) / len(v))
    #t least one apprentice with no calls
    if len(all_children_ids) != 0:
        visitcalls_melave_avg = 0
    else:
        visitcalls_melave_avg = visitcalls_melave_avg / len(visitcalls_melave_list) if len(
            visitcalls_melave_list) != 0 else 0
    call_panish = visitcalls_melave_avg - expected_gap


    if call_panish > 0:
        call_score = maxScore - call_panish / 2
    else:
        call_score = maxScore
    if call_score<0:
        call_score=0
    return call_score
def Eshcol_corrdintors_score():
    all_Eshcol_coord = db.session.query(user1.id, user1.cluster_id,user1.name,user1.institution_id).filter(user1.role_id == "2").all()
    eshcol_Cooordinator_score = dict()
    score_EshcolCoordProfile=[]
    for Eshcol_coord in all_Eshcol_coord:
        Eshcol_coord_id = Eshcol_coord[0]
        cluster_id = Eshcol_coord[1]
        all_Mosad_Cordinators = db.session.query(user1.id).filter(user1.role_id == "1",
                                                                  user1.cluster_id == cluster_id).all()
        if len(all_Mosad_Cordinators) == 0:
            eshcol_Cooordinator_score[100] = eshcol_Cooordinator_score.get(100, 0) + 1
            score_EshcolCoordProfile.append({"id":Eshcol_coord.id, "name":Eshcol_coord.name,"institution_id": Eshcol_coord.institution_id, "score":100})

            continue
        all_Mosad_Cordinators_list = [r[0] for r in all_Mosad_Cordinators]

        visit_Mosad_monthly_meetings_personal = db.session.query(Visit.user_id, Visit.visit_date).filter(Visit.title == "ישיבה_חודשית_אשכול_מוסד").filter(
            Visit.user_id.in_(list(all_Mosad_Cordinators_list))).order_by(Visit.visit_date).all()
        visit_Mosad_monthly_meetings_personal_score=compute_visit_score(all_Mosad_Cordinators, visit_Mosad_monthly_meetings_personal, 60, 30)
        Eshcol_coord_score=visit_Mosad_monthly_meetings_personal_score
        too_old = datetime.today() - timedelta(days=31)
        visit_Tohnit_monthly_meetings = db.session.query(Visit.user_id,
                                                         func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבה_חודשית_כלל_תוכנית", Visit.user_id == Eshcol_coord_id,
                                  Visit.visit_date > too_old).all()
        if visit_Tohnit_monthly_meetings:
            Eshcol_coord_score += 40
        eshcol_Cooordinator_score[Eshcol_coord_score] = eshcol_Cooordinator_score.get(Eshcol_coord_score, 0) + 1
        score_EshcolCoordProfile.append(
            {"id": Eshcol_coord.id, "name": Eshcol_coord.name, "institution_id": Eshcol_coord.institution_id,
             "score": Eshcol_coord_score})

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

    counts_melave_score,score_melaveProfile_list=melave_score(all_Apprentices)
    mosad_Cooordinator_score,score_MosadCoordProfile_list=mosad_Coordinators_score()
    eshcol_Cooordinator_score,score_EshcolCoordProfile_list=Eshcol_corrdintors_score()

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
            ent["date"]=ent["date"]
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