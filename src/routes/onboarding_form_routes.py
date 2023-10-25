import uuid

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from twilio.rest import Client

from app import red

onboarding_form_blueprint = Blueprint('onboarding_form', __name__, url_prefix='/onboarding_form')
@onboarding_form_blueprint.route('/getOTP', methods=['GET'])
def getOTP_form():
    created_by_phone = request.args.get('created_by_phone')
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
    verification_check = client.verify \
        .v2 \
        .services('VA3593d0ca97b77c0c47a1a330b81e2f36') \
        .verification_checks \
        .create(to=created_by_phone, code=otp)

    print(verification_check.status)
    if verification_check.status is None:
        return jsonify({"result": "error"}), HTTPStatus.OK
    accessToken=int(str(uuid.uuid4().int)[:5])
    userId=int(str(uuid.uuid4().int)[:5])
    red.hset(userId, "accessToken", accessToken)
    return jsonify({"result":accessToken}),HTTPStatus.OK

@onboarding_form_blueprint.route('/getAccessTocken', methods=['GET'])
def getAccessTocken():
    userId = request.args.get("userId")
    accessToken=int(str(uuid.uuid4().int)[:5])
    print(accessToken)
    red.hset(userId, "accessToken", accessToken)
    return jsonify({"result":accessToken}),HTTPStatus.OK
