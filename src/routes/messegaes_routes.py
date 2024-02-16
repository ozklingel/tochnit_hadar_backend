import datetime
import json
import time
from datetime import datetime,date

import boto3
import flask
from sqlalchemy import or_
from twilio.rest import Client

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from config import AWS_access_key_id, AWS_secret_access_key
from .user_Profile import toISO
from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.cluster_model import Cluster
from ..models.contact_form_model import ContactForm
from ..models.institution_model import Institution
from ..models.user_model import user1

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid

from ..models.visit_model import Visit

messegaes_form_blueprint = Blueprint('messegaes_form', __name__, url_prefix='/messegaes_form')


#from chat box
@messegaes_form_blueprint.route('/add', methods=['POST'])
def add_contact_form():
    data = request.json
    subject = data['subject']

    content = data['content']
    type="פניות_שירות"
    icon=""
    ent_group_name=""
    try:
        type = data['type']
        icon = data['icon']
        ent_group_name = str(data['ent_group'])

    except:
        print("no icon or type or ent_group")
    created_by_id = str(data['created_by_id'])[3:]
    created_for_ids = data['created_for_ids']
    mess_id=str(uuid.uuid1().int)[:5]
    for key in created_for_ids:
        try:
            ContactForm1 = ContactForm(
                id=mess_id ,#if ent_group_name!="" else str(uuid.uuid1().int)[:5],
                created_for_id=str(key['id'])[3:],
                created_by_id=created_by_id,
                content=content,
                subject=subject,
                created_at=date.today(),
                allreadyread=False,
                attachments=[],
                type=type,
                ent_group=ent_group_name,
                icon=icon
            )
            db.session.add(ContactForm1)
            db.session.commit()
        except Exception as e:
            return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if ContactForm1:
        print(f'add contact form: subject: [{subject}, content: {content}, created_by_id: {created_by_id}]')
        # TODO: add contact form to DB
        return jsonify({'result': "success"}), HTTPStatus.OK
