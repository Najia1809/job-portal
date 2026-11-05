# blueprints/auth.py - register, login, logout
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from extensions import db
from models import User, Role, JobSeeker, Employer
from forms import RegisterForm, LoginForm
from utils import safe_next

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.role.data).first()
        user = User(full_name=form.full_name.data.strip(),
                    email=form.email.data.strip().lower(),
                    role_id=role.id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # so that user.id is ready
        if role.name == "job_seeker":
            db.session.add(JobSeeker(user_id=user.id))
        else:
            db.session.add(Employer(user_id=user.id))
        db.session.commit()
        flash("Account created. Now you can login.", "success")
        return redirect(url_for("auth.login"))  # PRG pattern
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Wrong email or password.", "danger")
        elif not user.is_active:
            flash("Your account is blocked. Contact admin.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            session.permanent = form.remember.data
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = safe_next(request.args.get("next"))
            if next_page:
                return redirect(next_page)
            if user.role.name == "admin":
                return redirect(url_for("admin.index"))
            if user.role.name == "employer":
                return redirect(url_for("employer.dashboard"))
            return redirect(url_for("main.jobs"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You are logged out.", "info")
    return redirect(url_for("main.index"))
