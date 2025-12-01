from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.recruitment_models import (
    JobPosting, Candidate, Interview, JobOffer, RecruitmentPipeline
)
from app.schemas.hr_schemas import (
    JobPostingCreate, JobPostingUpdate, JobPostingResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    JobOfferCreate, JobOfferUpdate, JobOfferResponse,
    RecruitmentPipelineCreate, RecruitmentPipelineUpdate, RecruitmentPipelineResponse
)

router = APIRouter(prefix="/hr/recruitment", tags=["Human Resources - Recruitment"])

# Job Postings
@router.post("/job-postings", response_model=JobPostingResponse)
async def create_job_posting(
    posting_data: JobPostingCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting"""
    current_user, org_id = auth
   
    # Check for unique job code
    stmt = select(JobPosting).where(
        and_(
            JobPosting.organization_id == org_id,
            JobPosting.job_code == posting_data.job_code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Job code already exists")
   
    posting = JobPosting(
        **posting_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(posting)
    await db.commit()
    await db.refresh(posting)
   
    return posting

@router.get("/job-postings", response_model=List[JobPostingResponse])
async def get_job_postings(
    status: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    employment_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get job postings"""
    current_user, org_id = auth
   
    stmt = select(JobPosting).where(JobPosting.organization_id == org_id)
   
    if status:
        stmt = stmt.where(JobPosting.status == status)
    if department_id:
        stmt = stmt.where(JobPosting.department_id == department_id)
    if employment_type:
        stmt = stmt.where(JobPosting.employment_type == employment_type)
   
    stmt = stmt.order_by(desc(JobPosting.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/job-postings/{posting_id}", response_model=JobPostingResponse)
async def get_job_posting(
    posting_id: int,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get job posting by ID"""
    current_user, org_id = auth
   
    stmt = select(JobPosting).where(
        and_(
            JobPosting.id == posting_id,
            JobPosting.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    posting = result.scalar_one_or_none()
   
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
   
    return posting

@router.put("/job-postings/{posting_id}", response_model=JobPostingResponse)
async def update_job_posting(
    posting_id: int,
    posting_data: JobPostingUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a job posting"""
    current_user, org_id = auth
   
    stmt = select(JobPosting).where(
        and_(
            JobPosting.id == posting_id,
            JobPosting.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    posting = result.scalar_one_or_none()
   
    if not posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
   
    for field, value in posting_data.model_dump(exclude_unset=True).items():
        setattr(posting, field, value)
   
    await db.commit()
    await db.refresh(posting)
   
    return posting

# Candidates
@router.post("/candidates", response_model=CandidateResponse)
async def create_candidate(
    candidate_data: CandidateCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate"""
    current_user, org_id = auth
   
    candidate = Candidate(
        **candidate_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
   
    return candidate

@router.get("/candidates", response_model=List[CandidateResponse])
async def get_candidates(
    job_posting_id: Optional[int] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get candidates with filtering"""
    current_user, org_id = auth
   
    stmt = select(Candidate).where(Candidate.organization_id == org_id)
   
    if job_posting_id:
        stmt = stmt.where(Candidate.job_posting_id == job_posting_id)
    if stage:
        stmt = stmt.where(Candidate.stage == stage)
    if status:
        stmt = stmt.where(Candidate.status == status)
   
    stmt = stmt.order_by(desc(Candidate.application_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate by ID"""
    current_user, org_id = auth
   
    stmt = select(Candidate).where(
        and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    candidate = result.scalar_one_or_none()
   
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
   
    return candidate

@router.put("/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a candidate"""
    current_user, org_id = auth
   
    stmt = select(Candidate).where(
        and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    candidate = result.scalar_one_or_none()
   
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
   
    for field, value in candidate_data.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
   
    # Update stage timestamp
    if candidate_data.stage:
        candidate.stage_updated_at = datetime.now(timezone.utc)
   
    await db.commit()
    await db.refresh(candidate)
   
    return candidate

@router.put("/candidates/{candidate_id}/stage")
async def update_candidate_stage(
    candidate_id: int,
    stage: str = Query(..., description="New stage: new, screening, interview, assessment, offer, hired, rejected"),
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Move candidate to a new stage (Kanban update)"""
    current_user, org_id = auth
   
    stmt = select(Candidate).where(
        and_(
            Candidate.id == candidate_id,
            Candidate.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    candidate = result.scalar_one_or_none()
   
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
   
    candidate.stage = stage
    candidate.stage_updated_at = datetime.now(timezone.utc)
   
    await db.commit()
   
    return {"message": f"Candidate moved to {stage} stage"}

# Interviews
@router.post("/interviews", response_model=InterviewResponse)
async def create_interview(
    interview_data: InterviewCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Schedule an interview"""
    current_user, org_id = auth
   
    interview = Interview(
        **interview_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
   
    return interview

@router.get("/interviews", response_model=List[InterviewResponse])
async def get_interviews(
    candidate_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    scheduled_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get interviews"""
    current_user, org_id = auth
   
    stmt = select(Interview).where(Interview.organization_id == org_id)
   
    if candidate_id:
        stmt = stmt.where(Interview.candidate_id == candidate_id)
    if status:
        stmt = stmt.where(Interview.status == status)
    if scheduled_date:
        stmt = stmt.where(Interview.scheduled_date == scheduled_date)
   
    stmt = stmt.order_by(Interview.scheduled_date, Interview.scheduled_time).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update an interview"""
    current_user, org_id = auth
   
    stmt = select(Interview).where(
        and_(
            Interview.id == interview_id,
            Interview.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    interview = result.scalar_one_or_none()
   
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
   
    for field, value in interview_data.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
   
    await db.commit()
    await db.refresh(interview)
   
    return interview

# Job Offers
@router.post("/job-offers", response_model=JobOfferResponse)
async def create_job_offer(
    offer_data: JobOfferCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a job offer"""
    current_user, org_id = auth
   
    # Check for unique offer number
    stmt = select(JobOffer).where(
        and_(
            JobOffer.organization_id == org_id,
            JobOffer.offer_number == offer_data.offer_number
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Offer number already exists")
   
    offer = JobOffer(
        **offer_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
   
    return offer

@router.get("/job-offers", response_model=List[JobOfferResponse])
async def get_job_offers(
    candidate_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get job offers"""
    current_user, org_id = auth
   
    stmt = select(JobOffer).where(JobOffer.organization_id == org_id)
   
    if candidate_id:
        stmt = stmt.where(JobOffer.candidate_id == candidate_id)
    if status:
        stmt = stmt.where(JobOffer.status == status)
   
    stmt = stmt.order_by(desc(JobOffer.offer_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/job-offers/{offer_id}", response_model=JobOfferResponse)
async def update_job_offer(
    offer_id: int,
    offer_data: JobOfferUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a job offer"""
    current_user, org_id = auth
   
    stmt = select(JobOffer).where(
        and_(
            JobOffer.id == offer_id,
            JobOffer.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    offer = result.scalar_one_or_none()
   
    if not offer:
        raise HTTPException(status_code=404, detail="Job offer not found")
   
    for field, value in offer_data.model_dump(exclude_unset=True).items():
        setattr(offer, field, value)
   
    # Track response date
    if offer_data.status in ["accepted", "rejected"]:
        offer.candidate_response_date = datetime.now(timezone.utc)
   
    await db.commit()
    await db.refresh(offer)
   
    return offer

# Recruitment Pipeline Configuration
@router.post("/recruitment-pipelines", response_model=RecruitmentPipelineResponse)
async def create_recruitment_pipeline(
    pipeline_data: RecruitmentPipelineCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new recruitment pipeline stage"""
    current_user, org_id = auth
   
    pipeline = RecruitmentPipeline(
        **pipeline_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(pipeline)
    await db.commit()
    await db.refresh(pipeline)
   
    return pipeline

@router.get("/recruitment-pipelines", response_model=List[RecruitmentPipelineResponse])
async def get_recruitment_pipelines(
    pipeline_name: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get recruitment pipelines"""
    current_user, org_id = auth
   
    stmt = select(RecruitmentPipeline).where(RecruitmentPipeline.organization_id == org_id)
   
    if pipeline_name:
        stmt = stmt.where(RecruitmentPipeline.pipeline_name == pipeline_name)
    if is_active is not None:
        stmt = stmt.where(RecruitmentPipeline.is_active == is_active)
   
    stmt = stmt.order_by(RecruitmentPipeline.pipeline_name, RecruitmentPipeline.stage_order)
    result = await db.execute(stmt)
    return result.scalars().all()
