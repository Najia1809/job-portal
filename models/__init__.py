# models/__init__.py - imports every model so db.create_all() knows all 44 tables
from models.accounts import Role, Permission, RolePermission, User, Country, City
from models.seeker import (JobSeeker, Resume, Education, WorkExperience, Skill,
                           JobSeekerSkill, Certification, Language, JobSeekerLanguage)
from models.company import Industry, Company, CompanyBranch, Employer, CompanyReview, CompanyDocument
from models.jobs import JobCategory, JobType, ExperienceLevel, SalaryRange, Job, JobSkill, JobLocation
from models.hiring import (ApplicationStatus, Application, ApplicationStatusHistory, SavedJob,
                           Interview, InterviewFeedback, JobOffer, ShortlistedCandidate)
from models.comms import Message, Notification, JobAlert, EmailLog, Report
from models.billing import SubscriptionPlan, CompanySubscription, Payment
