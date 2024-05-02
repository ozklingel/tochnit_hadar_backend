import uuid
import time
from datetime import timedelta
from typing import List

from flask import Blueprint, request, jsonify, session
from http import HTTPStatus
import pyotp

from openpyxl.reader.excel import load_workbook
from timer_dict import TimerDict
from twilio.rest import Client

import config
from app import red, db
from src.models.city_model import City
from src.models.user_model import user1
from src.routes.Utils.Sms import send_sms_019
from src.routes.messegaes_routes import send_green_whatsapp

secret_key = pyotp.random_base32()
otp = pyotp.TOTP(secret_key, interval=120)
config.prev_otp=0
user_otp_dict= TimerDict(default_duration=timedelta(minutes=1))
onboarding_form_blueprint = Blueprint('onboarding_form', __name__, url_prefix='/onboarding_form')
@onboarding_form_blueprint.route('/getOTP', methods=['GET'])
def getOTP_form():
    try:
        created_by_phone = request.args.get('created_by_phone')
        userEnt = user1.query.get(created_by_phone)
        if userEnt is None:
            return jsonify({"result": "not in system"}), 401
        if str(created_by_phone) in user_otp_dict:
            return jsonify({"result": "already got otp"}), 401
        # Generate an OTP using TOTP after every 30 seconds
        send_sms_019(["559482844"],[created_by_phone],"your verify service verification code from **tochnit hadar** is : "+otp.now())
        user_otp_dict[str(created_by_phone)]=otp.now()
        config.prev_otp=str(otp.now())
        session['otp_code'] = str(otp.now())
        print(user_otp_dict)
        return jsonify({"result":"success"}),HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@onboarding_form_blueprint.route('/verifyOTP', methods=['GET'])
def verifyOTP_form():
    try:
        user_otp = request.args.get('otp')
        created_by_phone = request.args.get('created_by_phone')
        print("user_otp",user_otp)
        print("current TOTP is: ", otp.now())
        print("prev TOTP is: ", config.prev_otp)

        print("created_by_phone",created_by_phone)
        if (otp.verify(user_otp))==False:
            if session['otp_code']!=user_otp:
                print(user_otp,otp.now(),config.prev_otp)
                return jsonify({"result": "wrong otp","firsOnboarding": True}), 401
        userEnt = user1.query.get(created_by_phone)
        if userEnt is None:
            return jsonify({"result": "not in system","firsOnboarding": True}), 401
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
        accessToken=int(str(uuid.uuid4().int)[:5])
        print(accessToken)
        #red.hset(int(str(created_by_phone)), "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e),"firsOnboarding": True}), HTTPStatus.BAD_REQUEST


@onboarding_form_blueprint.route('/get_CitiesDB', methods=['GET'])
def get_CitiesDB():
    try:
        CityList = db.session.query(City.name).all()
        print(CityList)
        return jsonify([i[0] for i in [tuple(row) for row in CityList]])
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
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
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST

@onboarding_form_blueprint.route('/getOTP_whatsapp', methods=['get'])
def getOTP_whatsapp():
    try:
        created_by_phone = request.args.get('created_by_phone')
        created_by_phone_asList=["0"+str(created_by_phone)]
        userEnt = user1.query.get(created_by_phone)
        if userEnt is None:
            return jsonify({"result": "not in system"}), 401
        print(created_by_phone)
        print("your verify service verification code from tochnit hadar is:"+otp.now())
        returned: List[int] = send_green_whatsapp("your verify service verification code from *tochnit hadar* is : "+otp.now(), created_by_phone_asList)
        count_200 = returned.count(200)
        if count_200 == len(returned):
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return (jsonify({'result': str(f"success with: {count_200}, failed with: {(len(returned) - count_200)}")}),
                HTTPStatus.INTERNAL_SERVER_ERROR)
    except Exception as e:
        return jsonify({'result': str(e), "input:": str(created_by_phone)}), HTTPStatus.BAD_REQUEST
@onboarding_form_blueprint.route('/getOTP_whatsapp_twillo', methods=['GET'])
def getOTP_whatsapp_twillo():
    try:
        created_by_phone = request.args.get('created_by_phone')

        print(created_by_phone)
        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
        auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
        verify_sid = "VA280c3b665cf155bb76e5bc77bb5c750a"

        client = Client(account_sid, auth_token)
        created_by_phone="+972"+created_by_phone
        verification = client.verify.v2.services(verify_sid) \
            .verifications \
            .create(to=created_by_phone, channel="whatsapp")
        if verification.sid is None:
            return jsonify({"result": "error"}), HTTPStatus.OK
        print(verification.sid)
        return jsonify({"result":"success"}),HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
@onboarding_form_blueprint.route('/verifyOTP_whatsapp', methods=['GET'])
def verifyOTP_twilo():
        account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
        auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
        client = Client(account_sid, auth_token)
        otp = request.args.get('otp')
        created_by_phone = request.args.get('created_by_phone')
        print(otp)
        print(created_by_phone)

        result="error"
        try:
            verification_check = client.verify \
                .v2 \
                .services('VA280c3b665cf155bb76e5bc77bb5c750a') \
                .verification_checks \
                .create(to="+972"+created_by_phone, code=otp)
        except:
            return jsonify({"result": "not in system"}), HTTPStatus.OK

        print(verification_check.status)
        time.sleep(2.4)
        if verification_check.status !="approved":
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
            return jsonify({"result": accessToken, "firsOnboarding": False}), HTTPStatus.OK
        accessToken = int(str(uuid.uuid4().int)[:5])
        print(accessToken)
        # red.hset(int(str(created_by_phone)), "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK