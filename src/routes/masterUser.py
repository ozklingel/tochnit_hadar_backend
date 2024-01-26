import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from openpyxl.reader.excel import load_workbook
from sqlalchemy import func, and_

import config
from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.contact_form_model import ContactForm
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.gift import  gift
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')

@master_user_form_blueprint.route("/search_entities", methods=['GET'])
def search_entities():
    isMosad_coord = request.args.get("isMosad_coord")
    isEshcol_coord = request.args.get("isEshcol_coord")
    isMelave= request.args.get("isMelave")
    isApprentice = request.args.get("isApprentice")
    institution_name = request.args.get("institution_name")
    thpreiodList = request.args.get("thpreiod")
    institution_mahzor = request.args.get("institution_mahzor")
    eshcol = request.args.get("eshcol")
    marriage_status = request.args.get("marriage_status")
    base_address = request.args.get("base_address")
    city_name = request.args.get("city_name")+" " if request.args.get("city_name") is not None else None
    region = request.args.get("region")
    entityType=[]
    #query user table
    query = None
    if isMelave=="True":
        entityType.append("0")
    if isMosad_coord=="True":
        entityType.append("1")
    if isEshcol_coord=="True":
        entityType.append("2")
    if len(entityType):
        query = db.session.query(user1.id)
        query = query.filter(user1.role_id.in_(entityType))
        if institution_name:
            query = query.filter(user1.institution_id==Institution.id,Institution.name==institution_name)
        if eshcol:
            query = query.filter_by(eshcol=eshcol)
        if city_name:
            query = query.filter(City.id==user1.city_id,city_name==City.name)

    res1=None
    if query:
        res1 = query.all()
    query=None
    #query apprentice table
    if isApprentice=="True":
        query = db.session.query(Apprentice.id)
        if thpreiodList:
            print("thpreiodList",thpreiodList)
            query = query.filter(Apprentice.hadar_plan_session.in_(list(thpreiodList)))
            #query = query.filter_by(thpreiod=thpreiod)
        if institution_mahzor:
            query = query.filter_by(institution_mahzor=institution_mahzor)
        if marriage_status:
            query = query.filter_by(marriage_status=marriage_status)
        if base_address:
            query = query.filter_by(base_address=base_address)
        if institution_name:
            query = query.filter(Apprentice.institution_id==Institution.id,Institution.name==institution_name)
        if eshcol:
            query = query.filter_by(eshcol=eshcol)
        if city_name:
            #city_idDB = db.session.query(City.id).filter(City.name == city_name).first()
            print("city_idDB",city_name)
            #if city_idDB:
            query = query.filter(City.id==Apprentice.city_id,city_name==City.name)
    res2=None
    if query:
        res2 = query.all()
    print("app",res2)
    print("user",res1)
    appren_details=[]
    usedtails=[]
    for apprenEnt in res2:
        appren_details.append(db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name,Cluster.name,Institution.name,Apprentice.unit_name,Apprentice.hadar_plan_session,Apprentice.army_role,Apprentice.base_address,Apprentice.serve_type,Apprentice.marriage_status,Apprentice.institution_mahzor).filter(apprenEnt[0]==Apprentice.id,user1.cluster_id==Cluster.id,Institution.id==user1.institution_id).first())
    for userEnt in res1:
        usedtails.append(db.session.query(user1.id,user1.role_id,user1.name,user1.last_name,Cluster.name,Institution.name).filter(user1.id==userEnt[0],user1.cluster_id==Cluster.id,Institution.id==user1.institution_id).first())

    return jsonify({"users":
       [ {"id" :str(row[0]),"role_id":row[1],"name":row[2]
          ,"last_name":row[3],"Cluster":row[4]
          ,"Institution":row[5]} for row in [tuple(row) for row in usedtails]] if usedtails is not None else [],
                    "apprentices":
                        [{"id": str(row[0]),  "name": row[1]
                             , "last_name": row[2], "Cluster": row[3]
                             , "Institution": row[4], "unit_name": row[5], "base_address": row[6]
                          , "army_role": row[7], "hadar_plan_session": row[8]
                          , "institution_mahzor": row[9], "marriage_status": row[10]
                          , "serve_type": row[11]} for row in
                         [tuple(row) for row in appren_details]] if appren_details is not None else [],
                    }
    ), HTTPStatus.OK




@master_user_form_blueprint.route("/add_apprentice_excel", methods=['put'])
def add_apprentice_excel():
    from openpyxl import workbook
    path = '/home/ubuntu/flaskapp/Book1.xlsx'
    wb = load_workbook(filename=path)
    ws = wb.get_sheet_by_name('Sheet1')
    for row in ws.iter_rows(min_row=2):
        first_name = row[0].value
        last_name = row[1].value
        phone = row[3].value
        institution_name = row[2].value
        print(first_name)
        print(phone)

        try:
            institution_id = db.session.query(Institution).filter(
                Institution.name == str(institution_name)).first()
            Apprentice1 = Apprentice(
                id=int(str(phone)[1:]),
                name=first_name,
                last_name=last_name,
                phone=str(phone),
                institution_id=institution_id,
            )
            db.session.add(Apprentice1)
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    db.session.commit()

    return jsonify({'result': 'success'}), HTTPStatus.OK

