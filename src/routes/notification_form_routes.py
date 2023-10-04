from flask import Blueprint, request, jsonify
from http import HTTPStatus
from os import sys, path

pth = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
sys.path.append(pth)
from app import app, db
import uuid

from ..models.notification_model import notifications

notification_form_blueprint = Blueprint('notification_form', __name__, url_prefix='/notification_form')

@notification_form_blueprint.route('/add', methods=['POST'])
def add_notification_form():
    user = request.form.get('userId')
    apprenticeid = request.form.get('apprenticeid')
    event = request.form.get('event')
    date = request.form.get('date')

    print(user)

    newToner = notifications(

                    userid=user,
                    apprenticeid = apprenticeid,
                    event=event,
                    date=date,
                    timefromnow=None,
                    allreadyread=False,
                    id=int(str(uuid.uuid4().int)[:5]),

    )
    print(newToner)
    db.session.add(newToner)
    db.session.commit()
    if  newToner is None :
        # acount not found
        return jsonify(["Wrong id"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify({"result":"success"}), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/getAll', methods=['GET'])
def getAll_notification_form():
    user = request.args.get('created_by_id')
    print(user)

    notiList = db.session.query(notifications).filter(notifications.userid == user).all()
    my_dict = []
    for noti in notiList:
        my_dict.append(
            {"id": noti.id, "apprenticeId": noti.apprenticeid, "date": noti.date,
             "timeFromNow": noti.timefromnow, "event": noti.event, "allreadyread": noti.allreadyread,"numOfLinesDisplay":noti.numoflinesdisplay})

    if not notiList :
        # acount not found
        return jsonify(["Wrong id or emty list"])
    else:
        # print(f' notifications: {my_dict}]')
        # TODO: get Noti form to DB
        return jsonify(my_dict), HTTPStatus.OK
        # return jsonify([{'id':str(noti.id),'result': 'success',"apprenticeId":str(noti.apprenticeid),"date":str(noti.date),"timeFromNow":str(noti.timefromnow),"event":str(noti.event),"allreadyread":str(noti.allreadyread)}]), HTTPStatus.OK


@notification_form_blueprint.route('/setWasRead', methods=['post'])
def setWasRead_notification_form():
    notiId = request.form.get('noti_id')
    print(notiId)
    noti = notifications.query.get(notiId)
    noti.allreadyread = 'true'
    db.session.commit()
    if notiId:
        # print(f'setWasRead form: subject: [{subject}, notiId: {notiId}]')
        # TODO: add contact form to DB
        return jsonify({'result': 'success', 'notiId form': request.form}), HTTPStatus.OK


@notification_form_blueprint.route('/uploadPhoto', methods=['post'])
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


@notification_form_blueprint.route('/getProfileAtributes', methods=['post'])
def getProfileAtributes_form():
    created_by_id = request.form.get('created_by_id')
    print(created_by_id)

    if created_by_id:
        print(f' created_by_id: {created_by_id}]')
        # TODO: get Noti form to DB
        return jsonify([{'apprenticeId': '11', 'Pname': 'Oz', "Fname": "Kli", "birthDay": "20.3.2023",
                         "email": "oz@sd.com ", "town": "Aza", "area": "Dan", "userRole": "Melave", "Mosad": "Dan",
                         "Eshcol": "Aza", "apprenticeList": "Av,ra,ha"}, ]), HTTPStatus.OK