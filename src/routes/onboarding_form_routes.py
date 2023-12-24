import uuid
import time
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from twilio.rest import Client

from app import red
from src.models.user_model import user1

onboarding_form_blueprint = Blueprint('onboarding_form', __name__, url_prefix='/onboarding_form')
@onboarding_form_blueprint.route('/getOTP', methods=['GET'])
def getOTP_form():
    created_by_phone = request.args.get('created_by_phone')

    print(created_by_phone)
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
    auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
    verify_sid = "VA280c3b665cf155bb76e5bc77bb5c750a"

    client = Client(account_sid, auth_token)
    created_by_phone="+"+created_by_phone
    verification = client.verify.v2.services(verify_sid) \
        .verifications \
        .create(to=created_by_phone, channel="whatsapp")
    print("done")
    if verification.sid is None:
        return jsonify({"result": "error"}), HTTPStatus.OK
    print(verification.sid)
    return jsonify({"result":"success"}),HTTPStatus.OK

@onboarding_form_blueprint.route('/verifyOTP', methods=['GET'])
def verifyOTP_form():
    account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
    auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
    client = Client(account_sid, auth_token)
    otp = request.args.get('otp')
    created_by_phone = request.args.get('created_by_phone')
    print(otp)
    print(created_by_phone)

    result="error"
    created_by_phone="+"+created_by_phone

    verification_check = client.verify \
        .v2 \
        .services('VA280c3b665cf155bb76e5bc77bb5c750a') \
        .verification_checks \
        .create(to=created_by_phone, code=otp)

    print(verification_check.status)
    time.sleep(2.4)
    print(verification_check.status)
    if verification_check.status !="approved":
        return jsonify({"result": "error"}), HTTPStatus.OK
    userEnt = user1.query.get(created_by_phone[3:])
    if userEnt is None:
        return jsonify({"result": "not in system"}), HTTPStatus.OK
    print(userEnt.name)
    print(userEnt.last_name)
    print(userEnt.email)
    print(userEnt.birthday)
    print(userEnt.cluster_id)

    if userEnt.name and userEnt.last_name and userEnt.email and userEnt.birthday and userEnt.cluster_id:
        print("not null")
        red.hdel(int(str(created_by_phone)[3:]), "accessToken")
        accessToken = int(str(uuid.uuid4().int)[:5])
        red.hset(int(str(created_by_phone)[3:]), "accessToken", accessToken)
        return jsonify({"result": accessToken,"firsOnboarding":False}), HTTPStatus.OK
    print("null")
    accessToken=int(str(uuid.uuid4().int)[:5])
    print(accessToken)
    red.hset(int(str(created_by_phone)[3:]), "accessToken", accessToken)
    return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK

    return jsonify({"result": "error"}), HTTPStatus.OK

