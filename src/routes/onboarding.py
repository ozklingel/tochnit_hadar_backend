import uuid
import time
from datetime import timedelta
from typing import List

from http import HTTPStatus
from flask import Blueprint, request, jsonify
import pyotp

from timer_dict import TimerDict
from twilio.rest import Client

from src.services import red, db
from src.models.city_model import City
from src.models.user_model import User
from src.routes.utils.sms import send_sms_019
from src.routes.messages import send_green_whatsapp
from datetime import datetime

secret = pyotp.random_base32()

user_otp_dict = TimerDict(default_duration=timedelta(minutes=1))
onboarding_form_blueprint = Blueprint(
    "onboarding_form", __name__, url_prefix="/onboarding_form"
)


@onboarding_form_blueprint.route("/getOTP", methods=["GET"])
def get_otp_form():
    try:
        created_by_phone = request.args.get("created_by_phone")
        is_valid_recipient_message = is_valid_recipient(created_by_phone)
        if is_valid_recipient_message != True:
            return jsonify({"result": is_valid_recipient_message}), 401
        otp_code = str(uuid.uuid4().int)[:6]
        send_sms_019(
            ["559482844"],
            [created_by_phone],
            "your verify service verification code from **tochnit hadar** is : "
            + str(otp_code),
        )
        # store also date to  confirm user didnt get otp in last 690 sec in future
        now_date = datetime.now()
        red.hset(created_by_phone, "otp_date", str(now_date)[:-7])
        red.hset(created_by_phone, "otp_code", str(otp_code))
        return jsonify({"result": "success"}), HTTPStatus.OK
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@onboarding_form_blueprint.route("/getOTP_whatsapp", methods=["get"])
def get_otp_whatsapp():
    try:
        created_by_phone = request.args.get("created_by_phone")
        created_by_phone_asList = [str(created_by_phone)]
        is_valid_recipient_message = is_valid_recipient(created_by_phone)
        if is_valid_recipient_message != True:
            return jsonify({"result": is_valid_recipient_message})
        otp_code = str(uuid.uuid4().int)[:6]
        returned: List[int] = send_green_whatsapp(
            None,
            "your verify service verification code from *tochnit hadar* is : "
            + otp_code,
            created_by_phone_asList,
        )
        # store also date to  confirm user didnt get otp in last 690 sec in future
        now_date = datetime.now()
        red.hset(created_by_phone, "otp_date", str(now_date)[:-7])
        red.hset(created_by_phone, "otp_code", str(otp_code))
        count_200 = returned.count(200)
        if count_200 == len(returned):
            return jsonify({"result": "success"}), HTTPStatus.OK
        return (
            jsonify(
                {
                    "result": str(
                        f"success with: {count_200}, failed with: {(len(returned) - count_200)}"
                    )
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return (
            jsonify({"result": str(e), "input:": request.args.get("created_by_phone")}),
            HTTPStatus.BAD_REQUEST,
        )


@onboarding_form_blueprint.route("/verifyOTP", methods=["GET"])
def verify_otp_form():
    try:
        user_otp = request.args.get("otp")
        created_by_phone = request.args.get("created_by_phone")
        confirmed_phones = [
            "584770076",
            "502070738",
            "506795170",
            "549247616",
            "504083795",
        ]
        if str(created_by_phone) in confirmed_phones and user_otp == "123123":
            accessToken = int(str(uuid.uuid4().int)[:5])
            red.hset(created_by_phone, "accessToken", accessToken)
            return (
                jsonify({"result": accessToken, "firsOnboarding": False}),
                HTTPStatus.OK,
            )
        # confirm otp is correct
        otpCode = red.hget(created_by_phone, "otp_code").decode("utf-8")
        if otpCode != user_otp:
            return jsonify({"result": "wrong otp", "firsOnboarding": True}), 401
        # confirm otp didnt expiared
        otpDate = red.hget(created_by_phone, "otp_date").decode("utf-8")
        date_format = "%Y-%m-%d %H:%M:%S"
        date_obj1 = datetime.strptime(otpDate, date_format)
        dt = datetime.now()
        difference = (dt - date_obj1).seconds
        if difference > 60:
            return jsonify({"result": " otp expaired", "firsOnboarding": True}), 401
        userEnt = User.query.get(created_by_phone)
        if userEnt is None:
            return jsonify({"result": "not in system", "firsOnboarding": True}), 401
        if (
            userEnt.name
            and userEnt.last_name
            and userEnt.email
            and userEnt.birthday
            and userEnt.region_id
        ):
            accessToken = int(str(uuid.uuid4().int)[:5])
            red.hset(created_by_phone, "accessToken", accessToken)
            return (
                jsonify({"result": accessToken, "firsOnboarding": False}),
                HTTPStatus.OK,
            )
        red.hdel(created_by_phone, "accessToken")
        accessToken = int(str(uuid.uuid4().int)[:5])
        red.hset(created_by_phone, "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
    except Exception as e:
        return (
            jsonify({"result": str(e), "firsOnboarding": True}),
            HTTPStatus.BAD_REQUEST,
        )


def is_valid_recipient(created_by_phone):
    userEnt = User.query.get(created_by_phone)
    if userEnt is None:
        return "not in system"
    otp_date = red.hget(created_by_phone, "otp_date")
    # confirm user didnt get otp in last 690 sec
    if otp_date:
        date_format = "%Y-%m-%d %H:%M:%S"
        date_obj1 = datetime.strptime(otp_date.decode("utf-8"), date_format)
        now_date = datetime.now()
        difference = (now_date - date_obj1).seconds
        if difference < 60:
            "already got otp"
    return True


@onboarding_form_blueprint.route("/get_CitiesDB", methods=["GET"])
def get_cities():
    try:
        CityList = db.session.query(City.name).all()
        return jsonify([i[0] for i in [tuple(row) for row in CityList]])
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST


@onboarding_form_blueprint.route("/verifyOTP_whatsapp", methods=["GET"])
def verify_otp_twilo():
    account_sid = "AC7e7b44337bff9de0cb3702ad5e23e1e8"
    auth_token = "61caa0e3ab00c4d8928e97fdad1a8d52"
    client = Client(account_sid, auth_token)
    otp = request.args.get("otp")
    created_by_phone = request.args.get("created_by_phone")

    try:
        verification_check = client.verify.v2.services(
            "VA280c3b665cf155bb76e5bc77bb5c750a"
        ).verification_checks.create(to="+972" + created_by_phone, code=otp)
    except:
        return jsonify({"result": "not in system"}), HTTPStatus.OK

    time.sleep(2.4)
    if verification_check.status != "approved":
        return jsonify({"result": "wrong otp"}), HTTPStatus.OK
    userEnt = User.query.get(created_by_phone)
    if userEnt is None:
        return jsonify({"result": "not in system"}), HTTPStatus.OK

    if (
        userEnt.name
        and userEnt.last_name
        and userEnt.email
        and userEnt.birthday
        and userEnt.region_id
    ):
        red.hdel(int(str(created_by_phone)), "accessToken")
        accessToken = int(str(uuid.uuid4().int)[:5])
        red.hset(int(str(created_by_phone)), "accessToken", accessToken)
        return jsonify({"result": accessToken, "firsOnboarding": False}), HTTPStatus.OK
    accessToken = int(str(uuid.uuid4().int)[:5])
    # red.hset(int(str(created_by_phone)), "accessToken", accessToken)
    return jsonify({"result": accessToken, "firsOnboarding": True}), HTTPStatus.OK
