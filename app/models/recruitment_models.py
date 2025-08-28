# app/models/recruitment_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Job Management
class JobPosting(Base):
    """Job openings and requirements"""
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_job_posting_organization_id"), nullable=False, index=True)
    
    # Job details
    job_title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    job_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    department: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    employment_type: Mapped[str] = mapped_column(String, nullable=False, default="full_time")  # full_time, part_time, contract, internship
    
    # Job description
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    qualifications: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Experience and skills
    min_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Years
    max_experience: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    required_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Skills with proficiency levels
    preferred_skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Compensation
    min_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    max_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    salary_currency: Mapped[str] = mapped_column(String, nullable=False, default="INR")
    benefits: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Posting details
    posted_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.current_date())
    application_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    positions_available: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    positions_filled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Status and workflow
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, active, paused, closed, cancelled
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)  # Internal posting only
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Hiring manager
    hiring_manager_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_posting_hiring_manager_id"), nullable=False)
    posted_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_posting_posted_by_id"), nullable=False)
    
    # SEO and external posting
    external_posting_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    posting_platforms: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Where it's posted
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    hiring_manager: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User", foreign_keys=[hiring_manager_id])
    posted_by: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User", foreign_keys=[posted_by_id])
    
    # Recruitment relationships
    candidates: Mapped[List["JobApplication"]] = relationship("JobApplication", back_populates="job_posting")

    __table_args__ = (
        UniqueConstraint('organization_id', 'job_code', name='uq_job_posting_org_code'),
        Index('idx_job_posting_org_status', 'organization_id', 'status'),
        Index('idx_job_posting_deadline', 'application_deadline'),
        {'extend_existing': True}
    )

# Candidate Management
class Candidate(Base):
    """Candidate profiles and information"""
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_candidate_organization_id"), nullable=False, index=True)
    
    # Personal information
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    
    # Professional details
    current_designation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_company: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_experience: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)  # Years with decimal
    relevant_experience: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1), nullable=True)
    
    # Education
    highest_qualification: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    educational_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Detailed education history
    
    # Compensation
    current_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    expected_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    salary_currency: Mapped[str] = mapped_column(String, nullable=False, default="INR")
    
    # Availability
    notice_period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Days
    preferred_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    willing_to_relocate: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Documents and attachments
    resume_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cover_letter_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    portfolio_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Skills and assessments
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    assessment_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Source and tracking
    source: Mapped[str] = mapped_column(String, nullable=False, default="direct")  # direct, referral, portal, agency, social
    referral_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")  # active, blacklisted, hired, withdrawn
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Custom tags
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_candidate_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    # Recruitment relationships
    job_applications: Mapped[List["JobApplication"]] = relationship("JobApplication", back_populates="candidate")

    __table_args__ = (
        Index('idx_candidate_org_email', 'organization_id', 'email'),
        Index('idx_candidate_name', 'first_name', 'last_name'),
        Index('idx_candidate_status', 'status'),
        {'extend_existing': True}
    )

# Job Applications
class JobApplication(Base):
    """Applications submitted by candidates for job postings"""
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_job_application_organization_id"), nullable=False, index=True)
    
    # References
    job_posting_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_postings.id", name="fk_job_application_job_posting_id"), nullable=False, index=True)
    candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidates.id", name="fk_job_application_candidate_id"), nullable=False, index=True)
    
    # Application details
    application_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_responses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Responses to custom questions
    
    # Status tracking
    status: Mapped[str] = mapped_column(String, nullable=False, default="applied")  # applied, screening, interview, offer, rejected, hired, withdrawn
    stage: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Custom recruitment stages
    
    # Ranking and scoring
    overall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # Overall application score
    resume_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)  # Automated resume scoring
    recruiter_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    
    # Assignment and tracking
    assigned_recruiter_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_application_assigned_recruiter_id"), nullable=True)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Rejection details
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rejection_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Internal notes
    recruiter_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hiring_manager_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    job_posting: Mapped["JobPosting"] = relationship("JobPosting", back_populates="candidates")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="job_applications")
    assigned_recruiter: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    
    # Interview relationships
    interviews: Mapped[List["Interview"]] = relationship("Interview", back_populates="job_application")

    __table_args__ = (
        UniqueConstraint('job_posting_id', 'candidate_id', name='uq_job_application_job_candidate'),
        Index('idx_job_application_org_status', 'organization_id', 'status'),
        Index('idx_job_application_date', 'application_date'),
        {'extend_existing': True}
    )

