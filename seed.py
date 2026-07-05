from app import app
from models import db, User

with app.app_context():

    admin = User.query.filter_by(email="admin@trek.com").first()

    if admin:
        print("Admin already exists.")

    else:

        admin = User(
            full_name="Administrator",
            email="admin@trek.com",
            password="admin123",
            role="Admin",
            age=30,
            gender="Other"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully.")