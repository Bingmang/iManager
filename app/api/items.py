from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import iManagerItem, User
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/get_imanager/<path:item_id>')
def get_imanager(item_id):
    imanager = iManagerItem.query.filter_by(item_id=item_id).first()
    if imanager is not None:
        if g.current_user == imanager.owner:
            return jsonify(imanager.to_json())
        return forbidden('The Goalkeeper is NOT BELONGS to you! --By Goalkeeper')
    return forbidden('The Goalkeeper is NOT EXIST! --By Goalkeeper')


@api.route('/get_user_imanagers/<path:user_email>')
def get_user_imanagers(user_email):
    imanagers = g.current_user.imanagers.order_by(iManagerItem.registe_time)
    if imanagers is not None:
        if user_email == g.current_user.email:
            json_imanagers = {"imanagers": []}
            for imanager in imanagers:
                json_imanagers["imanagers"].append(imanager.to_json())
            return jsonify(json_imanagers)
        return forbidden('The Goalkeeper is NOT BELONGS to you! --By Goalkeeper')
    return forbidden('The Goalkeeper is NOT EXIST! --By Goalkeeper')