# app/schemas/recruitment_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# Job Posting Schemas
class JobPostingBase(BaseModel):
    job_title: str = Field(..., description="Job title")
    job_code: str = Field(..., description="Unique job code")
    department: str = Field(..., description="Department")
    location: str = Field(..., description="Job location")
    employment_type: str = Field(default="full_time")
    job_description: str = Field(..., description="Detailed job description")
    responsibilities: str = Field(..., description="Key responsibilities")
    requirements: str = Field(..., description="Job requirements")
    qualifications: str = Field(..., description="Required qualifications")
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    salary_currency: str = Field(default="INR")
    benefits: Optional[str] = None
    application_deadline: Optional[date] = None
    positions_available: int = Field(default=1)
    is_internal: bool = Field(default=False)
    is_remote: bool = Field(default=False)

class JobPostingCreate(JobPostingBase):
    hiring_manager_id: int = Field(..., description="Reference to hiring manager")

class JobPostingUpdate(BaseModel):
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    job_description: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    qualifications: Optional[str] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    benefits: Optional[str] = None
    application_deadline: Optional[date] = None
    positions_available: Optional[int] = None
    is_internal: Optional[bool] = None
    is_remote: Optional[bool] = None
    status: Optional[str] = None

class JobPostingResponse(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    hiring_manager_id: int
    posted_by_id: int
    posted_date: date
    positions_filled: int
    status: str
    external_posting_url: Optional[str] = None
    posting_platforms: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Candidate Schemas
class CandidateBase(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")
    current_designation: Optional[str] = None
    current_company: Optional[str] = None
    total_experience: Optional[Decimal] = None
    relevant_experience: Optional[Decimal] = None
    highest_qualification: Optional[str] = None
    educational_details: Optional[Dict[str, Any]] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    salary_currency: str = Field(default="INR")
    notice_period: Optional[int] = None
    preferred_location: Optional[str] = None
    willing_to_relocate: bool = Field(default=False)
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    source: str = Field(default="direct")
    referral_source: Optional[str] = None
    source_details: Optional[Dict[str, Any]] = None
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    current_designation: Optional[str] = None
    current_company: Optional[str] = None
    total_experience: Optional[Decimal] = None
    relevant_experience: Optional[Decimal] = None
    highest_qualification: Optional[str] = None
    educational_details: Optional[Dict[str, Any]] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    notice_period: Optional[int] = None
    preferred_location: Optional[str] = None
    willing_to_relocate: Optional[bool] = None
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    assessment_scores: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    referral_source: Optional[str] = None
    source_details: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class CandidateResponse(CandidateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    status: str
    assessment_scores: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

# Job Application Schemas
class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    custom_responses: Optional[Dict[str, Any]] = None

class JobApplicationCreate(JobApplicationBase):
    job_posting_id: int = Field(..., description="Reference to JobPosting")
    candidate_id: int = Field(..., description="Reference to Candidate")

class JobApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = None
    custom_responses: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    stage: Optional[str] = None
    overall_score: Optional[Decimal] = None
    resume_score: Optional[Decimal] = None
    recruiter_rating: Optional[int] = None
    assigned_recruiter_id: Optional[int] = None
    rejection_reason: Optional[str] = None
    rejection_feedback: Optional[str] = None
    recruiter_notes: Optional[str] = None
    hiring_manager_notes: Optional[str] = None

class JobApplicationResponse(JobApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_posting_id: int
    candidate_id: int
    organization_id: int
    application_date: datetime
    status: str
    stage: Optional[str] = None
    overall_score: Optional[Decimal] = None
    resume_score: Optional[Decimal] = None
    recruiter_rating: Optional[int] = None
    assigned_recruiter_id: Optional[int] = None
    last_activity_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    rejection_date: Optional[datetime] = None
    rejection_feedback: Optional[str] = None
    recruiter_notes: Optional[str] = None
    hiring_manager_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Interview Schemas
class InterviewBase(BaseModel):
    interview_type: str = Field(default="technical")
    interview_round: int = Field(default=1)
    interview_title: str = Field(..., description="Interview title")
    scheduled_date: datetime = Field(..., description="Interview date and time")
    duration_minutes: int = Field(default=60)
    interview_mode: str = Field(default="in_person")
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    secondary_interviewers: Optional[Dict[str, Any]] = None

class InterviewCreate(InterviewBase):
    job_application_id: int = Field(..., description="Reference to JobApplication")
    primary_interviewer_id: int = Field(..., description="Reference to primary interviewer")

class InterviewUpdate(BaseModel):
    interview_type: Optional[str] = None
    interview_round: Optional[int] = None
    interview_title: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    interview_mode: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    secondary_interviewers: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    overall_rating: Optional[int] = None
    recommendation: Optional[str] = None
    technical_score: Optional[Decimal] = None
    communication_score: Optional[Decimal] = None
    cultural_fit_score: Optional[Decimal] = None
    problem_solving_score: Optional[Decimal] = None
    interviewer_feedback: Optional[str] = None
    candidate_feedback: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    cancellation_reason: Optional[str] = None
    custom_scores: Optional[Dict[str, Any]] = None

class InterviewResponse(InterviewBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_application_id: int
    primary_interviewer_id: int
    organization_id: int
    status: str
    overall_rating: Optional[int] = None
    recommendation: Optional[str] = None
    technical_score: Optional[Decimal] = None
    communication_score: Optional[Decimal] = None
    cultural_fit_score: Optional[Decimal] = None
    problem_solving_score: Optional[Decimal] = None
    interviewer_feedback: Optional[str] = None
    candidate_feedback: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    cancellation_reason: Optional[str] = None
    rescheduled_from: Optional[datetime] = None
    custom_scores: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

# Job Offer Schemas
class JobOfferBase(BaseModel):
    offer_title: str = Field(..., description="Job offer title")
    valid_until: date = Field(..., description="Offer validity date")
    base_salary: Decimal = Field(..., description="Base salary amount")
    variable_pay: Optional[Decimal] = Field(default=Decimal('0'))
    bonus: Optional[Decimal] = Field(default=Decimal('0'))
    total_compensation: Decimal = Field(..., description="Total compensation")
    salary_currency: str = Field(default="INR")
    benefits_package: Optional[Dict[str, Any]] = None
    joining_bonus: Optional[Decimal] = Field(default=Decimal('0'))
    relocation_allowance: Optional[Decimal] = Field(default=Decimal('0'))
    employment_type: str = Field(default="permanent")
    probation_period: Optional[int] = None
    notice_period: Optional[int] = None
    start_date: Optional[date] = None
    work_location: str = Field(..., description="Work location")
    is_negotiable: bool = Field(default=True)
    special_conditions: Optional[str] = None

class JobOfferCreate(JobOfferBase):
    job_application_id: int = Field(..., description="Reference to JobApplication")

class JobOfferUpdate(BaseModel):
    offer_title: Optional[str] = None
    valid_until: Optional[date] = None
    base_salary: Optional[Decimal] = None
    variable_pay: Optional[Decimal] = None
    bonus: Optional[Decimal] = None
    total_compensation: Optional[Decimal] = None
    benefits_package: Optional[Dict[str, Any]] = None
    joining_bonus: Optional[Decimal] = None
    relocation_allowance: Optional[Decimal] = None
    employment_type: Optional[str] = None
    probation_period: Optional[int] = None
    notice_period: Optional[int] = None
    start_date: Optional[date] = None
    work_location: Optional[str] = None
    status: Optional[str] = None
    is_negotiable: Optional[bool] = None
    negotiation_notes: Optional[str] = None
    special_conditions: Optional[str] = None
    rejection_reason: Optional[str] = None

class JobOfferResponse(JobOfferBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    job_application_id: int
    organization_id: int
    offer_date: date
    status: str
    sent_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    negotiation_rounds: int
    negotiation_notes: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_date: Optional[datetime] = None
    offer_letter_path: Optional[str] = None
    contract_path: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

# Recruitment Pipeline Schemas
class RecruitmentPipelineBase(BaseModel):
    pipeline_name: str = Field(..., description="Pipeline name")
    stage_name: str = Field(..., description="Stage name")
    stage_order: int = Field(..., description="Stage order")
    stage_type: str = Field(default="standard")
    is_mandatory: bool = Field(default=True)
    auto_progress: bool = Field(default=False)
    requires_approval: bool = Field(default=False)
    default_duration_days: Optional[int] = None
    stage_description: Optional[str] = None
    stage_instructions: Optional[str] = None
    is_active: bool = Field(default=True)

class RecruitmentPipelineCreate(RecruitmentPipelineBase):
    pass

class RecruitmentPipelineUpdate(BaseModel):
    pipeline_name: Optional[str] = None
    stage_name: Optional[str] = None
    stage_order: Optional[int] = None
    stage_type: Optional[str] = None
    is_mandatory: Optional[bool] = None
    auto_progress: Optional[bool] = None
    requires_approval: Optional[bool] = None
    default_duration_days: Optional[int] = None
    stage_description: Optional[str] = None
    stage_instructions: Optional[str] = None
    is_active: Optional[bool] = None

class RecruitmentPipelineResponse(RecruitmentPipelineBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Dashboard Schemas
class RecruitmentMetrics(BaseModel):
    total_job_postings: int
    active_job_postings: int
    total_candidates: int
    active_applications: int
    interviews_scheduled: int
    offers_pending: int
    positions_filled_this_month: int
    average_time_to_hire: Optional[int] = None  # Days

class RecruitmentDashboard(BaseModel):
    recruitment_metrics: RecruitmentMetrics
    recent_applications: List[JobApplicationResponse] = []
    upcoming_interviews: List[InterviewResponse] = []
    pending_offers: List[JobOfferResponse] = []

# Bulk Operations Schemas
class BulkCandidateImport(BaseModel):
    candidates_data: List[CandidateCreate]
    
class CandidateImportResult(BaseModel):
    total_candidates: int
    successful: int
    failed: int
    errors: List[str] = []

class BulkStatusUpdate(BaseModel):
    application_ids: List[int]
    new_status: str
    notes: Optional[str] = None
    
class StatusUpdateResult(BaseModel):
    total_applications: int
    successful: int
    failed: int
    errors: List[str] = []