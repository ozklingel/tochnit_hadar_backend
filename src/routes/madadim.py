import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from sqlalchemy import func

from app import db, red
from src.models.apprentice_model import Apprentice
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
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
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

@madadim_form_blueprint.route("/missingMeetingApprentice", methods=['GET'])
def missingMeetingApprentice():
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    Oldvisitcalls = db.session.query(Visit.apprentice_id, Visit.visit_date).filter(Visit.title == "מפגש",
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
    melaveId = request.args.get("melaveId")
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

    too_old = datetime.datetime.today() - datetime.timedelta(days=100)
    forgotenApprenticeCount = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "שיחה",
                                                                 Visit.visit_date < too_old).all()
    print(forgotenApprenticeCount[0][0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitmeetingsBasis = db.session.query(func.count(Visit.title)).filter(Visit.user_id==melaveId,Visit.title == "מפגש",Visit.visit_in_army==True,
                                                                 Visit.visit_date < too_old).all()
    print(OldvisitmeetingsBasis[0][0])

    return jsonify({
        "numOfApprentice":ApprenticeCount[0][0],
        'Oldvisitmeetings': Oldvisitmeetings[0][0],
        'Oldvisitcalls': Oldvisitcalls[0][0],
        'OldvisitSadna': OldvisitSadna[0][0],
        'OldvisitCenes': OldvisitCenes[0][0],
        'visitHorim': visitHorim[0][0],
        'forgotenApprenticeCount': forgotenApprenticeCount[0][0],
        'OldvisitmeetingsBasis': OldvisitmeetingsBasis[0][0],

    }), HTTPStatus.OK


@madadim_form_blueprint.route("/mosadCoordinator", methods=['GET'])
def getMosadCoordinatorMadadim():
    mosadCoordinator = request.args.get("mosadCoordinator")
    print(mosadCoordinator)
    institutionId = db.session.query(user1.institution_id).filter(user1.id == mosadCoordinator).first()
    print(institutionId[0])
    totalMelaveCount = db.session.query(func.count(user1.id)).filter(user1.institution_id == institutionId[0]).all()
    print(totalMelaveCount[0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitSadna = db.session.query(func.count(Visit.id)).filter(Visit.user_id==user1.id,Visit.title == "סדנא",Visit.visit_date < too_old,user1.institution_id==institutionId[0]).all()
    print(OldvisitSadna[0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=180)
    OldvisitSpiritMeeting = db.session.query(func.count(Visit.id)).filter(Visit.user_id==user1.id,Visit.title == "מצבר",Visit.visit_date < too_old,user1.institution_id==institutionId[0]).all()
    print("OldvisitSpiritMeeting:" ,OldvisitSpiritMeeting[0])

    ###
    too_old = datetime.datetime.today() - datetime.timedelta(days=45)
    OldvisitCallMelavim = db.session.query(func.count(Visit.id)).filter(Visit.user_id==user1.id,user1.institution_id == institutionId[0],Visit.title=='שיחה' ,Visit.visit_date < too_old).all()
    print("OldvisitCallMelavim:" ,OldvisitCallMelavim[0])

    too_old = datetime.datetime.today() - datetime.timedelta(days=60)
    OldvisitMeetingMelavim = db.session.query(func.count(Visit.id)).filter(Visit.user_id==user1.id,user1.institution_id == institutionId[0],Visit.title=='מפגש' ,Visit.visit_date < too_old).all()
    print("OldvisitMeetingMelavim:" ,OldvisitMeetingMelavim[0])

    return jsonify({
        'totalMelaveCount': totalMelaveCount[0][0],
        'OldvisitSadna': OldvisitSadna[0][0],
        'OldvisitSpiritMeeting': OldvisitSpiritMeeting[0][0],
        'OldvisitMelavim': OldvisitCallMelavim[0][0],
        'OldvisitMeetingMelavim': OldvisitMeetingMelavim[0][0],

    }), HTTPStatus.OK