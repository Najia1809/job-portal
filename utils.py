# utils.py - small helper functions and decorators
from functools import wraps
from flask import session, redirect, url_for, flash, g, request
from extensions import db
from models import User


def load_user():
    """runs before every request, puts the logged in user in g.user"""
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.user is None:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """only allow users who have one of the given roles"""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if g.user is None or g.user.role.name not in roles:
                flash("You are not allowed to open that page.", "danger")
                return redirect(url_for("main.index"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


def safe_next(target):
    """only allow redirects inside our own website"""
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None
