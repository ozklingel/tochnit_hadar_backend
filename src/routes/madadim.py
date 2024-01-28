import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

madadim_form_blueprint = Blueprint('madadim', __name__, url_prefix='/madadim')


@madadim_form_blueprint.route("/lowScoreApprentice", methods=['GET'])
def lowScoreApprentice():
    Oldvisitcalls = db.session.query(Visit.apprentice_id,Institution.name).filter(Visit.apprentice_id==Apprentice.id,Institution.id==
                                                                                  Apprentice.institution_id,Visit.title =="נסיון_שנכשל" ).all()
    forgotenApprenticCount=0
    forgotenApprenticeList={}
    print(Oldvisitcalls)

    for ent in Oldvisitcalls:
        forgotenApprenticCount+=1
        if ent[1] not in forgotenApprenticeList:
            forgotenApprenticeList[ent[1]] =0
        forgotenApprenticeList[ent[1] ]+=1

    print(forgotenApprenticeList)

    print("forgotenApprenticeList:" ,forgotenApprenticeList)
    return jsonify({
    'lowScoreApprentice_Count': forgotenApprenticCount ,
    'lowScoreApprentice_List': [{"name":key,"value":value} for key, value in forgotenApprenticeList.items()],
               }), HTTPStatus.OK

    return jsonify({
    'result': "error:no result",
               }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingCalleApprentice", methods=['GET'])
def missingCalleApprentice():
    all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
        Apprentice.institution_id == Institution.id).all()
    # update apprentices meet
    visitcalls = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.apprentice_id,
                                                           Institution.id == Apprentice.institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.apprentice_id,
                                                                                           Institution.name).all()
    print(visitcalls)
    ids_have_visit = [r[0] for r in visitcalls]
    ids_no_visit=[]
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids_have_visit:
            ids_no_visit.append([ent[0],ent[1]])
    counts = dict()
    missingCallApprentice_total=0
    for i in visitcalls:
        vIsDate=i.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        if gap>21:
            missingCallApprentice_total+=1
            counts[i[2]] = counts.get(i[2], 0) + 1
    for i in ids_no_visit:
        missingCallApprentice_total += 1
        counts[i[1]] = counts.get(i[1], 0) + 1
    print(counts)
    return jsonify({
        'missingCallApprentice_total': missingCallApprentice_total,

        'missingCalleApprentice_count': [{"name":key,"value":value} for key, value in counts.items()],

    }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingMeetingApprentice", methods=['GET'])
def missingMeetingApprentice():
    all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
        Apprentice.institution_id == Institution.id).all()
    # update apprentices meet
    visitcalls = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.apprentice_id,
                                                           Institution.id == Apprentice.institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.apprentice_id,
                                                                                           Institution.name).all()
    print(visitcalls)
    ids_have_visit = [r[0] for r in visitcalls]
    ids_no_visit=[]
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids_have_visit:
            ids_no_visit.append([ent[0],ent[1]])
    counts = dict()
    missingmeetApprentice_total=0
    for i in visitcalls:
        vIsDate=i.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        if gap>21:
            missingmeetApprentice_total+=1
            counts[i[2]] = counts.get(i[2], 0) + 1
    for i in ids_no_visit:
        missingmeetApprentice_total += 1
        counts[i[1]] = counts.get(i[1], 0) + 1
    print(counts)
    return jsonify({
        'missingmeetApprentice_total': missingmeetApprentice_total,
        'missingmeetApprentice_count': [{"name":key,"value":value} for key, value in counts.items()],

    }), HTTPStatus.OK

@madadim_form_blueprint.route("/forgotenApprentices", methods=['GET'])
def forgotenApprentice():

        all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
            Apprentice.institution_id == Institution.id).all()
        # update apprentices meet
        visitcalls = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.name).filter(Apprentice.id == Visit.apprentice_id,
                                                               Institution.id == Apprentice.institution_id,
                                                               Visit.title == "שיחה").group_by(Visit.apprentice_id,
                                                                                               Institution.name).all()
        print(visitcalls)
        ids_have_visit = [r[0] for r in visitcalls]
        ids_no_visit = []
        # handle no record
        for ent in all_Apprentices:
            if ent.id not in ids_have_visit:
                ids_no_visit.append([ent[0], ent[1]])
        counts = dict()
        forgotenApprentice_total=0
        for i in visitcalls:
            vIsDate = i.visit_date
            now = datetime.date.today()
            gap = (now - vIsDate).days if vIsDate is not None else 0
            if gap > 100:
                forgotenApprentice_total+=1
                counts[i[2]] = counts.get(i[2], 0) + 1
        for i in ids_no_visit:
            forgotenApprentice_total += 1
            counts[i[1]] = counts.get(i[1], 0) + 1
        print(counts)
        return jsonify({
        'forgotenApprentice_total': forgotenApprentice_total,

            'forgotenApprentice_count': [{"name":key,"value":value} for key, value in counts.items()],

        }), HTTPStatus.OK

