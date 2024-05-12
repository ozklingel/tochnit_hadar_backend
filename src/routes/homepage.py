import datetime
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date
from sqlalchemy import func, or_
import config
from src.services import db, red
from src.models.apprentice_model import Apprentice
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.madadim import melave_score, mosad_Coordinators_score, eshcol_Coordinators_score
from src.routes.notification_form_routes import getAll_notification_form, convert_hebrewDate_to_Lozai

homepage_form_blueprint = Blueprint('homepage_form', __name__, url_prefix='/homepage_form')





def get_melave_score(eshcol="0",mosad="0"):
    # compute score diagram
    counts = dict()
    score_melaveProfile = []
    if eshcol!="0" and mosad!="0":
        all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_ids.contains("0"),user1.eshcol==eshcol,user1.institution_id==mosad).all()
    elif eshcol!="0":
        all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_ids.contains("0"),user1.eshcol==eshcol).all()
    elif mosad!="0":
        all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_ids.contains("0"),user1.institution_id==mosad).all()
    else:
        all_melave = db.session.query(user1.id,user1.name,user1.institution_id).filter(user1.role_ids.contains("0")).all()
    for melave in all_melave:
        melaveId = melave[0]
        melave_score1, call_gap_avg, meet_gap_avg,group_meeting_gap_avg = melave_score(melaveId)
        score_melaveProfile.append({"melave_score1":melave_score1,"melaveId":melaveId})
        counts[melave_score1] = counts.get(melave_score1, 0) + 1

    k, v = [], []
    for key, value in counts.items():
        k.append(key)
        v.append(value)
    return (k,v),score_melaveProfile



def get_mosad_Coordinators_score(eshcol="0"):
    if eshcol!="0":
        all_Mosad_coord = db.session.query(user1.id, user1.institution_id, user1.name).filter(
            user1.role_ids.contains("1"),user1.eshcol==eshcol).all()
    else:
        all_Mosad_coord = db.session.query(user1.id, user1.institution_id,user1.name).filter(user1.role_ids.contains("1")).all()
    mosad_Cooordinator_score_dict = dict()
    score_MosadCoordProfile=[]
    for mosad_coord in all_Mosad_coord:
        Mosad_coord_score=0
        mosadCoordinator = mosad_coord[0]
        mosad_Coordinators_score1, visitprofessionalMeet_melave_avg, avg_matzbarMeeting_gap, total_avg_call, total_avg_meet ,groupNeeting_gap_avg= mosad_Coordinators_score(
            mosadCoordinator)
        mosad_Cooordinator_score_dict[mosad_Coordinators_score1] = mosad_Cooordinator_score_dict.get(mosad_Coordinators_score1, 0) + 1
        score_MosadCoordProfile.append({"id":mosadCoordinator,"score":mosad_Coordinators_score1})
    k, v = [], []
    for key, value in mosad_Cooordinator_score_dict.items():
        k.append(key)
        v.append(value)
    return (k,v),score_MosadCoordProfile


def get_Eshcol_corrdintors_score():
    all_Eshcol_coord = db.session.query(user1.id, user1.cluster_id,user1.name,user1.institution_id).filter(user1.role_ids.contains("2")).all()
    eshcol_Cooordinator_score = dict()
    score_EshcolCoordProfile=[]
    for Eshcol_coord in all_Eshcol_coord:
        Eshcol_coord_id = Eshcol_coord[0]
        eshcolCoordinator_score1, avg__mosad_racaz_meeting_monthly = eshcol_Coordinators_score(Eshcol_coord_id)
        print("eshcolCoordinator_score1",eshcolCoordinator_score1)
        eshcol_Cooordinator_score[eshcolCoordinator_score1] = eshcol_Cooordinator_score.get(eshcolCoordinator_score1, 0) + 1
        score_EshcolCoordProfile.append({"score":eshcolCoordinator_score1,"id":Eshcol_coord_id})
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
        Visit.ent_reported).filter(Visit.title == config.call_report).all()
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
        if 21 >= gap:
            greenvisitcalls += 1
    # update apprentices meetings
    visitmeetings = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.ent_reported).filter(or_(Visit.title == config.personalMeet_report,Visit.title == config.groupMeet_report)).all()
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
        userId = request.args.get("userId")
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

        counts_melave_score,score_melaveProfile_list=get_melave_score()
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

@homepage_form_blueprint.route("/init_eshcolCoord", methods=['GET'])
def init_eshcolCoord():
    try:
        accessToken =request.headers.get('Authorization')
        print("accessToken:",accessToken)
        userId = request.args.get("userId")
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
        all_Apprentices = db.session.query(Apprentice.id).filter(Apprentice.eshcol==record.eshcol).all()

        counts_melave_score,score_melaveProfile_list=get_melave_score(eshcol=record.eshcol)
        mosad_Cooordinator_score,score_MosadCoordProfile_list=get_mosad_Coordinators_score()

        greenvisitmeetings,orangevisitmeetings,redvisitmeetings,greenvisitcalls,orangevisitcalls,redvisitcalls,forgotenApprenticCount=red_green_orange_status(all_Apprentices)

        return jsonify({
            'score_melaveProfile_list': score_melaveProfile_list,
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
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@homepage_form_blueprint.route("/init_mosadCoord", methods=['GET'])
def init_mosadCoord():
    try:
        print(request)
        accessToken =request.headers.get('Authorization')
        print("accessToken:",accessToken)
        userId = request.args.get("userId")
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
        all_Apprentices = db.session.query(Apprentice.id).filter(Apprentice.institution_id==record.institution_id).all()

        counts_melave_score,score_melaveProfile_list=get_melave_score(mosad=record.institution_id)

        greenvisitmeetings,orangevisitmeetings,redvisitmeetings,greenvisitcalls,orangevisitcalls,redvisitcalls,forgotenApprenticCount=red_green_orange_status(all_Apprentices)

        return jsonify({
            'score_melaveProfile_list': score_melaveProfile_list,
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
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


class Apprentice1:
    pass


@homepage_form_blueprint.route("/get_closest_Events", methods=['GET'])
def get_closest_Events():
    try:
        user = request.args.get("userId")

        ApprenticeList = db.session.query(Apprentice.birthday_ivry, Apprentice.id, Apprentice.accompany_id,
                                          Apprentice.name, Apprentice.last_name,Apprentice.birthday).filter(
            Apprentice.accompany_id == user).all()
        my_dict = []
        for Apprentice1 in ApprenticeList:
            # birthday
            gap_loazi=1000
            gap=1000
            if Apprentice1.birthday_ivry:
                thisYearBirthday = convert_hebrewDate_to_Lozai(Apprentice1.birthday_ivry)
                gap = (date.today() - thisYearBirthday).days
            if Apprentice1.birthday:
                gap_loazi=(datetime.today() - datetime(date.today().year, Apprentice1.birthday.month, Apprentice1.birthday.day)).days

            if (gap <= 0 and gap >= -30) or (gap_loazi <= 0 and gap_loazi >= -30) :
                my_dict.append(
                    {"id": str(Apprentice1.id),"subject":Apprentice1.id,
                     "date": datetime(thisYearBirthday.year, thisYearBirthday.month, thisYearBirthday.day).isoformat(),"created_at": str(thisYearBirthday),
                     "daysfromnow": gap, "event": "יומהולדת", "allreadyread": False,"description": "יומהולדת","frequency": "never" ,
                     "numOfLinesDisplay": 2})
        return jsonify(my_dict), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

def toISO(d):
    if d:
        Date=d.split(".")
        print(d)
        return datetime(int(Date[2]),int(Date[0]), int(Date[1])).isoformat()
    else:
        return None