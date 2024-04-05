from http import HTTPStatus

import requests
from flask import Blueprint, request, jsonify
from openpyxl.reader.excel import load_workbook

import config
from app import db
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.contact_form_model import ContactForm
from src.models.gift import gift
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')






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
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def addApperntice(wb):
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        first_name = row[2].value.strip()
        last_name = str(row[0].value).split(" ")[1]
        phone = row[1].value
        city = row[22].value.strip()
        address = row[4].value.strip()
        serve_type = row[5].value.strip()
        institution_name = row[6].value.strip()
        contact1_first_name = row[7].value.strip()
        contact1_phone = row[8].value.strip()
        contact2_first_name = row[9].value.strip()
        contact2_phone = row[10].value.strip()
        hadar_plan_session = row[11].value.strip()
        teacher_grade_a = row[12].value.strip() if row[12].value else ""
        teacher_grade_b = row[13].value.strip()
        contact1_email = row[15].value.strip()
        eshcol = row[14].value.strip()
        birthday_ivry = row[16].value
        marriage_status = row[17].value.strip()
        army_role = row[18].value.strip()  # מפקד?
        unit_name = row[19].value.strip()  # מפקד?
        teudatZehut = row[20].value.strip()  # מפקד?
        birthday_loazi = row[21].value.strip()  # מפקד?
        accompany_id = row[3].value  # מפקד?
        base_name = row[23].value.strip()
        contact3_first_name = row[24].value.strip()
        contact3_last_name = row[25].value.strip()
        contact3_email = row[26].value.strip()
        contact3_relation = row[27].value.strip()
        contact3_phone = row[28].value
        mail = row[29].value.strip()
        release_date = row[30].value.strip()
        recruitment_date = row[31].value.strip()
        marriage_date = row[32].value.strip()
        spirit_status = row[33].value
        institution_mahzor = row[34].value.strip()
        CityId = db.session.query(City.id).filter(City.name == city).first()[0]
        militaryCompoundId = db.session.query(Base.id).filter(Base.name == base_name).first()[0]

        # print(militaryCompoundId)

        try:
            institution_id = db.session.query(Institution.id).filter(Institution.name == str(institution_name)).first()
            Apprentice1 = Apprentice(
                city_id=CityId,
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
                contact3_relation=contact3_relation,
                contact3_email=contact3_email,
                contact3_last_name=contact3_last_name,
                contact3_first_name=contact3_first_name,
                contact3_phone=contact3_phone,
                email=mail,
                release_date=release_date,
                recruitment_date=recruitment_date,
                marriage_date=marriage_date,
                spirit_status=spirit_status,
                institution_mahzor=institution_mahzor

            )
            db.session.add(Apprentice1)
            db.session.commit()
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({'result': 'success'}), HTTPStatus.OK


def addUsers(wb):
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        name = str(row[0].value).split(" ")
        if row[2].value.strip() == "מלווה":
            role = 0
        elif row[2].value.strip() == "רכז":
            role = 1
        elif row[2].value.strip() == "רכז אשכול":
            role = 2
        elif row[2].value.strip() == "אחראי תוכנית":
            role = 3
        first_name = name[0].strip()
        last_name = name[1].strip()
        institution_name = row[1].value.strip()
        phone = str(row[4].value).replace("-", "").strip()
        email = row[3].value.strip()
        eshcol = row[5].value.strip()
        try:
            print("institution_name", institution_name)

            institution_id = db.session.query(Institution.id).filter(
                Institution.name == str(institution_name)).first()
            print("institution_id", institution_id)
            user = user1(
                id=int(str(phone).replace("-", "")),
                name=first_name,
                last_name=last_name,
                role_id=str(role),
                email=str(email),
                eshcol=eshcol,
                institution_id=institution_id.id,
            )
            db.session.add(user)
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    db.session.commit()

    return jsonify({'result': 'success'}), HTTPStatus.OK


@master_user_form_blueprint.route("/initDB", methods=['put'])
def deleteAll():
    try:

        giftCode = db.session.query(gift).delete()
        giftCode = db.session.query(Visit).delete()
        giftCode = db.session.query(ContactForm).delete()
        giftCode = db.session.query(notifications).delete()
        giftCode = db.session.query(user1).delete()
        giftCode = db.session.query(Apprentice).delete()
        path = 'data/apprentice_enter.xlsx'
        wb = load_workbook(filename=path)
        addApperntice(wb)
        path = 'data/user_enter.xlsx'
        wb = load_workbook(filename=path)
        addUsers(wb)

        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST