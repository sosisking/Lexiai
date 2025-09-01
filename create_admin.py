from src.main import create_app
from src.models.user import User
from src.models import db

app = create_app()

with app.app_context():
    admin = User(email="admin@lexiai.com", password="adminpassword", first_name="Admin", last_name="User", role="admin")
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully")

