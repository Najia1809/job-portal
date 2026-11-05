# models/company.py - companies and employers (6 tables)
from datetime import datetime
from extensions import db


class Industry(db.Model):
    __tablename__ = "industries"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    industry_id = db.Column(db.Integer, db.ForeignKey("industries.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    industry = db.relationship("Industry", backref="companies")
    city = db.relationship("City")


class CompanyBranch(db.Model):
    __tablename__ = "company_branches"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)

    company = db.relationship("Company", backref="branches")
    city = db.relationship("City")


class Employer(db.Model):
    # an employer (recruiter) is a user who works for a company
    __tablename__ = "employers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    position = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    user = db.relationship("User", backref=db.backref("employer", uselist=False))
    company = db.relationship("Company", backref="employers")


class CompanyReview(db.Model):
    __tablename__ = "company_reviews"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    job_seeker_id = db.Column(db.Integer, db.ForeignKey("job_seekers.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref="reviews")
    seeker = db.relationship("JobSeeker", backref="reviews")


class CompanyDocument(db.Model):
    __tablename__ = "company_documents"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    doc_type = db.Column(db.String(60), nullable=False)
    file_name = db.Column(db.String(200), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", backref="documents")
