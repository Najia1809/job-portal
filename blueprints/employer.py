# blueprints/employer.py - pages for employers (company, jobs, applications)
from flask import Blueprint, render_template, redirect, url_for, flash, g, request
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import (Company, Job, JobSkill, JobLocation, Industry, City, JobCategory, JobType,
                    ExperienceLevel, SalaryRange, Skill, Application, ApplicationStatus,
                    ApplicationStatusHistory, ShortlistedCandidate, Notification, SavedJob)
from forms import CompanyForm, JobForm
from utils import login_required, role_required

employer_bp = Blueprint("employer", __name__)


def my_job_or_404(job_id):
    """get a job, but only if it belongs to the logged in employer's company"""
    job = db.get_or_404(Job, job_id)
    if job.company_id != g.user.employer.company_id:
        from flask import abort
        abort(403)
    return job


def fill_job_choices(form):
    form.category_id.choices = [(c.id, c.name) for c in JobCategory.query.order_by(JobCategory.name)]
    form.job_type_id.choices = [(t.id, t.name) for t in JobType.query.order_by(JobType.name)]
    form.experience_level_id.choices = [(e.id, e.name) for e in ExperienceLevel.query.order_by(ExperienceLevel.id)]
    form.salary_range_id.choices = [(0, "Not shown")] + [(s.id, s.label) for s in SalaryRange.query.order_by(SalaryRange.min_salary)]
    form.city_id.choices = [(c.id, c.name) for c in City.query.order_by(City.name)]
    form.skills.choices = [(s.id, s.name) for s in Skill.query.order_by(Skill.name)]


@employer_bp.route("/dashboard")
@login_required
@role_required("employer")
def dashboard():
    employer = g.user.employer
    jobs = []
    if employer.company_id:
        jobs = Job.query.filter_by(company_id=employer.company_id).order_by(Job.created_at.desc()).all()
    return render_template("employer/dashboard.html", employer=employer, jobs=jobs)


@employer_bp.route("/company", methods=["GET", "POST"])
@login_required
@role_required("employer")
def company():
    employer = g.user.employer
    form = CompanyForm(obj=employer.company)
    form.industry_id.choices = [(i.id, i.name) for i in Industry.query.order_by(Industry.name)]
    form.city_id.choices = [(c.id, c.name) for c in City.query.order_by(City.name)]

    if form.validate_on_submit():
        if employer.company is None:
            company = Company()
            db.session.add(company)
            employer.company = company
        else:
            company = employer.company
        company.name = form.name.data.strip()
        company.industry_id = form.industry_id.data
        company.city_id = form.city_id.data
        company.website = form.website.data
        company.description = form.description.data
        db.session.commit()
        flash("Company details saved.", "success")
        return redirect(url_for("employer.dashboard"))
    return render_template("employer/company_form.html", form=form)


@employer_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@role_required("employer")
def job_new():
    employer = g.user.employer
    if employer.company_id is None:
        flash("First add your company details, then you can post jobs.", "warning")
        return redirect(url_for("employer.company"))

    form = JobForm()
    fill_job_choices(form)
    if form.validate_on_submit():
        job = Job(company_id=employer.company_id, employer_id=employer.id,
                  title=form.title.data.strip(), description=form.description.data,
                  category_id=form.category_id.data, job_type_id=form.job_type_id.data,
                  experience_level_id=form.experience_level_id.data,
                  salary_range_id=form.salary_range_id.data or None,
                  deadline=form.deadline.data, is_active=form.is_active.data)
        db.session.add(job)
        db.session.flush()
        db.session.add(JobLocation(job_id=job.id, city_id=form.city_id.data))
        for skill_id in form.skills.data:
            db.session.add(JobSkill(job_id=job.id, skill_id=skill_id))
        db.session.commit()
        flash("Job posted.", "success")
        return redirect(url_for("employer.dashboard"))
    return render_template("employer/job_form.html", form=form, editing=False)


@employer_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("employer")
def job_edit(job_id):
    job = my_job_or_404(job_id)
    form = JobForm(obj=job)
    fill_job_choices(form)

    if form.validate_on_submit():
        job.title = form.title.data.strip()
        job.description = form.description.data
        job.category_id = form.category_id.data
        job.job_type_id = form.job_type_id.data
        job.experience_level_id = form.experience_level_id.data
        job.salary_range_id = form.salary_range_id.data or None
        job.deadline = form.deadline.data
        job.is_active = form.is_active.data
        # rebuild skills and location
        job.job_skills.clear()
        job.locations.clear()
        db.session.flush()
        job.locations.append(JobLocation(city_id=form.city_id.data))
        for skill_id in form.skills.data:
            job.job_skills.append(JobSkill(skill_id=skill_id))
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("employer.dashboard"))

    if not form.is_submitted():
        form.skills.data = [js.skill_id for js in job.job_skills]
        form.city_id.data = job.locations[0].city_id if job.locations else None
        form.salary_range_id.data = job.salary_range_id or 0
    return render_template("employer/job_form.html", form=form, editing=True, job=job)


@employer_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@role_required("employer")
def job_delete(job_id):
    job = my_job_or_404(job_id)
    if job.applications:
        # we cannot delete a job that already has applications, so we only close it
        job.is_active = False
        db.session.commit()
        flash("This job has applications, so it was closed instead of deleted.", "warning")
        return redirect(url_for("employer.dashboard"))
    try:
        SavedJob.query.filter_by(job_id=job.id).delete()
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted.", "info")
    except IntegrityError:
        db.session.rollback()
        flash("Job could not be deleted because other records use it.", "danger")
    return redirect(url_for("employer.dashboard"))


@employer_bp.route("/jobs/<int:job_id>/applications")
@login_required
@role_required("employer")
def job_applications(job_id):
    job = my_job_or_404(job_id)
    apps = Application.query.filter_by(job_id=job.id).order_by(Application.applied_at.desc()).all()
    statuses = ApplicationStatus.query.order_by(ApplicationStatus.id).all()
    return render_template("employer/applications.html", job=job, applications=apps, statuses=statuses)


@employer_bp.route("/applications/<int:app_id>/status", methods=["POST"])
@login_required
@role_required("employer")
def update_status(app_id):
    application = db.get_or_404(Application, app_id)
    job = my_job_or_404(application.job_id)

    new_status = db.session.get(ApplicationStatus, request.form.get("status_id", type=int) or 0)
    note = request.form.get("note", "").strip()[:200]
    if new_status is None:
        flash("Please choose a valid status.", "danger")
        return redirect(url_for("employer.job_applications", job_id=job.id))

    application.status_id = new_status.id
    db.session.add(ApplicationStatusHistory(application_id=application.id, status_id=new_status.id,
                                            changed_by=g.user.id, note=note or None))
    if new_status.name == "Shortlisted":
        exists = ShortlistedCandidate.query.filter_by(job_id=job.id, job_seeker_id=application.job_seeker_id).first()
        if not exists:
            db.session.add(ShortlistedCandidate(job_id=job.id, job_seeker_id=application.job_seeker_id,
                                                shortlisted_by=g.user.employer.id))
    db.session.add(Notification(user_id=application.seeker.user_id, title="Application update",
                                body=f"Your application for {job.title} is now: {new_status.name}"))
    db.session.commit()
    flash(f"Status changed to {new_status.name}.", "success")
    return redirect(url_for("employer.job_applications", job_id=job.id))
