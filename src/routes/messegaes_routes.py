import uuid
from datetime import date
from http import HTTPStatus
from typing import Union, List

import requests
from flask import Blueprint, request, jsonify
from sqlalchemy import or_

import config
from app import db
from .Utils.Sms import send_sms_019
from .user_Profile import toISO
from ..models.apprentice_model import Apprentice
from ..models.city_model import City
from ..models.cluster_model import Cluster
from ..models.contact_form_model import ContactForm
from ..models.institution_model import Institution
from ..models.user_model import user1

messegaes_form_blueprint = Blueprint('messegaes_form', __name__, url_prefix='/messegaes_form')


@messegaes_form_blueprint.route('/send_sms', methods=['POST'])
def send_sms():
    try:
        data = request.json
        message: str = data['message']
        recipients: List[str] = data['recipients']
        sources: Union[List[str], str] = data['sources']
        responses = send_sms_019(sources, recipients, message)
        if responses is not None:
            numbers_to_add_to_019 = []
            for number in responses:
                if isinstance(responses[number], dict):
                    if (config.SendMessages.Sms.error_message_019
                            in responses[number].values()):
                        numbers_to_add_to_019.append(number)
                else:
                    if (config.SendMessages.Sms.error_message_019
                            in responses[number]):
                        numbers_to_add_to_019.append(number)
            if len(numbers_to_add_to_019) > 0:
                return jsonify({'result': {
                    "response": str(responses),
                    config.SendMessages.Sms.at_least_one_error: config.SendMessages.Sms.message_add_to_019 + str(
                        numbers_to_add_to_019)
                }
                }), HTTPStatus.INTERNAL_SERVER_ERROR
            return jsonify({'result': str(responses)}), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


def send_whatsapp_through_joni(sources: str, recipients: Union[List[str], str], message: str):
    if isinstance(recipients, str):
        recipients = [recipients]
    webhook = config.SendMessages.Whatsapp.webhook
    if not isinstance(sources, list):
        sources = [sources]
    for source in sources:
        message = config.SendMessages.Whatsapp.messagePrefix + source + "\n\n" + message
        for recipient in recipients:
            data = {config.SendMessages.Whatsapp.joni_to: recipient,
                    config.SendMessages.Whatsapp.joni_text: message}
            response = requests.post(webhook, json=data)
            if response.status_code != 200:
                response_json = response.json()
                return response_json


@messegaes_form_blueprint.route('/send_whatsapp', methods=['POST'])
def send_whatsapp():
    try:
        data = request.json
        message = data['message']
        recipients = data['recipients']
        sources = data['sources']
        returned = send_whatsapp_through_joni(sources, recipients, message)
        if returned:
            return jsonify({'result': str(returned)}), HTTPStatus.INTERNAL_SERVER_ERROR
        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


