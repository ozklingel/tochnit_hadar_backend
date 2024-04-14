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
        first_name = row[0].value.strip()
        last_name = str(row[1].value)
        phone = row[2].value
        city = row[3].value.strip()
        address = row[4].value.strip()
        teudatZehut = row[5].value  # מפקד?
        birthday_Ivry = row[6].value.strip()  # מפקד?
        birthday_loazi = row[7].value.strip()  # מפקד?

        marriage_status = row[8].value.strip()
        serve_type = row[9].value.strip()
        hadar_plan_session = row[10].value
        contact1_first_name = row[11].value.strip()
        contact1_phone = row[12].value.strip()
        contact1_email = row[13].value.strip()
        contact2_first_name = row[14].value.strip()
        contact2_phone = row[15].value.strip()
        contact2_email = row[16].value.strip()
        contact3_first_name = row[17].value.strip()
        contact3_phone = row[18].value
        contact3_email = row[19].value.strip()
        marriage_date = row[21].value
        teacher_grade_a = row[22].value.strip()
        teacher_grade_b = row[24].value.strip()
        paying = row[26].value.strip()
        matzbar = row[27].value.strip()
        high_school_name = row[28].value.strip()
        high_school_teacher_phone = row[29].value
        workstatus = row[30].value.strip()
        workplace = row[31].value.strip()
        educationfaculty = row[32].value.strip()
        workoccupation = row[33].value.strip()
        worktype = row[33].value.strip()
        unit_name = row[34].value.strip()  # מפקד?
        army_role = row[35].value.strip()  # מפקד?
        eshcol = row[36].value.strip()
        institution_name = row[37].value.strip()
        accompany_id = row[38].value  # מפקד?
        base_name = row[39].value.strip()
        CityId = db.session.query(City.id).filter(City.name == city).first()[0]
        militaryCompoundId = db.session.query(Base.id).filter(Base.name == base_name).first()[0]

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
                birthday_ivry=birthday_Ivry,
                birthday=birthday_loazi,
                unit_name=unit_name,
                eshcol=eshcol,
                accompany_id=accompany_id,
                contact3_email=contact3_email,
                contact3_first_name=contact3_first_name,
                contact3_phone=contact3_phone,
                # release_date=release_date,
                # recruitment_date=recruitment_date,
                marriage_date=marriage_date,
                spirit_status=matzbar,
                contact2_email=contact2_email,
                worktype=worktype,
                workoccupation=workoccupation,
                educationfaculty=educationfaculty,
                workplace=workplace,
                workstatus=workstatus,
                high_school_teacher_phone=high_school_teacher_phone,
                high_school_name=high_school_name,
                paying=paying,

            )
            db.session.add(Apprentice1)
            db.session.commit()
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({'result': 'success'}), HTTPStatus.OK


def addUsers(wb):
    sheet = wb.active
    for row in sheet.iter_rows(min_row=2):
        if row[5].value is None:
            continue
        if row[2].value.strip() == "מלווה":
            role = 0
        elif row[2].value.strip() == "רכז":
            role = 1
        elif row[2].value.strip() == "רכז אשכול":
            role = 2
        elif row[2].value.strip() == "אחראי תוכנית":
            role = 3
        first_name = row[0].value.strip()
        last_name = row[1].value.strip()
        institution_name = row[3].value.strip()
        phone = str(row[5].value).replace("-", "").strip()
        # email = row[3].value.strip()
        eshcol = row[4].value.strip()
        try:
            institution_id = db.session.query(Institution.id).filter(
                Institution.name == str(institution_name)).first()
            user = user1(
                id=int(str(phone).replace("-", "")),
                name=first_name,
                last_name=last_name,
                role_id=str(role),
                # email=str(email),
                eshcol=eshcol,
                institution_id=institution_id.id,
            )
            db.session.add(user)
            db.session.commit()

        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    return jsonify({'result': 'success'}), HTTPStatus.OK


@master_user_form_blueprint.route("/initDB", methods=['put'])
def initDB():
    try:

        giftCode = db.session.query(gift).delete()
        giftCode = db.session.query(Visit).delete()
        giftCode = db.session.query(ContactForm).delete()
        giftCode = db.session.query(notifications).delete()
        giftCode = db.session.query(user1).delete()
        giftCode = db.session.query(Apprentice).delete()
        path = 'data/apprentice_enter_lab.xlsx'
        wb = load_workbook(filename=path)
        addApperntice(wb)
        path = 'data/user_enter_lab.xlsx'
        wb = load_workbook(filename=path)
        addUsers(wb)

        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST