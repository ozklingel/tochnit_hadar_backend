import re

from flask import request

import config
from src.services import red


def validate_email(email):
    # Regular expression for email validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(email_pattern, email) is not None


def validate_date(date):
    # Regular expression for date validation in the format YYYY-MM-DD
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    return re.match(date_pattern, date) is not None


def correct_auth(external=True):
    if config.Authorization_is_On and external:
        userId = request.args.get("userId")
        accessToken = request.headers.get("Authorization")
        redisaccessToken = red.hget(userId, "accessToken").decode("utf-8")
        if redisaccessToken != accessToken:
            return False
        return True
    return True


def parse_payload(data):
    result_dict = {}
    for key, value in data.items():
        try:
            result_dict[key] = value
        except Exception as e:
            return e
    return result_dict


def verify_access_token():
    user_access_token = request.args.get("accessToken")
    userId = request.args.get("userId")
    redisaccessToken = red.hget(userId, "accessToken").decode("utf-8")
    if str(user_access_token) == str(redisaccessToken):
        return True
    return False
