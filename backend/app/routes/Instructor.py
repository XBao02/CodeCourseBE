from flask import Blueprint


instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')


@instructor_bp.get('/ping')
def ping():
    return {'module': 'instructor', 'ok': True}

