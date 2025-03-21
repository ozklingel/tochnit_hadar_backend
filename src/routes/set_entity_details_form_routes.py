from http import HTTPStatus
import re

from flask import Blueprint, request, jsonify
import boto3

from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.region_model import Region
from ..models.institution_model import Institution

from src.services import db

from ..models.user_model import User

setEntityDetails_form_blueprint = Blueprint('setEntityDetails_form', __name__, url_prefix='/setEntityDetails_form')


@setEntityDetails_form_blueprint.route('/setByType', methods=['PUT'])
def setEntityDetailsByType():
    if correct_auth() == False:
        return jsonify({'result': "wrong access token"}), HTTPStatus.OK
    data = request.json
    try:
        typeOfSet = data['typeOfSet']
        updatedEnt = None
        if typeOfSet == "Onboarding":
            entityId = str(data['entityId'])
            atrrToBeSet = data['atrrToBeSet']
            updatedEnt = User.query.get(entityId)
            for key in atrrToBeSet:
                if key == "city":
                    CityId = db.session.query(City).filter(
                        City.name == str(atrrToBeSet[key])).first()
                    setattr(updatedEnt, key, CityId)
                    continue
                if key == "region":
                    clusterId = db.session.query(Region).filter(
                        Region.name == str(atrrToBeSet[key])).first()
                    setattr(updatedEnt, key, clusterId)
                    continue
                if key == "email":
                    if validate_email(atrrToBeSet[key]):
                        setattr(updatedEnt, key, atrrToBeSet[key])
                    else:
                        return jsonify({'result': "email -wrong format"}), 401
                if key == "birthday":
                    if validate_date(atrrToBeSet[key]):
                        setattr(updatedEnt, key, atrrToBeSet[key])
                    else:
                        return jsonify({'result': "birthday -wrong format"}), 401
                setattr(updatedEnt, key, atrrToBeSet[key])
            db.session.commit()

        if typeOfSet == "userProfile":
            entityId = str(data['entityId'])
            atrrToBeSet = data['atrrToBeSet']
            updatedEnt = User.query.get(entityId)
            for key in atrrToBeSet:
                setattr(updatedEnt, key, str(atrrToBeSet[key]))
            db.session.commit()

        if typeOfSet == "apprenticeProflie":
            entityId = str(data['entityId'])
            atrrToBeSet = data['atrrToBeSet']
            updatedEnt = Apprentice.query.get(entityId)
            for key in atrrToBeSet:
                if key == "accompany_id":
                    setattr(updatedEnt, key, str(atrrToBeSet[key]))
                    continue
                setattr(updatedEnt, key, atrrToBeSet[key])
            db.session.commit()
        if typeOfSet == "mosadProflie":
            entityId = str(data['entityId'])
            atrrToBeSet = data['atrrToBeSet']
            updatedEnt = Institution.query.get(entityId)
            for key in atrrToBeSet:
                setattr(updatedEnt, key, atrrToBeSet[key])
            db.session.commit()
    except Exception as e:  # work on python 3.x
        return jsonify({'result': str(e)}), 401

    if updatedEnt:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
    return jsonify({'result': 'error'}), HTTPStatus.OK


def upload_file_to_s3(file, bucket_name, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    from app import app
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type  # Set appropriate content type as per the file
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], file.filename)


s3 = boto3.client(
    "s3"
)


def validate_email(email):
    # Regular expression for email validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email) is not None


def validate_date(date):
    # Regular expression for date validation in the format YYYY-MM-DD
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(date_pattern, date) is not None
