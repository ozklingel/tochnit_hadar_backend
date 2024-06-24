from datetime import datetime
from http import HTTPStatus
from flask import Blueprint, request, jsonify

from openpyxl.reader.excel import load_workbook

import config
from src.models.region_model import Region
from src.models.models_utils import to_iso
from src.services import db, red
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.message_model import Message
from src.models.institution_model import Institution
from src.models.task_model import Task
from src.models.user_model import User
from src.models.report_model import Report

from src.routes.apprentice_profile import visit_gap_color
from src.routes.set_entity_details_form_routes import validate_email

userProfile_form_blueprint = Blueprint('userProfile_form', __name__, url_prefix='/userProfile_form')


@userProfile_form_blueprint.route('/delete', methods=['post'])
def delete():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        userId = data['userId']
        updatedEnt = User.query.get(userId)
        if updatedEnt:
            db.session.query(Message).filter(Message.created_for_id == userId, ).delete()
            db.session.query(Message).filter(Message.created_by_id == userId, ).delete()
            db.session.query(Task).filter(Task.userid == userId).delete()
            db.session.query(User).filter(User.id == userId).delete()
        else:
            updatedEnt = Apprentice.query.get(userId)
            if updatedEnt:
                res = db.session.query(Task).filter(Task.subject == userId).delete()
                res = db.session.query(Report).filter(Report.ent_reported == userId, ).delete()
                res = db.session.query(Apprentice).filter(Apprentice.id == userId).delete()
            else:
                return jsonify({"result": str("no such id")}), HTTPStatus.BAD_REQUEST

        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@userProfile_form_blueprint.route("/update", methods=['put'])
def update():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        userId = request.args.get('userId')
        data = request.json
        updatedEnt = User.query.get(userId)
        for key in data:
            if key == "city":
                CityId = db.session.query(City).filter(
                    City.name == str(data[key])).first()
                setattr(updatedEnt, "city_id", CityId.id)
            if key == "region":
                ClusterId = db.session.query(Cluster.id).filter(
                    Cluster.name == str(data[key])).first()
                setattr(updatedEnt, "cluster_id", ClusterId.id)
            elif key == "email" or key == "birthday":
                if validate_email(data[key]):
                    setattr(updatedEnt, key, data[key])
                else:
                    return jsonify({'result': "email or date -wrong format"}), 401
            else:
                setattr(updatedEnt, key, data[key])

        db.session.commit()
        if updatedEnt:
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'no updatedEnt'}), 401
    except Exception as e:
        return jsonify({'result': str(e)}), 401


@userProfile_form_blueprint.route('/getProfileAtributes', methods=['GET'])
def getProfileAtributes_form():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        created_by_id = request.args.get('userId')
        userEnt = User.query.get(created_by_id)
        if userEnt:
            city = db.session.query(City).filter(City.id == userEnt.city_id).first()
            regionName = db.session.query(Region.name).filter(Region.id == city.region_id).first()
            myApprenticesNamesList = getmyApprenticesNames(created_by_id)
            city = db.session.query(City).filter(City.id == userEnt.city_id).first()
            list = userEnt.to_attributes(city.name, str(regionName[0]), myApprenticesNamesList)
            return jsonify(list), HTTPStatus.OK
        else:
            return jsonify(results="no such id"), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), 401


def getmyApprenticesNames(created_by_id):
    try:
        apprenticeList = db.session.query(Apprentice.id, Apprentice.name, Apprentice.last_name).filter(
            Apprentice.accompany_id == created_by_id).all()
        return [{"id": str(row[0]), "name": row[1], "last_name": row[2]} for row in apprenticeList]
    except Exception as e:
        return jsonify({'result': str(e)}), 401


