# app.py - main file of the Job Portal (Flask + SQLAlchemy)
# Project made by Najia for Web Engineering
import sqlite3
from flask import Flask, render_template
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config
from extensions import db, csrf


@event.listens_for(Engine, "connect")
def turn_on_foreign_keys(dbapi_connection, connection_record):
    # sqlite does not check foreign keys by default, so we turn it on
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)

    import models  # noqa  (so that all tables are known to SQLAlchemy)
    from utils import load_user
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.seeker import seeker_bp
    from blueprints.employer import employer_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(seeker_bp, url_prefix="/seeker")
    app.register_blueprint(employer_bp, url_prefix="/employer")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    app.before_request(load_user)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("error.html", code=403, message="Not allowed"), 403

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
