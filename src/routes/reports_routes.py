import datetime
import json
from datetime import datetime,date

import boto3
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

from config import AWS_access_key_id, AWS_secret_access_key
from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.cluster_model import Cluster
from ..models.institution_model import Institution
from ..models.user_model import user1

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid
from ..models.visit_model import Visit

reports_form_blueprint = Blueprint('reports_form', __name__, url_prefix='/reports_form')

@reports_form_blueprint.route('/add', methods=['post'])
def add_reports_form():
    data = request.json
    user = str(data['userId'])[3:]
    ent_group_name=""
    try:
        ent_group_name = str(data['ent_group'])
    except:
        print("no ent_group")
    if user:
        List_of_repored = data['List_of_repored']
        vis_id=int(str(uuid.uuid4().int)[:5])
        for key in List_of_repored:
            Visit1 = Visit(
                user_id=user,
                ent_reported=str(key['id'])[3:],
                note=data['event_details'],
                visit_in_army=bool(data['event_type']),
                visit_date=data['date'],
                allreadyread=False,
                id=vis_id,
                title=data['event_type'],
                attachments=[],
                ent_group=ent_group_name,
                description=data['description']
            )

            db.session.add(Visit1)

    try:
        db.session.commit()

    except Exception as e:
        return jsonify({'result': 'error'+str(e)}), HTTPStatus.BAD_REQUEST
    return jsonify({'result': "success"}), HTTPStatus.OK


@reports_form_blueprint.route('/getAll', methods=['GET'])
def getAll_reports_form():
    user = request.args.get('userId')[3:]
    print(user)
    reportList = db.session.query(Visit.ent_reported,Visit.ent_group,Visit.note,Visit.visit_date,Visit.id,Visit.title,Visit.description,Visit.attachments,Visit.allreadyread).filter(Visit.user_id == user).all()
    group_report_dict=dict()
    my_dict = []
    groped_rep=[]
    for noti in reportList:
        daysFromNow = (date.today() - noti.visit_date).days if noti.visit_date is not None else None
        if noti.ent_group !="":
            if noti.ent_group+str(noti.id) in  group_report_dict:
                group_report_dict[noti.ent_group+str(noti.id)].append(str(noti.ent_reported))
            else:
                print("created_for_id",noti.ent_reported)
                group_report_dict[noti.ent_group+str(noti.id)] = [str(noti.ent_reported)]
            groped_rep.append(noti)
        else:
            my_dict.append(
            {"id": str(noti.id), "reported_on":[str(noti.ent_reported)], "date":toISO(noti.visit_date),        "ent_group": "",
             "days_from_now": daysFromNow , "title": str(noti.title), "allreadyread": str(noti.allreadyread), "description": str(noti.note),"attachments": noti.attachments})
    for noti in groped_rep:
        if group_report_dict[noti.ent_group+str(noti.id)]!=None:
            my_dict.append(
                {"id": str(noti.id), "reported_on": group_report_dict[noti.ent_group+str(noti.id)], "date": toISO(noti.visit_date),
                 "ent_group": noti.ent_group,
                 "days_from_now": daysFromNow, "title": str(noti.title), "allreadyread": str(noti.allreadyread),
                 "description": str(noti.note), "attachments": noti.attachments})
            group_report_dict[noti.ent_group+str(noti.id)]=None

    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@reports_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_report_form():
    data = request.json
    report_id = data['report_id']
    print(report_id)
    try:
        num_rows_updated = Visit.query.filter_by(id=report_id).update(dict(allreadyread=True))
        db.session.commit()

        if report_id:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except:
        return jsonify({'result': 'wrong id'}), HTTPStatus.OK
def toISO(d):
    if d:
        return datetime(d.year, d.month, d.day).isoformat()
    else:
        return None

@reports_form_blueprint.route('/uploadPhoto', methods=['post'])
def uploadPhoto_form():
        reportId = request.args.get('reportId')
        print(reportId)
        updatedEnt = Visit.query.get(reportId)

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

@reports_form_blueprint.route('/delete', methods=['POST'])
def delete():
    try:
        data = request.json
        reportId = data['reportId']
        res = db.session.query(Visit).filter(Visit.id == reportId).delete()
        db.session.commit()
    except Exception as e:
        return jsonify({"result": str(e)}),HTTPStatus.BAD_REQUEST
    return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK

@reports_form_blueprint.route("/update", methods=['put'])
def updateTask():
    # get tasksAndEvents
    reportId = request.args.get("reportId")
    data = request.json
    updatedEnt = Visit.query.get(reportId)
    for key in data:
        setattr(updatedEnt, key, data[key])
    db.session.commit()
    if updatedEnt:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK
    return jsonify({'result': 'error'}), HTTPStatus.OK

@reports_form_blueprint.route("/filter_report", methods=['GET'])
def filter_report():
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
    reports_user=db.session.query(Visit.id).filter(Visit.user_id.in_(users)).all()
    reports_apprentice=db.session.query(Visit.id).filter(Visit.ent_reported.in_(apprentice)).all()
    ent_group_concat=", ".join(ent_group_dict.values())
    reports_ent_group=db.session.query(Visit.id).filter(Visit.ent_group==ent_group.id,ent_group.group_name==ent_group_concat).all()
    users_mess=[str(i[0]) for i in [tuple(row) for row in reports_user]]
    apprentice_mess=[str(i[0]) for i in [tuple(row) for row in reports_apprentice]]
    ent_group_mess=[str(i[0]) for i in [tuple(row) for row in reports_ent_group]]
    result=set(ent_group_mess+users_mess+apprentice_mess)
    print(result)
    return jsonify( [str(row) for row in result]
        ), HTTPStatus.OK
    print(ent_group_concat)


@reports_form_blueprint.route("/filter_to", methods=['GET'])
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
                        users,
                    "apprentice":
                        apprentice,
                    "ent_group":ent_group_concat
                    }
        ), HTTPStatus.OK


@reports_form_blueprint.route('/getById', methods=['GET'])
def getById():
    report_id = request.args.get('report_id')
    user = request.args.get('userId')[3:]
    print(report_id)
    report1 = db.session.query(Visit).filter(Visit.id == report_id).first()
    ent_group_list = db.session.query(ent_group.group_name).filter(ent_group.user_id == user).all()
    ent_group_list_name= [r[0] for r in ent_group_list]
    my_dict = []
    daysFromNow = (date.today() - report1.visit_date).days if report1.visit_date is not None else None
    if report1.ent_group in ent_group_list_name:
            ent_group_item = db.session.query(ent_group.group_name).filter(ent_group.id == report1.ent_group).first()
            my_dict.append(
                {"id": str(report1.id), "on": ent_group_item.group_name,
                 "date": toISO(report1.visit_date),
                 "days_from_now": daysFromNow, "title": str(report1.title), "allreadyread": str(report1.allreadyread),
                 "description": str(report1.note), "attachments": report1.attachments})

    else:
            my_dict.append(
            {"id": str(report1.id), "on":str(report1.ent_reported), "date":toISO(report1.visit_date),
             "days_from_now": daysFromNow , "title": str(report1.title), "allreadyread": str(report1.allreadyread), "description": str(report1.note),"attachments": report1.attachments})
    if not report1 :
        # acount not found
        return jsonify([])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK