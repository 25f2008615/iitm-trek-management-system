from flask import Flask, render_template, request, redirect, url_for, session

from config import Config
from models import db, User, Trek

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

            session["user_id"] = user.id
            session["full_name"] = user.full_name
            session["role"] = user.role

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

        new_user = User(
            full_name=request.form["full_name"],
            email=request.form["email"],
            password=request.form["password"],
            role="Trekker",
            age=int(request.form["age"]),
            gender=request.form["gender"]
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

        db.session.commit()

        return redirect(url_for("manage_treks"))

    treks = Trek.query.all()

    return render_template(
        "admin/manage_treks.html",
        treks=treks,
        trek_to_edit=trek_to_edit
    )


# ---------------- DELETE TREK ---------------- #

@app.route("/admin/delete-trek/<int:trek_id>")
def delete_trek(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("manage_treks"))


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)