# Interview Management
class Interview(Base):
    """Interview scheduling and management"""
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_interview_organization_id"), nullable=False, index=True)
    
    # References
    job_application_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_applications.id", name="fk_interview_job_application_id"), nullable=False, index=True)
    
    # Interview details
    interview_type: Mapped[str] = mapped_column(String, nullable=False, default="technical")  # technical, hr, final, group, behavioral
    interview_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    interview_title: Mapped[str] = mapped_column(String, nullable=False)
    
    # Scheduling
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    interview_mode: Mapped[str] = mapped_column(String, nullable=False, default="in_person")  # in_person, video, phone
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    meeting_link: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Interviewers
    primary_interviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_interview_primary_interviewer_id"), nullable=False)
    secondary_interviewers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional interviewer IDs
    
    # Status and results
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled")  # scheduled, completed, cancelled, rescheduled, no_show
    overall_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5 stars
    recommendation: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # proceed, reject, hold
    
    # Feedback and evaluation
    technical_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    communication_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    cultural_fit_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    problem_solving_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Comments and notes
    interviewer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    candidate_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weaknesses: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Cancellation/rescheduling
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rescheduled_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Custom evaluation criteria
    custom_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_interview_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    job_application: Mapped["JobApplication"] = relationship("JobApplication", back_populates="interviews")
    primary_interviewer: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User", foreign_keys=[primary_interviewer_id])
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index('idx_interview_org_date', 'organization_id', 'scheduled_date'),
        Index('idx_interview_status', 'status'),
        Index('idx_interview_interviewer', 'primary_interviewer_id'),
        {'extend_existing': True}
    )

# Offer Management
class JobOffer(Base):
    """Job offers and offer management"""
    __tablename__ = "job_offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_job_offer_organization_id"), nullable=False, index=True)
    
    # References
    job_application_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_applications.id", name="fk_job_offer_job_application_id"), nullable=False, index=True)
    
    # Offer details
    offer_title: Mapped[str] = mapped_column(String, nullable=False)
    offer_date: Mapped[date] = mapped_column(Date, nullable=False, default=func.current_date())
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Compensation package
    base_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    variable_pay: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    bonus: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    total_compensation: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    salary_currency: Mapped[str] = mapped_column(String, nullable=False, default="INR")
    
    # Benefits
    benefits_package: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    joining_bonus: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    relocation_allowance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    
    # Terms and conditions
    employment_type: Mapped[str] = mapped_column(String, nullable=False, default="permanent")
    probation_period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Months
    notice_period: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Days
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    work_location: Mapped[str] = mapped_column(String, nullable=False)
    
    # Status and tracking
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, sent, accepted, rejected, expired, withdrawn
    sent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Negotiation tracking
    is_negotiable: Mapped[bool] = mapped_column(Boolean, default=True)
    negotiation_rounds: Mapped[int] = mapped_column(Integer, default=0)
    negotiation_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Approval workflow
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_offer_approved_by_id"), nullable=True)
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Document management
    offer_letter_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contract_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Additional terms
    special_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_job_offer_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    job_application: Mapped["JobApplication"] = relationship("JobApplication")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[approved_by_id])
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index('idx_job_offer_org_status', 'organization_id', 'status'),
        Index('idx_job_offer_dates', 'offer_date', 'valid_until'),
        Index('idx_job_offer_application', 'job_application_id'),
        {'extend_existing': True}
    )

# Recruitment Pipeline Configuration
class RecruitmentPipeline(Base):
    """Customizable recruitment pipeline stages"""
    __tablename__ = "recruitment_pipelines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_recruitment_pipeline_organization_id"), nullable=False, index=True)
    
    # Pipeline details
    pipeline_name: Mapped[str] = mapped_column(String, nullable=False)
    stage_name: Mapped[str] = mapped_column(String, nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_type: Mapped[str] = mapped_column(String, nullable=False, default="standard")  # standard, interview, assessment, approval
    
    # Stage configuration
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_progress: Mapped[bool] = mapped_column(Boolean, default=False)  # Auto-progress to next stage
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Stage settings
    default_duration_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stage_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stage_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")

    __table_args__ = (
        UniqueConstraint('organization_id', 'pipeline_name', 'stage_order', name='uq_recruitment_pipeline_org_stage'),
        Index('idx_recruitment_pipeline_org_active', 'organization_id', 'is_active'),
        Index('idx_recruitment_pipeline_order', 'stage_order'),
        {'extend_existing': True}
    )