@messegaes_form_blueprint.route('/getAll', methods=['GET'])
def getAll_messegases_form():
    user = request.args.get('userId')[3:]
    print(user)
    messegasesList = db.session.query(ContactForm.created_for_id,ContactForm.created_at,ContactForm.id,
                                      ContactForm.attachments,ContactForm.type,ContactForm.icon,
                                      ContactForm.allreadyread,ContactForm.subject,ContactForm.content
                                      ,ContactForm.ent_group,ContactForm.created_by_id)\
        .filter(or_(ContactForm.created_for_id == user,ContactForm.created_by_id == user)).all()
    my_dict = []
    groped_mess=[]
    group_report_dict=dict()
    print(messegasesList)
    for mess in messegasesList:
        daysFromNow = (date.today() - mess.created_at).days if mess.created_at is not None else None
        if mess.ent_group !="":
            if mess.ent_group+str(mess.id) in  group_report_dict:
                group_report_dict[mess.ent_group+str(mess.id)].append(str(mess.created_for_id))
            else:
                group_report_dict[mess.ent_group+str(mess.id)] = [str(mess.created_for_id)]
            groped_mess.append(mess)
        else:
            my_dict.append(
                {"type":mess.type,"attachments":mess.attachments,"id": str(mess.id),"to":[str(mess.created_for_id)], "ent_group": "", "from": str(mess.created_by_id), "date":toISO(mess.created_at),
                 "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),"icon":mess.icon})

    for mess in groped_mess:
        if group_report_dict[mess.ent_group+str(mess.id)]!=None:
            my_dict.append(
                {"type": mess.type, "attachments": mess.attachments, "id": str(mess.id),
                 "from": str(mess.created_by_id), "date": toISO(mess.created_at),"to": group_report_dict[mess.ent_group+str(mess.id)],
                 "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),"ent_group":mess.ent_group,
                 "icon": mess.icon})
            group_report_dict[mess.ent_group+str(mess.id)]=None
    # print(f' notifications: {my_dict}]')
    # TODO: get Noti form to DB
    return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@messegaes_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_message_form():
    data = request.json
    message_id = data['message_id']
    print(message_id)
    try:
        #notis =ContactForm.query.filter_by(id=message_id)#db.session.query(ContactForm.id,ContactForm.allreadyread).filter(ContactForm.id==message_id).all()
        num_rows_updated = ContactForm.query.filter_by(id=message_id).update(dict(allreadyread=True))
        db.session.commit()

        if message_id:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as  e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/delete', methods=['DELETE','post'])
def deleteEnt():
       data=request.json
       try:
           entityId = str(data['entityId'])
           res = db.session.query(ContactForm).filter(ContactForm.id == entityId).delete()
           db.session.commit()
           return jsonify({'result': 'sucess'}), HTTPStatus.OK
       except Exception as e:
           return jsonify({'result': 'error'+str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
        message_Id = request.args.get('message_Id')
        print(message_Id)
        updatedEnt = ContactForm.query.get(message_Id)

        images_list=[]
        for imagefile in request.files.getlist('image'):
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
            images_list.append("https://th01-s3.s3.eu-north-1.amazonaws.com/"+new_filename)
        if updatedEnt:
            updatedEnt.attachments=images_list
            db.session.commit()
        #head = s3_client.head_object(Bucket=bucket_name, Key=new_filename)
            return jsonify({'result': 'success', 'image path': updatedEnt.attachments}), HTTPStatus.OK
        return jsonify({"result": "error"}),HTTPStatus.BAD_REQUEST

@messegaes_form_blueprint.route("/filter_to", methods=['GET'])
def filter_to():
    ent_group_dict=dict()
    roles = request.args.get("roles").split(",") if request.args.get("roles") is not None else None
    years = request.args.get("years").split(",") if request.args.get("years") is not None else None
    institutions = request.args.get("institutions").split(",") if request.args.get("institutions") is not None else None
    preiods = request.args.get("preiods").split(",") if request.args.get("preiods") is not None else None
    eshcols = request.args.get("eshcols").split(",") if request.args.get("eshcols") is not None else None
    statuses = request.args.get("statuses").split(",") if request.args.get("statuses") is not None else None
    bases = request.args.get("bases").split(",") if request.args.get("bases") is not None else None
    hativa = request.args.get("hativa").split(",") if request.args.get("hativa") is not None else None
    region = request.args.get("region") if request.args.get("region") is not None and "?"  not in request.args.get("region") else None
    city = request.args.get("city")
    entityType=[]
    #query user table
    print(roles[0])
    query = None
    if "melave" in roles:
        ent_group_dict["melave"]="מלוים"
        entityType.append("0")
    if "racazMosad" in roles:
        ent_group_dict["racazMosad"]="רכזי מוסד"
        entityType.append("1")
    if "racaz" in roles:
        ent_group_dict["racaz"]="רכזי אשכול"
        entityType.append("2")
    if len(entityType):
        query = db.session.query(user1.id)
        query = query.filter(user1.role_id.in_(entityType))
        if institutions:
            ent_group_dict["institutions"] = institutions
            query = query.filter(user1.institution_id==Institution.id,Institution.name.in_(institutions))
        if region:
            ent_group_dict["region"] = region
            query = query.filter(user1.cluster_id==Cluster.id,Cluster.name==region)
        if eshcols:
            ent_group_dict["eshcols"] = region
            query = query.filter(user1.eshcol.in_(eshcols))
        if city:
            ent_group_dict["city"] = city
            query = query.filter(City.id == user1.city_id, city == City.name)

    res1=[]
    if query:
        res1 = query.all()
    query=None
    #query apprentice table
    if "apprentice" in roles:
        ent_group_dict["apprentice"] = "חניכים"
        query = db.session.query(Apprentice.id)
        if institutions:
            ent_group_dict["institutions"] = ", ".join(institutions)
            query = query.filter(Apprentice.institution_id == Institution.id, Institution.name.in_(institutions))
        if years:
            ent_group_dict["years"] = years

            query = query.filter(Apprentice.hadar_plan_session.in_(years))
        if preiods:
            ent_group_dict["preiods"] = preiods

            query = query.filter(Apprentice.institution_mahzor.in_(preiods))
        if statuses:
            ent_group_dict["statuses"] = statuses

            query = query.filter(Apprentice.marriage_status.in_(statuses))
        if bases:
            ent_group_dict["bases"] = bases

            query = query.filter(Apprentice.base_address.in_(bases))
        if hativa:
            ent_group_dict["hativa"] = hativa

            query = query.filter(Apprentice.unit_name.in_(hativa))
        if region:
            ent_group_dict["region"] = region

            query = query.filter(Apprentice.cluster_id == Cluster.id, Cluster.name == region)
        if eshcols:
            ent_group_dict["eshcols"] = eshcols

            query = query.filter(Apprentice.eshcol.in_(eshcols))
        if city:
            ent_group_dict["city"] = city
            query = query.filter(City.id == Apprentice.city_id, city == City.name)
    res2=[]
    if query:
        res2 = query.all()
    print("app",res2)
    print("user",res1)
    users=   [str(i[0]) for i in [tuple(row) for row in res1]]
    apprentice=[str(i[0]) for i in [tuple(row) for row in res2]]
    ent_group_concat=", ".join(ent_group_dict.values())

    return jsonify({"users":
                        [str(i[0]) for i in [tuple(row) for row in users]],
                    "apprentice":
                        [str(i[0]) for i in [tuple(row) for row in apprentice]],
                    "ent_group":ent_group_concat
                    }
        ), HTTPStatus.OK

@messegaes_form_blueprint.route("/filter_meesages", methods=['GET'])
def filter_meesages():
    ent_group_dict=dict()
    roles = request.args.get("roles").split(",") if request.args.get("roles") is not None else None
    years = request.args.get("years").split(",") if request.args.get("years") is not None else None
    institutions = request.args.get("institutions").split(",") if request.args.get("institutions") is not None else None
    preiods = request.args.get("preiods").split(",") if request.args.get("preiods") is not None else None
    eshcols = request.args.get("eshcols").split(",") if request.args.get("eshcols") is not None else None
    statuses = request.args.get("statuses").split(",") if request.args.get("statuses") is not None else None
    bases = request.args.get("bases").split(",") if request.args.get("bases") is not None else None
    hativa = request.args.get("hativa").split(",") if request.args.get("hativa") is not None else None
    region = request.args.get("region") if request.args.get("region") is not None and "?"  not in request.args.get("region") else None
    city = request.args.get("city")
    entityType=[]
    #query user table
    print(roles[0])
    query = None
    if "melave" in roles:
        ent_group_dict["melave"]="מלוים"
        entityType.append("0")
    if "racazMosad" in roles:
        ent_group_dict["racazMosad"]="רכזי מוסד"
        entityType.append("1")
    if "racaz" in roles:
        ent_group_dict["racaz"]="רכזי אשכול"
        entityType.append("2")
    if len(entityType):
        query = db.session.query(user1.id)
        query = query.filter(user1.role_id.in_(entityType))
        if institutions:
            ent_group_dict["institutions"] = institutions
            query = query.filter(user1.institution_id==Institution.id,Institution.name.in_(institutions))
        if region:
            ent_group_dict["region"] = region
            query = query.filter(user1.cluster_id==Cluster.id,Cluster.name==region)
        if eshcols:
            ent_group_dict["eshcols"] = region
            query = query.filter(user1.eshcol.in_(eshcols))
        if city:
            ent_group_dict["city"] = city
            query = query.filter(City.id == user1.city_id, city == City.name)

    res1=[]
    if query:
        res1 = query.all()
    query=None
    #query apprentice table
    if "apprentice" in roles:
        ent_group_dict["apprentice"] = "חניכים"
        query = db.session.query(Apprentice.id)
        if institutions:
            ent_group_dict["institutions"] = ", ".join(institutions)
            query = query.filter(Apprentice.institution_id == Institution.id, Institution.name.in_(institutions))
        if years:
            ent_group_dict["years"] = years

            query = query.filter(Apprentice.hadar_plan_session.in_(years))
        if preiods:
            ent_group_dict["preiods"] = preiods

            query = query.filter(Apprentice.institution_mahzor.in_(preiods))
        if statuses:
            ent_group_dict["statuses"] = statuses

            query = query.filter(Apprentice.marriage_status.in_(statuses))
        if bases:
            ent_group_dict["bases"] = bases

            query = query.filter(Apprentice.base_address.in_(bases))
        if hativa:
            ent_group_dict["hativa"] = hativa

            query = query.filter(Apprentice.unit_name.in_(hativa))
        if region:
            ent_group_dict["region"] = region

            query = query.filter(Apprentice.cluster_id == Cluster.id, Cluster.name == region)
        if eshcols:
            ent_group_dict["eshcols"] = eshcols

            query = query.filter(Apprentice.eshcol.in_(eshcols))
        if city:
            ent_group_dict["city"] = city
            query = query.filter(City.id == Apprentice.city_id, city == City.name)
    res2=[]
    if query:
        res2 = query.all()
    print("app",res2)
    print("user",res1)
    users=   [str(i[0]) for i in [tuple(row) for row in res1]]
    apprentice=[str(i[0]) for i in [tuple(row) for row in res2]]
    mess_user=db.session.query(ContactForm.id).filter(or_(ContactForm.created_by_id.in_(users),ContactForm.created_for_id.in_(users))).all()
    #reports_apprentice=db.session.query(ContactForm.id).filter(ContactForm.created_for_id.in_(apprentice)).all()
    ent_group_concat=", ".join(ent_group_dict.values())
    mess_ent_group=db.session.query(ContactForm.id).filter(ContactForm.ent_group==ent_group.id,ent_group.group_name==ent_group_concat).all()
    users_mess=[str(i[0]) for i in [tuple(row) for row in mess_user]]
    #apprentice_mess=[str(i[0]) for i in [tuple(row) for row in reports_apprentice]]
    ent_group_mess=[str(i[0]) for i in [tuple(row) for row in mess_ent_group]]
    result=set(ent_group_mess+users_mess)
    print(result)
    return jsonify( [str(row) for row in result]
        ), HTTPStatus.OK

@messegaes_form_blueprint.route('/getById', methods=['GET'])
def getById():
    message_id = request.args.get('message_id')
    user = request.args.get('userId')[3:]
    print(message_id)
    mess1 = db.session.query(ContactForm).filter(ContactForm.id == message_id).first()
    ent_group_list = db.session.query(ent_group.group_name).filter(ent_group.user_id == user).all()
    ent_group_list_name= [r[0] for r in ent_group_list]
    my_dict = []
    daysFromNow = (date.today() - mess1.created_at).days if mess1.created_at is not None else None
    if mess1.ent_group in ent_group_list_name:
            group_name1 = db.session.query(ent_group.group_name).filter(ent_group.id == mess1.ent_group).first()
            my_dict.append(
                {"type": mess1.type, "attachments": mess1.attachments, "id": str(mess1.id),
                 "to": group_name1[0] if group_name1 else "לא ידוע", "date": toISO(mess1.created_at),
                 "content": mess1.content, "title": str(mess1.subject), "allreadyread": str(mess1.allreadyread),
                 "icon": mess1.icon})
    else:
        my_dict.append(
            {"type": mess1.type, "attachments": mess1.attachments, "id": str(mess1.id), "from": str(mess1.created_by_id),
             "date": toISO(mess1.created_at),
             "content": mess1.content, "title": str(mess1.subject), "allreadyread": str(mess1.allreadyread),
             "icon": mess1.icon})
    if not mess1 :
        # acount not found
        return jsonify([])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK