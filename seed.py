from app import app
from models import db, User

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(email="admin@trek.com").first()

    if not admin:

        admin = User(
            full_name="Administrator",
            email="admin@trek.com",
            password="admin123",
            role="Admin",
            age=30,
            gender="Other",
            is_approved=True
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully.")

    else:

        print("Admin already exists.")