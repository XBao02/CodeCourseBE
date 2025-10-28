from flask import Blueprint

instructor_bp = Blueprint('instructor', __name__, url_prefix='/api/instructor')

@instructor_bp.route('/courses', methods=['GET'])
def get_courses():
    # Add get instructor courses logic here
    pass

@instructor_bp.route('/course', methods=['POST'])
def create_course():
    # Add create course logic here
    pass

@instructor_bp.route('/course/<course_id>', methods=['PUT'])
def update_course(course_id):
    # Add update course logic here
    pass
