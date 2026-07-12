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
            
            if user.is_blacklisted:

                flash(
                    "Your account has been blacklisted by the Admin.",
                    "danger"
                )

                return redirect(url_for("login"))

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


#----------------- PROFILE ---------------------#

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        user.full_name = request.form["full_name"]
        user.age = int(request.form["age"])
        user.gender = request.form["gender"]

        db.session.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        user=user
    )
# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- USER TREKS ---------------- #

@app.route("/treks")
def treks():

    search = request.args.get("search", "")

    if search:

        treks = Trek.query.filter(
            (Trek.trek_name.ilike(f"%{search}%")) |
            (Trek.location.ilike(f"%{search}%"))
        ).all()

    else:

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

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    total_users = User.query.filter_by(role="Trekker").count()

    total_staff = User.query.filter_by(
        role="Staff",
        is_approved=True
    ).count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )


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
        trek.max_trekkers = int(request.form["max_trekkers"])
        trek.season = request.form["season"]
        trek.weather = request.form["weather"]
        trek.transport = request.form["transport"]
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

    search = request.args.get("search", "")

    if search:
        treks = Trek.query.filter(
            (Trek.trek_name.ilike(f"%{search}%")) |
            (Trek.location.ilike(f"%{search}%"))
        ).all()
    else:
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
    
    if trek.status != "Open":

        flash(
            "Bookings are closed for this trek.",
            "danger"
        )

        return redirect(
            url_for("trek_details", trek_id=trek.id)
        )

    if len(trek.bookings) >= trek.max_trekkers:

        flash("Sorry! This trek is fully booked.", "danger")

        return redirect(url_for("trek_details", trek_id=trek.id))

    existing_booking = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

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


# ---------------- MANAGE STAFF ---------------- #

@app.route("/admin/manage-staff")
def manage_staff():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    search = request.args.get("search", "")

    query = User.query.filter_by(
        role="Staff",
        is_approved=True
    )

    if search:

        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )

    staff_members = query.all()

    return render_template(
        "admin/manage_staff.html",
        staff_members=staff_members
    )


# ---------------- TOGGLE STAFF STATUS ---------------- #

@app.route("/admin/toggle-staff/<int:user_id>")
def toggle_staff(user_id):

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    staff = User.query.get_or_404(user_id)

    staff.is_blacklisted = not staff.is_blacklisted

    db.session.commit()

    flash(
        "Staff status updated successfully!",
        "success"
    )

    return redirect(url_for("manage_staff"))


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
    
#---------------STAFF PARTICIPANTS------------------#
    
@app.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):

    if session.get("role") != "Staff":
        return redirect(url_for("home"))

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != session["user_id"]:
        return redirect(url_for("staff_dashboard"))

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )
    
#------------------STAFF TOGGLE---------------------#    

@app.route("/staff/toggle-status/<int:trek_id>")
def toggle_trek_status(trek_id):

    if session.get("role") != "Staff":
        return redirect(url_for("home"))

    trek = Trek.query.get_or_404(trek_id)

    if trek.staff_id != session["user_id"]:
        return redirect(url_for("staff_dashboard"))

    
    print("Before:", trek.status)

    if trek.status == "Open":

        trek.status = "Started"

    elif trek.status == "Started":

        trek.status = "Completed"

    else:

        trek.status = "Open"

    print("After:", trek.status)

    db.session.commit()

    return redirect(url_for("staff_dashboard"))
    
# ---------------- VIEW ALL BOOKINGS ---------------- #

@app.route("/admin/view-bookings")
def admin_view_bookings():

    if session.get("role") != "Admin":
        return redirect(url_for("home"))

    bookings = Booking.query.all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)