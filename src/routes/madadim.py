
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from datetime import datetime,date,timedelta

from pyluach import dates
from sqlalchemy import func

import config
from app import db, red
from src.models.apprentice_model import Apprentice

from src.models.institution_model import Institution
from src.models.system_report import system_report
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.export_import import compute_visit_score
from src.routes.user_Profile import toISO

madadim_form_blueprint = Blueprint('madadim', __name__, url_prefix='/madadim')


@madadim_form_blueprint.route("/lowScoreApprentice", methods=['GET'])
def lowScoreApprentice():
    Oldvisitcalls = db.session.query(Visit.ent_reported,Institution.name).filter(Visit.ent_reported==Apprentice.id,Institution.id==
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
    visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                           Institution.id == Apprentice.institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.ent_reported,
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
        now=date.today()
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
    visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                           Institution.id == Apprentice.institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.ent_reported,
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
        now=date.today()
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
        visitcalls = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date"),
                                      Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                               Institution.id == Apprentice.institution_id,
                                                               Visit.title == "שיחה").group_by(Visit.ent_reported,
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
            now = date.today()
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
    visitcalls = db.session.query(Visit.ent_reported,Apprentice.name,Apprentice.last_name ,func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.ent_reported,
                                                           Institution.id == Apprentice.institution_id,Apprentice.institution_id==institution_id,
                                                           Visit.title == "שיחה").group_by(Visit.ent_reported,Apprentice.name,Apprentice.last_name,
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
        now = date.today()
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
    too_old = datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(Visit,Apprentice).filter(Visit.ent_reported==Apprentice.id,Visit.title == "שיחה",
                                                                 Visit.visit_date < too_old).filter(Apprentice.institution_id==institution).all()
    print(Oldvisitcalls[0])
    list=[]
    for ent in Oldvisitcalls:
        print(type(ent[0].visit_date))
        vIsDate=ent[0].visit_date
        now=date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        list.append({"apprentice":ent[1].name+ent[1].last_name,"gap":gap})

    return jsonify({
        'gapList': list,
    }), HTTPStatus.OK

def fetch_Diagram_monthly(related_id,type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30*12)
    data = db.session.query(system_report.creation_date,system_report.value).filter(system_report.type==type ,system_report.related_id==related_id,
                                                            system_report.creation_date > too_old).all()
    x_list=[1,2,3,4,5,6,7,8,9,10,11]
    y_list=[0,0,0,0,0,0,0,0,0,0,0]
    for row in data:
        month = row[0].month
        value= row[1]
        i=x_list.index(month)
        y_list[i]= value
    return  x_list,y_list,

def fetch_Diagram_rivonly(related_id,type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30*12)
    data = db.session.query(system_report.creation_date,system_report.value).filter(system_report.type==type ,
                                                            system_report.creation_date > too_old).all()
    x_list=[1,2,3,4]
    y_list=[0,0,0,0]
    for row in data:
        rivon = row[0].month%3
        value= row[1]
        i=x_list.index(rivon)
        y_list[i]= value
    return  x_list,y_list,

def fetch_Diagram_yearly(related_id,type="melave_Score"):
    too_old = datetime.today() - timedelta(days=30*12)
    data = db.session.query(system_report.creation_date,system_report.value).filter(system_report.type==type ,
                                                            system_report.creation_date > too_old).all()
    this_year=datetime.today().year
    x_list=[this_year-3,this_year-2,this_year-1,this_year]
    y_list=[0,0,0,0]
    for row in data:
        year = row[0].year
        value= row[1]
        i=x_list.index(year)
        y_list[i]= value
    return  x_list,y_list,

@madadim_form_blueprint.route("/melave", methods=['GET'])
def getMelaveMadadim():
    melaveId = request.args.get("melaveId")[3:]
    print(melaveId)
    ApprenticeCount = db.session.query(Apprentice.id).filter(Apprentice.accompany_id == melaveId).all()
    Apprentice_ids_call=[r[0] for r in ApprenticeCount]
    too_old = datetime.today() - timedelta(days=21)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_call:
            Apprentice_ids_call.remove(i[0])

    Apprentice_ids_meet=[r[0] for r in ApprenticeCount]
    too_old = datetime.today() - timedelta(days=90)
    Oldvisitmeet = db.session.query(Visit.ent_reported).filter(Visit.user_id==melaveId,Visit.title == "מפגש",
                                                                 Visit.visit_date >= too_old).all()
    for i in Oldvisitmeet:
        if i[0] in  Apprentice_ids_meet:
            Apprentice_ids_meet.remove(i[0])
#מפגש_מקצועי
    current_month=datetime.today().month
    start_Of_year = datetime.today() - timedelta(days=30*current_month)
    numOfQuarter_passed=int(current_month/3)
    newvisitProffesionalMeet_year = db.session.query(Visit.user_id).filter(Visit.user_id==melaveId,Visit.title == "מפגש_מקצועי",
                                                                 Visit.visit_date > start_Of_year).all()
    if numOfQuarter_passed==0:
        sadna_score=100
    else:
        sadna_score=100*len(newvisitProffesionalMeet_year)/numOfQuarter_passed

    start_Of_prev_year = datetime.today() - timedelta(days=30*current_month+30*12)
    _yearly_cenes = db.session.query(system_report).filter(system_report.type=="כנס_שנתי" ,
                                                            system_report.creation_date > start_Of_prev_year).all()
    newvisit_cenes=[]
    if len(_yearly_cenes)>0:
        newvisit_cenes = db.session.query(Visit.user_id).filter(Visit.user_id==melaveId,Visit.title == "כנס",
                                                                     Visit.visit_date > start_Of_year).all()
        cenes_score= 100*len(newvisit_cenes)/len(_yearly_cenes)
    else:
        cenes_score=100

    Apprentice_ids_Horim=[r[0] for r in ApprenticeCount]
    OldvisitHorim = db.session.query(Visit.ent_reported).filter(Visit.user_id==melaveId,Visit.title == "מפגש_הורים",
                                        Visit.visit_date>start_Of_year  ).all()
    for i in OldvisitHorim:
        if i[0] in  Apprentice_ids_call:
            Apprentice_ids_Horim.remove(i[0])

    Apprentice_ids_meetInArmy=[r[0] for r in ApprenticeCount]
    OldvisitmeetInArmy = db.session.query(Visit.ent_reported,Visit.visit_date).distinct(Visit.visit_date).filter(Visit.user_id==melaveId,Visit.title == "מפגש",Visit.visit_in_army==True,
                                                                 Visit.visit_date > start_Of_year).all()
    for i in OldvisitmeetInArmy:
        if i[0] in  Apprentice_ids_meetInArmy:
            Apprentice_ids_meetInArmy.remove(i[0])

    Apprentice_ids_forgoten=[r[0] for r in ApprenticeCount]
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(Visit.user_id==melaveId,Apprentice.id==Visit.ent_reported,Institution.id==Apprentice.institution_id,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,
                                                       Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.id.in_(list(Apprentice_ids_forgoten)),Apprentice.institution_id==Institution.id).all()

    done_forgoten_dict = [{"Institution_name": row[0], "name": row[1], "last_name": row[2],"base_address" :row[3],
                                     "army_role": row[4], "unit_name": row[5], "marriage_status": row[6],
                                     "serve_type": row[7],"hadar_plan_session": row[8]} for row in
                        [tuple(row) for row in forgotenApprentice_full_details]] if forgotenApprentice_full_details is not None else []
    melave_score1,call_gap_avg,meet_gap_avg=melave_score(melaveId)
    return jsonify({
        'melave_score': melave_score1,
        "numOfApprentice": len(ApprenticeCount),
        'oldvisitcalls': len(Apprentice_ids_call),
        'Oldvisitmeetings': len(Apprentice_ids_meet),
        'numOfQuarter_passed': numOfQuarter_passed,
        'sadna_todo': numOfQuarter_passed,
        'sadna_done': len(newvisitProffesionalMeet_year),
        'sadna_percent': sadna_score,
        'cenes_2year': len(_yearly_cenes),
        'newvisit_cenes': len(newvisit_cenes),
        'cenes_percent': cenes_score,
        'No_visitHorim': len(Apprentice_ids_Horim),
        'forgotenApprenticeCount': len(Apprentice_ids_forgoten),
        'new_visitmeeting_Army': len(Apprentice_ids_meetInArmy),

        'call_gap_avg': call_gap_avg,
        'meet_gap_avg': meet_gap_avg,
        'visitCall_monthlyGap_avg': fetch_Diagram_monthly(melaveId,"visitcalls_melave_avg"),
        'visitMeeting_monthlyGap_avg': fetch_Diagram_monthly(melaveId,"visitmeets_melave_avg"),
        'forgotenApprentice_full_details': Apprentice_ids_forgoten,
        'forgotenApprentice_rivonly': fetch_Diagram_rivonly(melaveId,"forgotenApprentice_cnt"),

        'visitsadna_presence': fetch_Diagram_rivonly(melaveId,"proffesionalMeet_presence"),
        'visitCenes_4_yearly_presence': fetch_Diagram_yearly(melaveId,"cenes_presence"),
        'visitHorim_4_yearly': fetch_Diagram_yearly(melaveId,"horim_meeting"),
    }), HTTPStatus.OK


@madadim_form_blueprint.route("/mosadCoordinator", methods=['GET'])
def mosadCoordinator(mosadCoordinator="empty"):
    if mosadCoordinator=="empty":
        mosadCoordinator = request.args.get("mosadCoordinator")[3:]
    print(mosadCoordinator)
    institutionId = db.session.query(user1.institution_id).filter(user1.id == mosadCoordinator).first()[0]
    all_Melave = db.session.query(user1.id).filter(user1.role_id=="0",user1.institution_id == institutionId).all()

    print(institutionId)
    old_Melave_ids_professional=[r[0] for r in all_Melave]
    too_old = datetime.today() - timedelta(days=90)
    newvisit_professional = db.session.query(Visit.user_id).filter(Visit.user_id==user1.id,user1.institution_id==institutionId,Visit.title == "מפגש_מקצועי",
                                                                 Visit.visit_date > too_old).all()
    for i in newvisit_professional:
        if i[0] in  old_Melave_ids_professional:
            old_Melave_ids_professional.remove(i[0])

    old_Melave_ids_matzbar = [r[0] for r in all_Melave]
    too_old = datetime.today() - timedelta(days=60)
    Oldvisit_matzbar = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,
                                                            user1.institution_id == institutionId,
                                                            Visit.title == "מצבר",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_matzbar:
        if i[0] in old_Melave_ids_matzbar:
            old_Melave_ids_matzbar.remove(i[0])

    all_apprenties_mosad = db.session.query(Apprentice.id).filter(Apprentice.institution_id == institutionId).all()

    old_apprenties_mosad_ids_call = [r[0] for r in all_apprenties_mosad]
    too_old = datetime.today() - timedelta(days=60)
    Oldvisit_call = db.session.query(Visit.ent_reported).filter(Visit.ent_reported == Apprentice.id,
                                                            Apprentice.institution_id == institutionId,
                                                            Visit.title == "שיחה",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_call:
        if i[0] in old_apprenties_mosad_ids_call:
            old_apprenties_mosad_ids_call.remove(i[0])

    old_apprenties_mosad_ids_meet = [r[0] for r in all_apprenties_mosad]
    too_old = datetime.today() - timedelta(days=60)
    Oldvisit_meet = db.session.query(Visit.ent_reported).filter(Visit.ent_reported == Apprentice.id,
                                                            Apprentice.institution_id == institutionId,
                                                            Visit.title == "מפגש",
                                                            Visit.visit_date > too_old).all()
    for i in Oldvisit_meet:
        if i[0] in old_apprenties_mosad_ids_meet:
            old_apprenties_mosad_ids_meet.remove(i[0])

    old_apprentice_ids_groupMeet=[r[0] for r in all_apprenties_mosad]
    too_old = datetime.today() - timedelta(days=60)
    new_visit_groupMeet = db.session.query(Visit.user_id).filter(Visit.user_id==user1.id,user1.institution_id==institutionId,Visit.title == "מפגש_קבוצתי",
                                                                 Visit.visit_date > too_old).all()
    for i in new_visit_groupMeet:
        if i[0] in  old_apprentice_ids_groupMeet:
            old_apprentice_ids_groupMeet.remove(i[0])

    too_old = datetime.today() - timedelta(days=365)
    isVisitenterMahzor=False
    visitenterMahzor = db.session.query(Visit.visit_date).filter(Visit.user_id==mosadCoordinator,Visit.title == "הזנת_מחזור",Visit.visit_date>too_old).all()
    if visitenterMahzor:
        isVisitenterMahzor=True

    too_old = datetime.today() - timedelta(days=365)
    visitDoForBogrim = db.session.query(Visit.visit_date,Visit.title,Visit.description).filter(Visit.user_id==mosadCoordinator,Visit.title == "עשייה_לבוגרים",Visit.visit_date>too_old).all()

    old_Melave_ids_MelavimMeeting = [r[0] for r in all_Melave]
    too_old = datetime.today() - timedelta(days=120)
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
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(Apprentice.id==Visit.ent_reported,institutionId==Apprentice.institution_id,Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    forgotenApprentice_full_details = db.session.query(Apprentice.id).filter(Apprentice.institution_id==Institution.id,Apprentice.id.in_(list(Apprentice_ids_forgoten))).all()
    mosad_Coordinators_score1,visitprofessionalMeet_melave_avg,avg_matzbarMeeting_gap,total_avg_call,total_avg_meet=mosad_Coordinators_score(mosadCoordinator)
    return jsonify({

        'mosadCoordinator_score': mosad_Coordinators_score1,
        'good_Melave_ids_sadna': len(all_Melave) - len(old_Melave_ids_professional),
        'all_Melave_mosad_count': len(all_Melave),
        'good_Melave_ids_matzbar': len(all_Melave) - len(old_Melave_ids_matzbar),
        'all_apprenties_mosad': len(all_apprenties_mosad),
        'good_apprenties_mosad_call': len(all_apprenties_mosad) - len(old_apprenties_mosad_ids_call),
        'good_apprenties_mosad_meet': len(all_apprenties_mosad) - len(old_apprenties_mosad_ids_meet),
        'good_apprentice_mosad_groupMeet': len(all_apprenties_mosad) - len(old_apprentice_ids_groupMeet),
        'isVisitenterMahzor': isVisitenterMahzor,
        'visitDoForBogrim': len(visitDoForBogrim),
        'new_MelavimMeeting': len(new_MelavimMeeting),
        'avg_presence_MelavimMeeting': (len(all_Melave) - len(old_Melave_ids_MelavimMeeting)) / len(all_Melave),
        'Apprentice_forgoten_count': len(Apprentice_ids_forgoten),

        'visitprofessionalMeet_melave_avg': visitprofessionalMeet_melave_avg,
        'avg_matzbarMeeting_gap': avg_matzbarMeeting_gap,
        'avg_apprenticeCall_gap': total_avg_call,
        'avg_apprenticeMeeting_gap': total_avg_meet,
        "visitDoForBogrim_list":[{"visit_date" :toISO(row[0]),"title":row[1],"description":row[2],"daysFromNow":(date.today() - row[0]).days} for row in visitDoForBogrim],
        'forgotenApprentice_full_details': Apprentice_ids_forgoten,

        'avg_presence_MelavimMeeting_monthly': fetch_Diagram_monthly(mosadCoordinator,"MelavimMeeting_presence"),
        'avg_matzbarMeeting_gap_monthly': fetch_Diagram_monthly(mosadCoordinator,"matzbarMeeting_gap"),
        'avg_apprenticeCall_gap_monthly':fetch_Diagram_monthly(mosadCoordinator,"apprenticeCall_gap"),
        'avg_apprenticeMeeting_gap_monthly':fetch_Diagram_monthly(mosadCoordinator,"apprenticeMeeting_gap"),
        'forgotenApprentice_rivonly': fetch_Diagram_rivonly(mosadCoordinator,"forgotenApprentice"),
    }), HTTPStatus.OK

@madadim_form_blueprint.route("/eshcolCoordinator", methods=['GET'])
def getEshcolCoordinatorMadadim():
    eshcolCoordinatorId = request.args.get("eshcolCoordinator")[3:]
    print(eshcolCoordinatorId)
    #get  Eshcol id
    eshcol = db.session.query(user1.eshcol).filter(user1.id == eshcolCoordinatorId).first()
    if eshcol =="":
        return jsonify({
            'result': "no eshcol",
        }), HTTPStatus.OK
    print("eshcol_id",eshcol)

    # total MosadCoordinator Count for this eshcol
    all_MosadCoordinator = db.session.query(user1.id).filter(user1.eshcol == eshcol[0],user1.role_id=="1").all()
    #EshcolMelvin = db.session.query(user1.id).filter(user1.cluster_id == eshcol[0],user1.role_id=="0").all()
    all_EshcolApprentices = db.session.query(Apprentice.id).filter(Apprentice.institution_id==Institution.id,Institution.eshcol_id==str(eshcol[0])).all()
    print("all_EshcolApprentices",all_EshcolApprentices)

    all_MosadCoordinator_ids_call = [r[0] for r in all_MosadCoordinator]
    too_old = datetime.today() - timedelta(days=30)
    new_visit_yeshiva = db.session.query(Visit.user_id).filter(Visit.user_id == user1.id,user1.role_id=="1",
                                                            user1.eshcol == eshcol[0],
                                                            Visit.title == "מפגש",
                                                            Visit.visit_date > too_old).all()
    for i in new_visit_yeshiva:
        if i[0] in all_MosadCoordinator_ids_call:
            all_MosadCoordinator_ids_call.remove(i[0])

    too_old = datetime.today() - timedelta(days=30)
    newvisit_yeshiva_Tohnit = db.session.query(Visit.visit_date).filter(Visit.user_id==eshcolCoordinatorId,Visit.title == "מפגש_כלל_תוכנית",Visit.visit_date>too_old).all()

    Apprentice_ids_forgoten=[r[0] for r in all_EshcolApprentices]
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(Apprentice.id==Visit.ent_reported,Institution.id==Apprentice.institution_id,Institution.eshcol_id==eshcol[0],Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in  Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    eshcolCoordinator_score1,avg__mosad_racaz_meeting_monthly=eshcol_Coordinators_score(eshcolCoordinatorId)
    return jsonify({
        'eshcolCoordinator_score': eshcolCoordinator_score1,
        'all_MosadCoordinator_count': len(all_MosadCoordinator),
        'good__mosad_racaz_meeting': len(all_MosadCoordinator) - len(all_MosadCoordinator_ids_call),
        'newvisit_yeshiva_Tohnit': "100" if len(newvisit_yeshiva_Tohnit) > 0 else "0",
        'Apprentice_forgoten_count': len(Apprentice_ids_forgoten),
        'all_EshcolApprentices_count': len(all_EshcolApprentices),
        'avg__mosad_racaz_meeting_monthly': avg__mosad_racaz_meeting_monthly,
        'avg__mosad_racaz_meeting_monthly_Diagram': fetch_Diagram_monthly(eshcolCoordinatorId, "mosad_racaz_meeting"),

        'forgotenApprentice_full_details': Apprentice_ids_forgoten,
        'forgotenApprentice_4_rivonly': fetch_Diagram_rivonly(eshcolCoordinatorId,"forgotenApprentice"),

    }), HTTPStatus.OK

def melave_score(melaveId):
    # compute score diagram
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        if len(all_melave_Apprentices)==0:
            return 100,0,0
        visitcalls = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "שיחה", Visit.user_id == melaveId,Visit.visit_date>config.call_madad_date).order_by(Visit.visit_date).all()
        call_score,call_gap_avg=compute_visit_score(all_melave_Apprentices,visitcalls,12,21)

        visitmeetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "מפגש", Visit.user_id == melaveId,Visit.visit_date>config.meet_madad_date).order_by(Visit.visit_date).all()
        personal_meet_score,personal_meet_gap_avg=compute_visit_score(all_melave_Apprentices,visitmeetings,12,90)
        group_meeting = db.session.query(Visit.ent_reported, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.ent_reported).filter(Visit.title == "מפגש_קבוצתי", Visit.user_id == melaveId).first()
        gap = (date.today() - group_meeting.visit_date).days if group_meeting is not None else 100
        group_meeting_score = 0
        if gap <= 60:
            group_meeting_score += 12

        professional_2monthly = db.session.query(Visit.user_id,
                                                 func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "מפגש_מקצועי", Visit.user_id == melaveId).first()
        gap = (date.today() - professional_2monthly.visit_date).days if professional_2monthly is not None else 100
        professional_2monthly_score = 0
        if gap < 90:
            professional_2monthly_score += 6.6

        cenes_yearly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "כנס_שנתי", Visit.user_id == melaveId).first()
        gap = (date.today() - cenes_yearly.visit_date).days if cenes_yearly is not None else 400
        cenes_yearly_score = 0
        if gap < 365:
            cenes_yearly_score += 6.6

        yeshiva_monthly = db.session.query(Visit.user_id, func.max(Visit.visit_date).label("visit_date")).group_by(
            Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == melaveId).first()
        gap = (date.today() - yeshiva_monthly.visit_date).days if yeshiva_monthly is not None else 100
        yeshiva_monthly_score = 0
        if gap < 30:
            yeshiva_monthly_score += 6.6

        Horim_meeting = db.session.query(Visit.ent_reported).filter(Visit.title == "מפגש_הורים", Visit.user_id == melaveId).all()
        Horim_meeting_score = 0
        if len(Horim_meeting) == len(all_melave_Apprentices):
            Horim_meeting_score += 10
        too_old = datetime.today() - timedelta(days=365)
        base_meeting = db.session.query(Visit.visit_date).distinct(Visit.visit_date).filter(Visit.title == "מפגש",Visit.visit_in_army==True,
                                Visit.visit_date > too_old, Visit.user_id == melaveId).group_by(Visit.visit_date).count()

        base_meeting_score = 0
        if base_meeting > 2:
            base_meeting_score += 10
        melave_score = base_meeting_score + Horim_meeting_score + professional_2monthly_score + yeshiva_monthly_score + \
                       cenes_yearly_score + \
                       group_meeting_score + personal_meet_score + call_score
        print(personal_meet_gap_avg)
        return melave_score,call_gap_avg,personal_meet_gap_avg

def mosad_Coordinators_score(mosadCoord_id):
    print(mosadCoord_id)
    institution_id = db.session.query( user1.institution_id).filter(user1.id==mosadCoord_id).first()
    all_Mosad_Melave = db.session.query(user1.id).filter(user1.role_id == "0",
                                                         user1.institution_id == institution_id[0]).all()

    if len(all_Mosad_Melave) == 0:
        return 100,0,0,0,0
    all_Mosad_Melaves_list = [r[0] for r in all_Mosad_Melave]
    total_avg_call=0
    total_avg_meet=0
    total_call_score_avg=0
    total_personal_meet_score_avg=0
    for melaveId in all_Mosad_Melaves_list:
        all_melave_Apprentices = db.session.query(Apprentice.id).filter(
            Apprentice.accompany_id == melaveId).all()
        old_call_Apprentice_count=0
        old_meet_Apprentice_count=0
        good_meet_Apprentice_count=0
        good_call_Apprentice_count=0
        for Apprentice1 in all_melave_Apprentices:
            visitEvent = db.session.query(Visit).filter(Visit.ent_reported == Apprentice1.id,Visit.title=="שיחה").order_by(Visit.visit_date.desc()).first()
            #handle no row
            gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
            if gap > 30 or visitEvent is None:
                old_call_Apprentice_count+=1
            visitEvent = db.session.query(Visit).filter(Visit.ent_reported == Apprentice1.id,Visit.title=="מפגש").order_by(Visit.visit_date.desc()).first()
            #handle no row
            gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
            if gap > 90 or visitEvent is None:
                old_meet_Apprentice_count+=1
            good_meet_Apprentice_count = (len(all_melave_Apprentices) - old_meet_Apprentice_count) / len(
                all_melave_Apprentices)
            good_call_Apprentice_count = (len(all_melave_Apprentices) - old_call_Apprentice_count) / len(
                all_melave_Apprentices)

        visitEvent = db.session.query(Visit).filter(Visit.user_id == melaveId,
                                                    Visit.title == "מפגש_קבוצתי").order_by(
            Visit.visit_date.desc()).first()
        # handle no row
        gap = (date.today() - visitEvent.visit_date).days if visitEvent is not None else 0
        groupMeet_score=10
        if gap > 30 or visitEvent is None:
            groupMeet_score = 0
        apprentice_interaction_Score=groupMeet_score+good_call_Apprentice_count*10+good_meet_Apprentice_count*10
        #compute avg
        visitcalls = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "שיחה", Visit.user_id == melaveId, Visit.visit_date > config.call_madad_date).order_by(
            Visit.visit_date).all()
        call_score, call_gap_avg = compute_visit_score(all_melave_Apprentices, visitcalls, 10, 21)
        total_avg_call+=call_gap_avg
        total_call_score_avg+=call_score
        visitmeetings = db.session.query(Visit.ent_reported, Visit.visit_date).filter(
            Visit.title == "מפגש", Visit.user_id == melaveId, Visit.visit_date > config.meet_madad_date).order_by(
            Visit.visit_date).all()
        personal_meet_score, personal_meet_gap_avg = compute_visit_score(all_melave_Apprentices, visitmeetings, 10, 90)
        total_avg_meet+=personal_meet_gap_avg
        total_personal_meet_score_avg+=personal_meet_score
    #divid by num of melave
    total_avg_meet=total_avg_meet/len(all_Mosad_Melaves_list)
    total_avg_call=total_avg_call/len(all_Mosad_Melaves_list)
    Mosad_coord_score=apprentice_interaction_Score

    #מצבר=30
    visit_matzbar_meetings = db.session.query(Visit.user_id, Visit.visit_date).filter(Visit.title == "מצבר").filter(
        Visit.user_id.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
    visit_matzbar_meetings_score,visitMatzbar_melave_avg=compute_visit_score(all_Mosad_Melave, visit_matzbar_meetings, 30, 90)
    Mosad_coord_score+=visit_matzbar_meetings_score
    #מפגש_מקצועי=10
    visit_mosad_professional_meetings = db.session.query(Visit.user_id, Visit.visit_date).filter(Visit.title == "מפגש_מקצועי").filter(
        Visit.user_id.in_(list(all_Mosad_Melaves_list))).order_by(Visit.visit_date).all()
    visit_mosad_professional_meetings_score,visitprofessionalMeet_melave_avg=compute_visit_score(all_Mosad_Melave, visit_mosad_professional_meetings, 30, 90)
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
            Visit.user_id).filter(Visit.title == "ישיבת_מלוים", Visit.user_id == mosadCoord_id,
                                  Visit.visit_date > too_old).all()
        if visit_allMelavim_monthly_meetings:
            Mosad_coord_score += 10
            Mosad_coord_score+=5*len(visit_allMelavim_monthly_meetings)/len(all_Mosad_Melave) if len(all_Mosad_Melave)!=0 else 0
    #עשייה_לבוגרים=5
    too_old = datetime.today() - timedelta(days=365)
    visit_did_for_apprentice = db.session.query(Visit.user_id,
                                                     ).filter(Visit.title == "עשייה_לבוגרים", Visit.user_id == mosadCoord_id,
                              Visit.visit_date > too_old).all()
    if len(visit_did_for_apprentice)>=3:
        Mosad_coord_score += 5
    #הזנת_מחזור_חדש=10
    too_old = datetime.today() - timedelta(days=365)
    visit_Hazana_new_THsession = db.session.query(Visit.user_id,
                                                     func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.user_id).filter(Visit.title == "הזנת_מחזור_חדש", Visit.user_id == mosadCoord_id,
                              Visit.visit_date > too_old).all()
    if len(visit_Hazana_new_THsession)>=1:
        Mosad_coord_score += 10

    return Mosad_coord_score,visitprofessionalMeet_melave_avg,visitMatzbar_melave_avg,total_avg_call,total_avg_meet

def eshcol_Coordinators_score(eshcolCoord_id):
    print("eshcolCoord_id",eshcolCoord_id)
    eshcol = db.session.query( user1.eshcol).filter(user1.id==eshcolCoord_id).first()[0]
    all_eshcol_mosadCoord = db.session.query(user1.id).filter(user1.role_id == "1",
                                                         user1.eshcol == eshcol).all()
    all_eshcol_apprentices = db.session.query(Apprentice.id).filter(
                                                         Apprentice.eshcol == eshcol).all()
    if len(all_eshcol_mosadCoord) == 0:
        return 100,0
    all_eshcol_mosadCoord_list = [r[0] for r in all_eshcol_mosadCoord]
    total_eshcol_mosad_gap=0
    for mosadCoordId in all_eshcol_mosadCoord_list:
        visitEvent = db.session.query(Visit).filter(Visit.user_id == mosadCoordId,Visit.title=="ישיבת_מוסד_אשכול" ,Visit.visit_date>config.eshcolMosadMeet_madad_date).all()
        if visitEvent ==[]:
            continue
        mosadCoordId_gap=0
        for vis in visitEvent:
            gap = (date.today() - vis.visit_date).days
            mosadCoordId_gap+=gap
        total_eshcol_mosad_gap+=mosadCoordId_gap/len(visitEvent)
    total_eshcol_mosad_gap=total_eshcol_mosad_gap/len(all_eshcol_mosadCoord)
    if total_eshcol_mosad_gap<=30:
        total_eshcol_mosad_score=60
    else:
        total_eshcol_mosad_score=0

    tohnit_yeshiva = db.session.query(Visit.user_id,
                                             func.max(Visit.visit_date).label("visit_date")).group_by(
        Visit.user_id).filter(Visit.title == "מפגש_מקצועי", Visit.user_id == eshcolCoord_id).first()
    gap = (date.today() - tohnit_yeshiva.visit_date).days if tohnit_yeshiva is not None else 100
    tohnit_yeshiva_score = 0
    if gap < 30:
        tohnit_yeshiva_score += 40

    Apprentice_ids_forgoten = [r[0] for r in all_eshcol_apprentices]
    too_old = datetime.today() - timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.ent_reported).filter(
                                                                 Apprentice.id == Visit.ent_reported,
                                                                 eshcol == Apprentice.eshcol,
                                                                 Visit.title == "שיחה",
                                                                 Visit.visit_date > too_old).all()
    for i in Oldvisitcalls:
        if i[0] in Apprentice_ids_forgoten:
            Apprentice_ids_forgoten.remove(i[0])
    eshcolCoord_score=tohnit_yeshiva_score+total_eshcol_mosad_score
    return eshcolCoord_score,total_eshcol_mosad_gap






