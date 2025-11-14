from flask import Blueprint


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.get('/ping')
def ping():
    return {'module': 'admin', 'ok': True}

