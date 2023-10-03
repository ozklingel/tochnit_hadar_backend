from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db
from src.models.apprentice_model import Apprentice
from src.models.user_model import user1

userProfile_form_blueprint = Blueprint('userProfile_form', __name__, url_prefix='/userProfile_form')


@userProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    raw_images = []
    images = request.files.getlist("file")
    image_names = []
    for image in images:
        image_name = image.filename
        image_names.append(image_name)
        # img_raw = tf.image.decode_image(
        #    open(image_name, 'rb').read(), channels=3)
        # raw_images.append(img_raw)
    if image_names:
        print(f'image form: subject: [ image: {image_names}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'image form': request.form}), HTTPStatus.OK


@userProfile_form_blueprint.route('/myApprentices', methods=['GET'])
def getmyApprentices_form():
    created_by_id = request.args.get('created_by_id')
    print(created_by_id)

    reportList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        my_dict.append(
            {"id": str(noti.id), "FName": str(noti.name), "PName": str(noti.last_name),
             "institution_id": noti.institution_id, "hadar_plan_session ": str(noti.hadar_plan_session), "serve_type": noti.serve_type,
             "family_status": str(noti.marriage_status), "base_address": str(noti.base_address)})

    if reportList is None:
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@userProfile_form_blueprint.route('/getProfileAtributes', methods=['GET'])
def getProfileAtributes_form():
    created_by_id = request.args.get('userId')
    userEnt = user1.query.get(created_by_id)

    if userEnt:
#apprentice to id
        myApprenticesNamesList=getmyApprenticesNames(created_by_id)
        list = {"id":userEnt.id, "Pname":userEnt.name, "Fname":userEnt.last_name, "birthDay":userEnt.birthday, "email":userEnt.email,
                       "town":userEnt.address, "area":userEnt.cluster_id, "userRole":userEnt.role_id, "Mosad":userEnt.institution_id, "Eshcol":userEnt.cluster_id,
                       "apprenticeList":str(myApprenticesNamesList), "phone":userEnt.phone}
        return jsonify(results=list), HTTPStatus.OK
    else:
        return jsonify(ErrorDescription="no such id"), HTTPStatus.OK



def getmyApprenticesNames(created_by_id):

    reportList = db.session.query(Apprentice.id,Apprentice.name,Apprentice.last_name).filter(Apprentice.accompany_id == created_by_id).all()
    names=""
    for noti in reportList:
        if noti.name.replace(" ", "")!="":
            names+=str(noti.name)
            names+=str(noti.last_name)
            names+=","

        '''
        my_dict.append(
            {"id": str(noti.id), "FName": str(noti.name), "PName": str(noti.last_name)})
'''
    return names.replace(" ", "")[:-1]
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@userProfile_form_blueprint.route('/myApprentice', methods=['GET'])
def getmyApprentice_form():
    print("created_by_id")
    created_by_id = request.args.get('created_by_id')
    apprenticeId = request.args.get('apprenticeId')
    print(created_by_id)
    reportList = db.session.query(Apprentice).filter(Apprentice.accompany_id == created_by_id,Apprentice.id == apprenticeId).all()
    print(reportList)
    my_dict = []
    for noti in reportList:
        my_dict.append(
            {"id": noti.id, "PName": noti.name, "last_name": noti.last_name,
             "institution_id": noti.institution_id, "hadar_plan_session ": noti.hadar_plan_session, "serve_type": noti.serve_type,
             "family_status": noti.marriage_status, "base_address": noti.base_address
             , "phone": noti.phone, "birthday": noti.birthday, "email": noti.email
             , "marriage_status": noti.marriage_status, "marriage_date": noti.marriage_date, "wife_name": noti.wife_name
             , "wife_phone": noti.wife_phone, "city_id": noti.city_id, "address": noti.address
             , "father_name": noti.father_name, "father_phone": noti.father_phone, "mother_name": noti.mother_name
             , "mother_phone": noti.mother_phone, "mother_email": noti.mother_email, "high_school_name": noti.high_school_name
             , "high_school_teacher": noti.high_school_teacher, "high_school_teacher_phone": noti.high_school_teacher_phone, "pre_army_institution": noti.pre_army_institution
                , "teacher_grade_a": noti.teacher_grade_a, "teacher_grade_a_phone": noti.teacher_grade_a_phone, "base_address": noti.base_address
                , "teacher_grade_b": noti.teacher_grade_b, "recruitment_date": noti.recruitment_date, "release_date": noti.release_date
                , "teacher_grade_b_phone": noti.teacher_grade_b_phone, "unit_name": noti.unit_name, "paying": noti.paying
                , "accompany_connect_status": noti.accompany_connect_status, "army_role": noti.army_role, "spirit_status": noti.spirit_status
             })

    if reportList is None or len(my_dict) == 0:
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"Apparentice_atrr":my_dict[0]}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK




