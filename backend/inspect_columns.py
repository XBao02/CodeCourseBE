from app import create_app
from app.models import db
from sqlalchemy import text
app = create_app()
with app.app_context():
    engine = db.session.get_bind()
    with engine.connect() as conn:
        for table in ['skill_profiles','learning_paths','learning_path_items','placement_questions']:
            cols = [row[0] for row in conn.execute(text(f"SHOW COLUMNS FROM {table}"))]
            print(table, cols)
