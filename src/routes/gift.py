import csv
import datetime
import uuid

import boto3
from openpyxl.reader.excel import load_workbook
from flask import Blueprint, request, jsonify, send_file
from http import HTTPStatus
from src.services import db, red
from src.models.gift import gift
from src.models.notification_model import notifications

gift_blueprint = Blueprint('gift', __name__, url_prefix='/gift')


@gift_blueprint.route("/add_giftCode_excel", methods=['put'])
def add_giftCode_excel():
    try:
        file = request.files['file']
        wb = load_workbook(file)
        sheet = wb.active
        not_commited = []
        for row in sheet.iter_rows(min_row=2):
            code = row[0].value
            was_used = False
            gift1 = gift(code=code, was_used=was_used)
            db.session.add(gift1)
            try:
                db.session.commit()
            except Exception as e:
                not_commited.append(code)
        return jsonify({'result': 'success', "not_commited": not_commited}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@gift_blueprint.route('/getGift', methods=['GET'])
def getGift():
    try:
        teudat_zehut = request.args.get('teudat_zehut')
        base = request.args.get('base')
        giftCode = db.session.query(gift).filter(gift.was_used == False).first()
        print(giftCode)
        if not giftCode:
            # acount not found
            return jsonify({'result': 'no code available'}), HTTPStatus.OK
        else:
            return jsonify({'result': str(giftCode.code)}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@gift_blueprint.route("/delete", methods=['put'])
def delete():
    try:
        giftCode1 = request.args.get('giftCode')
        apprentice_id = request.args.get('')

        giftCode = db.session.query(gift).filter(gift.code == giftCode1).first()
        if giftCode is not None:
            giftCode.was_used = True
            # res = db.session.query(gift).filter(gift.code == giftCode.code).delete()
            res = db.session.query(notifications).filter(
                notifications.subject == apprentice_id,
                notifications.event == "יומהולדת",
            ).delete()

            db.session.commit()

        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@gift_blueprint.route("/deleteAll", methods=['put'])
def deleteAll():
    try:

        giftCode = db.session.query(gift).delete()
        db.session.commit()

        return jsonify({'result': 'success'}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST


@gift_blueprint.route("/getGifts_cnt", methods=['get'])
def getGifts_cnt():
    try:

        giftCodes_all = db.session.query(gift).all()
        giftCodes_used = db.session.query(gift).filter(gift.was_used == True).all()
        giftCodes_all_cnt = len(giftCodes_all) or 0
        giftCodes_used_cnt = len(giftCodes_used) or 0

        return jsonify(f"מומשו {giftCodes_used_cnt} מתוך {giftCodes_all_cnt} קודי מתנה"), HTTPStatus.OK
    except Exception as e:
        return jsonify({'result': str(e)}), HTTPStatus.BAD_REQUEST
