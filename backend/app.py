from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, '.env')
    # Load environment variables
    if os.path.exists(env_path):
        load_dotenv(env_path)

    app = Flask(__name__)
    # Load config from environment for secrets and CORS
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", app.config["SECRET_KEY"])  # fallback

    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        CORS(app, origins=[o.strip() for o in cors_origins.split(",") if o.strip()])
    else:
        CORS(app)

    # Init JWT (SECRET_KEY / JWT_SECRET_KEY từ .env)
    JWTManager(app)

    # Register blueprints
    try:
        from app.routes.AI import ai_bp
        from app.routes.Auth import auth_bp
        from app.routes.Admin import admin_bp
        from app.routes.Instructor import instructor_bp
        from app.routes.Student import student_bp

        app.register_blueprint(ai_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(instructor_bp)
        app.register_blueprint(student_bp)
    except Exception as e:
        # Log error but keep app constructible
        app.logger.error(f"Failed to register blueprints: {e}")

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app


# WSGI entrypoint
app = create_app()

if __name__ == "__main__":
    # Enable running with: python app.py
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    app.run(host=host, port=port, debug=debug)
