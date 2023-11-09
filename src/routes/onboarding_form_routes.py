import uuid

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from twilio.rest import Client

from app import red
from src.models.user_model import user1

onboarding_form_blueprint = Blueprint('onboarding_form', __name__, url_prefix='/onboarding_form')
@onboarding_form_blueprint.route('/getOTP', methods=['GET'])
def getOTP_form():
    created_by_phone = request.args.get('created_by_phone')
    userEnt = user1.query.get(created_by_phone[4:])
    if userEnt is None:
        return jsonify({"result": "not in system"}), HTTPStatus.OK

    print(created_by_phone)
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = "ACee3a45e05b65cb79d8e0fe684e389957"
    auth_token = "80087a55520bea1c7b33ab99b83acf3d"
    client = Client(account_sid, auth_token)

    verification = client.verify \
                         .v2 \
                         .services('VA3593d0ca97b77c0c47a1a330b81e2f36') \
                         .verifications \
                         .create(to=created_by_phone, channel='sms')
    if verification.sid is None:
        return jsonify({"result": "error"}), HTTPStatus.OK
    print(verification.sid)
    return jsonify({"result":"success"}),HTTPStatus.OK

@onboarding_form_blueprint.route('/verifyOTP', methods=['GET'])
def verifyOTP_form():
    account_sid = "ACee3a45e05b65cb79d8e0fe684e389957"
    auth_token = "80087a55520bea1c7b33ab99b83acf3d"
    client = Client(account_sid, auth_token)
    otp = request.args.get('otp')
    created_by_phone = request.args.get('created_by_phone')
    print(otp)
    print(created_by_phone)

    result="error"
    try:
        verification_check = client.verify \
            .v2 \
            .services('VA3593d0ca97b77c0c47a1a330b81e2f36') \
            .verification_checks \
            .create(to=created_by_phone, code=otp)

        print(verification_check.status)
        result=verification_check.status
        if verification_check.status !="approved":
            return jsonify({"result": "error"}), HTTPStatus.OK
        userEnt = user1.query.get(created_by_phone[4:])
        if userEnt is None:
            return jsonify({"result": "not in system"}), HTTPStatus.OK
        if userEnt.name and userEnt.last_name and userEnt.email and userEnt.birthday and userEnt.cluster_id:
            accessToken = int(str(uuid.uuid4().int)[:5])
            red.hset(int(str(created_by_phone)[4:]), "accessToken", accessToken)
            return jsonify({"result": accessToken,"firsOnboarding":False}), HTTPStatus.OK

        accessToken=int(str(uuid.uuid4().int)[:5])
        red.hset(int(str(created_by_phone)[4:]), "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
    except:
        if result =="approved":
            userEnt = user1.query.get(created_by_phone[4:])
            print("approved")
            print(userEnt)

            if userEnt is None:
                return jsonify({"result": "not in system"}), HTTPStatus.OK


            if (userEnt.name and userEnt.last_name and userEnt.email and userEnt.birthday and userEnt.cluster_id) and (userEnt.name!='' and userEnt.last_name!='' and userEnt.email!='' and userEnt.birthday!='' and userEnt.cluster_id!=''):
                accessToken = int(str(uuid.uuid4().int)[:5])
                #red.hset(int(str(created_by_phone)[4:]), "accessToken", accessToken)
                return jsonify({"result": accessToken, "firsOnboarding": False}), HTTPStatus.OK
            accessToken = int(str(uuid.uuid4().int)[:5])
            red.hset(int(str(created_by_phone)[4:]), "accessToken", accessToken)
            return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
        return jsonify({"result": "error"}), HTTPStatus.OK


