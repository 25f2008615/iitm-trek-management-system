from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False) 

    role = db.Column(db.String(20), nullable=False)

    age = db.Column(db.Integer, nullable=False)

    gender = db.Column(db.String(10), nullable=False)
    
    is_approved = db.Column(db.Boolean, default=True)
    
    is_blacklisted = db.Column(
    db.Boolean,
    default=False
    )

    treks = db.relationship("Trek", backref="staff", lazy=True)

    bookings = db.relationship("Booking", backref="user", lazy=True)

class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(100), nullable=False)

    location = db.Column(db.String(100), nullable=False)

    difficulty = db.Column(db.String(20), nullable=False)

    duration_days = db.Column(db.Integer, nullable=False)

    distance_km = db.Column(db.Float, nullable=False)

    price = db.Column(db.Integer, nullable=False)

    max_trekkers = db.Column(db.Integer, nullable=False)

    season = db.Column(db.String(20), nullable=False)

    weather = db.Column(db.String(30), nullable=False)

    transport = db.Column(db.String(50), nullable=False)

    description = db.Column(db.Text)
    
    status = db.Column(
    db.String(20),
    nullable=False,
    default="Open"
    )

    image_url = db.Column(db.String(255))

    staff_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True) 

    bookings = db.relationship("Booking", backref="trek", lazy=True)

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )

    booking_date = db.Column(db.Date, nullable=False)

    number_of_people = db.Column(db.Integer, nullable=False)

    total_amount = db.Column(db.Integer, nullable=False)

    payment_status = db.Column(
        db.String(20),
        nullable=False,
        default="Paid"
    )

    