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
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

userProfile_form_blueprint = Blueprint('userProfile_form', __name__, url_prefix='/userProfile_form')

@userProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        print(request.form.to_dict())
        data = request.form.to_dict()
        created_by_id = data['userId'][3:]
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
        updatedEnt = user1.query.get(created_by_id)
        updatedEnt.photo_path=new_filename
        db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
        return jsonify({'result': 'success', 'image path': new_filename}), HTTPStatus.OK




@userProfile_form_blueprint.route('/myApprentices', methods=['GET'])
def getmyApprentices_form():
    created_by_id = request.args.get('userId')[3:]
    print(created_by_id)

    apprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id).all()
    print(apprenticeList)
    my_dict = []
    for noti in apprenticeList:
        print(noti.city_id)
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        print(city)
        reportList = db.session.query(Visit.id).filter(Visit.apprentice_id == noti.id).all()
        eventlist = db.session.query(notifications.id,notifications.event,notifications.details).filter(
                                                                           notifications.apprenticeid == noti.id,
                                                                           notifications.numoflinesdisplay == 3).all()
        my_dict.append(
            {"highSchoolRavMelamed_phone": noti.high_school_teacher_phone
                     ,"highSchoolRavMelamed_name": noti.high_school_teacher,
                  "highSchoolRavMelamed_email": noti.high_school_teacher_email,

                 "thRavMelamedYearA_name": noti.teacher_grade_a,
                 "thRavMelamedYearA_phone": noti.teacher_grade_a_phone,
                 "thRavMelamedYearA_email": noti.teacher_grade_a_email,

                 "thRavMelamedYearB_name": noti.teacher_grade_b,
                 "thRavMelamedYearB_phone": noti.teacher_grade_b_phone,
                 "thRavMelamedYearB_email": noti.teacher_grade_b_email,
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
             "contact1_first_name": noti.contact1_first_name,
             "contact1_last_name": noti.contact1_last_name,
             "contact1_phone": noti.contact1_phone,
             "contact1_email": noti.contact1_email,
             "contact1_relation": noti.contact1_relation,
             "contact2_first_name": noti.contact2_first_name,
             "contact2_last_name": noti.contact2_last_name,
             "contact2_phone": noti.contact2_phone,
             "contact2_email": noti.contact2_email,
             "contact2_relation": noti.contact2_relation,
             "contact3_first_name": noti.contact3_first_name,
             "contact3_last_name": noti.contact3_last_name,
             "contact3_phone": noti.contact3_phone,
             "contact3_email": noti.contact3_email,
             "contact3_relation": noti.contact3_relation,

             "reports": [
                 [str(i[0]) for i in [tuple(row) for row in reportList]]
             ],
             "events": [
                 [str(i[0]) for i in  [tuple(row) for row in eventlist]]
             ]
                , "id": str(noti.id), "thMentor": str(noti.accompany_id),
             "militaryPositionNew": str(noti.militaryPositionNew)
                , "avatar": noti.photo_path if noti.photo_path!="" else "https://www.gravatar.com/avatar", "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": noti.institution_id, "thPeriod": str(noti.hadar_plan_session),
             "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(noti.base_address),
             "phone": noti.phone, "email": noti.email,
             "birthday": toISO(noti.birthday),  "marriage_date": toISO(noti.marriage_date),
             "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
             "unit_name": noti.unit_name,
             "onlineStatus": noti.accompany_connect_status, "matsber": noti.spirit_status, "paying": noti.paying,
             "militaryDateOfDischarge": toISO(noti.release_date),
             "militaryDateOfEnlistment": toISO(noti.recruitment_date)
                , "militaryUpdatedDateTime": toISO(noti.militaryupdateddatetime),
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


@userProfile_form_blueprint.route('/getProfileAtributes', methods=['GET'])
def getProfileAtributes_form():
    print(request.headers.get('Authorization'))
    created_by_id = request.args.get('userId')[3:]
    userEnt = user1.query.get(created_by_id)
    if userEnt:
        myApprenticesNamesList=getmyApprenticesNames(created_by_id)
        city = db.session.query(City).filter(City.id == userEnt.city_id).first()
        list = {"id":str(userEnt.id), "firstName":userEnt.name, "lastName":userEnt.last_name, "dateOfBirthInMsSinceEpoch": toISO(userEnt.birthday), "email":userEnt.email,
                       "city":city.name, "region":str(userEnt.cluster_id), "role":str(userEnt.role_id), "institution":str(userEnt.institution_id), "cluster":str(userEnt.cluster_id),
                       "apprentices":str(myApprenticesNamesList), "phone":str(userEnt.id),"teudatZehut":userEnt.teudatZehut, "avatar":userEnt.photo_path}
        return jsonify(results="success",attributes=list), HTTPStatus.OK
    else:
        return jsonify(ErrorDescription="no such id"), HTTPStatus.OK



def getmyApprenticesNames(created_by_id):

    apprenticeList = db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name).filter(Apprentice.accompany_id == created_by_id).all()
    names=""
    print("created_by_id" ,created_by_id)
    print("apprenticeList",apprenticeList)
    for noti in apprenticeList:
        if noti.name:
            names+=str(noti.name)
            names +=" "
            names+=str(noti.last_name)
            names+=","
    return names[:-1]
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@userProfile_form_blueprint.route('/myApprentice', methods=['GET'])
def getmyApprentice_form():
    created_by_id = request.args.get('userId')[3:]
    apprenticeId = request.args.get('apprenticeId')[3:]
    print(created_by_id)
    print(apprenticeId)
    noti = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id,Apprentice.id == apprenticeId).first()
    my_dict = []
    if noti:
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        reportList = db.session.query(Visit.id).filter(Visit.apprentice_id == noti.id).all()
        eventlist = db.session.query(notifications.id, notifications.event, notifications.details).filter(
            notifications.apprenticeid == noti.id,
            notifications.numoflinesdisplay == 3).all()
        my_dict.append(
            {"highSchoolRavMelamed_phone": noti.high_school_teacher_phone
                , "highSchoolRavMelamed_name": noti.high_school_teacher,
             "highSchoolRavMelamed_email": noti.high_school_teacher_email,

             "thRavMelamedYearA_name": noti.teacher_grade_a,
             "thRavMelamedYearA_phone": noti.teacher_grade_a_phone,
             "thRavMelamedYearA_email": noti.teacher_grade_a_email,

             "thRavMelamedYearB_name": noti.teacher_grade_b,
             "thRavMelamedYearB_phone": noti.teacher_grade_b_phone,
             "thRavMelamedYearB_email": noti.teacher_grade_b_email,
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
             "contact1_first_name": noti.contact1_first_name,
             "contact1_last_name": noti.contact1_last_name,
             "contact1_phone": noti.contact1_phone,
             "contact1_email": noti.contact1_email,
             "contact1_relation": noti.contact1_relation,
             "contact2_first_name": noti.contact2_first_name,
             "contact2_last_name": noti.contact2_last_name,
             "contact2_phone": noti.contact2_phone,
             "contact2_email": noti.contact2_email,
             "contact2_relation": noti.contact2_relation,
             "contact3_first_name": noti.contact3_first_name,
             "contact3_last_name": noti.contact3_last_name,
             "contact3_phone": noti.contact3_phone,
             "contact3_email": noti.contact3_email,
             "contact3_relation": noti.contact3_relation,

             "reports":
                 [str(i[0]) for i in [tuple(row) for row in reportList]]
             ,
             "events":
                 [str(i[0]) for i in [tuple(row) for row in eventlist]]

                , "id": str(noti.id), "thMentor": str(noti.accompany_id),
             "militaryPositionNew": str(noti.militaryPositionNew)
                , "avatar": noti.photo_path if noti.photo_path!="" else "https://www.gravatar.com/avatar" , "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": noti.institution_id, "thPeriod": str(noti.hadar_plan_session),
             "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(noti.base_address),
             "phone": noti.phone, "email": noti.email,
             "birthday": toISO(noti.birthday), "marriage_date": toISO(noti.marriage_date),
             "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
             "unit_name": noti.unit_name,
             "onlineStatus": noti.accompany_connect_status, "matsber": noti.spirit_status, "paying": noti.paying,
             "militaryDateOfDischarge": toISO(noti.release_date),
             "militaryDateOfEnlistment": toISO(noti.recruitment_date)
                , "militaryUpdatedDateTime": toISO(noti.militaryupdateddatetime),
             "militaryPositionOld": noti.militarypositionold, "educationalInstitution": noti.educationalinstitution
                , "educationFaculty": noti.educationfaculty, "workOccupation": noti.workoccupation,
             "workType": noti.worktype, "workPlace": noti.workplace, "workStatus": noti.workstatus

             })

    if noti is None or len(my_dict) == 0:
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict[0]), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

def toISO(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None