@userProfile_form_blueprint.route("/add_user_excel", methods=['put'])
def add_user_excel():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    file = request.files['file']
    wb = load_workbook(file)
    sheet = wb.active
    uncommited_ids = []
    for row in sheet.iter_rows(min_row=2):
        if row[0].value is None or row[1].value is None or row[2].value is None or row[5].value is None:
            uncommited_ids.append(row[5].value)
            continue
        role_ids = ""
        if "מלווה" in row[2].value.strip():
            role_ids += "0,"
        if "רכז מוסד" in row[2].value.strip():
            role_ids += "1,"
        if "רכז אשכול" in row[2].value.strip():
            role_ids += "2,"
        if "אחראי תוכנית" in row[2].value.strip():
            role_ids += "3,"
        role_ids = role_ids[:-1]
        first_name = row[0].value.strip()
        last_name = row[1].value.strip()
        institution_name = row[3].value.strip() if not row[3].value is None else "לא ידוע"
        eshcol = row[4].value.strip() if not row[4].value is None else "" if not row[4].value is None else "לא ידוע"
        phone = str(row[5].value).replace("-", "").strip()
        # email = row[3].value.strip()
        try:
            institution_id = db.session.query(Institution.id).filter(
                Institution.name == str(institution_name)).first()

            user = User(
                id=int(str(phone).replace("-", "")),
                name=first_name,
                last_name=last_name,
                role_ids=role_ids,
                # email=str(email),
                cluster_id=eshcol,
                institution_id=institution_id[0],
            )

            db.session.add(user)

            db.session.commit()
        except Exception as e:
            return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': "success", "uncommited_ids": [x for x in uncommited_ids if x is not None]})


@userProfile_form_blueprint.route("/add_user_manual", methods=['post'])
def add_user_manual():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json
    try:
        first_name = data['first_name']
        last_name = data['last_name']
        phone = data['phone']
        institution_id = data['institution_id']
        city_name = "עלי"
        try:
            city_name = data['city_name'] or "עלי"
        except:
            print("no city")
        role_ids = data['role_ids']
        CityId = db.session.query(City).filter(City.name == city_name).first()
        # institution_id = db.session.query(Institution.id).filter(Institution.name==institution_name).first()
        institution_id = institution_id[0] if institution_id else 0
        useEnt = User(
            id=int(phone[1:]),
            name=first_name,
            last_name=last_name,
            role_ids=role_ids,
            institution_id=institution_id,
            city_id=CityId.id,
            cluster_id=CityId.cluster_id,
            photo_path="https://www.gravatar.com/avatar"
        )
        db.session.add(useEnt)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.BAD_REQUEST

    if useEnt:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK


