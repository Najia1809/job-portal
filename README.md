# Job Portal (Flask + SQLAlchemy)

Web Engineering project made by Najia.

A job portal where companies post jobs and people apply for them.
There are 3 types of users: **Job Seeker**, **Employer** and **Admin**.

## What it does

- **Job Seeker**: register, login, edit profile and skills, search jobs, apply, save jobs, see application status, withdraw an application
- **Employer**: add company details, post / edit / delete jobs, see applications, change status (Applied, Shortlisted, Interview, Offered, Rejected)
- **Admin**: one generic panel to Create, Read, Update and Delete records of **all 44 tables**

## How to run

1. Make a virtual environment and activate it

   ```
   python -m venv venv
   venv\Scripts\activate        (Windows)
   source venv/bin/activate     (Linux / Mac)
   ```

2. Install packages

   ```
   pip install -r requirements.txt
   ```

3. Create the database with sample data (this deletes the old database)

   ```
   python seed.py
   ```

4. Start the website

   ```
   python app.py
   ```

   Open http://127.0.0.1:5000

## Deploy on Render

1. Push this project to a GitHub repository (the `venv` folder and `jobportal.db` are ignored by `.gitignore`).
2. On Render, create a **PostgreSQL** database (Free plan). Copy its **Internal Database URL**.
3. Create a **Web Service** from the GitHub repo and use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python seed.py --if-empty && gunicorn "app:create_app()" --workers 1 --bind 0.0.0.0:$PORT`
   - Environment variables:
     - `DATABASE_URL` = the Internal Database URL from step 2
     - `SECRET_KEY` = any long random text
4. Deploy. The first start creates all 44 tables and adds the sample data. Next restarts do not delete anything, because of `--if-empty`.

Notes:
- The Free web service sleeps after 15 minutes without visitors, so the first page can take about a minute to open.
- The Free Render database expires 30 days after it is created.
- `python seed.py` (without `--if-empty`) deletes everything and makes new sample data. Do not run it on the live database.

## Sample accounts (made by seed.py)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@jobportal.com | admin123 |
| Employer | employer@technova.com | employer123 |
| Job Seeker | seeker@example.com | seeker123 |

## Environment variables (optional)

- `SECRET_KEY` - secret key for sessions (a default dev key is used if not set)
- `DATABASE_URL` - database address (default is a local SQLite file `jobportal.db`; on Render it is PostgreSQL)

## Project structure

```
app.py              app factory, registers blueprints
config.py           settings
extensions.py       db and csrf objects
forms.py            Flask-WTF forms with server side validation
utils.py            login_required / role_required helpers
seed.py             sample data for all tables
models/             44 SQLAlchemy models in 7 files
blueprints/         auth, main, seeker, employer, admin
templates/          Jinja2 templates (all extend base.html)
static/             css
```

## Database (44 tables)

- Accounts: users, roles, permissions, role_permissions, countries, cities
- Job seeker: job_seekers, resumes, education, work_experience, skills, job_seeker_skills, certifications, languages, job_seeker_languages
- Company: industries, companies, company_branches, employers, company_reviews, company_documents
- Jobs: job_categories, job_types, experience_levels, salary_ranges, jobs, job_skills, job_locations
- Hiring: application_statuses, applications, application_status_history, saved_jobs, interviews, interview_feedback, job_offers, shortlisted_candidates
- Communication: messages, notifications, job_alerts, email_logs, reports
- Billing: subscription_plans, company_subscriptions, payments

Every table is connected to another table with a foreign key. SQLite foreign key checking is turned on in `app.py`.

## Flask concepts used

- Routing with `<int:id>` converters and correct GET / POST methods
- Blueprints
- Jinja2 template inheritance (`extends` / `block`), loops, conditions, macros
- SQLAlchemy models, relationships and full CRUD
- Server side validation with Flask-WTF (and manual validation in the admin panel)
- Sessions (login), a cookie (last search), flash messages
- Post-Redirect-Get after every form submit
- CSRF protection on all forms
