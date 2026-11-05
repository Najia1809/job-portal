# models/hiring.py - applications and the hiring process (8 tables)
from datetime import datetime
from extensions import db


class ApplicationStatus(db.Model):
    __tablename__ = "application_statuses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"))
    status_id = db.Column(db.Integer, db.ForeignKey("application_statuses.id"), nullable=False)
    cover_letter = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    # one seeker can apply only one time for one job
    __table_args__ = (db.UniqueConstraint("job_id", "job_seeker_id"),)

    job = db.relationship("Job", backref="applications")
    seeker = db.relationship("JobSeeker", backref="applications")
    resume = db.relationship("Resume")
    status = db.relationship("ApplicationStatus")


class ApplicationStatusHistory(db.Model):
    __tablename__ = "application_status_history"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("application_statuses.id"), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    note = db.Column(db.String(200))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship("Application", backref="history")
    status = db.relationship("ApplicationStatus")


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("job_seeker_id", "job_id"),)

    seeker = db.relationship("JobSeeker", backref="saved_jobs")
    job = db.relationship("Job", backref="saved_by")


class Interview(db.Model):
    __tablename__ = "interviews"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    mode = db.Column(db.String(30), default="Online")
    location = db.Column(db.String(150))
    notes = db.Column(db.Text)

    application = db.relationship("Application", backref="interviews")


class InterviewFeedback(db.Model):
    __tablename__ = "interview_feedback"
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey("interviews.id"), nullable=False)
    given_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text)

    interview = db.relationship("Interview", backref="feedback")


class JobOffer(db.Model):
    __tablename__ = "job_offers"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    salary_offered = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), default="Pending")
    expiry_date = db.Column(db.Date)
    offered_at = db.Column(db.DateTime, default=datetime.utcnow)

    application = db.relationship("Application", backref="offers")


class ShortlistedCandidate(db.Model):
    __tablename__ = "shortlisted_candidates"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    shortlisted_by = db.Column(db.Integer, db.ForeignKey("employers.id"), nullable=False)
    shortlisted_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("job_id", "job_seeker_id"),)

    job = db.relationship("Job", backref="shortlisted")
    seeker = db.relationship("JobSeeker", backref="shortlisted")
    employer = db.relationship("Employer")
