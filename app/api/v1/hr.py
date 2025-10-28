# app/api/v1/hr.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta
import os
import uuid

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.hr_models import (
    EmployeeProfile, AttendanceRecord, LeaveType, 
    LeaveApplication, PerformanceReview
)
from app.schemas.hr_schemas import (
    EmployeeProfileCreate, EmployeeProfileUpdate, EmployeeProfileResponse,
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse,
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse,
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewResponse,
    HRDashboard, EmployeeDashboard, AttendanceSummary
)
from app.services.pdf_extraction import pdf_extraction_service

router = APIRouter(prefix="/hr", tags=["Human Resources"])

# Employee Profile Management
@router.post("/employees", response_model=EmployeeProfileResponse)
async def create_employee_profile(
    employee_data: EmployeeProfileCreate = Depends(),
    documents: List[UploadFile] = File(None),
    auth: tuple = Depends(require_access("hr", "create")),

    db: AsyncSession = Depends(get_db)
):

    """Create a new employee profile with optional documents"""

    current_user, org_id = auth
    
    # Check if employee profile already exists for this user
    stmt = select(EmployeeProfile).where(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.user_id == employee_data.user_id
        )
    )
    result = await db.execute(stmt)
    existing_profile = result.scalar_one_or_none()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user"
        )
    
    # Check if employee code is unique within organization
    stmt = select(EmployeeProfile).where(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employee_code == employee_data.employee_code
        )
    )
    result = await db.execute(stmt)
    existing_code = result.scalar_one_or_none()
    
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee code already exists"
        )
    
    employee_profile = EmployeeProfile(
        **employee_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    # Handle document uploads
    uploaded_docs = []
    if documents:
        if len(documents) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 5 documents allowed"
            )
        
        for doc in documents:
            if not doc.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF documents are allowed"
                )
            
            # Save document
            doc_path = await pdf_extraction_service._save_temp_file(doc)
            uploaded_docs.append(doc_path)
            
            # Optional: Extract data from document
            # extracted = await pdf_extraction_service.extract_kyc_data(doc)
            # Update employee_profile with extracted data if needed
    
    # Save documents paths to employee profile
    employee_profile.documents = uploaded_docs  # Assuming documents is a list field
    
    db.add(employee_profile)
    await db.commit()
    await db.refresh(employee_profile)
    
    return employee_profile

