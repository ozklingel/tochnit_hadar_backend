
import uuid
import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from openpyxl.reader.excel import load_workbook

from app import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.visit_model import Visit

apprentice_Profile_form_blueprint = Blueprint('apprentice_Profile_form', __name__, url_prefix='/apprentice_Profile_form')
@apprentice_Profile_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        apprenticetId = data['apprenticetId']
        print(apprenticetId)
        res = db.session.query(notifications).filter(notifications.apprenticeid == apprenticetId, ).delete()
        res = db.session.query(Visit).filter(Visit.ent_reported == apprenticetId, ).delete()
        res = db.session.query(Apprentice).filter(Apprentice.id == apprenticetId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.OK
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@apprentice_Profile_form_blueprint.route("/update", methods=['put'])
def updateTask():
    try:
        # get tasksAndEvents
        apprenticetId = request.args.get("apprenticetId")
        print(apprenticetId)
        data = request.json
        updatedEnt = Apprentice.query.get(apprenticetId)
        for key in data:
            setattr(updatedEnt, key, data[key])
        db.session.commit()
        if updatedEnt:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@apprentice_Profile_form_blueprint.route("/add_apprentice_manual", methods=['post'])
def add_apprentice():
    data = request.json
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
        militarycompound_name= data['militarycompound_name']

        militarycompoundid = db.session.query(Base).filter(Base.name==militarycompound_name).first()
        CityId = db.session.query(City).filter(City.name==city_name).first()
        institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        institution_id=institution_id[0] if institution_id is not None else 0
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
            base_address=str(militarycompoundid.id),
            city_id=CityId.id,
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

@apprentice_Profile_form_blueprint.route("/add_apprentice_excel", methods=['put'])
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