# models/jobs.py - jobs and the lookup tables used by jobs (7 tables)
from datetime import datetime
from extensions import db


class JobCategory(db.Model):
    __tablename__ = "job_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class JobType(db.Model):
    __tablename__ = "job_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class ExperienceLevel(db.Model):
    __tablename__ = "experience_levels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class SalaryRange(db.Model):
    __tablename__ = "salary_ranges"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(60), nullable=False)
    min_salary = db.Column(db.Integer, nullable=False)
    max_salary = db.Column(db.Integer, nullable=False)


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey("employers.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("job_categories.id"), nullable=False)
    job_type_id = db.Column(db.Integer, db.ForeignKey("job_types.id"), nullable=False)
    experience_level_id = db.Column(db.Integer, db.ForeignKey("experience_levels.id"), nullable=False)
    salary_range_id = db.Column(db.Integer, db.ForeignKey("salary_ranges.id"))
    deadline = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref="jobs")
    employer = db.relationship("Employer", backref="jobs")
    category = db.relationship("JobCategory", backref="jobs")
    job_type = db.relationship("JobType", backref="jobs")
    level = db.relationship("ExperienceLevel", backref="jobs")
    salary_range = db.relationship("SalaryRange", backref="jobs")


class JobSkill(db.Model):
    __tablename__ = "job_skills"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint("job_id", "skill_id"),)

    job = db.relationship("Job", backref=db.backref("job_skills", cascade="all, delete-orphan"))
    skill = db.relationship("Skill")


class JobLocation(db.Model):
    __tablename__ = "job_locations"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint("job_id", "city_id"),)

    job = db.relationship("Job", backref=db.backref("locations", cascade="all, delete-orphan"))
    city = db.relationship("City")
