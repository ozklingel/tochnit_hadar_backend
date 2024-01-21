import json
import pickle
from datetime import datetime
import time
import uuid
import boto3

import werkzeug
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

institutionProfile_form_blueprint = Blueprint('institutionProfile_form', __name__, url_prefix='/institutionProfile_form')

@institutionProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        print(request.form.to_dict())
        data = request.form.to_dict()
        created_by_id = data['institution_id'][3:]
        print(request.files)
        imagefile = request.files['image']
        #filename = werkzeug.utils.secure_filename(imagefile.filename)
        #print("\nReceived image File name : " + imagefile.filename)
        #imagefile.save( filename)
        new_filename = uuid.uuid4().hex + '.' + imagefile.filename.rsplit('.', 1)[1].lower()
        bucket_name = "th01-s3"
        session = boto3.Session()
        s3_client = session.client('s3',
                            aws_access_key_id=AWS_access_key_id,
                            aws_secret_access_key=AWS_secret_access_key)
        s3 = boto3.resource('s3',
                            aws_access_key_id=AWS_access_key_id,
                            aws_secret_access_key=AWS_secret_access_key)
        print(new_filename)
        try:
            s3_client.upload_fileobj(imagefile, bucket_name, new_filename)
        except:
            return jsonify({'result': 'faild', 'image path': new_filename}), HTTPStatus.OK
        updatedEnt = Institution.query.get(id)
        updatedEnt.photo_path=new_filename
        db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
        return jsonify({'result': 'success', 'image path': new_filename}), HTTPStatus.OK




@institutionProfile_form_blueprint.route('/apprentice_and_melave', methods=['GET'])
def getmyApprentices_form():
    institution_id = int(request.args.get('institution_id'))
    print(institution_id)
    melave_List = db.session.query(user1).filter(user1.institution_id== institution_id,user1.role_id=="0").all()
    apprenticeList = db.session.query(Apprentice).filter(Apprentice.institution_id == institution_id).all()
    print(melave_List)
    my_dict = []
    for noti in melave_List:
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        my_dict.append(
            {
                "role": "מלווה",
                "first_name": noti.name,
                "last_name": noti.last_name,
                "address": {
                    "country": "IL",
                    "city": city.name,
                    "cityId": noti.city_id,
                    "street": noti.address,
                    "houseNumber": "1",
                    "apartment": "1",
                    "region": str(city.cluster_id),
                    "entrance": "a",
                    "floor": "1",
                    "postalCode": "12131",
                    "lat": 32.04282620026557,
                    "lng": 34.75186193813887
                },
            })
        print(my_dict)
    for noti in apprenticeList:
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        my_dict.append(
            {

                "address": {
                    "country": "IL",
                    "city": city.name if city is  not None else "",
                    "cityId": noti.city_id,
                    "street": noti.address,
                    "houseNumber": "1",
                    "apartment": "1",
                    "region": str(city.cluster_id) if city is  not None else "",
                    "entrance": "a",
                    "floor": "1",
                    "postalCode": "12131",
                    "lat": 32.04282620026557,
                    "lng": 34.75186193813887
                },
                 "id": str(noti.id), "thMentor": str(noti.accompany_id),
             "militaryPositionNew": str(noti.militaryPositionNew)
                , "avatar": noti.photo_path if noti.photo_path is not None else 'https://www.gravatar.com/avatar' , "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": str(noti.institution_id), "thPeriod": str(noti.hadar_plan_session),
             "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(noti.base_address),
             "phone": noti.phone, "email": noti.email, "teudatZehut": noti.teudatZehut,
             "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
             "unit_name": noti.unit_name,
             "onlineStatus": noti.accompany_connect_status, "matsber": str(noti.spirit_status),

             "militaryPositionOld": noti.militarypositionold, "educationalInstitution": noti.educationalinstitution
                , "educationFaculty": noti.educationfaculty, "workOccupation": noti.workoccupation,
             "workType": noti.worktype, "workPlace": noti.workplace, "workStatus": noti.workstatus

             })

    if apprenticeList is None:
        # acount not found
        return jsonify({"result":"Wrong id"})
    if apprenticeList ==[]:
        # acount not found
        return jsonify({"result":"empty"})
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@institutionProfile_form_blueprint.route('/getProfileAtributes', methods=['GET'])
def getProfileAtributes_form():
    print(request.headers.get('Authorization'))
    institution_id = request.args.get('institution_id')
    institution_Ent = Institution.query.get(institution_id)
    if institution_Ent:
        city = db.session.query(City).filter(str(City.id) == institution_Ent.city_id).first()
        list = {"id":str(institution_Ent.id), "name":institution_Ent.name, "owner_id":institution_Ent.owner_id,
                "contact_phone":institution_Ent.contact_phone,
                       "city":city.name if city is not None else "", "contact_name":str(institution_Ent.contact_name), "phone":str(institution_Ent.phone), "address":str(institution_Ent.address),
                "avatar":institution_Ent.logo_path if institution_Ent.logo_path is not None else 'https://www.gravatar.com/avatar',
                "shluha":str(institution_Ent.shluha), "roshYeshiva_phone":institution_Ent.roshYeshiva_phone, "roshYeshiva_name":institution_Ent.roshYeshiva_name,
                "admin_phone":str(institution_Ent.admin_phone), "admin_name":institution_Ent.admin_name}
        return jsonify(list), HTTPStatus.OK
    else:
        return jsonify(results="no such id"), HTTPStatus.OK

@institutionProfile_form_blueprint.route("/add_mosad", methods=['post'])
def add_mosad():
    data = request.json
    print(data)
    name = data['name']
    shluha = data['shluha']
    roshYeshiva_phone = data['roshYeshiva_phone']
    roshYeshiva_name = data['roshYeshiva_name']
    admin_phone = data['admin_phone']
    admin_name = data['admin_name']
    contact_name = data['contact_name']
    contact_phone = data['contact_phone']
    city = data['city']+" " if data['city'] is not None else None
    phone = data['phone']
    print(city)
    try:
        cityid = db.session.query(City.id).filter(City.name==city).first()
        print(cityid)
        Institution1 = Institution(
            id=int(str(uuid.uuid4().int)[:5]),
            name=name,
            phone=phone,
            city_id=cityid[0] if cityid is not None else "",
            shluha =shluha,
            roshYeshiva_phone = roshYeshiva_phone,
            roshYeshiva_name = roshYeshiva_name,
            admin_phone = admin_phone,
            admin_name =admin_name,
            contact_name =contact_name,
            contact_phone = contact_phone
        )
        db.session.add(Institution1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if Institution1:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK


