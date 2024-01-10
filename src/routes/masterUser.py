import datetime

from flask import Blueprint, request, jsonify
from http import HTTPStatus

from openpyxl.reader.excel import load_workbook
from sqlalchemy import func, and_

from app import db, red
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit
from src.routes.notification_form_routes import getAll_notification_form

master_user_form_blueprint = Blueprint('master_user', __name__, url_prefix='/master_user')


@master_user_form_blueprint.route("/search_entities", methods=['GET'])
def search_entities():
    isMosad_coord = request.args.get("isMosad_coord")
    isEshcol_coord = request.args.get("isEshcol_coord")
    isMelave= request.args.get("isMelave")
    isApprentice = request.args.get("isApprentice")
    institution_id = request.args.get("institution_id")
    thpreiodList = request.args.get("thpreiod")
    institution_mahzor = request.args.get("institution_mahzor")
    eshcol = request.args.get("eshcol")
    marriage_status = request.args.get("marriage_status")
    base_address = request.args.get("base_address")
    city_name = request.args.get("city_name")+" " if request.args.get("city_name") is not None else None
    region = request.args.get("region")
    entityType=[]
    #query user table
    query = None
    if isMelave=="True":
        entityType.append("0")
    if isMosad_coord=="True":
        entityType.append("1")
    if isEshcol_coord=="True":
        entityType.append("2")
    if len(entityType):
        query = db.session.query(user1.id)
        query = query.filter(user1.role_id.in_(entityType))
        if institution_id:
            query = query.filter_by(institution_id=institution_id)
        if eshcol:
            query = query.filter_by(eshcol=eshcol)
        if city_name:
            city_idDB = db.session.query(City.id).filter(City.name == city_name).first()
            if city_idDB:
                query = query.filter_by(city_id=city_idDB.id)
    res1=None
    if query:
        res1 = query.all()
    query=None
    #query apprentice table
    if isApprentice=="True":
        query = db.session.query(Apprentice.id)
        if thpreiodList:
            print("thpreiodList",thpreiodList)
            query = query.filter(Apprentice.hadar_plan_session.in_(list(thpreiodList)))
            #query = query.filter_by(thpreiod=thpreiod)
        if institution_mahzor:
            query = query.filter_by(institution_mahzor=institution_mahzor)
        if marriage_status:
            query = query.filter_by(marriage_status=marriage_status)
        if base_address:
            query = query.filter_by(base_address=base_address)
        if institution_id:
            query = query.filter_by(institution_id=institution_id)
        if eshcol:
            query = query.filter_by(eshcol=eshcol)
        if city_name:
            city_idDB = db.session.query(City.id).filter(City.name == city_name).first()
            print("city_idDB",city_idDB)
            if city_idDB:
                query = query.filter_by(city_id=city_idDB.id)
    res2=None
    if query:
        res2 = query.all()
    print("res2",res2)
    return jsonify({"users":
        [str(i[0]) for i in [tuple(row) for row in res1]] if res1 is not None else [],
                    "apprentices":
                        [str(i[0]) for i in [tuple(row) for row in res2]] if res2 is not None else [],

                    }
    ), HTTPStatus.OK



@master_user_form_blueprint.route("/add_apprentice_manual", methods=['post'])
def add_apprentice():
    data = request.json
    print(data)
    first_name = data['first_name']
    last_name = data['last_name']
    phone = data['phone']
    institution_name = data['institution_name']
    try:
        institution_id = db.session.query(Institution).filter(
            Institution.name == institution_name).first()
        Apprentice1 = Apprentice(
            id=phone[1:],
            name=first_name,
            last_name=last_name,
            phone=phone,
            institution_id=institution_id,
        )
        db.session.add(Apprentice1)
        db.session.commit()
    except Exception as e:
        return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

    if Apprentice1:
        # TODO: add contact form to DB
        return jsonify({'result': 'success'}), HTTPStatus.OK

@master_user_form_blueprint.route("/add_apprentice_excel", methods=['put'])
def add_apprentice_excel():
    from openpyxl import workbook
    path = '/home/ubuntu/flaskapp/Book1.xlsx'
    wb = load_workbook(filename=path)
    ws = wb.get_sheet_by_name('Sheet1')
    for row in ws.iter_rows(min_row=2):
                first_name = row[0].value
                last_name = row[1].value
                phone = row[3].value
                institution_name = row[2].value
                print(first_name)
                print(phone)

                try:
                    institution_id = db.session.query(Institution).filter(
                        Institution.name == str(institution_name)).first()
                    Apprentice1 = Apprentice(
                        id=int(str(phone)[1:]),
                        name=first_name,
                        last_name=last_name,
                        phone=str(phone),
                        institution_id=institution_id,
                    )
                    db.session.add(Apprentice1)
                    db.session.commit()
                except Exception as e:
                    return jsonify({'result': 'error while inserting'+str(e)}), HTTPStatus.BAD_REQUEST

                if Apprentice1:
                    # TODO: add contact form to DB
                    return jsonify({'result': 'success'}), HTTPStatus.OK

