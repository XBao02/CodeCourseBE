from flask import Blueprint


student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.get('/ping')
def ping():
    return {'module': 'student', 'ok': True}