@master_user_form_blueprint.route('/deleteEnt', methods=['PUT'])
def deleteEnt():
       data=request.json
       try:
           typeOfSet = data['typeOfSet']

           print(typeOfSet)
           updatedEnt=None
           if typeOfSet=="mosad":
               entityId = str(data['entityId'])
               res = db.session.query(Institution).filter(Institution.id == entityId).delete()
           if typeOfSet == "user":
               entityId = str(data['entityId'])[3:]
               res = db.session.query(ContactForm).filter(ContactForm.created_for_id == entityId,).delete()
               res = db.session.query(ContactForm).filter(ContactForm.created_by_id == entityId,).delete()

               res = db.session.query(user1).filter(user1.id == entityId).delete()
           if typeOfSet == "apprentice":
               entityId = str(data['entityId'])[3:]
               res = db.session.query(notifications).filter(notifications.apprenticeid == entityId,).delete()
               res = db.session.query(Visit).filter(Visit.apprentice_id == entityId,).delete()
               res = db.session.query(Apprentice).filter(Apprentice.id == entityId).delete()
           if typeOfSet == "gift":
               entityId = str(data['entityId'])
               res = db.session.query(gift).filter(gift.code == entityId).delete()
           db.session.commit()
           return jsonify({'result': 'sucess'}), HTTPStatus.OK
       except Exception as e:
           return jsonify({'result': 'error'+str(e)}), HTTPStatus.OK



@master_user_form_blueprint.route('/setSetting_madadim', methods=['post'])
def setSetting_madadim():
    data = request.json
    try:
        config.call_madad_date = data['call_madad_date']
        config.meet_madad_date = data['meet_madad_date']
        config.groupMeet_madad_date = data['groupMeet_madad_date']
        config.callHorim_madad_date = data['callHorim_madad_date']
        config.madadA_date = data['madadA_date']
        config.madadB_date = data['madadB_date']
        config.madadC_date = data['madadC_date']
        config.madadD_date = data['madadD_date']
    except Exception as e:
        return jsonify({'result': "fail-"+str(e)}), HTTPStatus.OK
    return jsonify({'result': 'success'}), HTTPStatus.OK


@master_user_form_blueprint.route('/getAllSetting_madadim', methods=['GET'])
def getNotificationSetting_form():

    return jsonify({"madadD_date":config.madadD_date,
                    "madadC_date":config.madadC_date
                    ,"madadB_date":config.madadB_date,
                    "madadA_date": config.madadA_date,
                    "callHorim_madad_date": config.callHorim_madad_date
                       , "callHorim_madad_date": config.callHorim_madad_date,
                    "groupMeet_madad_date": config.groupMeet_madad_date,
                    "call_madad_date": config.call_madad_date
                       , "meet_madad_date": config.meet_madad_date
                    }), HTTPStatus.OK

@master_user_form_blueprint.route("/add_apprentice_manual", methods=['post'])
def add_apprentice():
    data = request.json
    print(data)
    try:
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        institution_name = data['institution_name']
        accompany_id = data['accompany_id']
        birthday = data['birthday']
        city_name = data['city_name']
        maritalstatus= data['maritalstatus']
        marriage_date= data['marriage_date']
        unit_name= data['unit_name']
        serve_type= data['serve_type']#סדיר
        release_date= data['release_date']
        recruitment_date= data['recruitment_date']
        onlinestatus= data['onlinestatus']#אונלין?
        matsber= data['matsber']#מצב רוחני
        hadar_plan_session= data['hadar_plan_session']#מחזןר בהדר thperiod
        email= data['email']
        birthday= data['birthday']
        address= data['address']#רחוב ובית
        creationdate= data['creationdate']
        teudatzehut= data['teudatzehut']
        institution_mahzor= data['institution_mahzor']


        cluster_id=db.session.query(Cluster.id).filter(Cluster.name==city_name).first()
        CityId = db.session.query(City).filter(City.name==city_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        print(institution_id)
        Apprentice1 = Apprentice(
            id=int(phone[1:]),
            name=first_name,
            last_name=last_name,
            phone=phone,
            maritalstatus=birthday,
            marriage_date=birthday,
            unit_name=birthday,
            serve_type=birthday,
            release_date=birthday,
            recruitment_date=birthday,
            onlinestatus=birthday,
            matsber=birthday,
            hadar_plan_session=birthday,
            email=birthday,
            address=birthday,
            creationdate=birthday,
            teudatzehut=birthday,
            institution_mahzor=birthday,
            institution_id=institution_id.id,
            accompany_id=int(accompany_id[1:]),
            city_id=CityId.id,
            cluster_id=cluster_id.id,
            photo_path="https://www.gravatar.com/avatar"
        )
        db.session.add(Apprentice1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if Apprentice1:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK

@master_user_form_blueprint.route("/add_user_manual", methods=['post'])
def add_user_manual():
    data = request.json
    print(data)
    try:
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        institution_name = data['institution_name']
        city_name = data['city_name']
        role_id = data['role_id']
        cluster_id=db.session.query(Cluster.id).filter(Cluster.name==city_name).first()
        CityId = db.session.query(City).filter(City.name==city_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        print(institution_id)
        useEnt = user1(
            id=int(phone[1:]),
            name=first_name,
            last_name=last_name,
            role_id=role_id,
            #institution_id=institution_id.id,
            #city_id=CityId.id,
            #cluster_id=cluster_id.id,
            photo_path="https://www.gravatar.com/avatar"
        )
        db.session.add(useEnt)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if useEnt:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK

