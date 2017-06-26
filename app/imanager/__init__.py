from flask import Blueprint

imanager = Blueprint('imanager', __name__)

from . import views, forms
