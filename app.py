from flask import Flask, render_template, request, redirect, url_for, session, flash

from config import Config
from models import db, User, Trek, Booking 
from datetime import date

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("user/home.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:

            if user.role == "Staff" and not user.is_approved:

                flash(
                    "Your account is waiting for Admin approval.",
                    "warning"
                )

                return redirect(url_for("login"))

            session["user_id"] = user.id
            session["full_name"] = user.full_name
            session["role"] = user.role

            if user.role == "Staff":
                return redirect(url_for("staff_dashboard"))

            elif user.role == "Admin":
                return redirect(url_for("admin_dashboard"))

            return redirect(url_for("home"))

        return render_template(
            "auth/login.html",
            error="Invalid email or password."
        )

    return render_template("auth/login.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        role = request.form["role"]

        new_user = User(
            full_name=request.form["full_name"],
            email=request.form["email"],
            password=request.form["password"],
            role=role,
            age=int(request.form["age"]),
            gender=request.form["gender"],
            is_approved=(role != "Staff")
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("auth/register.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- USER TREKS ---------------- #

@app.route("/treks")
def treks():

    treks = Trek.query.all()

    return render_template(
        "user/treks.html",
        treks=treks
    )


# ---------------- TREK DETAILS ---------------- #

@app.route("/trek/<int:trek_id>")
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return render_template(
        "user/trek_details.html",
        trek=trek
    )


# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin/dashboard")
def admin_dashboard():

    return render_template("admin/dashboard.html")


# ---------------- MANAGE TREKS ---------------- #

@app.route("/admin/manage-treks", methods=["GET", "POST"])
def manage_treks():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    edit_id = request.args.get("edit_id")
    trek_to_edit = None

    if edit_id:
        trek_to_edit = Trek.query.get_or_404(int(edit_id))

    if request.method == "POST":

        trek_id = request.form.get("trek_id")

        if trek_id:
            trek = Trek.query.get_or_404(int(trek_id))
        else:
            trek = Trek(
                distance_km=0,
                max_trekkers=0,
                season="Not Assigned",
                weather="Not Assigned",
                transport="Not Assigned",
                image_url="",
                staff_id=None
            )
            db.session.add(trek)

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration_days = int(request.form["duration_days"])
        trek.price = int(request.form["price"])
        trek.description = request.form["description"]

        staff_id = request.form.get("staff_id")

        if staff_id:
            trek.staff_id = int(staff_id)
        else:
            trek.staff_id = None

        db.session.commit()

        if trek_id:
            flash("Trek updated successfully!", "success")
        else:
            flash("Trek added successfully!", "success")

        return redirect(url_for("manage_treks"))

    treks = Trek.query.all()

    staff_members = User.query.filter_by(
        role="Staff",
        is_approved=True
    ).all()

    return render_template(
        "admin/manage_treks.html",
        treks=treks,
        trek_to_edit=trek_to_edit,
        staff_members=staff_members
    )


# ---------------- DELETE TREK ---------------- #

@app.route("/admin/delete-trek/<int:trek_id>")
def delete_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()
    
    flash("Trek deleted successfully!", "success")

    return redirect(url_for("manage_treks"))

# ---------------- BOOK TREK ------------------#

@app.route("/book-trek/<int:trek_id>")
def book_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    trek = Trek.query.get_or_404(trek_id)

    existing_booking = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
        ).first()

    print("Session user_id:", session["user_id"])
    print("Current trek_id:", trek.id)
    print("Existing booking:", existing_booking)

    if existing_booking:
        
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("my_bookings"))

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_date=date.today(),
        number_of_people=1,
        total_amount=trek.price,
        payment_status="Paid"
    )

    db.session.add(booking)
    db.session.commit()
    
    flash("Trek booked successfully!", "success")

    return redirect(url_for("my_bookings"))


# ----------- MY BOOKINGS ----------------#

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )

# ---------------- APPROVE STAFF ---------------- #

@app.route("/admin/approve-staff")
def approve_staff_page():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    staff_members = User.query.filter_by(
        role="Staff",
        is_approved=False
    ).all()

    return render_template(
        "admin/approve_staff.html",
        staff_members=staff_members
    )


@app.route("/admin/approve-staff/<int:user_id>")
def approve_staff(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    staff = User.query.get_or_404(user_id)

    staff.is_approved = True

    db.session.commit()

    flash("Staff approved successfully!", "success")

    return redirect(url_for("approve_staff_page"))


# ---------------- STAFF DASHBOARD ---------------- #

@app.route("/staff/dashboard")
def staff_dashboard():

    if session.get("role") != "Staff":
        return redirect(url_for("home"))

    treks = Trek.query.filter_by(
        staff_id=session["user_id"]
    ).all()

    return render_template(
        "staff/dashboard.html",
        treks=treks
    )


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)