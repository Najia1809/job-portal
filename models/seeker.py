# models/seeker.py - everything about a job seeker (9 tables)
from datetime import datetime
from extensions import db


class JobSeeker(db.Model):
    __tablename__ = "job_seekers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    headline = db.Column(db.String(150))
    summary = db.Column(db.Text)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"))
    expected_salary = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("seeker", uselist=False))
    city = db.relationship("City")


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(200))
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    seeker = db.relationship("JobSeeker", backref="resumes")


class Education(db.Model):
    __tablename__ = "education"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    institute = db.Column(db.String(150), nullable=False)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    grade = db.Column(db.String(30))

    seeker = db.relationship("JobSeeker", backref="education")


class WorkExperience(db.Model):
    __tablename__ = "work_experience"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)

    seeker = db.relationship("JobSeeker", backref="experience")


class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)


class JobSeekerSkill(db.Model):
    __tablename__ = "job_seeker_skills"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    level = db.Column(db.String(20), default="Beginner")
    __table_args__ = (db.UniqueConstraint("job_seeker_id", "skill_id"),)

    seeker = db.relationship("JobSeeker", backref="seeker_skills")
    skill = db.relationship("Skill")


class Certification(db.Model):
    __tablename__ = "certifications"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issued_by = db.Column(db.String(150))
    year = db.Column(db.Integer)

    seeker = db.relationship("JobSeeker", backref="certifications")


class Language(db.Model):
    __tablename__ = "languages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class JobSeekerLanguage(db.Model):
    __tablename__ = "job_seeker_languages"
    id = db.Column(db.Integer, primary_key=True)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey("languages.id"), nullable=False)
    proficiency = db.Column(db.String(30), default="Fluent")
    __table_args__ = (db.UniqueConstraint("job_seeker_id", "language_id"),)

    seeker = db.relationship("JobSeeker", backref="seeker_languages")
    language = db.relationship("Language")