# from chat box
@messegaes_form_blueprint.route('/add', methods=['POST'])
def add_contact_form():
    try:
        data = request.json
        subject = data['subject']
        content = data['content']
        type = "פניות_שירות"
        icon = ""
        attachments = []
        ent_group_name = ""
        try:
            type = data['type']
            icon = data['icon']
            attachments = data['attachments']

            ent_group_name = str(data['ent_group'])

        except:
            print("no icon or type or ent_group or attachments")
        created_by_id = str(data['created_by_id'])
        created_for_ids = data['created_for_ids']
        mess_id = str(uuid.uuid1().int)[:5]
        for key in created_for_ids:
            try:
                ContactForm1 = ContactForm(
                    id=mess_id,  # if ent_group_name!="" else str(uuid.uuid1().int)[:5],
                    created_for_id=str(key['id']),
                    created_by_id=created_by_id,
                    content=content,
                    subject=subject,
                    created_at=date.today(),
                    allreadyread=False,
                    attachments=attachments,
                    type=type,
                    ent_group=ent_group_name,
                    icon=icon
                )
                db.session.add(ContactForm1)
                db.session.commit()
                return jsonify({'result': 'success'}), HTTPStatus.OK

            except Exception as e:
                return jsonify({'result': 'error while inserting' + str(e)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/getAll', methods=['GET'])
def getAll_messegases_form():
    try:
        user = request.args.get('userId')
        print(user)
        messegasesList = db.session.query(ContactForm.created_for_id, ContactForm.created_at, ContactForm.id,
                                          ContactForm.attachments, ContactForm.type, ContactForm.icon,
                                          ContactForm.allreadyread, ContactForm.subject, ContactForm.content
                                          , ContactForm.ent_group, ContactForm.created_by_id) \
            .filter(or_(ContactForm.created_for_id == user, ContactForm.created_by_id == user)).all()
        my_dict = []
        groped_mess = []
        group_report_dict = dict()
        print(messegasesList)
        for mess in messegasesList:
            daysFromNow = (date.today() - mess.created_at).days if mess.created_at is not None else None
            if mess.ent_group != "":
                if mess.ent_group + str(mess.id) in group_report_dict:
                    group_report_dict[mess.ent_group + str(mess.id)].append(str(mess.created_for_id))
                else:
                    group_report_dict[mess.ent_group + str(mess.id)] = [str(mess.created_for_id)]
                groped_mess.append(mess)
            else:
                my_dict.append(
                    {"type": mess.type, "attachments": mess.attachments, "id": str(mess.id),
                     "to": [str(mess.created_for_id)], "ent_group": "", "from": str(mess.created_by_id),
                     "date": toISO(mess.created_at),
                     "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),
                     "icon": mess.icon})

        for mess in groped_mess:
            if group_report_dict[mess.ent_group + str(mess.id)] != None:
                my_dict.append(
                    {"type": mess.type, "attachments": mess.attachments, "id": str(mess.id),
                     "from": str(mess.created_by_id), "date": toISO(mess.created_at),
                     "to": group_report_dict[mess.ent_group + str(mess.id)],
                     "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),
                     "ent_group": mess.ent_group,
                     "icon": mess.icon})
                group_report_dict[mess.ent_group + str(mess.id)] = None
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_message_form():
    data = request.json
    message_id = data['message_id']
    print(message_id)
    try:
        # notis =ContactForm.query.filter_by(id=message_id)#db.session.query(ContactForm.id,ContactForm.allreadyread).filter(ContactForm.id==message_id).all()
        num_rows_updated = ContactForm.query.filter_by(id=message_id).update(dict(allreadyread=True))
        db.session.commit()

        if message_id:
            # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
            # TODO: add contact form to DB
            return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/delete', methods=['DELETE', 'post'])
def deleteEnt():
    data = request.json
    try:
        entityId = str(data['entityId'])
        res = db.session.query(ContactForm).filter(ContactForm.id == entityId).delete()
        db.session.commit()
        return jsonify({'result': 'sucess'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': 'error' + str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route("/filter_to", methods=['GET'])
def filter_to():
    try:
        ent_group_dict = dict()
        roles = request.args.get("roles").split(",") if request.args.get("roles") is not None else None
        years = request.args.get("years").split(",") if request.args.get("years") is not None else None
        institutions = request.args.get("institutions").split(",") if request.args.get(
            "institutions") is not None else None
        preiods = request.args.get("preiods").split(",") if request.args.get("preiods") is not None else None
        eshcols = request.args.get("eshcols").split(",") if request.args.get("eshcols") is not None else None
        statuses = request.args.get("statuses").split(",") if request.args.get("statuses") is not None else None
        bases = request.args.get("bases").split(",") if request.args.get("bases") is not None else None
        hativa = request.args.get("hativa").split(",") if request.args.get("hativa") is not None else None
        region = request.args.get("region") if request.args.get("region") is not None and "?" not in request.args.get(
            "region") else None
        city = request.args.get("city")
        entityType = []
        # query user table
        print(roles[0])
        query = None
        if "melave" in roles:
            ent_group_dict["melave"] = "מלוים"
            entityType.append("0")
        if "racazMosad" in roles:
            ent_group_dict["racazMosad"] = "רכזי מוסד"
            entityType.append("1")
        if "racaz" in roles:
            ent_group_dict["racaz"] = "רכזי אשכול"
            entityType.append("2")
        if len(entityType):
            query = db.session.query(user1.id)
            query = query.filter(user1.role_id.in_(entityType))
            if institutions:
                ent_group_dict["institutions"] = institutions
                query = query.filter(user1.institution_id == Institution.id, Institution.name.in_(institutions))
            if region:
                ent_group_dict["region"] = region
                query = query.filter(user1.cluster_id == Cluster.id, Cluster.name == region)
            if eshcols:
                ent_group_dict["eshcols"] = region
                query = query.filter(user1.eshcol.in_(eshcols))
            if city:
                ent_group_dict["city"] = city
                query = query.filter(City.id == user1.city_id, city == City.name)

        res1 = []
        if query:
            res1 = query.all()
        query = None
        # query apprentice table
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
        res2 = []
        if query:
            res2 = query.all()
        users = [str(i[0]) for i in [tuple(row) for row in res1]]
        apprentice = [str(i[0]) for i in [tuple(row) for row in res2]]
        print("app", apprentice)
        print("user", users)
        ent_group_concat = ""
        if apprentice != [] or users != []:
            ent_group_concat = ", ".join(ent_group_dict.values())
        result = set(users + apprentice)

        return jsonify({"filtered": [str(row) for row in result],
                        "ent_group": ent_group_concat
                        }
                       ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route("/filter_meesages", methods=['GET'])
def filter_meesages():
    try:
        ent_group_dict = dict()
        roles = request.args.get("roles").split(",") if request.args.get("roles") is not None else None
        years = request.args.get("years").split(",") if request.args.get("years") is not None else None
        institutions = request.args.get("institutions").split(",") if request.args.get(
            "institutions") is not None else None
        preiods = request.args.get("preiods").split(",") if request.args.get("preiods") is not None else None
        eshcols = request.args.get("eshcols").split(",") if request.args.get("eshcols") is not None else None
        statuses = request.args.get("statuses").split(",") if request.args.get("statuses") is not None else None
        bases = request.args.get("bases").split(",") if request.args.get("bases") is not None else None
        hativa = request.args.get("hativa").split(",") if request.args.get("hativa") is not None else None
        region = request.args.get("region") if request.args.get("region") is not None and "?" not in request.args.get(
            "region") else None
        city = request.args.get("city")
        entityType = []
        # query user table
        print(roles[0])
        query = None
        if "melave" in roles:
            ent_group_dict["melave"] = "מלוים"
            entityType.append("0")
        if "racazMosad" in roles:
            ent_group_dict["racazMosad"] = "רכזי מוסד"
            entityType.append("1")
        if "racaz" in roles:
            ent_group_dict["racaz"] = "רכזי אשכול"
            entityType.append("2")
        if len(entityType):
            query = db.session.query(user1.id)
            query = query.filter(user1.role_id.in_(entityType))
            if institutions:
                ent_group_dict["institutions"] = institutions
                query = query.filter(user1.institution_id == Institution.id, Institution.name.in_(institutions))
            if region:
                ent_group_dict["region"] = region
                query = query.filter(user1.cluster_id == Cluster.id, Cluster.name == region)
            if eshcols:
                ent_group_dict["eshcols"] = region
                query = query.filter(user1.eshcol.in_(eshcols))
            if city:
                ent_group_dict["city"] = city
                query = query.filter(City.id == user1.city_id, city == City.name)

        res1 = []
        if query:
            res1 = query.all()
        query = None
        # query apprentice table
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
        res2 = []
        if query:
            res2 = query.all()
        print("app", res2)
        print("user", res1)
        users = [str(i[0]) for i in [tuple(row) for row in res1]]
        apprentice = [str(i[0]) for i in [tuple(row) for row in res2]]
        mess_user = db.session.query(ContactForm.id).filter(
            or_(ContactForm.created_by_id.in_(users), ContactForm.created_for_id.in_(users))).all()
        # reports_apprentice=db.session.query(ContactForm.id).filter(ContactForm.created_for_id.in_(apprentice)).all()
        # ent_group_concat=", ".join(ent_group_dict.values())
        # mess_ent_group=db.session.query(ContactForm.id).filter(ContactForm.ent_group==ent_group.id,ent_group.group_name==ent_group_concat).all()
        users_mess = [str(i[0]) for i in [tuple(row) for row in mess_user]]
        # apprentice_mess=[str(i[0]) for i in [tuple(row) for row in reports_apprentice]]
        # ent_group_mess=[str(i[0]) for i in [tuple(row) for row in mess_ent_group]]
        result = users_mess  # set(ent_group_mess+users_mess)
        print(result)
        return jsonify([str(row) for row in result]
                       ), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK


@messegaes_form_blueprint.route('/getById', methods=['GET'])
def getById():
    try:
        message_id = request.args.get('message_id')
        print(message_id)
        messegasesList = db.session.query(ContactForm.created_for_id, ContactForm.created_at, ContactForm.id,
                                          ContactForm.attachments, ContactForm.type, ContactForm.icon,
                                          ContactForm.allreadyread, ContactForm.subject, ContactForm.content
                                          , ContactForm.ent_group, ContactForm.created_by_id) \
            .filter(or_(ContactForm.id == message_id)).all()

        my_dict = []
        groped_mess = []
        group_report_dict = dict()
        print(messegasesList)
        for mess in messegasesList:
            daysFromNow = (date.today() - mess.created_at).days if mess.created_at is not None else None
            if mess.ent_group != "":
                if mess.ent_group + str(mess.id) in group_report_dict:
                    group_report_dict[mess.ent_group + str(mess.id)].append(str(mess.created_for_id))
                else:
                    group_report_dict[mess.ent_group + str(mess.id)] = [str(mess.created_for_id)]
                groped_mess.append(mess)
            else:
                my_dict.append(
                    {"type": mess.type, "attachments": mess.attachments, "id": str(mess.id),
                     "to": [str(mess.created_for_id)], "ent_group": "", "from": str(mess.created_by_id),
                     "date": toISO(mess.created_at),
                     "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),
                     "icon": mess.icon})

        for mess in groped_mess:
            if group_report_dict[mess.ent_group + str(mess.id)] != None:
                my_dict.append(
                    {"type": mess.type, "attachments": mess.attachments, "id": str(mess.id),
                     "from": str(mess.created_by_id), "date": toISO(mess.created_at),
                     "to": group_report_dict[mess.ent_group + str(mess.id)],
                     "content": mess.content, "title": str(mess.subject), "allreadyread": str(mess.allreadyread),
                     "ent_group": mess.ent_group,
                     "icon": mess.icon})
                group_report_dict[mess.ent_group + str(mess.id)] = None
        return jsonify(my_dict[0]), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.OK