@madadim_form_blueprint.route("/forgotenApprentice_Mosad", methods=['GET'])
def missingMeetingApprentice_Mosad():
    institution_id = request.args.get("institutionId")
    print(institution_id)
    all_Apprentices = db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name).filter(
        Apprentice.institution_id == institution_id).all()
    # update apprentices meet
    visitcalls = db.session.query(Visit.apprentice_id,Apprentice.name,Apprentice.last_name ,func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.apprentice_id,
                                                           Institution.id == Apprentice.institution_id,Apprentice.institution_id==institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.apprentice_id,Apprentice.name,Apprentice.last_name,
                                                                                           Institution.name).all()
    print(visitcalls)
    ids_have_visit = [r[0] for r in visitcalls]
    ids_no_visit = []
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids_have_visit:
            ids_no_visit.append([ent[0], ent[1],ent[2]])
    counts = dict()
    for i in visitcalls:
        vIsDate = i.visit_date
        now = datetime.date.today()
        gap = (now - vIsDate).days if vIsDate is not None else 0
        if gap > 100:
            counts[ent[1]+" "+ent[2]] = gap
    for i in ids_no_visit:
        counts[ent[1]+" "+ent[2]] = 101
    print(counts)
    return jsonify({
        'missingmeetApprentice_count': counts,

    }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingCallsApprentice_Mosad", methods=['GET'])
def missingCallsApprentice_Mosad():
    institution = request.args.get("institutionId")
    print(institution)
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(Visit,Apprentice).filter(Visit.apprentice_id==Apprentice.id,Visit.title == "שיחה",
                                                                 Visit.visit_date < too_old).filter(Apprentice.institution_id==institution).all()
    print(Oldvisitcalls[0])
    list=[]
    for ent in Oldvisitcalls:
        print(type(ent[0].visit_date))
        vIsDate=ent[0].visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        list.append({"apprentice":ent[1].name+ent[1].last_name,"gap":gap})

    return jsonify({
        'gapList': list,
    }), HTTPStatus.OK

@madadim_form_blueprint.route("/melave", methods=['GET'])
def getMelaveMadadim():
    melaveId = request.args.get("melaveId")[3:]
    print(melaveId)
    ApprenticeCount = db.session.query(Apprentice.id).filter(Apprentice.accompany_id == melaveId).all()
    Apprentice_ids_call=[r[0] for r in ApprenticeCount]
    too_old = datetime.datetime.today() - datetime.timedelta(days=21)
    Oldvisitcalls = db.session.query(Visit.apprentice_id).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_call:
            Apprentice_ids_call.remove(i[0])
    print(len(Apprentice_ids_call))

    Apprentice_ids_meet=[r[0] for r in ApprenticeCount]
    too_old = datetime.datetime.today() - datetime.timedelta(days=21)
    Oldvisitmeet = db.session.query(Visit.apprentice_id).filter(Visit.user_id==melaveId,Visit.title == "מפגש",
                                                                 Visit.visit_date >= too_old).all()
    for i in Oldvisitmeet:
        if i[0] in  Apprentice_ids_meet:
            Apprentice_ids_meet.remove(i[0])
    print(len(Apprentice_ids_meet))

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitProffesionalMeet = db.session.query(Visit.user_id).filter(Visit.user_id==melaveId,Visit.title == "מפגש_מקצועי",
                                                                 Visit.visit_date > too_old).all()
    if len(OldvisitProffesionalMeet)>=2:
           sadna_score=100
    if len(OldvisitProffesionalMeet) == 1:
        sadna_score = 50
    if len(OldvisitProffesionalMeet) == 0:
        sadna_score = 0

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    Oldvisit_cenes = db.session.query(Visit.user_id).filter(Visit.user_id==melaveId,Visit.title == "כנס",
                                                                 Visit.visit_date > too_old).all()
    if len(Oldvisit_cenes)>=2:
           cenes_score=100
    if len(Oldvisit_cenes) == 1:
        cenes_score = 50
    if len(Oldvisit_cenes) == 0:
        cenes_score = 0

    Apprentice_ids_Horim=[r[0] for r in ApprenticeCount]
    OldvisitHorim = db.session.query(Visit.apprentice_id).filter(Visit.user_id==melaveId,Visit.title == "מפגש_הורים"
                                                                 ).all()
    for i in OldvisitHorim:
        if i[0] in  Apprentice_ids_call:
            Apprentice_ids_Horim.remove(i[0])
    print(len(Apprentice_ids_call))


    Apprentice_ids_meetInArmy=[r[0] for r in ApprenticeCount]
    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitmeetInArmy = db.session.query(Visit.apprentice_id,Visit.visit_date).distinct(Visit.visit_date).filter(Visit.user_id==melaveId,Visit.title == "מפגש",Visit.visit_in_army==True,
                                                                 Visit.visit_date > too_old).all()
    for i in OldvisitmeetInArmy:
        if i[0] in  Apprentice_ids_meetInArmy:
            Apprentice_ids_meetInArmy.remove(i[0])
    print(len(Apprentice_ids_meetInArmy))

    Apprentice_ids_forgoten=[r[0] for r in ApprenticeCount]
    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.apprentice_id).filter(Visit.user_id==melaveId,Apprentice.id==Visit.apprentice_id,Institution.id==Apprentice.institution_id,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    print(len(Apprentice_ids_forgoten))
    forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,
                                                       Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.id.in_(list(Apprentice_ids_forgoten)),Apprentice.institution_id==Institution.id).all()

    done_forgoten_dict = [{"Institution_name": row[0], "name": row[1], "last_name": row[2],"base_address" :row[3],
                                     "army_role": row[4], "unit_name": row[5], "marriage_status": row[6],
                                     "serve_type": row[7],"hadar_plan_session": row[8]} for row in
                        [tuple(row) for row in forgotenApprentice_full_details]] if forgotenApprentice_full_details is not None else []

    return jsonify({
        'melave_score': 55,

        "numOfApprentice": len(ApprenticeCount),
        'Oldvisitmeetings': len(Apprentice_ids_meet),
        'new_visitmeeting_Army': len(Apprentice_ids_meetInArmy),
        'oldvisitcalls': len(Apprentice_ids_call),
        'sadna_score': sadna_score,
        'cenes_score': cenes_score,
        'No_visitHorim': len(Apprentice_ids_Horim),
        'forgotenApprenticeCount': len(Apprentice_ids_forgoten),
        'forgotenApprentice_full_details': done_forgoten_dict,
        'forgotenApprentice_4_yearly': [[3, 2, 0, 2], [1, 2, 3, 4]],

        'visitCall_monthlyGap_avg': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'visitMeeting_monthlyGap_avg': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'visitCall_currentGap_avg': 21,
        'visitmeeting_currentGap_avg': 22,
        'visitsadna_startYear': 22,
        'visitsadna_presence': [[21, 20, 20, 20], [1, 2, 3, 4]],

        'visitCenes_yearly': True,
        'visitCenes_yearly_presence': 1,
        'visitCenes_4_yearly_presence': [[1, 0, 0, 0], [2022, 2023, 2024, 2025]],
        'visitHorim_yearly': 2,
        'visitHorim_4_yearly': [[92, 0, 12, 0], [2022, 2023, 2024, 2025]],
    }), HTTPStatus.OK