@userProfile_form_blueprint.route('/myPersonas', methods=['GET'])
def myPersonas():
    try:
        if correct_auth()==False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        created_by_id = request.args.get('userId')
        apprenticeList = []
        user1ent = db.session.query(User.role_ids, User.institution_id, User.cluster_id).filter(
            User.id == created_by_id).first()
        if "0" in user1ent.role_ids:
            apprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id).all()
            userList = []
        if "1" in user1ent.role_ids:
            apprenticeList = db.session.query(Apprentice).filter(
                Apprentice.institution_id == user1ent.institution_id).all()
            userList = db.session.query(User).filter(User.institution_id == user1ent.institution_id).all()
        if "2" in user1ent.role_ids:
            apprenticeList = db.session.query(Apprentice).filter(Apprentice.cluster_id == user1ent.cluster_id).all()
            userList = db.session.query(User).filter(User.institution_id == user1ent.institution_id).all()
        if "3" in user1ent.role_ids:
            apprenticeList = db.session.query(Apprentice).all()
            userList = db.session.query(User).all()

        my_dict = []

        for noti in apprenticeList:
            accompany = db.session.query(User.name, User.last_name).filter(
                User.id == Apprentice.accompany_id).first()
            call_status = visit_gap_color(config.call_report, noti, 30, 15)
            personalMeet_status = visit_gap_color(config.personalMeet_report, noti, 100, 80)
            Horim_status = visit_gap_color(config.HorimCall_report, noti, 365, 350)
            city = db.session.query(City).filter(City.id == noti.city_id).first()
            reportList = db.session.query(Report.id).filter(Report.ent_reported == noti.id).all()
            eventlist = db.session.query(Task.id, Task.event, Task.details,
                                         Task.date).filter(Task.subject == str(noti.id)).all()
            base_id = db.session.query(Base.id).filter(Base.id == int(noti.base_address)).first()
            base_id = base_id[0] if base_id else 0
            my_dict.append(
                {"role":[],
                    "Horim_status": Horim_status,
                 "personalMeet_status": personalMeet_status,
                 "call_status": call_status,
                 "highSchoolRavMelamed_phone": noti.high_school_teacher_phone
                    , "highSchoolRavMelamed_name": noti.high_school_teacher,
                 "highSchoolRavMelamed_email": noti.high_school_teacher_email,

                 "thRavMelamedYearA_name": noti.teacher_grade_a,
                 "thRavMelamedYearA_phone": noti.teacher_grade_a_phone,
                 "thRavMelamedYearA_email": noti.teacher_grade_a_email,

                 "thRavMelamedYearB_name": noti.teacher_grade_b,
                 "thRavMelamedYearB_phone": noti.teacher_grade_b_phone,
                 "thRavMelamedYearB_email": noti.teacher_grade_b_email,
                 "address": {
                     "country": "IL",
                     "city": city.name if city else "",
                     "cityId": str(noti.city_id),
                     "street": noti.address,
                     "houseNumber": "1",
                     "apartment": "1",
                     "region": str(city.region_id) if city else "",
                     "entrance": "a",
                     "floor": "1",
                     "postalCode": "12131",
                     "lat": 32.04282620026557,  # no need city cord
                     "lng": 34.75186193813887
                 },
                 "contact1_first_name": noti.contact1_first_name,
                 "contact1_last_name": noti.contact1_last_name,
                 "contact1_phone": noti.contact1_phone,
                 "contact1_email": noti.contact1_email,
                 "contact1_relation": noti.contact1_relation,
                 "contact2_first_name": noti.contact2_first_name,
                 "contact2_last_name": noti.contact2_last_name,
                 "contact2_phone": noti.contact2_phone,
                 "contact2_email": noti.contact2_email,
                 "contact2_relation": noti.contact2_relation,
                 "contact3_first_name": noti.contact3_first_name,
                 "contact3_last_name": noti.contact3_last_name,
                 "contact3_phone": noti.contact3_phone,
                 "contact3_email": noti.contact3_email,
                 "contact3_relation": noti.contact3_relation,
                 "activity_score": len(reportList),

                 "reports":
                     [str(i[0]) for i in [tuple(row) for row in reportList]]
                    ,
                 "events": [{"id": row[0], "subject": row[0],
                      "date": to_iso(row[3]),
                      "created_at": to_iso(row[3]),
                      "event": row[1], "allreadyread": False, "description":row[2],
                      "frequency": "never",
                      }for row in
                      eventlist],
                "id": str(noti.id),
                "thMentor_name": accompany.name + " " + accompany.last_name,
                 "thMentor_id": str(noti.accompany_id),
                 "militaryPositionNew": str(noti.militaryPositionNew),
                "avatar": noti.photo_path if noti.photo_path is not None else 'https://www.gravatar.com/avatar',
                 "name": str(noti.name), "last_name": str(noti.last_name),
                 "institution_id": str(noti.institution_id), "thPeriod": str(noti.hadar_plan_session),
                 "serve_type": noti.serve_type,
                 "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(base_id),
                 "phone": str(noti.id), "email": noti.email, "teudatZehut": noti.teudatZehut,
                 "birthday": to_iso(noti.birthday) if noti.birthday else "", "marriage_date": to_iso(noti.marriage_date),
                 "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
                 "unit_name": noti.unit_name,
                 "matsber": str(noti.spirit_status),
                 "militaryDateOfDischarge": to_iso(noti.release_date),
                 "militaryDateOfEnlistment": to_iso(noti.recruitment_date),
                 "militaryUpdatedDateTime": to_iso(noti.militaryupdateddatetime),
                 "militaryPositionOld": noti.militaryPositionOld,
                 "educationalInstitution": noti.educationalinstitution,
                 "educationFaculty": noti.educationfaculty,
                 "workOccupation": noti.workoccupation,
                 "workType": noti.worktype,
                 "workPlace": noti.workplace,
                 "workStatus": noti.workstatus,
                 "paying": noti.paying

                 })
        for noti in userList:
            reportList = db.session.query(Report.id).filter(Report.user_id == noti.id).all()
            city = db.session.query(City).filter(City.id == noti.city_id).first()
            my_dict.append(
                {"role":[int(r) for r in noti.role_ids.split(",")],
                    "Horim_status": "",
                 "personalMeet_status": "",
                 "call_status": "",
                 "highSchoolRavMelamed_phone": ""
                    , "highSchoolRavMelamed_name": "",
                 "highSchoolRavMelamed_email": "",

                 "thRavMelamedYearA_name": "",
                 "thRavMelamedYearA_phone": "",
                 "thRavMelamedYearA_email": "",

                 "thRavMelamedYearB_name": "",
                 "thRavMelamedYearB_phone": "",
                 "thRavMelamedYearB_email": "",
                 "address": {
                     "country": "IL",
                     "city": city.name if city else "",
                     "cityId": str(noti.city_id),
                     "street": noti.address,
                     "houseNumber": "1",
                     "apartment": "1",
                     "region": str(city.region_id) if city else "",
                     "entrance": "a",
                     "floor": "1",
                     "postalCode": "12131",
                     "lat": 32.04282620026557,  # no need city cord
                     "lng": 34.75186193813887
                 },
                 "contact1_first_name": "",
                 "contact1_last_name": "",
                 "contact1_phone": "",
                 "contact1_email": "",
                 "contact1_relation": "",
                 "contact2_first_name": "",
                 "contact2_last_name": "",
                 "contact2_phone": "",
                 "contact2_email": "",
                 "contact2_relation": "",
                 "contact3_first_name": "",
                 "contact3_last_name": "",
                 "contact3_phone": "",
                 "contact3_email": "",
                 "contact3_relation": "",
                 "activity_score": len(reportList),
                 "reports": [],
                 "events": [],
                 "id": str(noti.id),
                 "thMentor": "",
                 "militaryPositionNew": "",
                 "avatar": noti.photo_path if noti.photo_path is not None else 'https://www.gravatar.com/avatar',
                 "name": str(noti.name), "last_name": str(noti.last_name),
                 "institution_id": str(noti.institution_id), "thPeriod": "",
                 "serve_type": "",
                 "marriage_status": "",
                 "militaryCompoundId": "",
                 "phone": str(noti.id),
                 "email": noti.email,
                 "teudatZehut": noti.teudatZehut,
                 "birthday": "",
                 "marriage_date": "",
                 "highSchoolInstitution": "",
                 "army_role": "",
                 "unit_name": "",
                 "matsber": "",
                 "militaryDateOfDischarge": "",
                 "militaryDateOfEnlistment": "",
                 "militaryUpdatedDateTime": "",
                 "militaryPositionOld": "", "educationalInstitution": "",
                 "educationFaculty": "", "workOccupation": "",
                 "workType": "", "workPlace": "", "workStatus": "",
                 "paying": ""

                 })
        return jsonify(my_dict)
    except Exception as e:
        return jsonify({'result': str(e)}), 401
def correct_auth(external=True):
    if config.Authorization_is_On and external:
        userId = request.args.get("userId")
        accessToken = request.headers.get('Authorization')
        redisaccessToken = red.hget(userId, "accessToken").decode("utf-8")
        print("accessToken: ", accessToken)
        print("redisaccessToken: ", redisaccessToken)
        if redisaccessToken != accessToken:
            return False
        return True
    return True
