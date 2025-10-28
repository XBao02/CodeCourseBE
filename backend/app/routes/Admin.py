from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
def get_users():
    # Add get users logic here
    pass

@admin_bp.route('/courses', methods=['GET'])
def get_courses():
    # Add get courses logic here
    pass

@admin_bp.route('/reports', methods=['GET'])
def get_reports():
    # Add reports logic here
    pass