@madadim_form_blueprint.route("/mosadCoordinator", methods=['GET'])
def getMosadCoordinatorMadadim():
    mosadCoordinator = request.args.get("mosadCoordinator")[3:]
    print(mosadCoordinator)
    institutionId = db.session.query(user1.institution_id).filter(user1.id == mosadCoordinator).first()[0]
    all_Melave = db.session.query(user1.id).filter(user1.role_id=="0",user1.institution_id == institutionId).all()

    print(institutionId)
    old_Melave_ids_professional=[r[0] for r in all_Melave]
    too_old = datetime.datetime.today() - datetime.timedelta(days=90)
    newvisit_professional = db.session.query(Visit.user_id).filter(Visit.user_id==user1.id,user1.institution_id==institutionId,Visit.title == "מפגש_מקצועי",
                                                                 Visit.visit_date > too_old).all()
    print(old_Melave_ids_professional)
    for i in newvisit_professional:
        if i[0] in  old_Melave_ids_professional:
            old_Melave_ids_professional.remove(i[0])
    print(old_Melave_ids_professional)

    old_Melave_ids_matzbar = [r[0] for r in all_Melave]
    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    Oldvisit_matzbar = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,
                                                            user1.institution_id == institutionId,
                                                            Visit.title == "מצבר",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_matzbar:
        if i[0] in old_Melave_ids_matzbar:
            old_Melave_ids_matzbar.remove(i[0])

    all_apprenties_mosad = db.session.query(Apprentice.id).filter(Apprentice.institution_id == institutionId).all()

    old_apprenties_mosad_ids_call = [r[0] for r in all_apprenties_mosad]
    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    Oldvisit_call = db.session.query(Visit.apprentice_id).filter(Visit.apprentice_id == Apprentice.id,
                                                            Apprentice.institution_id == institutionId,
                                                            Visit.title == "שיחה",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_call:
        if i[0] in old_apprenties_mosad_ids_call:
            old_apprenties_mosad_ids_call.remove(i[0])

    old_apprenties_mosad_ids_meet = [r[0] for r in all_apprenties_mosad]
    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    Oldvisit_meet = db.session.query(Visit.apprentice_id).filter(Visit.apprentice_id == Apprentice.id,
                                                            Apprentice.institution_id == institutionId,
                                                            Visit.title == "מפגש",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_meet:
        if i[0] in old_apprenties_mosad_ids_meet:
            old_apprenties_mosad_ids_meet.remove(i[0])

    old_apprentice_ids_groupMeet=[r[0] for r in all_apprenties_mosad]
    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    new_visit_groupMeet = db.session.query(Visit.user_id).filter(Visit.user_id==user1.id,user1.institution_id==institutionId,Visit.title == "מפגש_קבוצתי",
                                                                 Visit.visit_date > too_old).all()
    for i in new_visit_groupMeet:
        if i[0] in  old_apprentice_ids_groupMeet:
            old_apprentice_ids_groupMeet.remove(i[0])


    too_old = datetime.datetime.today() - datetime.timedelta(days=365)
    isVisitenterMahzor=False
    visitenterMahzor = db.session.query(Visit.visit_date).filter(Visit.user_id==mosadCoordinator,Visit.title == "הזנת_מחזור",Visit.visit_date>too_old).all()
    if visitenterMahzor:
        isVisitenterMahzor=True

    too_old = datetime.datetime.today() - datetime.timedelta(days=365)
    visitDoForBogrim = db.session.query(Visit.visit_date,Visit.title,Visit.description).filter(Visit.user_id==mosadCoordinator,Visit.title == "עשייה_לבוגרים",Visit.visit_date>too_old).all()


    old_Melave_ids_MelavimMeeting = [r[0] for r in all_Melave]
    too_old = datetime.datetime.today() - datetime.timedelta(days=120)
    new_MelavimMeeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.user_id == user1.id,
                                                                user1.institution_id == institutionId,
                                                                Visit.title == "מפגש_מלוים",
                                                         Visit.visit_date > too_old).all()
    good_MelavimMeeting_ = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,
                                                                user1.institution_id == institutionId,
                                                                Visit.title == "מפגש_מלוים",
                                                         Visit.visit_date > too_old).all()

    for i in good_MelavimMeeting_:
        if i[0] in old_Melave_ids_MelavimMeeting:
            old_Melave_ids_MelavimMeeting.remove(i[0])


    Apprentice_ids_forgoten=[r[0] for r in all_apprenties_mosad]
    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.apprentice_id).filter(Apprentice.id==Visit.apprentice_id,institutionId==Apprentice.institution_id,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,
                                                       Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.institution_id==Institution.id,Apprentice.id.in_(list(Apprentice_ids_forgoten))).all()

    return jsonify({

        'mosadCoordinator_score': 55,

        'good_Melave_ids_sadna': len(all_Melave) - len(old_Melave_ids_professional),
        'good_Melave_ids_matzbar': len(all_Melave) - len(old_Melave_ids_matzbar),
        'good_apprenties_mosad_call': len(all_apprenties_mosad) - len(old_apprenties_mosad_ids_call),

        'good_apprenties_mosad_meet': len(all_apprenties_mosad) - len(old_apprenties_mosad_ids_meet),
        'good_apprentice_mosad_groupMeet': len(all_apprenties_mosad) - len(old_apprentice_ids_groupMeet),
        'all_Melave_mosad_count': len(all_Melave),

        'all_apprenties_mosad': len(all_apprenties_mosad),
        'Apprentice_forgoten_count': len(Apprentice_ids_forgoten),
        'forgotenApprentice_full_details': [tuple(row) for row in forgotenApprentice_full_details],
        'new_MelavimMeeting': len(new_MelavimMeeting),
        'visitDoForBogrim': len(visitDoForBogrim),
        'isVisitenterMahzor': isVisitenterMahzor,
        'avg_presence_MelavimMeeting': (len(all_Melave) - len(old_Melave_ids_MelavimMeeting)) / len(all_Melave),
        'avg_presence_MelavimMeeting_monthly': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'avg_matzbarMeeting_gap': 60,
        'avg_matzbarMeeting_gap_monthly': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'avg_apprenticeCall_gap': 60,
        'avg_apprenticeCall_gap_monthly': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'avg_apprenticeMeeting_gap': 60,
        'avg_apprenticeMeeting_gap_monthly': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                              [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        "visitDoForBogrim_list": [tuple(row) for row in visitDoForBogrim],
        'forgotenApprentice_4_yearly': [[3, 2, 0, 2], [1, 2, 3, 4]],
    }), HTTPStatus.OK

@madadim_form_blueprint.route("/eshcolCoordinator", methods=['GET'])
def getEshcolCoordinatorMadadim():
    eshcolCoordinatorId = request.args.get("eshcolCoordinator")[3:]
    print(eshcolCoordinatorId)
    #get the Eshcol id
    eshcol_id = db.session.query(user1.cluster_id).filter(user1.id == eshcolCoordinatorId).first()
    print("eshcol_id",eshcol_id)

    # total MosadCoordinator Count for this eshcol
    all_MosadCoordinator = db.session.query(user1.id).filter(user1.cluster_id == eshcol_id[0],user1.role_id=="1").all()
    EshcolMelvin = db.session.query(user1.id).filter(user1.cluster_id == eshcol_id[0],user1.role_id=="0").all()
    all_EshcolApprentices = db.session.query(Apprentice.id).filter(Apprentice.institution_id==Institution.id,Institution.owner_id==str(eshcol_id[0])).all()

    all_MosadCoordinator_ids_call = [r[0] for r in all_MosadCoordinator]
    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    new_visit_yeshiva = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,user1.role_id=="1",
                                                            user1.cluster_id == eshcol_id[0],
                                                            Visit.title == "מפגש",
                                                            Visit.visit_date > too_old).all()
    for i in new_visit_yeshiva:
        if i[0] in all_MosadCoordinator_ids_call:
            all_MosadCoordinator_ids_call.remove(i[0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=30)
    newvisit_yeshiva_Tohnit = db.session.query(Visit.visit_date).filter(Visit.user_id==eshcolCoordinatorId,Visit.title == "מפגש_כלל_תוכנית",Visit.visit_date>too_old).all()

    Apprentice_ids_forgoten=[r[0] for r in all_EshcolApprentices]
    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.apprentice_id).filter(Apprentice.id==Visit.apprentice_id,Institution.id==Apprentice.institution_id,Institution.owner_id==str(eshcol_id[0]),Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,
                                                       Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.institution_id==Institution.id,Apprentice.id.in_(list(Apprentice_ids_forgoten))).all()

    return jsonify({
        'eshcolCoordinator_score': 55,

        'newvisit_yeshiva_Tohnit': "100" if len(newvisit_yeshiva_Tohnit) > 0 else "0",
        'all_MosadCoordinator_count': len(all_MosadCoordinator),
        'good__mosad_racaz_meeting': len(all_MosadCoordinator) - len(all_MosadCoordinator_ids_call),
        'Apprentice_forgoten_count': len(Apprentice_ids_forgoten),
        'all_EshcolApprentices_count': len(all_EshcolApprentices),
        'forgotenApprentice_full_details': [tuple(row) for row in forgotenApprentice_full_details],
        'avg_apprenticeCall_gap': 60,
        'good__mosad_racaz_meeting_monthly': [[21, 20, 20, 20, 20, 20, 20, 20, 20, 20, 15],
                                              [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]],
        'forgotenApprentice_4_yearly': [[3, 2, 0, 2], [1, 2, 3, 4]],

    }), HTTPStatus.OK






