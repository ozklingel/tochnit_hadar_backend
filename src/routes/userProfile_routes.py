import pickle

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from app import db, red
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
    created_by_id = request.args.get('userId')
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
    created_by_id = request.args.get('userId')
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


@userProfile_form_blueprint.route("/save", methods=['POST'])
def save():
    id = str(request.form['id']).lower()


    # check if data of the username already exists in the redis
    if red.hgetall(id).keys():
        print("hget id:", red.hgetall(id))
        # return a msg , saying the user already exists(from redis)
        return jsonify({'result': 'already exists(from redis)'}), HTTPStatus.OK

    # if not in redis, then check in db
    elif len(list(red.hgetall(id))) == 0:
        record = user1.query.filter_by(id=id).first()
        print("Records fecthed from db:", record)

        if record:

            # return a msg to the template, saying the user already exists(from database)
            return jsonify({'result': 'already exists(from db)'}), HTTPStatus.OK

    # if data of the username doesnot exist anywhere, create a new record in DataBase and store in Redis also
    # create a new record in DataBase
    new_record = user1(username=id)
    db.session.add(new_record)
    db.session.commit()

    # store in Redis also
    #red.hset(username, "place", place)


    # cross-checking if the record insertion was successful into database
    record = user1.query.filter_by(id=id).first()
    print("Records fetched from db after insert:", record)

    # cross-checking if the insertion was successful into redis
    print("key-values from redis after insert:", red.hgetall(id))

    # return a success message upon saving
    return jsonify({'result': 'id was inserted'}), HTTPStatus.OK

@userProfile_form_blueprint.route("/homepage", methods=['GET'])
def homepage():
    userId = request.args.get("userId")
    print("Userid:", str(userId))
    user_id = red.hget(userId,"id")
    print("GET Redis:", user_id)

    if not user_id:
        record = user1.query.filter_by(id=userId).first()
        print("GET db Record:", record)
        if not record:
            print("No data in redis or db")
            return jsonify({'result': f"Record not yet defined for {userId}"}), HTTPStatus.OK
        print("in db")
        red.hset(userId,"id", record.id)
        red.hset(userId,"name", record.name)
        red.hset(userId,"lastname", record.last_name)
        red.hset(userId, "email",record.email)
        red.hset(userId, "role",record.role_id)

        print("User stored in cache.")
        return jsonify({'result': 'from db','user':record.id}), HTTPStatus.OK
    user_name = red.hget(userId,"name")
    user_lastname = red.hget(userId,"lastname")
    return jsonify({'userid':user_id.decode("utf-8"),
                    'user_lastname':user_lastname.decode("utf-8"),
                    'user_name':user_name.decode("utf-8")}), HTTPStatus.OK


