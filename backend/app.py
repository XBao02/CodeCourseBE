from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Quan trọng: CHỈ import db – KHÔNG import create_app
from app.models import db


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')

    # Load .env
    if os.path.exists(env_path):
        load_dotenv(env_path)

    app = Flask(__name__)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        # "mysql+pymysql://root:@localhost:/CodeCourse"
        "mysql+pymysql://root:123@localhost:3306/CodeCourse"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Init extensions
    db.init_app(app)
    JWTManager(app)

    # CORS - Enable for all origins and methods
    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        CORS(app, 
             origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization"])
    else:
        CORS(app, 
             origins="*",
             methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             allow_headers=["Content-Type", "Authorization"])

    # Register blueprints
    try:
        from app.routes.AI import ai_bp
        from app.routes.Auth import auth_bp
        from app.routes.Admin import admin_bp
        from app.routes.Instructor import instructor_bp
        from app.routes.Student import student_bp
        from app.routes.AIQuiz import ai_quiz_bp
        
        app.register_blueprint(ai_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(instructor_bp)
        app.register_blueprint(student_bp)
        app.register_blueprint(ai_quiz_bp)

    except Exception as e:
        app.logger.error(f"Failed to register blueprints: {e}")

    # Health endpoint
    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app


# Application entry
app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    app.run(host=host, port=port, debug=debug)
