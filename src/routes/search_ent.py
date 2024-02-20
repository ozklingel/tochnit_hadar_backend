from http import HTTPStatus

from flask import Blueprint, request, jsonify
from openpyxl.reader.excel import load_workbook
from werkzeug.utils import secure_filename

import config
from app import db
from src.models.apprentice_model import Apprentice
from src.models.city_model import City
from src.models.cluster_model import Cluster
from src.models.contact_form_model import ContactForm
from src.models.eshcol_model import Eshcol
from src.models.gift import gift
from src.models.institution_model import Institution
from src.models.notification_model import notifications
from src.models.user_model import user1
from src.models.visit_model import Visit

search_bar_form_blueprint = Blueprint('search_bar', __name__, url_prefix='/search_bar')

@search_bar_form_blueprint.route("/search_entities", methods=['GET'])
def search_entities():
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
            entityType.append("0")
        if "racazMosad" in roles:
            entityType.append("1")
        if "racaz" in roles:
            entityType.append("2")
        if len(entityType):
            query = db.session.query(user1.id)
            query = query.filter(user1.role_id.in_(entityType))
            if institutions:
                query = query.filter(user1.institution_id == Institution.id, Institution.name.in_(institutions))
            if region:
                query = query.filter(user1.cluster_id == Cluster.id, Cluster.name == region)
            if eshcols:
                query = query.filter(user1.eshcol.in_(eshcols))
            if city:
                query = query.filter(City.id == user1.city_id, city == City.name)

        res1 = []
        if query:
            res1 = query.all()
        query = None
        # query apprentice table
        if "apprentice" in roles:
            query = db.session.query(Apprentice.id)
            if institutions:
                query = query.filter(Apprentice.institution_id == Institution.id, Institution.name.in_(institutions))
            if years:

                query = query.filter(Apprentice.hadar_plan_session.in_(years))
            if preiods:

                query = query.filter(Apprentice.institution_mahzor.in_(preiods))
            if statuses:

                query = query.filter(Apprentice.marriage_status.in_(statuses))
            if bases:

                query = query.filter(Apprentice.base_address.in_(bases))
            if hativa:

                query = query.filter(Apprentice.unit_name.in_(hativa))
            if region:

                query = query.filter(Apprentice.cluster_id == Cluster.id, Cluster.name == region)
            if eshcols:

                query = query.filter(Apprentice.eshcol.in_(eshcols))
            if city:
                query = query.filter(City.id == Apprentice.city_id, city == City.name)
        res2 = []
        if query:
            res2 = query.all()
        users = [str(i[0]) for i in [tuple(row) for row in res1]]
        apprentice = [str(i[0]) for i in [tuple(row) for row in res2]]
        print("app", apprentice)
        print("user", users)

        result = set(users + apprentice)

        return jsonify({"filtered": [str(row) for row in result]
                        }
                       ), HTTPStatus.OK


