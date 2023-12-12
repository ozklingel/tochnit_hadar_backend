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