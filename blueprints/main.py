# blueprints/main.py - public pages (home, job list, job detail)
from flask import Blueprint, render_template, request, current_app, make_response, g
from sqlalchemy import or_
from extensions import db
from models import Job, Company, JobLocation, JobCategory, JobType, City, SavedJob, Application

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    latest = Job.query.filter_by(is_active=True).order_by(Job.created_at.desc()).limit(6).all()
    # we saved the last search in a cookie, show it again on home page
    last_search = request.cookies.get("last_search", "")
    return render_template("index.html", jobs=latest, last_search=last_search)


@main_bp.route("/jobs")
def jobs():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", type=int)
    job_type = request.args.get("job_type", type=int)
    city = request.args.get("city", type=int)
    page = request.args.get("page", 1, type=int)

    query = Job.query.filter_by(is_active=True).join(Company, Job.company_id == Company.id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.ilike(like), Company.name.ilike(like)))
    if category:
        query = query.filter(Job.category_id == category)
    if job_type:
        query = query.filter(Job.job_type_id == job_type)
    if city:
        query = query.join(JobLocation, JobLocation.job_id == Job.id).filter(JobLocation.city_id == city)

    pagination = query.order_by(Job.created_at.desc()).paginate(
        page=page, per_page=current_app.config["JOBS_PER_PAGE"], error_out=False)

    response = make_response(render_template(
        "jobs.html", pagination=pagination, q=q, category=category, job_type=job_type, city=city,
        categories=JobCategory.query.order_by(JobCategory.name).all(),
        job_types=JobType.query.order_by(JobType.name).all(),
        cities=City.query.order_by(City.name).all()))
    if q:
        # cookie remembers the last search for 7 days
        response.set_cookie("last_search", q, max_age=7 * 24 * 60 * 60, httponly=True, samesite="Lax")
    return response


@main_bp.route("/jobs/<int:job_id>")
def job_detail(job_id):
    job = db.get_or_404(Job, job_id)
    already_applied = False
    already_saved = False
    if g.user is not None and g.user.seeker is not None:
        seeker_id = g.user.seeker.id
        already_applied = Application.query.filter_by(job_id=job.id, job_seeker_id=seeker_id).first() is not None
        already_saved = SavedJob.query.filter_by(job_id=job.id, job_seeker_id=seeker_id).first() is not None
    return render_template("job_detail.html", job=job,
                           already_applied=already_applied, already_saved=already_saved)
