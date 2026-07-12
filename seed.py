from app import app
from models import db, User, Trek

with app.app_context():

    db.create_all()

    # ---------------- Admin ----------------

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

    # ---------------- Demo Staff ----------------

    staff = User.query.filter_by(email="staff@trek.com").first()

    if not staff:

        staff = User(
            full_name="Demo Staff",
            email="staff@trek.com",
            password="staff123",
            role="Staff",
            age=28,
            gender="Other",
            is_approved=True
        )

        db.session.add(staff)
        db.session.commit()

    # ---------------- Demo Treks ----------------

    if Trek.query.count() == 0:

        treks = [

            Trek(
                trek_name="Kedarkantha Trek",
                distance_km=20,
                location="Uttarakhand",
                difficulty="Easy",
                duration_days=6,
                price=7000,
                max_trekkers=15,
                season="Winter",
                weather="Snow",
                transport="Bus",
                description="Beautiful winter trek.",
                status="Open",
                staff_id=staff.id
            ),

            Trek(
                trek_name="Hampta Pass Trek",
                distance_km=26,
                location="Himachal Pradesh",
                difficulty="Moderate",
                duration_days=5,
                price=8500,
                max_trekkers=20,
                season="Summer",
                weather="Pleasant",
                transport="Bus",
                description="Amazing crossover trek.",
                status="Open"
            ),

            Trek(
                trek_name="Valley of Flowers",
                distance_km=18,
                location="Uttarakhand",
                difficulty="Moderate",
                duration_days=7,
                price=9500,
                max_trekkers=25,
                season="Monsoon",
                weather="Cool",
                transport="Bus",
                description="Famous flower valley.",
                status="Open"
            )

        ]

        db.session.add_all(treks)
        db.session.commit()

    print("Database seeded successfully.")