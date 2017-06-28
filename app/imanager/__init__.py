from flask import Blueprint

imanager = Blueprint('imanager', __name__)

from . import views, forms, error
from ..models import Permission

@imanager.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)