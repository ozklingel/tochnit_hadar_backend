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
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(Visit.apprentice_id,Visit.visit_date).filter(Visit.title =="שיחה" ,Visit.visit_date<too_old).all()
    forgotenApprenticCount=0
    forgotenApprenticeList={}
    print(Oldvisitcalls)
    if Oldvisitcalls:
        for ent in Oldvisitcalls:
            apprenticeEnt = db.session.query(Apprentice.institution_id).filter(Apprentice.id == ent.apprentice_id).first()
            forgotenApprenticCount+=1
            if apprenticeEnt.institution_id not in forgotenApprenticeList:
                forgotenApprenticeList[apprenticeEnt.institution_id] =0
            forgotenApprenticeList[apprenticeEnt.institution_id]+=1
        InstitutionList = db.session.query(Institution.id,Institution.name).all()
        print(forgotenApprenticeList)
        print(InstitutionList)
        for ent in InstitutionList:
            if ent[0] in forgotenApprenticeList:
                forgotenApprenticeList[ent[1]] = forgotenApprenticeList[ent[0]]
                del forgotenApprenticeList[ent[0]]
        print("forgotenApprenticeList:" ,forgotenApprenticeList)
        return jsonify({
        'forgotenApprenticCount': forgotenApprenticCount,
        'forgotenApprenticeList':forgotenApprenticeList
                   }), HTTPStatus.OK
    else:
        return jsonify({
        'result': "error:no result",
                   }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingCalleApprentice", methods=['GET'])
def missingCalleApprentice():
    all_Apprentices = db.session.query(Apprentice.id,Institution.name).filter(Apprentice.institution_id==Institution.id).all()
    # update apprentices call
    visitcalls = db.session.query(Visit.apprentice_id,func.max(Visit.visit_date).label("visit_date"),Institution.name).filter(Apprentice.id==Visit.apprentice_id,Institution.id==Apprentice.institution_id,Visit.title == "שיחה").group_by(Visit.apprentice_id,Institution.name).all()
    print(visitcalls)
    ids=[r[0] for r in visitcalls]
    #handle no record
    for ent in all_Apprentices:
        if ent.id not in ids:
            ids.append(ent[0])
    counts = dict()
    for i in visitcalls:
        counts[i[2]] = counts.get(i[2], 0) + 1
    print(counts)
    return jsonify({
        'missingCalleApprentice_count': counts,

    }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingMeetingApprentice", methods=['GET'])
def missingMeetingApprentice():
    all_Apprentices = db.session.query(Apprentice.id, Institution.name).filter(
        Apprentice.institution_id == Institution.id).all()
    # update apprentices call
    visitcalls = db.session.query(Visit.apprentice_id, func.max(Visit.visit_date).label("visit_date"),
                                  Institution.name).filter(Apprentice.id == Visit.apprentice_id,
                                                           Institution.id == Apprentice.institution_id,
                                                           Visit.title == "מפגש").group_by(Visit.apprentice_id,
                                                                                           Institution.name).all()
    print(visitcalls)
    ids = [r[0] for r in visitcalls]
    # handle no record
    for ent in all_Apprentices:
        if ent.id not in ids:
            ids.append(ent[0])
    counts = dict()
    for i in visitcalls:
        counts[i[2]] = counts.get(i[2], 0) + 1
    print(counts)
    return jsonify({
        'missingCalleApprentice_count': counts,

    }), HTTPStatus.OK

@madadim_form_blueprint.route("/forgotenApprentices", methods=['GET'])
def forgotenApprentice():
    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    Oldvisitcalls = db.session.query(Visit.apprentice_id, Visit.visit_date).filter(Visit.title == "שיחה",
                                                                                   Visit.visit_date < too_old).all()
    forgotenApprenticCount = 0
    forgotenApprenticeList = {}
    print(Oldvisitcalls)
    if Oldvisitcalls:
        for ent in Oldvisitcalls:
            apprenticeEnt = db.session.query(Apprentice.institution_id).filter(
                Apprentice.id == ent.apprentice_id).first()
            forgotenApprenticCount += 1
            if apprenticeEnt.institution_id not in forgotenApprenticeList:
                forgotenApprenticeList[apprenticeEnt.institution_id] = 0
            forgotenApprenticeList[apprenticeEnt.institution_id] += 1
        InstitutionList = db.session.query(Institution.id, Institution.name).all()
        print(forgotenApprenticeList)
        print(InstitutionList)
        for ent in InstitutionList:
            if ent[0] in forgotenApprenticeList:
                forgotenApprenticeList[ent[1]] = forgotenApprenticeList[ent[0]]
                del forgotenApprenticeList[ent[0]]
        print("forgotenApprenticeList:", forgotenApprenticeList)
        return jsonify({
            'forgotenApprenticCount': forgotenApprenticCount,
            'forgotenApprenticeList': forgotenApprenticeList
        }), HTTPStatus.OK
    else:
        return jsonify({
            'result': "error:no result",
        }), HTTPStatus.OK

@madadim_form_blueprint.route("/missingMeetingApprentice_Mosad", methods=['GET'])
def missingMeetingApprentice_Mosad():
    institution = request.args.get("institutionId")
    print(institution)
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(Visit,Apprentice).filter(Visit.apprentice_id==Apprentice.id,Visit.title == "מפגש",
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
    ApprenticeCount = db.session.query(func.count(Apprentice.id)).filter(Apprentice.accompany_id == melaveId).all()
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
                                                                 Visit.visit_date < too_old).all()
    print(Oldvisitcalls[0][0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    Oldvisitmeetings = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "מפגש",
                                                                 Visit.visit_date < too_old).all()
    print(Oldvisitmeetings[0][0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitSadna = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "סדנא",
                                                                 Visit.visit_date < too_old).all()
    print(OldvisitSadna[0][0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitCenes = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "כנס",
                                                                 Visit.visit_date < too_old).all()
    print(OldvisitCenes[0][0])

    visitHorim = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "הורים").all()
    print(visitHorim[0][0])


    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitmeetingsBasis = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "מפגש",Visit.visit_in_army==True,
                                                                 Visit.visit_date < too_old).all()
    print(OldvisitmeetingsBasis[0][0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    forgotenApprentice = db.session.query(Visit.apprentice_id).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
                                                                  Visit.visit_date < too_old).all()
    forgotenApprenticeCount=len(forgotenApprentice)
    forgotenApprentice_full_details=[]
    for ent in forgotenApprentice:
        forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.id==ent[0],Apprentice.institution_id==Institution.id).first()


    return jsonify({
        "numOfApprentice":ApprenticeCount[0][0],
        'Oldvisitmeetings': Oldvisitmeetings[0][0],
        'Oldvisitcalls': Oldvisitcalls[0][0],
        'OldvisitSadna': OldvisitSadna[0][0],
        'OldvisitCenes': OldvisitCenes[0][0],
        'visitHorim': visitHorim[0][0],
        'forgotenApprenticeCount': forgotenApprenticeCount,
        'forgotenApprentice_full_details':   [tuple(row) for row in forgotenApprentice_full_details]
,

        'OldvisitmeetingsBasis': OldvisitmeetingsBasis[0][0],

    }), HTTPStatus.OK


@madadim_form_blueprint.route("/mosadCoordinator", methods=['GET'])
def getMosadCoordinatorMadadim():
    mosadCoordinator = request.args.get("mosadCoordinator")[3:]
    print(mosadCoordinator)
    institutionId = db.session.query(user1.institution_id).filter(user1.id == mosadCoordinator).first()
    totalMelaveCount = db.session.query(func.count(user1.id)).filter(user1.institution_id == institutionId[0]).all()

    too_old_sadnaValue = 180
    OldvisitSadna = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "סדנא",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_sadnaCounter=0
    for ent in OldvisitSadna:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_sadnaValue:
            too_old_sadnaCounter=+1
    avgSadnaGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_SpiritMeetingValue = 180
    OldvisitSpiritMeeting = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "מצבר",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_SpiritMeetingCounter=0
    for ent in OldvisitSpiritMeeting:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_SpiritMeetingValue:
            too_old_SpiritMeetingCounter=+1
    avgSpiritMeetingGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_CallMelavimValue = 45
    OldvisitCallMelavim = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "שיחה",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_CallMelavimCounter=0
    for ent in OldvisitCallMelavim:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_CallMelavimValue:
            too_old_CallMelavimCounter=+1
    avgCallMelavimGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_MeetingMelavimValue = 60
    OldvisitMeetingMelavim = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "מפגש",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_MeetingMelavimCounter=0
    for ent in OldvisitMeetingMelavim:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_MeetingMelavimValue:
            too_old_MeetingMelavimCounter=+1
    avgMeetingMelavimGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_HaburaMelavimValue = 45
    OldvisitHaburaMelavim = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "חבורה",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_HaburaMelavimCounter=0
    for ent in OldvisitHaburaMelavim:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_HaburaMelavimValue:
            too_old_HaburaMelavimCounter=+1
    avgHaburaMelavimGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_enterMahzorValue = 365
    OldvisitenterMahzor = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "הזנת_מחזור",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_enterMahzorCounter=0
    for ent in OldvisitenterMahzor:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_enterMahzorValue:
            too_old_enterMahzorCounter=+1
    avgenterMahzorGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_ForApprenticesActionValue = 180
    OldvisitForApprenticesAction = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "עשיה_לבוגרים",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_ForApprenticesActionCounter=0
    for ent in OldvisitForApprenticesAction:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_ForApprenticesActionValue:
            too_old_ForApprenticesActionCounter=+1
    avgForApprenticesActionGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_MeetMelaveValue = 45
    OldvisitMeetMelave = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "פגישת_מלווה",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_MeetMelaveCounter=0
    for ent in OldvisitMeetMelave:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_MeetMelaveValue:
            too_old_MeetMelaveCounter=+1
    avgMeetMelaveGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old_MonthlyYeshivaValue = 30
    OldvisitMonthlyYeshiva = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "ישיבה_חודשית",user1.institution_id==institutionId[0]).all()
    gapList=[]
    too_old_MonthlyYeshivaCounter=0
    for ent in OldvisitMonthlyYeshiva:
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_MonthlyYeshivaValue:
            too_old_MonthlyYeshivaCounter=+1
    avgMonthlyYeshivaGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old = datetime.datetime.today() - datetime.timedelta(days=100)

    forgotenApprentice = db.session.query(Visit.apprentice_id).filter(Visit.user_id==user1.id,Visit.title == "שיחה",
                                                                  Visit.visit_date < too_old,user1.institution_id==institutionId[0]).all()
    forgotenApprenticeCount=len(forgotenApprentice)
    forgotenApprentice_full_details=[]
    for ent in forgotenApprentice:
        forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.id==ent[0],Apprentice.institution_id==Institution.id).first()

    eshcol_ApprenticeCount = db.session.query(Apprentice.id,user1).filter(Apprentice.accompany_id==user1.id,user1.cluster_id==institutionId[0]).all()
    print("eshcol_ApprenticeCount",len(eshcol_ApprenticeCount))
    return jsonify({
        'totalMelaveCount': totalMelaveCount[0][0],
        'forgotenApprenticeCount': forgotenApprenticeCount,
        'forgotenApprentice_full_details': [tuple(row) for row in forgotenApprentice_full_details],
        'avgMonthlyYeshivaGap': avgMonthlyYeshivaGap,
        'approved_MonthlyYeshiva_counter': totalMelaveCount[0][0] - too_old_MonthlyYeshivaCounter,
        'too_old_MonthlyYeshivaCounter': too_old_MonthlyYeshivaCounter,
        'too_old_MonthlyYeshivaValue': too_old_MonthlyYeshivaValue,

        'avgMeetMelaveGap': avgMeetMelaveGap,
        'approved_MeetMelave_counter': totalMelaveCount[0][0] - too_old_MeetMelaveCounter,
        'too_old_MeetMelaveCounter': too_old_MeetMelaveCounter,
        'too_old_MeetMelaveValue': too_old_MeetMelaveValue,

        'avgForApprenticesActionGap': avgForApprenticesActionGap,
        'approved_ForApprenticesAction_counter': totalMelaveCount[0][0] - too_old_enterMahzorCounter,
        'too_old_ForApprenticesActionCounter': too_old_ForApprenticesActionCounter,
        'too_old_ForApprenticesActionValue': too_old_ForApprenticesActionValue,

        'avgenterMahzorGap': avgenterMahzorGap,
        'approved_enterMahzor_counter': totalMelaveCount[0][0] - too_old_enterMahzorCounter,
        'too_old_enterMahzorCounter': too_old_enterMahzorCounter,
        'too_old_enterMahzorValue': too_old_enterMahzorValue,

        'avgHaburaMelavimGap': avgHaburaMelavimGap,
        'approved_HaburaMelavim_counter': totalMelaveCount[0][0] - too_old_HaburaMelavimCounter,
        'too_old_HaburaMelavimCounter': too_old_HaburaMelavimCounter,
        'too_old_HaburaMelavimValue': too_old_HaburaMelavimValue,

        'avgMeetingMelavimGap': avgMeetingMelavimGap,
        'approved_MeetingMelavim_counter': totalMelaveCount[0][0] - too_old_MeetingMelavimCounter,
        'too_old_MeetingMelavimCounter': too_old_MeetingMelavimCounter,
        'too_old_MeetingMelavimValue': too_old_MeetingMelavimValue,

        'avgCallMelavimGap': avgCallMelavimGap,
        'approved_CallMelavim_counter': totalMelaveCount[0][0] - too_old_CallMelavimCounter,
        'too_old_CallMelavimCounter': too_old_CallMelavimCounter,
        'too_old_CallMelavimValue': too_old_CallMelavimValue,

        'avgSpiritMeetingGap': avgSpiritMeetingGap,
        'approved_SpiritMeeting_counter': totalMelaveCount[0][0] - too_old_SpiritMeetingCounter,
        'too_old_SpiritMeetingCounter': too_old_SpiritMeetingCounter,
        'too_old_SpiritMeetingValue': too_old_SpiritMeetingValue,

        'avgSadnaGap': avgSadnaGap,
        'approved_sadna_counter': totalMelaveCount[0][0]-too_old_sadnaCounter,
        'too_old_sadna_counter': too_old_sadnaCounter,
        'too_old_sadnaValue': too_old_sadnaValue,
    }), HTTPStatus.OK

@madadim_form_blueprint.route("/eshcolCoordinator", methods=['GET'])
def getEshcolCoordinatorMadadim():
    eshcolCoordinatorId = request.args.get("eshcolCoordinator")[3:]
    print(eshcolCoordinatorId)
    #get the Eshcol id
    eshcol_id = db.session.query(user1.cluster_id).filter(user1.id == eshcolCoordinatorId).first()
    print("eshcol_id",eshcol_id)
    print(type(user1.role_id))
    print(type(eshcol_id[0]))
    # total MosadCoordinator Count for this eshcol
    totalMosadCoordinatorCount = db.session.query(func.count(user1.id)).filter(user1.cluster_id == eshcol_id[0],str(user1.role_id)=="2").all()
    EshcolMelvin = db.session.query(user1.id).filter(user1.cluster_id == eshcol_id[0],str(user1.role_id)=="1").all()
    totalApprenticeCount=0
    for ent  in EshcolMelvin :
        apprenticeCount = db.session.query(func.count(Apprentice.id)).filter(Apprentice.accompany_id == ent[0]
                                                                                   ).all()
        totalApprenticeCount+=apprenticeCount[0]

    too_old_MonthlyYeshivaValue = 30
    #ישיבה עם רכזי מוסד
    OldvisitMonthlyYeshiva = db.session.query(Visit.visit_date).filter(Visit.user_id==user1.id,Visit.title == "ישיבה_חודשית_רכז",user1.cluster_id==eshcol_id[0],str(user1.role_id)=="2").all()
    gapList=[]
    too_old_MonthlyYeshivaCounter=0
    num_of_MOsadCoordintor=0
    for ent in OldvisitMonthlyYeshiva:
        num_of_MOsadCoordintor+=1
        vIsDate=ent.visit_date
        now=datetime.date.today()
        gap = (now-vIsDate).days if vIsDate is not None else 0
        gapList.append(gap)
        if gap>too_old_MonthlyYeshivaValue:
            too_old_MonthlyYeshivaCounter=+1
    avgMonthlyYeshivaGap=sum(gapList) / len(gapList) if len(gapList)!=0 else 0

    too_old = datetime.datetime.today() - datetime.timedelta(days=30)
    OldvisitRoshTohnit = db.session.query(func.count(Visit.title)).filter(Visit.user_id==eshcolCoordinatorId,Visit.title == "מפגש_חודשית_אחראי_תוכנית",
                                                                 Visit.visit_date < too_old).first()
    print("OldvisitRoshTohnit",OldvisitRoshTohnit[0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    forgotenApprentice = db.session.query(Visit.apprentice_id).filter(Visit.user_id==user1.id,Visit.title == "שיחה",
                                                                  Visit.visit_date < too_old,user1.cluster_id==eshcol_id[0]).all()
    forgotenApprenticeCount=len(forgotenApprentice)
    forgotenApprentice_full_details=[]
    for ent in forgotenApprentice:
        forgotenApprentice_full_details = db.session.query(Institution.name,Apprentice.name,Apprentice.last_name,Apprentice.base_address,Apprentice.army_role,Apprentice.unit_name,Apprentice.marriage_status,Apprentice.serve_type,Apprentice.hadar_plan_session).filter(Apprentice.id==ent[0],Apprentice.institution_id==Institution.id).first()

    eshcol_ApprenticeCount = db.session.query(Apprentice.id,user1).filter(Apprentice.accompany_id==user1.id,user1.cluster_id==eshcol_id[0]).all()
    print("eshcol_ApprenticeCount",len(eshcol_ApprenticeCount))
    return jsonify({
        'totalMosadCoordinatorCount': totalMosadCoordinatorCount[0][0],
        'too_old_MonthlyYeshivaCounter': too_old_MonthlyYeshivaCounter,
        'OldvisitRoshTohnit': OldvisitRoshTohnit[0],
        'totalApprenticeCount': totalApprenticeCount,
        'forgotenApprenticeCount': forgotenApprenticeCount,
        'num_of_MOsadCoordintor':num_of_MOsadCoordintor,
        'avgMonthlyYeshivaGap': avgMonthlyYeshivaGap,
        'eshcol_ApprenticeCount': len(eshcol_ApprenticeCount),
        'forgotenApprentice_full_details':    [tuple(row) for row in forgotenApprentice_full_details]
,

    }), HTTPStatus.OK






