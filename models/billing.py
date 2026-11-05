# models/billing.py - subscription plans and payments (3 tables)
from datetime import datetime
from extensions import db


class SubscriptionPlan(db.Model):
    __tablename__ = "subscription_plans"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    job_limit = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)


class CompanySubscription(db.Model):
    __tablename__ = "company_subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("subscription_plans.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    company = db.relationship("Company", backref="subscriptions")
    plan = db.relationship("SubscriptionPlan", backref="subscriptions")


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey("company_subscriptions.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    method = db.Column(db.String(30), default="Card")
    status = db.Column(db.String(30), default="Paid")
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)

    subscription = db.relationship("CompanySubscription", backref="payments")
