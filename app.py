from flask import Flask, render_template, request , redirect, url_for, session

from config import Config
from models import db, User , Trek

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("user/home.html")

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

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

@app.route("/treks")
def treks():

    treks = Trek.query.all()

    return render_template(
        "user/treks.html",
        treks=treks
    )

@app.route("/trek/<int:trek_id>")
def trek_details(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    return render_template(
        "user/trek_details.html",
        trek=trek
    )

@app.route("/admin/dashboard")
def admin_dashboard():

    return render_template("admin/dashboard.html")

@app.route("/admin/manage-treks", methods=["GET", "POST"])
def manage_treks():

    if request.method == "POST":

        new_trek = Trek(
            trek_name=request.form["trek_name"],
            location=request.form["location"],
            difficulty=request.form["difficulty"],
            duration_days=int(request.form["duration_days"]),
            distance_km=0,
            price=int(request.form["price"]),
            max_trekkers=0,
            season="Not Assigned",
            weather="Not Assigned",
            transport="Not Assigned",
            description=request.form["description"],
            image_url="",
            staff_id=None
        )

        db.session.add(new_trek)
        db.session.commit()

        return redirect(url_for("manage_treks"))

    treks = Trek.query.all()

    return render_template(
        "admin/manage_treks.html",
        treks=treks
    )

if __name__ == "__main__":
    app.run(debug=True)