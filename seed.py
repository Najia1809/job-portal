# seed.py - puts sample data in all 44 tables
# WARNING: this deletes the old database and makes a fresh one. Run it with:  python seed.py
from datetime import date, datetime, timedelta
from app import create_app
from extensions import db
from models import (Role, Permission, RolePermission, User, Country, City, JobSeeker, Resume,
                    Education, WorkExperience, Skill, JobSeekerSkill, Certification, Language,
                    JobSeekerLanguage, Industry, Company, CompanyBranch, Employer, CompanyReview,
                    CompanyDocument, JobCategory, JobType, ExperienceLevel, SalaryRange, Job,
                    JobSkill, JobLocation, ApplicationStatus, Application, ApplicationStatusHistory,
                    SavedJob, Interview, InterviewFeedback, JobOffer, ShortlistedCandidate, Message,
                    Notification, JobAlert, EmailLog, Report, SubscriptionPlan, CompanySubscription,
                    Payment)


def add_all(items):
    db.session.add_all(items)
    db.session.flush()
    return items


def make_user(name, email, password, role):
    user = User(full_name=name, email=email, role_id=role.id)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def seed(reset=True):
    if reset:
        db.drop_all()
    db.create_all()

    # ---------- roles and permissions ----------
    admin_role, employer_role, seeker_role = add_all([
        Role(name="admin", description="Manages the whole website"),
        Role(name="employer", description="Posts jobs and hires people"),
        Role(name="job_seeker", description="Searches and applies for jobs"),
    ])
    manage_users, manage_jobs, post_jobs, apply_jobs, view_reports = add_all([
        Permission(name="manage_users", description="Add, edit, block users"),
        Permission(name="manage_jobs", description="Edit or close any job"),
        Permission(name="post_jobs", description="Post new jobs"),
        Permission(name="apply_jobs", description="Apply for jobs"),
        Permission(name="view_reports", description="See reported jobs"),
    ])
    add_all([RolePermission(role_id=admin_role.id, permission_id=p.id)
             for p in (manage_users, manage_jobs, post_jobs, apply_jobs, view_reports)])
    add_all([RolePermission(role_id=employer_role.id, permission_id=p.id) for p in (post_jobs, manage_jobs)])
    add_all([RolePermission(role_id=seeker_role.id, permission_id=apply_jobs.id)])

    # ---------- locations ----------
    pakistan, uae = add_all([Country(name="Pakistan", code="PK"), Country(name="United Arab Emirates", code="AE")])
    lahore, karachi, islamabad, rawalpindi, faisalabad, dubai = add_all([
        City(name="Lahore", country_id=pakistan.id), City(name="Karachi", country_id=pakistan.id),
        City(name="Islamabad", country_id=pakistan.id), City(name="Rawalpindi", country_id=pakistan.id),
        City(name="Faisalabad", country_id=pakistan.id), City(name="Dubai", country_id=uae.id),
    ])
    cities = {"Lahore": lahore, "Karachi": karachi, "Islamabad": islamabad,
              "Rawalpindi": rawalpindi, "Faisalabad": faisalabad, "Dubai": dubai}

    # ---------- lookup tables ----------
    it, education_ind, health, finance, marketing_ind = add_all([
        Industry(name="Information Technology"), Industry(name="Education"), Industry(name="Healthcare"),
        Industry(name="Finance"), Industry(name="Marketing")])
    cats = {n: c for n, c in zip(
        ["Software Development", "Data Science", "Design", "Marketing", "Teaching"],
        add_all([JobCategory(name=n) for n in ["Software Development", "Data Science", "Design", "Marketing", "Teaching"]]))}
    types = {n: t for n, t in zip(
        ["Full-time", "Part-time", "Internship", "Remote", "Contract"],
        add_all([JobType(name=n) for n in ["Full-time", "Part-time", "Internship", "Remote", "Contract"]]))}
    levels = {n: l for n, l in zip(
        ["Fresher", "Junior", "Mid Level", "Senior"],
        add_all([ExperienceLevel(name=n) for n in ["Fresher", "Junior", "Mid Level", "Senior"]]))}
    ranges = {s[0]: r for s, r in zip(
        [("PKR 30,000 - 60,000", 30000, 60000), ("PKR 60,000 - 100,000", 60000, 100000),
         ("PKR 100,000 - 200,000", 100000, 200000), ("PKR 200,000+", 200000, 500000)],
        add_all([SalaryRange(label="PKR 30,000 - 60,000", min_salary=30000, max_salary=60000),
                 SalaryRange(label="PKR 60,000 - 100,000", min_salary=60000, max_salary=100000),
                 SalaryRange(label="PKR 100,000 - 200,000", min_salary=100000, max_salary=200000),
                 SalaryRange(label="PKR 200,000+", min_salary=200000, max_salary=500000)]))}
    skill_names = ["Python", "Flask", "Django", "SQL", "JavaScript", "HTML/CSS", "Machine Learning",
                   "Communication", "Excel", "Figma"]
    skills = {n: s for n, s in zip(skill_names, add_all([Skill(name=n) for n in skill_names]))}
    english, urdu, punjabi = add_all([Language(name="English"), Language(name="Urdu"), Language(name="Punjabi")])
    applied, shortlisted, interview_st, offered, rejected = add_all([
        ApplicationStatus(name=n) for n in ["Applied", "Shortlisted", "Interview", "Offered", "Rejected"]])
    free_plan, basic_plan, premium_plan = add_all([
        SubscriptionPlan(name="Free", price=0, job_limit=2, duration_days=30),
        SubscriptionPlan(name="Basic", price=5000, job_limit=10, duration_days=30),
        SubscriptionPlan(name="Premium", price=15000, job_limit=50, duration_days=30)])

    # ---------- users ----------
    admin = make_user("Admin", "admin@jobportal.com", "admin123", admin_role)
    emp_user = make_user("Ali Raza", "employer@technova.com", "employer123", employer_role)
    seeker_user = make_user("Sara Ahmed", "seeker@example.com", "seeker123", seeker_role)

    # ---------- company ----------
    company = Company(name="TechNova Solutions", industry_id=it.id, city_id=lahore.id,
                      website="https://technova.example.com", is_verified=True,
                      description="A software house that builds web and AI products for clients.")
    db.session.add(company)
    db.session.flush()
    add_all([CompanyBranch(company_id=company.id, name="Karachi Office", address="Clifton Block 5", city_id=karachi.id),
             CompanyDocument(company_id=company.id, doc_type="Registration Certificate", file_name="technova_registration.pdf")])
    employer = Employer(user_id=emp_user.id, company_id=company.id, position="HR Manager", phone="03001234567")
    db.session.add(employer)
    db.session.flush()

    # ---------- jobs ----------
    job_data = [
        ("Python Flask Developer", "We need a Flask developer to build and maintain our web apps. You will work with SQLAlchemy, Jinja2 templates and REST APIs.", "Software Development", "Full-time", "Junior", "PKR 60,000 - 100,000", "Lahore", ["Python", "Flask", "SQL"]),
        ("Data Science Intern", "Join our data team as an intern. You will clean data, build simple ML models and make charts.", "Data Science", "Internship", "Fresher", "PKR 30,000 - 60,000", "Lahore", ["Python", "Machine Learning", "Excel"]),
        ("Frontend Developer", "Build nice and responsive pages with HTML, CSS and JavaScript for our clients.", "Software Development", "Full-time", "Junior", "PKR 60,000 - 100,000", "Islamabad", ["HTML/CSS", "JavaScript"]),
        ("UI/UX Designer", "Design clean screens and prototypes in Figma and work closely with developers.", "Design", "Full-time", "Mid Level", "PKR 100,000 - 200,000", "Karachi", ["Figma", "Communication"]),
        ("Digital Marketing Executive", "Plan social media campaigns and track their results every week.", "Marketing", "Part-time", "Fresher", "PKR 30,000 - 60,000", "Rawalpindi", ["Communication", "Excel"]),
        ("Computer Science Teacher", "Teach programming basics to school students and prepare simple lab work.", "Teaching", "Full-time", "Junior", "PKR 30,000 - 60,000", "Faisalabad", ["Python", "Communication"]),
        ("Django Backend Developer (Remote)", "Work remotely on Django projects. You should know databases and REST APIs well.", "Software Development", "Remote", "Mid Level", "PKR 100,000 - 200,000", "Dubai", ["Python", "Django", "SQL"]),
        ("Machine Learning Engineer", "Build and deploy ML models for real products. Experience with Python is a must.", "Data Science", "Full-time", "Senior", "PKR 200,000+", "Lahore", ["Python", "Machine Learning", "SQL"]),
    ]
    jobs = []
    for i, (title, desc, cat, jtype, level, salary, city, skill_list) in enumerate(job_data):
        job = Job(title=title, description=desc, company_id=company.id, employer_id=employer.id,
                  category_id=cats[cat].id, job_type_id=types[jtype].id, experience_level_id=levels[level].id,
                  salary_range_id=ranges[salary].id, deadline=date.today() + timedelta(days=30 + i * 3),
                  created_at=datetime.utcnow() - timedelta(days=i))
        db.session.add(job)
        db.session.flush()
        db.session.add(JobLocation(job_id=job.id, city_id=cities[city].id))
        for s in skill_list:
            db.session.add(JobSkill(job_id=job.id, skill_id=skills[s].id))
        jobs.append(job)
    db.session.flush()

    # ---------- job seeker profile ----------
    seeker = JobSeeker(user_id=seeker_user.id, phone="03111234567", headline="Python Developer (Fresh Graduate)",
                       summary="I like building web apps and learning machine learning.",
                       city_id=lahore.id, expected_salary=80000)
    db.session.add(seeker)
    db.session.flush()
    resume = Resume(job_seeker_id=seeker.id, title="Sara Ahmed - CV", file_name="sara_cv.pdf", is_default=True)
    db.session.add(resume)
    db.session.flush()
    add_all([
        Education(job_seeker_id=seeker.id, degree="BS Computer Science", institute="Punjab University", start_year=2021, end_year=2025, grade="3.4 CGPA"),
        WorkExperience(job_seeker_id=seeker.id, job_title="Python Intern", company_name="Code Labs", start_date=date(2025, 1, 1), end_date=date(2025, 4, 1), description="Worked on small Flask projects."),
        JobSeekerSkill(job_seeker_id=seeker.id, skill_id=skills["Python"].id, level="Intermediate"),
        JobSeekerSkill(job_seeker_id=seeker.id, skill_id=skills["Flask"].id, level="Beginner"),
        JobSeekerSkill(job_seeker_id=seeker.id, skill_id=skills["SQL"].id, level="Intermediate"),
        Certification(job_seeker_id=seeker.id, title="Python for Everybody", issued_by="Coursera", year=2024),
        JobSeekerLanguage(job_seeker_id=seeker.id, language_id=english.id, proficiency="Fluent"),
        JobSeekerLanguage(job_seeker_id=seeker.id, language_id=urdu.id, proficiency="Native"),
    ])

    # ---------- applications and hiring ----------
    app1 = Application(job_id=jobs[0].id, job_seeker_id=seeker.id, resume_id=resume.id, status_id=interview_st.id,
                       cover_letter="I have worked with Flask and SQLAlchemy in my internship and I want to learn more with your team.")
    app2 = Application(job_id=jobs[1].id, job_seeker_id=seeker.id, resume_id=resume.id, status_id=applied.id,
                       cover_letter="I am a fresh graduate and I am very interested in data science work.")
    app3 = Application(job_id=jobs[2].id, job_seeker_id=seeker.id, resume_id=resume.id, status_id=offered.id,
                       cover_letter="I know HTML, CSS and some JavaScript and I can learn fast.")
    add_all([app1, app2, app3])
    add_all([
        ApplicationStatusHistory(application_id=app1.id, status_id=applied.id, changed_by=seeker_user.id, note="Application submitted"),
        ApplicationStatusHistory(application_id=app1.id, status_id=shortlisted.id, changed_by=emp_user.id, note="Good profile"),
        ApplicationStatusHistory(application_id=app1.id, status_id=interview_st.id, changed_by=emp_user.id, note="Interview next week"),
        ApplicationStatusHistory(application_id=app2.id, status_id=applied.id, changed_by=seeker_user.id, note="Application submitted"),
        ApplicationStatusHistory(application_id=app3.id, status_id=applied.id, changed_by=seeker_user.id, note="Application submitted"),
        ApplicationStatusHistory(application_id=app3.id, status_id=offered.id, changed_by=emp_user.id, note="Offer sent"),
    ])
    interview = Interview(application_id=app1.id, scheduled_at=datetime.utcnow() + timedelta(days=5),
                          mode="Online", location="Google Meet", notes="Bring your project examples.")
    db.session.add(interview)
    db.session.flush()
    add_all([
        InterviewFeedback(interview_id=interview.id, given_by=emp_user.id, rating=4, comments="Good basics, needs more practice."),
        JobOffer(application_id=app3.id, salary_offered=70000, status="Pending", expiry_date=date.today() + timedelta(days=7)),
        ShortlistedCandidate(job_id=jobs[0].id, job_seeker_id=seeker.id, shortlisted_by=employer.id),
        SavedJob(job_seeker_id=seeker.id, job_id=jobs[7].id),
    ])

    # ---------- communication, reports and billing ----------
    add_all([
        Message(sender_id=emp_user.id, receiver_id=seeker_user.id, subject="Interview invitation",
                body="Hello Sara, we would like to invite you for an online interview."),
        Notification(user_id=seeker_user.id, title="Application update", body="Your application for Python Flask Developer is now: Interview"),
        Notification(user_id=emp_user.id, title="New application", body="Sara Ahmed applied for Data Science Intern"),
        JobAlert(job_seeker_id=seeker.id, keyword="python", category_id=cats["Software Development"].id, city_id=lahore.id),
        EmailLog(user_id=seeker_user.id, subject="Welcome to Job Portal", status="Sent"),
        Report(reporter_id=seeker_user.id, job_id=jobs[4].id, reason="The description looks copied from another website.", status="Open"),
        CompanyReview(company_id=company.id, job_seeker_id=seeker.id, rating=4, comment="Friendly team and quick replies."),
    ])
    subscription = CompanySubscription(company_id=company.id, plan_id=basic_plan.id, start_date=date.today(),
                                       end_date=date.today() + timedelta(days=30), is_active=True)
    db.session.add(subscription)
    db.session.flush()
    db.session.add(Payment(subscription_id=subscription.id, amount=5000, method="Card", status="Paid"))

    db.session.commit()


if __name__ == "__main__":
    import sys
    app = create_app()
    with app.app_context():
        # "python seed.py --if-empty" is used on Render: it fills the database
        # only the first time, so our data is not deleted on every restart
        if "--if-empty" in sys.argv:
            has_data = Role.query.count() > 0
            db.session.remove()  # release the lock, otherwise postgres waits forever
            if has_data:
                print("Database already has data, skipping seed.")
                sys.exit(0)
            seed(reset=False)  # tables are new, nothing to delete
        else:
            seed()
        print("Done! Database is ready with sample data.")
        print("Admin    : admin@jobportal.com    / admin123")
        print("Employer : employer@technova.com  / employer123")
        print("Seeker   : seeker@example.com     / seeker123")
