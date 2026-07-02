from flask import Flask, render_template, request , redirect, url_for

from config import Config
from models import db, User

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

if __name__ == "__main__":
    app.run(debug=True)