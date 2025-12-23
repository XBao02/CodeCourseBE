from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Quan trọng: CHỈ import db – KHÔNG import create_app
from sqlalchemy import text

from app.models import db
from app.utils.seed import seed_default_instructor, seed_question_bank
from config import MYSQL_CONN


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
    # Prefer DATABASE_URL from .env; fallback to local XAMPP MySQL (root, no password)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", MYSQL_CONN)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Debug: Log JWT_SECRET_KEY on startup
    print(f"✅ Backend started with JWT_SECRET_KEY: {app.config['JWT_SECRET_KEY'][:30]}...")

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
        from app.routes.Payment import payment_bp
        from app.routes.payment_va import va_payment_bp
        from app.routes.sepay_webhook import sepay_webhook_bp
        from app.routes.EmailVerification import email_verification_bp
        from app.routes.PlacementAI import placement_ai_bp
        from app.routes.LearningPath import learning_path_bp
        from app.routes.Chat import chat_bp

        app.register_blueprint(ai_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(instructor_bp)
        app.register_blueprint(student_bp)
        app.register_blueprint(ai_quiz_bp)
        app.register_blueprint(payment_bp)
        app.register_blueprint(va_payment_bp)
        app.register_blueprint(sepay_webhook_bp)
        app.register_blueprint(email_verification_bp)
        app.register_blueprint(placement_ai_bp)
        app.register_blueprint(learning_path_bp)
        app.register_blueprint(chat_bp)

    except Exception as e:
        app.logger.error(f"Failed to register blueprints: {e}")

    # Health endpoint
    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app


# Application entry
def _ensure_columns(flask_app: Flask):
    with flask_app.app_context():
        engine = db.session.get_bind()
        with engine.connect() as connection:
            try:
                exists_payment = connection.execute(text("SHOW TABLES LIKE 'Payments'")).first()
                if not exists_payment:
                    connection.execute(
                        text(
                            """
                            CREATE TABLE Payments (
                              Id INT AUTO_INCREMENT PRIMARY KEY,
                              UserId BIGINT NOT NULL,
                              CourseId INT NOT NULL,
                              Amount DECIMAL(12,2) NOT NULL DEFAULT 0,
                              VaAccountNumber VARCHAR(64) NOT NULL UNIQUE,
                              BankCode VARCHAR(32) NOT NULL,
                              Status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                              TransactionId VARCHAR(128),
                              PaymentCode VARCHAR(64) UNIQUE,
                              PaidAt DATETIME NULL,
                              CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                              INDEX idx_payments_user (UserId),
                              INDEX idx_payments_course (CourseId),
                              CONSTRAINT fk_payments_user FOREIGN KEY (UserId) REFERENCES Users(Id),
                              CONSTRAINT fk_payments_course FOREIGN KEY (CourseId) REFERENCES Courses(Id)
                            )
                            """
                        )
                    )
                else:
                    for column, definition in [
                        ("PaymentCode", "VARCHAR(64) UNIQUE"),
                        ("BankCode", "VARCHAR(32) NOT NULL DEFAULT 'MBbank'"),
                        ("TransactionId", "VARCHAR(128)"),
                        ("PaidAt", "DATETIME NULL"),
                        ("Status", "VARCHAR(20) NOT NULL DEFAULT 'PENDING'"),
                    ]:
                        exists_col = connection.execute(
                            text("SHOW COLUMNS FROM Payments LIKE :column"), {"column": column}
                        ).first()
                        if not exists_col:
                            connection.execute(text(f"ALTER TABLE Payments ADD COLUMN {column} {definition}"))
            except Exception as exc:
                flask_app.logger.warning("Failed to ensure Payments table: %s", exc)
            for table, column, definition in [
                ("Payments", "BankCode", "VARCHAR(32) NOT NULL DEFAULT 'MBbank'"),
                ("Payments", "TransactionId", "VARCHAR(128)"),
                ("Payments", "PaidAt", "DATETIME NULL"),
                ("Payments", "Status", "VARCHAR(20) NOT NULL DEFAULT 'PENDING'"),
                ("skill_profiles", "RecommendedCourseIds", "JSON"),
                ("learning_paths", "RecommendedCourseIds", "JSON"),
                ("learning_path_items", "CourseIds", "JSON"),
                ("placement_questions", "BatchId", "VARCHAR(64)"),
                ("placement_questions", "Difficulty", "VARCHAR(64)"),
                ("placement_question_bank", "Difficulty", "VARCHAR(64)"),
                ("placement_question_bank", "Language", "VARCHAR(64) DEFAULT 'general' NOT NULL"),
                ("skill_profiles", "Language", "VARCHAR(64) DEFAULT 'general' NOT NULL"),
                ("placement_tests", "Language", "VARCHAR(64) DEFAULT 'general' NOT NULL"),
                ("placement_questions", "Language", "VARCHAR(64) DEFAULT 'general' NOT NULL"),
                ("Courses", "Language", "VARCHAR(64) DEFAULT 'general' NOT NULL"),
                ("Messages", "AttachmentUrl", "VARCHAR(500)"),
                ("Messages", "AttachmentType", "VARCHAR(20)"),
                ("Messages", "AttachmentName", "VARCHAR(255)"),
                ("Messages", "MessageType", "VARCHAR(20) DEFAULT 'text'"),
            ]:
                try:
                    exists = connection.execute(
                        text(f"SHOW COLUMNS FROM {table} LIKE :column"),
                        {"column": column},
                    ).first()
                    if not exists:
                        connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
                except Exception as exc:
                    flask_app.logger.warning(
                        "Failed to ensure column %s.%s (%s)", table, column, exc
                    )


def _ensure_default_data(flask_app: Flask):
    with flask_app.app_context():
        try:
            db.create_all()
        except Exception as exc:  # pragma: no cover - best effort schema sync
            flask_app.logger.warning("Failed to create missing tables: %s", exc)
        seed_default_instructor()
        seed_question_bank()
        _ensure_columns(flask_app)


app = create_app()
_ensure_default_data(app)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in ("1", "true", "True")
    app.run(host=host, port=port, debug=debug)
