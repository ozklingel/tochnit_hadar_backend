
import uuid
from random import randrange

import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus

from openpyxl.reader.excel import load_workbook

from src.services import db, red
from config import AWS_secret_access_key, AWS_access_key_id
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.institution_model import Institution, front_end_dict
from src.models.user_model import user1
from src.routes.setEntityDetails_form_routes import validate_email

institutionProfile_form_blueprint = Blueprint('institutionProfile_form', __name__, url_prefix='/institutionProfile_form')

@institutionProfile_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
    if request.method == "POST":
        institution_id = request.args.get('institution_id')
        print(institution_id)
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
        updatedEnt = Institution.query.get(institution_id)
        updatedEnt.logo_path="https://th01-s3.s3.eu-north-1.amazonaws.com/"+new_filename
        db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
        return jsonify({'result': 'success', 'image path': new_filename}), HTTPStatus.OK





@institutionProfile_form_blueprint.route('/apprentice_and_melave', methods=['GET'])
def getmyApprentices_form():
    institution_id = int(request.args.get('institution_id'))
    print(institution_id)
    melave_List = db.session.query(user1).filter(user1.institution_id== institution_id,user1.role_ids.contains("0")).all()
    apprenticeList = db.session.query(Apprentice).filter(Apprentice.institution_id == institution_id).all()
    print(melave_List)
    my_dict = []
    for noti in melave_List:
        city = db.session.query(City).filter(City.id == noti.city_id).first()
        my_dict.append(
            {
                "id": str(noti.id),
                "role": "מלווה",
                "first_name": noti.name,
                "last_name": noti.last_name,
                "address": {
                    "country": "IL",
                    "city": city.name,
                    "cityId": str(noti.city_id),
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
                "id": str(noti.id),
                "address": {
                    "country": "IL",
                    "city": city.name if city is  not None else "",
                    "cityId": str(noti.city_id),
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
    institution_id = request.args.get('institution_id')
    institution_Ent = Institution.query.get(institution_id)
    if institution_Ent:
        city = db.session.query(City).filter(str(City.id) == institution_Ent.city_id).first()
        list = {"id":str(institution_Ent.id), "name":institution_Ent.name, "owner_id":institution_Ent.owner_id,
                "contact_phone":institution_Ent.contact_phone,
                       "city":city.name if city is not None else "", "contact_name":str(institution_Ent.contact_name), "phone":str(institution_Ent.phone), "address":institution_Ent.address,
                "avatar":institution_Ent.logo_path if institution_Ent.logo_path is not None else 'https://www.gravatar.com/avatar',
                "eshcol":str(institution_Ent.eshcol_id), "roshYeshiva_phone":institution_Ent.roshYeshiva_phone, "roshYeshiva_name":institution_Ent.roshYeshiva_name,
                "admin_phone":str(institution_Ent.admin_phone), "admin_name":institution_Ent.admin_name}
        return jsonify(list), HTTPStatus.OK
    else:
        return jsonify(results="no such id"), HTTPStatus.OK

@institutionProfile_form_blueprint.route("/add_mosad", methods=['post'])
def add_mosad():
    data = request.json
    print(data)
    name = data['name']
    eshcol = data['eshcol']
    roshYeshiva_phone = data['roshYeshiva_phone']
    roshYeshiva_name = data['roshYeshiva_name']
    admin_phone = data['admin_phone']
    admin_name = data['admin_name']
    contact_name = data['contact_name']
    contact_phone = data['contact_phone']
    owner_id = data['owner_id']

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
            eshcol_id =eshcol,
            roshYeshiva_phone = roshYeshiva_phone,
            roshYeshiva_name = roshYeshiva_name,
            admin_phone = admin_phone,
            admin_name =admin_name,
            contact_name =contact_name,
            owner_id=owner_id,
            contact_phone = contact_phone
        )
        db.session.add(Institution1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if Institution1:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK

@institutionProfile_form_blueprint.route('/getAll', methods=['GET'])
def getAll():
    inst_List = db.session.query(Institution).all()
    if inst_List==[]:
        return jsonify([]), HTTPStatus.OK
    #print(inst_List)
    my_list = []
    for r in inst_List:
        city=None
        region=None
        if r.city_id !="":
            city = db.session.query(City).filter(City.id == r.city_id).first()
            region = db.session.query(Cluster).filter(Cluster.id == city.cluster_id).first()
        melave_List = db.session.query(user1).filter(user1.institution_id == r.id, user1.role_ids.contains("0")).all()
        apprenticeList = db.session.query(Apprentice.id).filter(Apprentice.institution_id == r.id).all()
        my_list.append(
            {"id":str(r.id),"roshYeshiva_phone":r.roshYeshiva_phone,"roshYeshiva_name":r.roshYeshiva_name,
                     "admin_name":r.admin_name,"admin_phone":r.admin_phone,
                   "name":r.name,"racaz_id":r.owner_id,"logo_path":r.logo_path or "",
                     "contact_phone":r.contact_phone,       "address": {
                     "country": "IL",
                     "city": city.name if city else "",
                     "cityId": r.city_id,
                     "street": r.address,
                     "houseNumber": "1",
                     "apartment": "1",
                    "shluha": "12131",

                    "region": region.name if region else "",
                     "entrance": "a",
                     "floor": "1",
                     "postalCode": "12131",
                     "lat": 32.04282620026557,
                     "lng": 34.75186193813887
                 },
             "score":randrange(100),
             "apprenticeList":[str(row.id ) for row in apprenticeList],
             "melave_List": [str(row.id) for row in melave_List],

             "phone":r.phone,"city_id":r.city_id })
    return jsonify(my_list), HTTPStatus.OK
@institutionProfile_form_blueprint.route('/getMahzors', methods=['get'])
def getMahzors():
    try:
        eshcols_appren = db.session.query(Apprentice.institution_mahzor).distinct(Apprentice.institution_mahzor).all()
        eshcols_appren_ids=[str(row[0])for row in eshcols_appren]
        return  eshcols_appren_ids
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
@institutionProfile_form_blueprint.route("/update", methods=['put'])
def update():
    try:
        # get tasksAndEvents
        mosad_Id = request.args.get("mosad_Id")
        data = request.json
        updatedEnt = Institution.query.get(mosad_Id)
        for key in data:
            if key == "city":
                CityId = db.session.query(City).filter(
                    City.name == str(data[key])).first()
                print("CityId", CityId)
                setattr(updatedEnt, "city_id", CityId.id)
            if key == "region":
                ClusterId = db.session.query(Cluster.id).filter(
                    Cluster.name == str(data[key])).first()
                print("ClusterId", ClusterId.id)
                setattr(updatedEnt, "cluster_id", ClusterId.id)
            elif key == "email" or key == "birthday":
                if validate_email(data[key]):
                    setattr(updatedEnt, key, data[key])
                else:
                    return jsonify({'result': "email or date -wrong format"}), 401
            else:
                setattr(updatedEnt, front_end_dict[key], data[key])
        db.session.commit()
        if updatedEnt:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
        return jsonify({'result': 'error'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK

@institutionProfile_form_blueprint.route("/add_mosad_excel", methods=['put'])
def add_mosad_excel():

    file = request.files['file']
    print(file)
    wb = load_workbook(file)
    sheet = wb.active
    not_commited = []
    for row in sheet.iter_rows(min_row=2):
        name = row[0].value.strip()
        phone = str(row[1].value)
        email = row[2].value.strip()
        eshcol = row[3].value.strip()
        roshYeshiva_phone = row[4].value
        roshYeshiva_name = row[5].value.strip()
        admin_phone = row[6].value.strip()
        admin_name = row[7].value.strip()
        owner_id = row[8].value
        logo_path = row[9].value.strip() if row[9].value else ""
        address = row[10].value.strip()
        city = row[11].value.strip()
        contact_name = row[12].value.strip()
        contact_phone = row[13].value
        try:
            CityId = db.session.query(City.id).filter(City.name == city).first()
            Institution1 = db.session.query(Institution.id).filter(Institution.name == name).first()
            if Institution1:
                not_commited.append(name)
                continue
            Institution1 = Institution(
                #email=email,
                id=int(str(uuid.uuid4().int)[:5]),
                eshcol_id=eshcol,
                roshYeshiva_phone=roshYeshiva_phone,
                roshYeshiva_name=roshYeshiva_name,
                admin_phone=admin_phone,
                admin_name=admin_name,
                name=name,
                owner_id=owner_id,
                logo_path=logo_path,
                contact_phone=str(contact_phone),
                contact_name=str(contact_name),
                phone=phone,
                city_id=CityId.id,
                address=address
            )
            db.session.add(Institution1)
            db.session.commit()
        except Exception as e:
            not_commited.append(name)
    return jsonify({'result': 'success', "not_commited": not_commited}), HTTPStatus.OK


@institutionProfile_form_blueprint.route('/delete', methods=['DELETE', 'post'])
def deleteEnt():
    data = request.json
    try:
        entityId = str(data['entityId'])
        res = db.session.query(Institution).filter(Institution.id == entityId).delete()
        db.session.commit()
        return jsonify({'result': 'sucess'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.BAD_REQUEST