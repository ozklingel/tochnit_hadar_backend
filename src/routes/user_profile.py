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
from src.routes.set_entity_details_form_routes import validate_email, validate_date
from src.logic import my_personas

userProfile_form_blueprint = Blueprint(
    'userProfile_form', __name__, url_prefix='/userProfile_form')


@userProfile_form_blueprint.route('/delete', methods=['post'])
def delete():
    try:
        if correct_auth() == False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        data = request.json
        userId = data['userId']
        updatedEnt = User.query.get(userId)
        if updatedEnt:
            db.session.query(Message).filter(
                Message.created_for_id == userId, ).delete()
            db.session.query(Message).filter(
                Message.created_by_id == userId, ).delete()
            db.session.query(Task).filter(Task.userid == userId).delete()
            db.session.query(User).filter(User.id == userId).delete()
        else:
            updatedEnt = Apprentice.query.get(userId)
            if updatedEnt:
                res = db.session.query(Task).filter(
                    Task.subject == userId).delete()
                res = db.session.query(Report).filter(
                    Report.ent_reported == userId, ).delete()
                res = db.session.query(Apprentice).filter(
                    Apprentice.id == userId).delete()
            else:
                return jsonify({"result": str("no such id")}), HTTPStatus.BAD_REQUEST

        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({"result": "success"}), HTTPStatus.OK


@userProfile_form_blueprint.route("/update", methods=['put'])
def update():
    try:
        if correct_auth() == False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        userId = request.args.get('userId')
        data = request.json
        updatedEnt = User.query.get(userId)
        for key in data:
            if key == "birthday":
                if validate_date(data[key]):
                    setattr(updatedEnt, key, data[key])
            elif key == "email" or key == "birthday":
                if validate_email(data[key]):
                    setattr(updatedEnt, key, data[key])
                else:
                    return jsonify({'result': "email or date -wrong format"}), 401
            else:
                setattr(updatedEnt, key, data[key])
        print(updatedEnt.region_id)
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
        if correct_auth() == False:
            return jsonify({'result': "wrong access token"}), HTTPStatus.OK
        created_by_id = request.args.get('userId')
        userEnt = User.query.get(created_by_id)
        if userEnt:
            city = db.session.query(City).filter(
                City.id == userEnt.city_id).first()
            regionName = db.session.query(Region.name).filter(
                Region.id == userEnt.region_id).first()
            myApprenticesNamesList = getmyApprenticesNames(created_by_id)
            city = db.session.query(City).filter(
                City.id == userEnt.city_id).first()
            list = userEnt.to_attributes(city.name, str(
                regionName[0]), myApprenticesNamesList)
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
        institution_name = row[3].value.strip(
        ) if not row[3].value is None else "לא ידוע"
        eshcol = row[4].value.strip(
        ) if not row[4].value is None else "" if not row[4].value is None else "לא ידוע"
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
                institution_id=institution_id[0] if institution_id else None,
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
        return my_personas.get_personas(request.args.get('userId'))
    except Exception as e:
        raise e


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
