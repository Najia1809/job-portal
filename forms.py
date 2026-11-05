# forms.py - all Flask-WTF forms (server side validation is done here)
from datetime import date
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, SelectMultipleField,
                     TextAreaField, IntegerField, DateField, BooleanField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo, ValidationError,
                                Optional, NumberRange, URL)
from models import User


class RegisterForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField("I am a", choices=[("job_seeker", "Job Seeker"), ("employer", "Employer")])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=60)])
    confirm = PasswordField("Confirm Password",
                            validators=[DataRequired(), EqualTo("password", message="Passwords must match.")])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("This email is already registered.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")


class ProfileForm(FlaskForm):
    phone = StringField("Phone", validators=[Optional(), Length(min=7, max=20)])
    headline = StringField("Headline (example: Python Developer)", validators=[Optional(), Length(max=150)])
    summary = TextAreaField("About me", validators=[Optional(), Length(max=1000)])
    city_id = SelectField("City", coerce=int, validators=[Optional()])
    expected_salary = IntegerField("Expected salary (per month)", validators=[Optional(), NumberRange(min=0)])
    skills = SelectMultipleField("My skills", coerce=int, validators=[Optional()])
    resume_title = StringField("Resume title", validators=[Optional(), Length(max=100)])


class ApplyForm(FlaskForm):
    cover_letter = TextAreaField("Cover letter", validators=[DataRequired(), Length(min=20, max=2000)])
    resume_id = SelectField("Resume", coerce=int, validators=[Optional()])


class CompanyForm(FlaskForm):
    name = StringField("Company name", validators=[DataRequired(), Length(min=2, max=120)])
    industry_id = SelectField("Industry", coerce=int, validators=[DataRequired()])
    city_id = SelectField("City", coerce=int, validators=[DataRequired()])
    website = StringField("Website", validators=[Optional(), URL(), Length(max=200)])
    description = TextAreaField("About the company", validators=[Optional(), Length(max=1500)])


class JobForm(FlaskForm):
    title = StringField("Job title", validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20, max=3000)])
    category_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    job_type_id = SelectField("Job type", coerce=int, validators=[DataRequired()])
    experience_level_id = SelectField("Experience level", coerce=int, validators=[DataRequired()])
    salary_range_id = SelectField("Salary range", coerce=int, validators=[Optional()])
    city_id = SelectField("City", coerce=int, validators=[DataRequired()])
    skills = SelectMultipleField("Required skills", coerce=int, validators=[Optional()])
    deadline = DateField("Last date to apply", validators=[Optional()])
    is_active = BooleanField("Job is open", default=True)

    def validate_deadline(self, field):
        if field.data and field.data < date.today():
            raise ValidationError("Deadline cannot be in the past.")
