# blueprints/seeker.py - pages for job seekers
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, g
from extensions import db
from models import (Job, Application, ApplicationStatus, ApplicationStatusHistory, SavedJob,
                    Skill, JobSeekerSkill, City, Resume, Notification)
from forms import ProfileForm, ApplyForm
from utils import login_required, role_required

seeker_bp = Blueprint("seeker", __name__)


@seeker_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("job_seeker")
def profile():
    seeker = g.user.seeker
    form = ProfileForm(obj=seeker)
    form.city_id.choices = [(0, "-- select city --")] + [(c.id, c.name) for c in City.query.order_by(City.name)]
    form.skills.choices = [(s.id, s.name) for s in Skill.query.order_by(Skill.name)]

    if form.validate_on_submit():
        seeker.phone = form.phone.data
        seeker.headline = form.headline.data
        seeker.summary = form.summary.data
        seeker.city_id = form.city_id.data or None
        seeker.expected_salary = form.expected_salary.data

        # replace old skills with the new selected ones
        JobSeekerSkill.query.filter_by(job_seeker_id=seeker.id).delete()
        for skill_id in form.skills.data:
            db.session.add(JobSeekerSkill(job_seeker_id=seeker.id, skill_id=skill_id))

        if form.resume_title.data:
            resume = Resume.query.filter_by(job_seeker_id=seeker.id, is_default=True).first()
            if resume:
                resume.title = form.resume_title.data
            else:
                db.session.add(Resume(job_seeker_id=seeker.id, title=form.resume_title.data, is_default=True))
        db.session.commit()
        flash("Profile saved.", "success")
        return redirect(url_for("seeker.profile"))

    if not form.is_submitted():
        form.skills.data = [ss.skill_id for ss in seeker.seeker_skills]
        form.city_id.data = seeker.city_id or 0
        default_resume = Resume.query.filter_by(job_seeker_id=seeker.id, is_default=True).first()
        form.resume_title.data = default_resume.title if default_resume else ""
    return render_template("seeker/profile.html", form=form)


@seeker_bp.route("/apply/<int:job_id>", methods=["GET", "POST"])
@login_required
@role_required("job_seeker")
def apply(job_id):
    job = db.get_or_404(Job, job_id)
    seeker = g.user.seeker

    if not job.is_active or (job.deadline and job.deadline < date.today()):
        flash("This job is closed.", "warning")
        return redirect(url_for("main.job_detail", job_id=job.id))
    if Application.query.filter_by(job_id=job.id, job_seeker_id=seeker.id).first():
        flash("You already applied for this job.", "info")
        return redirect(url_for("main.job_detail", job_id=job.id))

    form = ApplyForm()
    form.resume_id.choices = [(0, "No resume")] + [(r.id, r.title) for r in seeker.resumes]

    if form.validate_on_submit():
        applied = ApplicationStatus.query.filter_by(name="Applied").first()
        application = Application(job_id=job.id, job_seeker_id=seeker.id,
                                  resume_id=form.resume_id.data or None,
                                  status_id=applied.id, cover_letter=form.cover_letter.data)
        db.session.add(application)
        db.session.flush()
        db.session.add(ApplicationStatusHistory(application_id=application.id, status_id=applied.id,
                                                changed_by=g.user.id, note="Application submitted"))
        # tell the employer
        db.session.add(Notification(user_id=job.employer.user_id,
                                    title="New application",
                                    body=f"{g.user.full_name} applied for {job.title}"))
        db.session.commit()
        flash("Application submitted. Good luck!", "success")
        return redirect(url_for("seeker.applications"))
    return render_template("seeker/apply.html", form=form, job=job)


@seeker_bp.route("/applications")
@login_required
@role_required("job_seeker")
def applications():
    apps = (Application.query.filter_by(job_seeker_id=g.user.seeker.id)
            .order_by(Application.applied_at.desc()).all())
    return render_template("seeker/applications.html", applications=apps)


@seeker_bp.route("/applications/<int:app_id>/withdraw", methods=["POST"])
@login_required
@role_required("job_seeker")
def withdraw(app_id):
    application = db.get_or_404(Application, app_id)
    if application.job_seeker_id != g.user.seeker.id:
        flash("That is not your application.", "danger")
        return redirect(url_for("seeker.applications"))
    if application.status.name != "Applied":
        flash("You can only withdraw an application that is still in Applied status.", "warning")
        return redirect(url_for("seeker.applications"))
    ApplicationStatusHistory.query.filter_by(application_id=application.id).delete()
    db.session.delete(application)
    db.session.commit()
    flash("Application withdrawn.", "info")
    return redirect(url_for("seeker.applications"))


@seeker_bp.route("/save/<int:job_id>", methods=["POST"])
@login_required
@role_required("job_seeker")
def save_job(job_id):
    job = db.get_or_404(Job, job_id)
    if not SavedJob.query.filter_by(job_id=job.id, job_seeker_id=g.user.seeker.id).first():
        db.session.add(SavedJob(job_id=job.id, job_seeker_id=g.user.seeker.id))
        db.session.commit()
        flash("Job saved.", "success")
    return redirect(url_for("main.job_detail", job_id=job.id))


@seeker_bp.route("/unsave/<int:job_id>", methods=["POST"])
@login_required
@role_required("job_seeker")
def unsave_job(job_id):
    saved = SavedJob.query.filter_by(job_id=job_id, job_seeker_id=g.user.seeker.id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()
        flash("Job removed from saved list.", "info")
    return redirect(url_for("seeker.saved"))


@seeker_bp.route("/saved")
@login_required
@role_required("job_seeker")
def saved():
    items = (SavedJob.query.filter_by(job_seeker_id=g.user.seeker.id)
             .order_by(SavedJob.saved_at.desc()).all())
    return render_template("seeker/saved.html", items=items)
