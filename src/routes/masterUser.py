from http import HTTPStatus

from flask import Blueprint, request, jsonify
from openpyxl.reader.excel import load_workbook

import config
from app import db
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.contact_form_model import ContactForm
from src.models.gift import gift
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')

@master_user_form_blueprint.route("/add_apprentice_excel", methods=['put'])
def add_apprentice_excel():
    #/home/ubuntu/flaskapp/
    file = request.files['file']

    wb = load_workbook(file)
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        first_name = row[2].value
        last_name = str(row[0].value).split(" ")[0]
        phone = row[1].value
        city = row[3].value
        address = row[4].value
        serve_type = row[5].value
        institution_name = row[6].value
        contact1_first_name = row[7].value
        contact1_phone = row[8].value
        contact2_first_name = row[9].value
        contact2_phone = row[10].value
        hadar_plan_session = row[11].value
        teacher_grade_a = row[12].value
        teacher_grade_b = row[13].value
        contact1_email = row[15].value
        eshcol = row[14].value
        birthday_ivry = row[16].value
        marriage_status = row[17].value
        army_role = row[18].value#מפקד?
        unit_name = row[19].value#מפקד?
        teudatZehut = row[20].value#מפקד?
        birthday_loazi = row[21].value#מפקד?
        accompany_id = row[22].value#מפקד?
        militaryCompoundId=row[23].value
        print(city)
        CityId = db.session.query(City.id).filter(City.name==city).first()[0]
        print(CityId)

        try:
            institution_id = db.session.query(Institution.id).filter(Institution.name == str(institution_name)).first()
            Apprentice1 = Apprentice(
                id=phone,
                base_address=militaryCompoundId,
                institution_id=institution_id[0] if institution_id is not None else 0,
                address=address,
                serve_type=serve_type,
                name=first_name,
                last_name=last_name,
                phone=str(phone),
                army_role=army_role,
                marriage_status=marriage_status,
                contact1_email=contact1_email,
                teacher_grade_b=teacher_grade_b,
                teacher_grade_a=teacher_grade_a,
                hadar_plan_session=hadar_plan_session,
                contact2_phone=contact2_phone,
                contact2_first_name=contact2_first_name,
                contact1_phone=contact1_phone,
                contact1_first_name=contact1_first_name,
                teudatZehut=teudatZehut,
                birthday=birthday_loazi,
                unit_name=unit_name,
                eshcol=eshcol,
                accompany_id=accompany_id,

            )
            db.session.add(Apprentice1)
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.OK
    db.session.commit()

    return jsonify({'result': 'success'}), HTTPStatus.OK
@master_user_form_blueprint.route("/add_user_excel", methods=['put'])
def add_user_excel():
    #/home/ubuntu/flaskapp/
    #path = '/home/ubuntu/flaskapp/data/user_enter.xlsx'
    path = 'data/user_enter.xlsx'
    wb = load_workbook(filename=path)
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        name=str(row[0].value).split(" ")
        if row[2].value == "מלווה" :
            role=0
        elif row[2].value == "רכז" :
            role = 1
        elif row[2].value == "רכז אשכול":
            role = 2
        elif row[2].value == "אחראי תוכנית":
            role = 3
        first_name =name[0]
        last_name = name[1]
        institution_name = row[1].value
        phone = str(row[4].value).replace("-","")
        email = row[3].value
        eshcol = row[5].value
        try:
            institution_id = db.session.query(Institution.id).filter(
                Institution.name == str(institution_name)).first()
            print("institution_id",institution_id)
            user = user1(
                id=int(str(phone).replace("-","")),
                name=first_name,
                last_name=last_name,
                role_id=str(role),
                email=str(email),
                eshcol=eshcol,
                institution_id=institution_id.id,
            )
            db.session.add(user)
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.OK
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
               entityId = str(data['entityId'])
               res = db.session.query(ContactForm).filter(ContactForm.created_for_id == entityId,).delete()
               res = db.session.query(ContactForm).filter(ContactForm.created_by_id == entityId,).delete()
               res = db.session.query(notifications).filter(notifications.userid == entityId,).delete()

               res = db.session.query(user1).filter(user1.id == entityId).delete()
           if typeOfSet == "apprentice":
               entityId = str(data['entityId'])
               res = db.session.query(notifications).filter(notifications.apprenticeid == entityId,).delete()
               res = db.session.query(Visit).filter(Visit.ent_reported == entityId,).delete()
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
    try:
        return jsonify({"eshcolMosadMeet_madad_date":config.eshcolMosadMeet_madad_date,
                        "tochnitMeet_madad_date":config.tochnitMeet_madad_date
                        ,"doForBogrim_madad_date":config.doForBogrim_madad_date,
                        "matzbarmeet_madad_date": config.matzbarmeet_madad_date,
                        "professionalMeet_madad_date": config.professionalMeet_madad_date
                           , "callHorim_madad_date": config.callHorim_madad_date,
                        "groupMeet_madad_date": config.groupMeet_madad_date,
                        "meet_madad_date": config.meet_madad_date
                           , "call_madad_date": config.call_madad_date
                           , "cenes_report": config.cenes_report

                        }), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
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
        teudatzehut= data['teudatzehut']
        institution_mahzor= data['institution_mahzor']


        cluster_id=db.session.query(Cluster.id).filter(Cluster.name==city_name).first()
        CityId = db.session.query(City).filter(City.name==city_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        institution_id=institution_id[0] if institution_id is not None else 0
        print(institution_id)
        Apprentice1 = Apprentice(
            id=int(phone[1:]),
            name=first_name,
            last_name=last_name,
            phone=phone,
            marriage_status=maritalstatus,
            marriage_date=marriage_date,
            unit_name=unit_name,
            serve_type=serve_type,
            release_date=release_date,
            recruitment_date=recruitment_date,
            accompany_connect_status=onlinestatus,
            spirit_status=matsber,
            hadar_plan_session=hadar_plan_session,
            email=email,
            address=address,
            teudatZehut=teudatzehut,
            institution_mahzor=institution_mahzor,
            institution_id=institution_id,
            accompany_id=int(accompany_id[1:]),
            #city_id=CityId.id,
            #cluster_id=cluster_id.id,
            photo_path="https://www.gravatar.com/avatar",
            birthday=birthday
        )
        db.session.add(Apprentice1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.OK

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
        city_name = data['city_name'] if "?" not in data['city_name'] else "עלי"

        role_id = data['role_id']
        CityId = db.session.query(City).filter(City.name==city_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        institution_id=institution_id[0] if institution_id else 0
        print(institution_id)
        useEnt = user1(
            id=int(phone[1:]),
            name=first_name,
            last_name=last_name,
            role_id=role_id,
            institution_id=institution_id,
            city_id=CityId.id,
            cluster_id=CityId.cluster_id,
            photo_path="https://www.gravatar.com/avatar"
        )
        db.session.add(useEnt)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.OK

    if useEnt:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK

