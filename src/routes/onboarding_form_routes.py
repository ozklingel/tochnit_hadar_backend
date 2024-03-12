import uuid
import time
from flask import Blueprint, request, jsonify
from http import HTTPStatus
import pyotp

from openpyxl.reader.excel import load_workbook
from twilio.rest import Client

from app import red, db
from src.models.city_model import City
from src.models.user_model import user1
from src.routes.Utils.Sms import send_sms_019

secret_key = pyotp.random_base32()
otp = pyotp.TOTP(secret_key, interval=60)
onboarding_form_blueprint = Blueprint('onboarding_form', __name__, url_prefix='/onboarding_form')
@onboarding_form_blueprint.route('/getOTP', methods=['GET'])
def getOTP_form():
    try:
        created_by_phone = request.args.get('created_by_phone')
        # Create a secret key (keep it secret!)̥
        secret_key = pyotp.random_base32()
        # Generate an OTP using TOTP after every 30 seconds
        print("Your TOTP is: ", otp.now())
        send_sms_019("+972549247616",created_by_phone,otp.now())
        return jsonify({"result":"success"}),HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
@onboarding_form_blueprint.route('/verifyOTP', methods=['GET'])
def verifyOTP_form():
    try:
        user_otp = request.args.get('otp')
        created_by_phone = request.args.get('created_by_phone')

        if (otp.verify(user_otp))==False:
            return jsonify({"result": "wrong otp"}), HTTPStatus.OK
        userEnt = user1.query.get(created_by_phone)
        if userEnt is None:
            return jsonify({"result": "not in system"}), HTTPStatus.OK
        print(userEnt.name)
        print(userEnt.last_name)
        print(userEnt.email)
        print(userEnt.birthday)
        print(userEnt.cluster_id)

        if userEnt.name and userEnt.last_name and userEnt.email and userEnt.birthday and userEnt.cluster_id:
            print("not null")
            red.hdel(int(str(created_by_phone)), "accessToken")
            accessToken = int(str(uuid.uuid4().int)[:5])
            red.hset(int(str(created_by_phone)), "accessToken", accessToken)
            return jsonify({"result": accessToken,"firsOnboarding":False}), HTTPStatus.OK
        print("null")
        accessToken=int(str(uuid.uuid4().int)[:5])
        print(accessToken)
        red.hset(int(str(created_by_phone)), "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@onboarding_form_blueprint.route('/get_CitiesDB', methods=['GET'])
def get_CitiesDB():
    try:
        CityList = db.session.query(City.name).all()
        print(CityList)
        return jsonify([i[0] for i in [tuple(row) for row in CityList]])
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
@onboarding_form_blueprint.route('/upload_CitiesDB', methods=['GET'])
def upload_CitiesDB():
    try:
        my_list = []
        #/home/ubuntu/flaskapp/src/routes/
        path = '/home/ubuntu/flaskapp/citiesToAdd.xlsx'
        wb = load_workbook(filename=path)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2):
                my_list.append(City(int(row[2].value), row[1].value.strip(), int(row[0].value)))
        for ent in my_list:
            db.session.add(ent)
        db.session.commit()
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK