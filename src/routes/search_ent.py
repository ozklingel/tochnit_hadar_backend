from http import HTTPStatus
from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from src.models.cluster_model import Cluster
from src.services import db
from src.models.apprentice_model import Apprentice
from src.models.base_model import Base
from src.models.city_model import City
from src.models.region_model import Region
from src.models.institution_model import Institution
from src.models.user_model import User

search_bar_form_blueprint = Blueprint("search_bar", __name__, url_prefix="/search_bar")


@search_bar_form_blueprint.route("/search_entities", methods=["GET"])
def search_entities():
    try:

        users, apprentice, ent_group_dict = filter_by_request(request)

        result = set(users + apprentice)

        return jsonify({"filtered": [str(row) for row in result]}), HTTPStatus.OK

    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.OK


def filter_by_request(request_):
    try:
        ent_group_dict = dict()
        roles = (
            request_.args.get("roles").split(",")
            if request_.args.get("roles") is not None
            else None
        )
        years = (
            request_.args.get("years").split(",")
            if request_.args.get("years") is not None
            else None
        )
        institutions = (
            request_.args.get("institutions").split(",")
            if request_.args.get("institutions") is not None
            else None
        )
        preiods = (
            request_.args.get("preiods").split(",")
            if request_.args.get("preiods") is not None
            else None
        )
        eshcols = (
            request_.args.get("eshcols").split(",")
            if request_.args.get("eshcols") is not None
            else None
        )
        statuses = (
            request_.args.get("statuses").split(",")
            if request_.args.get("statuses") is not None
            else None
        )
        bases = (
            request_.args.get("bases").split(",")
            if request_.args.get("bases") is not None
            else None
        )
        hativa = (
            request_.args.get("hativa").split(",")
            if request_.args.get("hativa") is not None
            else None
        )
        army_role = (
            request_.args.get("army_role").split(",")
            if request_.args.get("army_role") is not None
            else None
        )
        region = (
            request_.args.get("region")
            if request_.args.get("region") is not None
            and "?" not in request_.args.get("region")
            else None
        )
        city = request_.args.get("city")
        entityType = []

        if not roles:
            return [], [], ent_group_dict
        # query user table
        query = None
        if "מלוה" in roles:
            ent_group_dict["melave"] = "מלוים"
            entityType.append("0")
        if "רכז מוסד" in roles:
            ent_group_dict["racazMosad"] = "רכזי מוסד"
            entityType.append("1")
        if "רכז אשכול" in roles:
            ent_group_dict["racaz"] = "רכזי אשכול"
            entityType.append("2")
        if "אחראי תוכנית" in roles:
            ent_group_dict["achrai tochnit"] = "אחראי תוכנית"
            entityType.append("3")
        if len(entityType) > 0:
            query = db.session.query(User.id).distinct(User.id)
            filter_list = [User.role_ids.contains(x) for x in entityType]

            query = query.filter(or_(*filter_list))
            if institutions:
                ent_group_dict["institutions"] = (
                    str(institutions).replace("[", "").replace("]", "")
                )
                query = query.filter(
                    User.institution_id == Institution.id,
                    Institution.name.in_(institutions),
                )
            if region:
                ent_group_dict["region"] = region
                query = query.filter(User.region_id == Region.id, Region.name == region)
            if eshcols:
                ent_group_dict["eshcols"] = (
                    str(eshcols).replace("[", "").replace("]", "")
                )
                query = query.filter(
                    User.cluster_id == Cluster.id, Cluster.name.in_(eshcols)
                )
            if city:
                ent_group_dict["city"] = city
                query = query.filter(User.city_id == City.id, city == City.name)

        res1 = []
        if query and not (hativa or army_role or bases or statuses or preiods or years):
            res1 = query.all()

        query = None
        # query apprentice table
        if "חניך" in roles:
            ent_group_dict["apprentice"] = "חניכים"
            query = db.session.query(Apprentice.id).distinct(Apprentice.id)
            if institutions:
                ent_group_dict["institutions"] = ", ".join(institutions)
                query = query.filter(
                    Apprentice.institution_id == Institution.id,
                    Institution.name.in_(institutions),
                )
            if years:
                ent_group_dict["years"] = str(years).replace("[", "").replace("]", "")

                query = query.filter(Apprentice.hadar_plan_session.in_(years))
            if preiods:
                ent_group_dict["preiods"] = (
                    str(preiods).replace("[", "").replace("]", "")
                )

                query = query.filter(Apprentice.institution_mahzor.in_(preiods))
            if statuses:
                ent_group_dict["statuses"] = (
                    str(statuses).replace("[", "").replace("]", "")
                )
                query = query.filter(Apprentice.marriage_status.in_(statuses))
            if bases:
                ent_group_dict["bases"] = str(bases).replace("[", "").replace("]", "")
                query = query.filter(
                    Base.id == Apprentice.base_address, Base.name.in_(bases)
                )
            if hativa:
                ent_group_dict["hativa"] = str(hativa).replace("[", "").replace("]", "")

                query = query.filter(Apprentice.unit_name.in_(hativa))
            if army_role:
                ent_group_dict["army_role"] = (
                    str(hativa).replace("[", "").replace("]", "")
                )
                query = query.filter(Apprentice.army_role.in_(army_role))
            if region:
                ent_group_dict["region"] = region
                query = query.filter(
                    Apprentice.city_id == City.id,
                    City.region_id == Region.id,
                    Region.name == region,
                )
            if eshcols:
                ent_group_dict["eshcols"] = (
                    str(eshcols).replace("[", "").replace("]", "")
                )
                query = query.filter(
                    Apprentice.cluster_id == Cluster.id, Cluster.name.in_(eshcols)
                )
            if city:
                ent_group_dict["city"] = city
                query = query.filter(City.id == Apprentice.city_id, city == City.name)
        res2 = []
        if query:
            try:
                res2 = query.all()
            except Exception as e:
                print(str(e))
        users = [str(i[0]) for i in [tuple(row) for row in res1]]
        apprentice = [str(i[0]) for i in [tuple(row) for row in res2]]
        return users, apprentice, ent_group_dict
    except Exception as e:
        return jsonify({"result": str(e)}), HTTPStatus.BAD_REQUEST
