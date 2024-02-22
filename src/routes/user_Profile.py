import json
import pickle
from datetime import datetime
import time
import uuid
from enum import Enum

import boto3

import werkzeug
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.contact_form_model import ContactForm
from src.models.notification_model import notifications
from src.models.role import role_dict
from src.models.user_model import user1
from src.models.visit_model import Visit

userProfile_form_blueprint = Blueprint('userProfile_form', __name__, url_prefix='/userProfile_form')
role_name = Enum('Color', ['melave', 'racaz_mosad', 'racaz_eshcol'])
@userProfile_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        userId = data['userId'][3:]
        res = db.session.query(ContactForm).filter(ContactForm.created_for_id == userId, ).delete()
        res = db.session.query(ContactForm).filter(ContactForm.created_by_id == userId, ).delete()
        res = db.session.query(notifications).filter(notifications.userid == userId, ).delete()

        res = db.session.query(user1).filter(user1.id == userId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@userProfile_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    userId = request.args.get('userId')[3:]
    print(userId)
    data = request.json
    updatedEnt = user1.query.get(userId)
    for key in data:
        setattr(updatedEnt, key, data[key])
    db.session.commit()
    if updatedEnt:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
    return jsonify({'result': 'error'}), HTTPStatus.OK
@userProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        created_by_id = request.args.get('userId')[3:]
        print(created_by_id)
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
        updatedEnt.photo_path="https://th01-s3.s3.eu-north-1.amazonaws.com/"+new_filename
        db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
        return jsonify({'result': 'success', 'image path': new_filename}), HTTPStatus.OK




@userProfile_form_blueprint.route('/myApprentices', methods=['GET'])
def getmyApprentices_form():
    created_by_id = request.args.get('userId')[3:]
    print(created_by_id)
    user1ent = db.session.query(user1.role_id,user1.institution_id,user1.eshcol).filter(user1.id==created_by_id).first()
    if user1ent.role_id=="0":
        apprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id).all()
    if user1ent.role_id=="1":
        apprenticeList = db.session.query(Apprentice).filter(Apprentice.institution_id == user1ent.institution_id).all()
    if user1ent.role_id == "2":
        apprenticeList = db.session.query(Apprentice).filter(Apprentice.eshcol == user1ent.eshcol).all()

    print(apprenticeList)
    my_dict = []

    for noti in apprenticeList:
        print(noti.city_id)
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        print(city)
        reportList = db.session.query(Visit.id).filter(Visit.ent_reported == noti.id).all()
        eventlist = db.session.query(notifications.id,notifications.event,notifications.details,notifications.date).filter(
                                                                           notifications.apprenticeid == noti.id,
                                                                           notifications.numoflinesdisplay == 3).all()
        base_id = db.session.query(Base.id).filter(Base.id == int(noti.base_address)).first()
        base_id = base_id[0] if base_id else 0
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
                    "city": city.name if city else "",
                    "cityId": noti.city_id,
                    "street": noti.address,
                    "houseNumber": "1",
                    "apartment": "1",
                    "region": str(city.cluster_id) if city else "",
                    "entrance": "a",
                    "floor": "1",
                    "postalCode": "12131",
                    "lat": 32.04282620026557,#no need city cord
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

                  [{"id" :str(row[0]),"title":row[1],"description":row[2],"date" : toISO(row[3])} for row in eventlist]

                , "id": str(noti.id), "thMentor": str(noti.accompany_id),
             "militaryPositionNew": str(noti.militaryPositionNew)
                , "avatar": noti.photo_path if noti.photo_path is not None else 'https://www.gravatar.com/avatar' , "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": str(noti.institution_id), "thPeriod": str(noti.hadar_plan_session),
             "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(base_id),
             "phone": noti.phone, "email": noti.email, "teudatZehut": noti.teudatZehut,
             "birthday": toISO(noti.birthday),  "marriage_date": toISO(noti.marriage_date),
             "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
             "unit_name": noti.unit_name,
             "onlineStatus": noti.accompany_connect_status, "matsber": str(noti.spirit_status),
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
        return jsonify([])
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
        list = {"id":str(userEnt.id), "firstName":userEnt.name, "lastName":userEnt.last_name, "date_of_birth": toISO(userEnt.birthday), "email":userEnt.email,
                       "city":city.name, "region":str(userEnt.cluster_id), "role":str(userEnt.role_id), "institution":str(userEnt.institution_id), "cluster":str(userEnt.cluster_id),
                       "apprentices":myApprenticesNamesList, "phone":str(userEnt.id),"teudatZehut":str(userEnt.teudatZehut), "avatar":userEnt.photo_path if userEnt.photo_path is not None else 'https://www.gravatar.com/avatar'}
        return jsonify(list), HTTPStatus.OK
    else:
        return jsonify(results="no such id"), HTTPStatus.OK



def getmyApprenticesNames(created_by_id):

    apprenticeList = db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name).filter(Apprentice.accompany_id == created_by_id).all()
    return [{"id": str(row[0]), "name": row[1], "last_name": row[2]} for row in apprenticeList]

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
        reportList = db.session.query(Visit.id).filter(Visit.ent_reported == noti.id).all()
        eventlist = db.session.query(notifications.id, notifications.event, notifications.details,notifications.date).filter(
            notifications.apprenticeid == noti.id,
            notifications.numoflinesdisplay == 3).all()
        base_id = db.session.query(Base.id).filter(Base.id == int(noti.base_address)).first()
        base_id = base_id[0] if base_id else 0

        print("base_id",base_id)
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
                 [{"id": row[0], "title": row[1], "description": row[2],"date" : toISO(row[3])} for row in eventlist]
                , "id": str(noti.id), "thMentor": str(noti.accompany_id),
             "militaryPositionNew": str(noti.militaryPositionNew)
                , "avatar": noti.photo_path if noti.photo_path is not None else 'https://www.gravatar.com/avatar', "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": str(noti.institution_id), "thPeriod": str(noti.hadar_plan_session),
             "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "militaryCompoundId": str(base_id),
             "phone": noti.phone, "email": noti.email,
             "birthday": toISO(noti.birthday), "marriage_date": toISO(noti.marriage_date),
             "highSchoolInstitution": noti.highSchoolInstitution, "army_role": noti.army_role,
             "unit_name": noti.unit_name,
             "onlineStatus": noti.accompany_connect_status, "matsber": str(noti.spirit_status),
             "militaryDateOfDischarge": toISO(noti.release_date),
             "militaryDateOfEnlistment": toISO(noti.recruitment_date)
                , "militaryUpdatedDateTime": toISO(noti.militaryupdateddatetime),
             "militaryPositionOld": noti.militarypositionold, "educationalInstitution": noti.educationalinstitution
                , "educationFaculty": noti.educationfaculty, "workOccupation": noti.workoccupation,
             "workType": noti.worktype, "workPlace": noti.workplace, "workStatus": noti.workstatus

             })

    if noti is None or len(my_dict) == 0:
        # acount not found
        return jsonify({"result": "no such id"}), HTTPStatus.OK
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