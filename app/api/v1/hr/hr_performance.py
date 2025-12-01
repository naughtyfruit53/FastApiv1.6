from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.hr_models import (
    PerformanceReview, Goal, ReviewCycle, FeedbackForm
)
from app.schemas.hr_schemas import (
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewResponse,
    GoalCreate, GoalUpdate, GoalResponse,
    ReviewCycleCreate, ReviewCycleUpdate, ReviewCycleResponse,
    FeedbackFormCreate, FeedbackFormUpdate, FeedbackFormResponse
)

router = APIRouter(prefix="/hr", tags=["Human Resources - Performance"])

# Performance Review Management
@router.post("/performance-reviews", response_model=PerformanceReviewResponse)
async def create_performance_review(
    review_data: PerformanceReviewCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new performance review"""
    current_user, org_id = auth
   
    performance_review = PerformanceReview(
        **review_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(performance_review)
    await db.commit()
    await db.refresh(performance_review)
   
    return performance_review

@router.get("/performance-reviews", response_model=List[PerformanceReviewResponse])
async def get_performance_reviews(
    employee_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    review_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get performance reviews with filtering"""
    current_user, org_id = auth
   
    stmt = select(PerformanceReview).where(
        PerformanceReview.organization_id == org_id
    )
   
    # Apply filters
    if employee_id:
        stmt = stmt.where(PerformanceReview.employee_id == employee_id)
   
    if reviewer_id:
        stmt = stmt.where(PerformanceReview.reviewer_id == reviewer_id)
   
    if review_type:
        stmt = stmt.where(PerformanceReview.review_type == review_type)
   
    if status:
        stmt = stmt.where(PerformanceReview.status == status)
   
    # Order by review period (newest first)
    stmt = stmt.order_by(desc(PerformanceReview.review_period_start))
   
    result = await db.execute(stmt.offset(skip).limit(limit))
    reviews = result.scalars().all()
    return reviews

@router.put("/performance-reviews/{review_id}", response_model=PerformanceReviewResponse)
async def update_performance_review(
    review_id: int,
    review_data: PerformanceReviewUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update performance review"""
    current_user, org_id = auth
   
    stmt = select(PerformanceReview).where(
        and_(
            PerformanceReview.id == review_id,
            PerformanceReview.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    review = result.scalar_one_or_none()
   
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performance review not found"
        )
   
    # Update fields
    for field, value in review_data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)
   
    # Set submission/acknowledgment dates based on status
    if review_data.status == "submitted" and not review.submitted_date:
        review.submitted_date = datetime.utcnow()
    elif review_data.status == "acknowledged" and not review.acknowledged_date:
        review.acknowledged_date = datetime.utcnow()
   
    await db.commit()
    await db.refresh(review)
   
    return review

# Goals/OKRs Management
@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal_data: GoalCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new goal or OKR"""
    current_user, org_id = auth
   
    goal = Goal(
        **goal_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
   
    return goal

@router.get("/goals", response_model=List[GoalResponse])
async def get_goals(
    employee_id: Optional[int] = Query(None),
    goal_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    review_cycle_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get goals with filtering"""
    current_user, org_id = auth
   
    stmt = select(Goal).where(Goal.organization_id == org_id)
   
    if employee_id:
        stmt = stmt.where(Goal.employee_id == employee_id)
    if goal_type:
        stmt = stmt.where(Goal.goal_type == goal_type)
    if status:
        stmt = stmt.where(Goal.status == status)
    if review_cycle_id:
        stmt = stmt.where(Goal.review_cycle_id == review_cycle_id)
   
    stmt = stmt.order_by(desc(Goal.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get goal by ID"""
    current_user, org_id = auth
   
    stmt = select(Goal).where(
        and_(
            Goal.id == goal_id,
            Goal.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    goal = result.scalar_one_or_none()
   
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
   
    return goal

@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a goal"""
    current_user, org_id = auth
   
    stmt = select(Goal).where(
        and_(
            Goal.id == goal_id,
            Goal.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    goal = result.scalar_one_or_none()
   
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
   
    for field, value in goal_data.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
   
    await db.commit()
    await db.refresh(goal)
   
    return goal

@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: int,
    auth: tuple = Depends(require_access("hr", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a goal"""
    current_user, org_id = auth
   
    stmt = select(Goal).where(
        and_(
            Goal.id == goal_id,
            Goal.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    goal = result.scalar_one_or_none()
   
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
   
    await db.delete(goal)
    await db.commit()
   
    return {"message": "Goal deleted successfully"}

# Review Cycles Management
@router.post("/review-cycles", response_model=ReviewCycleResponse)
async def create_review_cycle(
    cycle_data: ReviewCycleCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review cycle"""
    current_user, org_id = auth
   
    cycle = ReviewCycle(
        **cycle_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
   
    db.add(cycle)
    await db.commit()
    await db.refresh(cycle)
   
    return cycle

@router.get("/review-cycles", response_model=List[ReviewCycleResponse])
async def get_review_cycles(
    status: Optional[str] = Query(None),
    cycle_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get review cycles"""
    current_user, org_id = auth
   
    stmt = select(ReviewCycle).where(ReviewCycle.organization_id == org_id)
   
    if status:
        stmt = stmt.where(ReviewCycle.status == status)
    if cycle_type:
        stmt = stmt.where(ReviewCycle.cycle_type == cycle_type)
    if is_active is not None:
        stmt = stmt.where(ReviewCycle.is_active == is_active)
   
    stmt = stmt.order_by(desc(ReviewCycle.start_date))
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/review-cycles/{cycle_id}", response_model=ReviewCycleResponse)
async def get_review_cycle(
    cycle_id: int,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get review cycle by ID"""
    current_user, org_id = auth
   
    stmt = select(ReviewCycle).where(
        and_(
            ReviewCycle.id == cycle_id,
            ReviewCycle.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()
   
    if not cycle:
        raise HTTPException(status_code=404, detail="Review cycle not found")
   
    return cycle

@router.put("/review-cycles/{cycle_id}", response_model=ReviewCycleResponse)
async def update_review_cycle(
    cycle_id: int,
    cycle_data: ReviewCycleUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a review cycle"""
    current_user, org_id = auth
   
    stmt = select(ReviewCycle).where(
        and_(
            ReviewCycle.id == cycle_id,
            ReviewCycle.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    cycle = result.scalar_one_or_none()
   
    if not cycle:
        raise HTTPException(status_code=404, detail="Review cycle not found")
   
    for field, value in cycle_data.model_dump(exclude_unset=True).items():
        setattr(cycle, field, value)
   
    await db.commit()
    await db.refresh(cycle)
   
    return cycle

# 360 Feedback Forms
@router.post("/feedback-forms", response_model=FeedbackFormResponse)
async def create_feedback_form(
    form_data: FeedbackFormCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a feedback form template or response"""
    current_user, org_id = auth
   
    form = FeedbackForm(
        **form_data.model_dump(),
        organization_id=org_id
    )
   
    db.add(form)
    await db.commit()
    await db.refresh(form)
   
    return form

@router.get("/feedback-forms", response_model=List[FeedbackFormResponse])
async def get_feedback_forms(
    is_template: Optional[bool] = Query(None),
    feedback_type: Optional[str] = Query(None),
    reviewee_id: Optional[int] = Query(None),
    review_cycle_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get feedback forms"""
    current_user, org_id = auth
   
    stmt = select(FeedbackForm).where(FeedbackForm.organization_id == org_id)
   
    if is_template is not None:
        stmt = stmt.where(FeedbackForm.is_template == is_template)
    if feedback_type:
        stmt = stmt.where(FeedbackForm.feedback_type == feedback_type)
    if reviewee_id:
        stmt = stmt.where(FeedbackForm.review_reviewee_id == reviewee_id)
    if review_cycle_id:
        stmt = stmt.where(FeedbackForm.review_cycle_id == review_cycle_id)
    if status:
        stmt = stmt.where(FeedbackForm.status == status)
   
    stmt = stmt.order_by(desc(FeedbackForm.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/feedback-forms/{form_id}", response_model=FeedbackFormResponse)
async def update_feedback_form(
    form_id: int,
    form_data: FeedbackFormUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a feedback form"""
    current_user, org_id = auth
   
    stmt = select(FeedbackForm).where(
        and_(
            FeedbackForm.id == form_id,
            FeedbackForm.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    form = result.scalar_one_or_none()
   
    if not form:
        raise HTTPException(status_code=404, detail="Feedback form not found")
   
    for field, value in form_data.model_dump(exclude_unset=True).items():
        setattr(form, field, value)
   
    # Mark as completed if status changed to completed
    if form_data.status == "completed" and not form.completed_at:
        form.completed_at = datetime.now(timezone.utc)
   
    await db.commit()
    await db.refresh(form)
   
    return form
