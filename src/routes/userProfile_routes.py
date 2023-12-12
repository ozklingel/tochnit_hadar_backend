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
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

userProfile_form_blueprint = Blueprint('userProfile_form', __name__, url_prefix='/userProfile_form')

@userProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        print(request.form.to_dict())
        data = request.form.to_dict()
        created_by_id = data['userId'][4:]
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
    created_by_id = request.args.get('userId')[4:]
    print(created_by_id)

    apprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id).all()
    print(apprenticeList)
    my_dict = []
    for noti in apprenticeList:
        my_dict.append(
            {"id": str(noti.id), "name": str(noti.name), "last_name": str(noti.last_name),
             "institution_id": noti.institution_id, "hadar_plan_session ": str(noti.hadar_plan_session), "serve_type": noti.serve_type,
             "marriage_status": str(noti.marriage_status), "base_address": str(noti.base_address),
             "phone": noti.phone, "email": noti.email,
             "birthday": time.mktime(datetime.strptime(noti.birthday.strip(),'%Y-%m-%d').timetuple()) if noti.birthday is not None else None, "wife_phone": noti.wife_phone,
             "wife_name": noti.wife_name, "marriage_date": noti.marriage_date,
             "city_id": noti.city_id, "father_phone": noti.father_phone,
             "father_email": noti.father_email,
             "father_name": noti.father_name, "mother_email": noti.mother_email,
             "mother_phone": noti.mother_phone, "mother_name": noti.mother_name,
             "high_school_teacher_phone": noti.high_school_teacher_phone, "high_school_teacher": noti.high_school_teacher,
             "teacher_grade_b_phone": noti.teacher_grade_b_phone, "teacher_grade_b": noti.teacher_grade_b, "teacher_grade_a": noti.teacher_grade_a,
             "pre_army_institution": noti.pre_army_institution, "army_role": noti.army_role, "unit_name": noti.unit_name,
             "accompany_connect_status": noti.accompany_connect_status, "spirit_status": noti.spirit_status, "paying": noti.paying,
             "release_date": noti.release_date, "recruitment_date": noti.recruitment_date
                , "militaryUpdatedDateTime": time.mktime(noti.militaryupdateddatetime.timetuple() ) if noti.birthday is not None else None,
             "militaryPositionOld": noti.militarypositionold,"educationalInstitution": noti.educationalinstitution
                , "educationFaculty": noti.educationfaculty, "workOccupation": noti.workoccupation,
             "workType": noti.worktype,"workPlace": noti.workplace, "workStatus": noti.workstatus

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
    created_by_id = request.args.get('userId')[4:]
    userEnt = user1.query.get(created_by_id)
    if userEnt:
        myApprenticesNamesList=getmyApprenticesNames(created_by_id)
        list = {"id":str(userEnt.id), "firstName":userEnt.name, "lastName":userEnt.last_name, "dateOfBirthInMsSinceEpoch":userEnt.birthday, "email":userEnt.email,
                       "city":userEnt.address, "region":str(userEnt.cluster_id), "role":str(userEnt.role_id), "institution":str(userEnt.institution_id), "cluster":str(userEnt.cluster_id),
                       "apprentices":str(myApprenticesNamesList), "phone":userEnt.phone, "photo_path":userEnt.photo_path}
        return jsonify(results="success",attributes=list), HTTPStatus.OK
    else:
        return jsonify(ErrorDescription="no such id"), HTTPStatus.OK



def getmyApprenticesNames(created_by_id):

    apprenticeList = db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name).filter(Apprentice.accompany_id == created_by_id).all()
    names=""
    print(created_by_id)
    print(apprenticeList)
    for noti in apprenticeList:
        if noti.name.replace(" ", "")!="":
            names+=str(noti.name).replace(" ", "")
            names +=" "
            names+=str(noti.last_name).replace(" ", "")
            names+=","
    return names[:-1]
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@userProfile_form_blueprint.route('/myApprentice', methods=['GET'])
def getmyApprentice_form():
    created_by_id = request.args.get('userId')[4:]
    apprenticeId = request.args.get('apprenticeId')[4:]
    print(created_by_id)
    print(apprenticeId)
    apprenticeList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id,Apprentice.id == apprenticeId).first()
    print(apprenticeList)
    my_dict = []
    for noti in apprenticeList:
        my_dict.append(
            {"id": noti.id, "PName": noti.name, "last_name": noti.last_name,
             "institution_id": noti.institution_id, "hadar_plan_session ": noti.hadar_plan_session, "serve_type": noti.serve_type,
             "family_status": noti.marriage_status, "base_address": noti.base_address
             , "phone": noti.phone, "birthday": time.mktime(datetime.strptime(noti.birthday.strip(),'%Y-%m-%d').timetuple()) if noti.birthday is not None else None, "email": noti.email
             , "marriage_status": noti.marriage_status, "marriage_date": noti.marriage_date, "wife_name": noti.wife_name
             , "wife_phone": noti.wife_phone, "city_id": noti.city_id, "address": noti.address
             , "father_name": noti.father_name, "father_phone": noti.father_phone, "mother_name": noti.mother_name
             , "mother_phone": noti.mother_phone, "mother_email": noti.mother_email, "high_school_name": noti.high_school_name
             , "high_school_teacher": noti.high_school_teacher, "high_school_teacher_phone": noti.high_school_teacher_phone, "pre_army_institution": noti.pre_army_institution
                , "teacher_grade_a": noti.teacher_grade_a, "teacher_grade_a_phone": noti.teacher_grade_a_phone, "base_address": noti.base_address
                , "teacher_grade_b": noti.teacher_grade_b, "recruitment_date": noti.recruitment_date, "release_date": noti.release_date
                , "teacher_grade_b_phone": noti.teacher_grade_b_phone, "unit_name": noti.unit_name, "paying": noti.paying
                , "accompany_connect_status": noti.accompany_connect_status, "army_role": noti.army_role, "spirit_status": noti.spirit_status
                , "militaryUpdatedDateTime": time.mktime(noti.militaryupdateddatetime.timetuple()), "militaryPositionOld": noti.militarypositionold,"educationalInstitution": noti.educationalinstitution
                , "educationFaculty": noti.educationfaculty, "workOccupation": noti.workoccupation,
             "workType": noti.worktype,"workPlace": noti.workplace, "workStatus": noti.workstatus

             })

    if apprenticeList is None or len(my_dict) == 0:
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"Apparentice_atrr":my_dict[0]}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

