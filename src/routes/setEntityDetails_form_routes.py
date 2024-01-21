import json
from http import HTTPStatus
from itertools import product
from os import sys, path

from flask import Blueprint, request, jsonify, redirect
import boto3, botocore

from werkzeug.utils import secure_filename

from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.cluster_model import Cluster
from ..models.institution_model import Institution

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import db, app
from ..models.user_model import user1
setEntityDetails_form_blueprint = Blueprint('setEntityDetails_form', __name__, url_prefix='/setEntityDetails_form')
@setEntityDetails_form_blueprint.route('/setByType', methods=['PUT'])
def setEntityDetailsByType():
       data=request.json
       try:
           typeOfSet = data['typeOfSet']
           print(typeOfSet)
           updatedEnt=None
           if typeOfSet=="Onboarding":
               entityId =str(data['entityId'])[3:]
               print(entityId)
               atrrToBeSet = data['atrrToBeSet']
               updatedEnt = user1.query.get(entityId)
               for key in atrrToBeSet:
                   if key == "city":
                       CityId = db.session.query(City).filter(
                           City.name == str(atrrToBeSet[key])).first()
                       setattr(updatedEnt, key,CityId )
                       continue
                   if key == "region":
                       clusterId = db.session.query(Cluster).filter(
                           Cluster.name == str(atrrToBeSet[key])).first()
                       setattr(updatedEnt, key, clusterId)
                       continue
                   setattr(updatedEnt, key, atrrToBeSet[key])
               db.session.commit()

           if typeOfSet == "userProfile":
                   entityId =str(data['entityId'])[3:]
                   print(entityId);
                   atrrToBeSet = data['atrrToBeSet']
                   print(atrrToBeSet);
                   updatedEnt = user1.query.get(entityId)
                   for key in atrrToBeSet:
                       setattr(updatedEnt, key, str(atrrToBeSet[key]))
                   db.session.commit()

           if typeOfSet ==  "apprenticeProflie":
                   entityId =str(data['entityId'])[3:]
                   print(entityId)
                   atrrToBeSet = data['atrrToBeSet']
                   updatedEnt = Apprentice.query.get(entityId)
                   for key in atrrToBeSet:
                       if key== "accompany_id":
                           setattr(updatedEnt, key, str(atrrToBeSet[key])[3:])
                           continue
                       setattr(updatedEnt, key, atrrToBeSet[key])
                   db.session.commit()
           if typeOfSet == "mosadProflie":
               entityId = str(data['entityId'])
               print(entityId)
               atrrToBeSet = data['atrrToBeSet']
               updatedEnt = Institution.query.get(entityId)
               for key in atrrToBeSet:
                   setattr(updatedEnt, key, atrrToBeSet[key])
               db.session.commit()
       except Exception as e:  # work on python 3.x
           return jsonify({'result': str(e)}), HTTPStatus.OK

       if updatedEnt:
               # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
                # TODO: add contact form to DB
                return jsonify({'result': 'success'}), HTTPStatus.OK
       return jsonify({'result': 'error'}), HTTPStatus.OK

@setEntityDetails_form_blueprint.route("/uploadPhoto", methods=["POST"])
def upload_file():
    if "user_file" not in request.files:
        return "No user_file key in request.files"

    file = request.files["user_file"]

    if file.filename == "":
        return "Please select a file"

    if file:
        file.filename = secure_filename(file.filename)
        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
        return str(output)

    else:
        return redirect("/")

def upload_file_to_s3(file, bucket_name, acl="public-read"):
    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type    #Set appropriate content type as per the file
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], file.filename)

app.config['S3_BUCKET'] = "S3_BUCKET_NAME"
app.config['S3_KEY'] = "AWS_ACCESS_KEY"
app.config['S3_SECRET'] = "AWS_ACCESS_SECRET"
app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'


s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)