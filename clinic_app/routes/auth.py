from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from clinic_app import db, mail, login_manager
from clinic_app.models import User
import random
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# 👑 Homepage
@auth_bp.route("/")
def home():
    return render_template("home.html")


# 📨 Login — Email Entry + OTP Send
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not recognized", "danger")
            return redirect(url_for("auth.login"))

        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)
        session["otp"] = otp
        session["otp_expiry"] = expiry.isoformat()

        msg = Message(subject="Your OTP Code", recipients=[email])
        msg.body = f"Your Tiara Clinics OTP is: {otp}\n\nThis code will expire in 5 minutes."
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Email failed to send: {e}", "danger")
            return redirect(url_for("auth.login"))

        session["email"] = email
        flash("OTP sent to your email", "info")
        return redirect(url_for("auth.verify"))

    return render_template("login.html")


# 🔐 Verify OTP
@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    email = session.get("email")
    if not email:
        flash("Session expired. Please login again.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        entered = request.form.get("otp")
        
        otp = session.get("otp")
        expiry_str = session.get("otp_expiry")

        if not otp or not expiry_str:
            flash("No OTP record found. Try again.", "danger")
            return redirect(url_for("auth.login"))

        expiry = datetime.fromisoformat(expiry_str)
        if datetime.utcnow() > expiry:
            flash("OTP expired. Please login again.", "danger")
            session.pop("otp", None)
            session.pop("otp_expiry", None)
            return redirect(url_for("auth.login"))

        if entered == otp:
            user = User.query.filter_by(email=email).first()
            login_user(user)
            flash("Logged in successfully!", "success")
            session.pop("otp", None)
            session.pop("otp_expiry", None)
            return redirect(url_for("dashboard.view"))

        flash("Invalid OTP. Please try again.", "danger")
        return redirect(url_for("auth.verify"))

    return render_template("verify.html")


# 🚪 Logout
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("auth.login"))


# 🧠 Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
