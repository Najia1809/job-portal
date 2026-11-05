# config.py - settings of the Job Portal project (made by Najia)
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_database_url():
    # on Render we get DATABASE_URL (postgres). On our laptop we use sqlite.
    url = os.environ.get("DATABASE_URL")
    if not url:
        return "sqlite:///" + os.path.join(BASE_DIR, "jobportal.db")
    # hosts give "postgres://" or "postgresql://", but we installed the psycopg2
    # driver, so we tell SQLAlchemy clearly to use it: "postgresql+psycopg2://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Config:
    # secret key is needed for sessions and csrf
    SECRET_KEY = os.environ.get("SECRET_KEY", "najia-job-portal-dev-key")
    SQLALCHEMY_DATABASE_URI = get_database_url()
    # checks the connection before using it (needed for hosted databases)
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JOBS_PER_PAGE = 6
    ADMIN_PER_PAGE = 15