@router.get("/employees", response_model=List[EmployeeProfileResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    employment_status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get list of employees with filtering and pagination"""

    current_user, org_id = auth
    
    stmt = select(EmployeeProfile).where(
        EmployeeProfile.organization_id == org_id
    )
    
    # Apply filters
    if search:
        stmt = stmt.join(User).where(
            or_(
                User.full_name.ilike(f"%{search}%"),
                EmployeeProfile.employee_code.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if department:
        stmt = stmt.join(User).where(User.department == department)
    
    if employment_status:
        stmt = stmt.where(EmployeeProfile.employment_status == employment_status)
    
    # Order by creation date (newest first)
    stmt = stmt.order_by(desc(EmployeeProfile.created_at))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    employees = result.scalars().all()
    return employees

@router.get("/employees/{employee_id}", response_model=EmployeeProfileResponse)
async def get_employee(
    employee_id: int,
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get employee profile by ID"""

    current_user, org_id = auth
    
    stmt = select(EmployeeProfile).where(
        and_(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return employee

@router.put("/employees/{employee_id}", response_model=EmployeeProfileResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeProfileUpdate = Depends(),
    documents: List[UploadFile] = File(None),
    auth: tuple = Depends(require_access("hr", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Update employee profile with optional new documents"""

    current_user, org_id = auth
    
    stmt = select(EmployeeProfile).where(
        and_(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if employee code is unique (if being updated)
    if employee_data.employee_code and employee_data.employee_code != employee.employee_code:
        stmt = select(EmployeeProfile).where(
            and_(
                EmployeeProfile.organization_id == org_id,
                EmployeeProfile.employee_code == employee_data.employee_code,
                EmployeeProfile.id != employee_id
            )
        )
        result = await db.execute(stmt)
        existing_code = result.scalar_one_or_none()
        
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee code already exists"
            )
    
    # Update fields
    for field, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    # Handle new documents
    if documents:
        new_docs = []
        for doc in documents:
            if not doc.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF documents are allowed"
                )
            
            doc_path = await pdf_extraction_service._save_temp_file(doc)
            new_docs.append(doc_path)
        
        # Append new documents (limit total to 5)
        current_docs = employee.documents or []
        employee.documents = current_docs + new_docs
        if len(employee.documents) > 5:
            employee.documents = employee.documents[-5:]  # Keep latest 5
    
    employee.updated_by_id = current_user.id
    
    await db.commit()
    await db.refresh(employee)
    
    return employee

# Attendance Management
@router.post("/attendance", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    attendance_data: AttendanceRecordCreate,
    auth: tuple = Depends(require_access("hr", "create")),

    db: AsyncSession = Depends(get_db)
):

    """Create attendance record"""

    current_user, org_id = auth
    
    # Check if attendance record already exists for this date
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.organization_id == org_id,
            AttendanceRecord.employee_id == attendance_data.employee_id,
            AttendanceRecord.attendance_date == attendance_data.attendance_date
        )
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this date"
        )
    
    attendance_record = AttendanceRecord(
        **attendance_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(attendance_record)
    await db.commit()
    await db.refresh(attendance_record)
    
    return attendance_record

@router.get("/attendance", response_model=List[AttendanceRecordResponse])
async def get_attendance_records(
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get attendance records with filtering"""

    current_user, org_id = auth
    
    stmt = select(AttendanceRecord).where(
        AttendanceRecord.organization_id == org_id
    )
    
    # Apply filters
    if employee_id:
        stmt = stmt.where(AttendanceRecord.employee_id == employee_id)
    
    if start_date:
        stmt = stmt.where(AttendanceRecord.attendance_date >= start_date)
    
    if end_date:
        stmt = stmt.where(AttendanceRecord.attendance_date <= end_date)
    
    if status:
        stmt = stmt.where(AttendanceRecord.attendance_status == status)
    
    # Order by date (newest first)
    stmt = stmt.order_by(desc(AttendanceRecord.attendance_date))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    records = result.scalars().all()
    return records

@router.put("/attendance/{attendance_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    attendance_id: int,
    attendance_data: AttendanceRecordUpdate,
    auth: tuple = Depends(require_access("hr", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Update attendance record"""

    current_user, org_id = auth
    
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.id == attendance_id,
            AttendanceRecord.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update fields
    for field, value in attendance_data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    
    # Set approval details if being approved
    if attendance_data.is_approved is not None and attendance_data.is_approved:
        record.approved_by_id = current_user.id
        record.approved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(record)
    
    return record

# Leave Type Management
@router.post("/leave-types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type_data: LeaveTypeCreate,
    auth: tuple = Depends(require_access("hr", "create")),

    db: AsyncSession = Depends(get_db)
):

    """Create a new leave type"""

    current_user, org_id = auth
    
    # Check if leave type code is unique within organization
    stmt = select(LeaveType).where(
        and_(
            LeaveType.organization_id == org_id,
            LeaveType.code == leave_type_data.code
        )
    )
    result = await db.execute(stmt)
    existing_code = result.scalar_one_or_none()
    
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type code already exists"
        )
    
    leave_type = LeaveType(
        **leave_type_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(leave_type)
    await db.commit()
    await db.refresh(leave_type)
    
    return leave_type

@router.get("/leave-types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get all leave types"""

    current_user, org_id = auth
    
    stmt = select(LeaveType).where(
        LeaveType.organization_id == org_id
    )
    
    if is_active is not None:
        stmt = stmt.where(LeaveType.is_active == is_active)
    
    result = await db.execute(stmt.order_by(LeaveType.name))
    leave_types = result.scalars().all()
    return leave_types

# Leave Application Management
@router.post("/leave-applications", response_model=LeaveApplicationResponse)
async def create_leave_application(
    leave_data: LeaveApplicationCreate,
    auth: tuple = Depends(require_access("hr", "create")),

    db: AsyncSession = Depends(get_db)
):

    """Create a new leave application"""

    current_user, org_id = auth
    
    leave_application = LeaveApplication(
        **leave_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(leave_application)
    await db.commit()
    await db.refresh(leave_application)
    
    return leave_application

@router.get("/leave-applications", response_model=List[LeaveApplicationResponse])
async def get_leave_applications(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get leave applications with filtering"""

    current_user, org_id = auth
    
    stmt = select(LeaveApplication).where(
        LeaveApplication.organization_id == org_id
    )
    
    # Apply filters
    if employee_id:
        stmt = stmt.where(LeaveApplication.employee_id == employee_id)
    
    if status:
        stmt = stmt.where(LeaveApplication.status == status)
    
    if start_date:
        stmt = stmt.where(LeaveApplication.start_date >= start_date)
    
    if end_date:
        stmt = stmt.where(LeaveApplication.end_date <= end_date)
    
    # Order by application date (newest first)
    stmt = stmt.order_by(desc(LeaveApplication.applied_date))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    applications = result.scalars().all()
    return applications

@router.put("/leave-applications/{application_id}/approve")
async def approve_leave_application(
    application_id: int,
    approval_remarks: Optional[str] = None,
    auth: tuple = Depends(require_access("hr", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Approve a leave application"""

    current_user, org_id = auth
    
    stmt = select(LeaveApplication).where(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending applications can be approved"
        )
    
    application.status = "approved"
    application.approved_by_id = current_user.id
    application.approved_date = datetime.utcnow()
    application.approval_remarks = approval_remarks
    
    await db.commit()
    
    return {"message": "Leave application approved successfully"}

@router.put("/leave-applications/{application_id}/reject")
async def reject_leave_application(
    application_id: int,
    approval_remarks: str,
    auth: tuple = Depends(require_access("hr", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Reject a leave application"""

    current_user, org_id = auth
    
    stmt = select(LeaveApplication).where(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )
    
    if application.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending applications can be rejected"
        )
    
    application.status = "rejected"
    application.approved_by_id = current_user.id
    application.approved_date = datetime.utcnow()
    application.approval_remarks = approval_remarks
    
    await db.commit()
    
    return {"message": "Leave application rejected successfully"}

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

# Dashboard APIs
@router.get("/dashboard", response_model=HRDashboard)
async def get_hr_dashboard(
    auth: tuple = Depends(require_access("hr", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get HR dashboard summary"""

    current_user, org_id = auth
    
    # Total employees
    stmt = select(func.count()).select_from(EmployeeProfile).where(
        EmployeeProfile.organization_id == org_id
    )
    result = await db.execute(stmt)
    total_employees = result.scalar_one()
    
    # Active employees
    stmt = select(func.count()).select_from(EmployeeProfile).where(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employment_status == "active"
        )
    )
    result = await db.execute(stmt)
    active_employees = result.scalar_one()
    
    # Employees on leave today
    today = date.today()
    stmt = select(func.count()).select_from(LeaveApplication).where(
        and_(
            LeaveApplication.organization_id == org_id,
            LeaveApplication.status == "approved",
            LeaveApplication.start_date <= today,
            LeaveApplication.end_date >= today
        )
    )
    result = await db.execute(stmt)
    employees_on_leave = result.scalar_one()
    
    # Pending leave approvals
    stmt = select(func.count()).select_from(LeaveApplication).where(
        and_(
            LeaveApplication.organization_id == org_id,
            LeaveApplication.status == "pending"
        )
    )
    result = await db.execute(stmt)
    pending_leave_approvals = result.scalar_one()
    
    # Upcoming performance reviews (next 30 days)
    next_month = today + timedelta(days=30)
    stmt = select(func.count()).select_from(PerformanceReview).where(
        and_(
            PerformanceReview.organization_id == org_id,
            PerformanceReview.status.in_(["draft", "submitted"]),
            PerformanceReview.review_period_end.between(today, next_month)
        )
    )
    result = await db.execute(stmt)
    upcoming_performance_reviews = result.scalar_one()
    
    # Recent joiners (last 30 days)
    last_month = today - timedelta(days=30)
    stmt = select(func.count()).select_from(EmployeeProfile).where(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.hire_date >= last_month
        )
    )
    result = await db.execute(stmt)
    recent_joiners = result.scalar_one()
    
    # Employees in probation
    stmt = select(func.count()).select_from(EmployeeProfile).where(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employment_status == "active",
            EmployeeProfile.confirmation_date.is_(None),
            EmployeeProfile.hire_date.isnot(None)
        )
    )
    result = await db.execute(stmt)
    employees_in_probation = result.scalar_one()
    
    # Calculate average attendance rate for current month
    current_month = today.replace(day=1)
    stmt = select(func.avg(AttendanceRecord.total_hours)).where(
        and_(
            AttendanceRecord.organization_id == org_id,
            AttendanceRecord.attendance_date >= current_month,
            AttendanceRecord.attendance_status == "present"
        )
    )
    result = await db.execute(stmt)
    average_attendance_rate = result.scalar_one() or None
    
    return HRDashboard(
        total_employees=total_employees,
        active_employees=active_employees,
        employees_on_leave=employees_on_leave,
        pending_leave_approvals=pending_leave_approvals,
        upcoming_performance_reviews=upcoming_performance_reviews,
        recent_joiners=recent_joiners,
        employees_in_probation=employees_in_probation,
        average_attendance_rate=average_attendance_rate
    )