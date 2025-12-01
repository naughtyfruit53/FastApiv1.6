# app/api/v1/hr.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.hr_models import (
    EmployeeProfile, AttendanceRecord, LeaveType, 
    LeaveApplication, PerformanceReview,
    Department, Position, WorkShift, HolidayCalendar
)
from app.schemas.hr_schemas import (
    EmployeeProfileCreate, EmployeeProfileUpdate, EmployeeProfileResponse,
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordResponse,
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse,
    LeaveApplicationCreate, LeaveApplicationUpdate, LeaveApplicationResponse,
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewResponse,
    HRDashboard, EmployeeDashboard, AttendanceSummary,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    PositionCreate, PositionUpdate, PositionResponse,
    WorkShiftCreate, WorkShiftUpdate, WorkShiftResponse,
    HolidayCalendarCreate, HolidayCalendarUpdate, HolidayCalendarResponse
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


# ============================================================================
# Department Management
# ============================================================================

@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new department"""
    current_user, org_id = auth
    
    # Check if department code is unique
    stmt = select(Department).where(
        and_(
            Department.organization_id == org_id,
            Department.code == department_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Department code already exists")
    
    department = Department(
        **department_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(department)
    await db.commit()
    await db.refresh(department)
    
    return department


@router.get("/departments")
async def get_departments(
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all departments"""
    
    current_user, org_id = auth
    
    stmt = select(Department).where(Department.organization_id == org_id)
    
    if is_active is not None:
        stmt = stmt.where(Department.is_active == is_active)
    
    stmt = stmt.order_by(Department.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/departments/{department_id}")
async def get_department(
    department_id: int,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get department by ID"""
    
    current_user, org_id = auth
    
    stmt = select(Department).where(
        and_(
            Department.id == department_id,
            Department.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return department


@router.put("/departments/{department_id}")
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update department"""
    
    current_user, org_id = auth
    
    stmt = select(Department).where(
        and_(
            Department.id == department_id,
            Department.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    for field, value in department_data.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    
    await db.commit()
    await db.refresh(department)
    
    return department


# ============================================================================
# Position Management
# ============================================================================

@router.post("/positions")
async def create_position(
    position_data: PositionCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new position"""
    
    current_user, org_id = auth
    
    # Check if position code is unique
    stmt = select(Position).where(
        and_(
            Position.organization_id == org_id,
            Position.code == position_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Position code already exists")
    
    position = Position(
        **position_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(position)
    await db.commit()
    await db.refresh(position)
    
    return position


@router.get("/positions")
async def get_positions(
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all positions"""
    
    current_user, org_id = auth
    
    stmt = select(Position).where(Position.organization_id == org_id)
    
    if department_id:
        stmt = stmt.where(Position.department_id == department_id)
    
    if is_active is not None:
        stmt = stmt.where(Position.is_active == is_active)
    
    stmt = stmt.order_by(Position.title)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/positions/{position_id}")
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update position"""
    
    current_user, org_id = auth
    
    stmt = select(Position).where(
        and_(
            Position.id == position_id,
            Position.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    position = result.scalar_one_or_none()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    for field, value in position_data.model_dump(exclude_unset=True).items():
        setattr(position, field, value)
    
    await db.commit()
    await db.refresh(position)
    
    return position


# ============================================================================
# Work Shift Management
# ============================================================================

@router.post("/shifts")
async def create_work_shift(
    shift_data: WorkShiftCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new work shift"""
    
    current_user, org_id = auth
    
    # Check if shift code is unique
    stmt = select(WorkShift).where(
        and_(
            WorkShift.organization_id == org_id,
            WorkShift.code == shift_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Shift code already exists")
    
    shift = WorkShift(
        **shift_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    
    return shift


@router.get("/shifts")
async def get_work_shifts(
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all work shifts"""
    
    current_user, org_id = auth
    
    stmt = select(WorkShift).where(WorkShift.organization_id == org_id)
    
    if is_active is not None:
        stmt = stmt.where(WorkShift.is_active == is_active)
    
    stmt = stmt.order_by(WorkShift.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/shifts/{shift_id}")
async def update_work_shift(
    shift_id: int,
    shift_data: WorkShiftUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update work shift"""
    
    current_user, org_id = auth
    
    stmt = select(WorkShift).where(
        and_(
            WorkShift.id == shift_id,
            WorkShift.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    shift = result.scalar_one_or_none()
    
    if not shift:
        raise HTTPException(status_code=404, detail="Work shift not found")
    
    for field, value in shift_data.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    
    await db.commit()
    await db.refresh(shift)
    
    return shift


# ============================================================================
# Holiday Calendar Management
# ============================================================================

@router.post("/holidays")
async def create_holiday(
    holiday_data: HolidayCalendarCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new holiday"""
    
    current_user, org_id = auth
    
    # Check if holiday already exists for this date
    stmt = select(HolidayCalendar).where(
        and_(
            HolidayCalendar.organization_id == org_id,
            HolidayCalendar.holiday_date == holiday_data.holiday_date
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Holiday already exists for this date")
    
    holiday = HolidayCalendar(
        **holiday_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)
    
    return holiday


@router.get("/holidays")
async def get_holidays(
    year: Optional[int] = Query(None),
    holiday_type: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all holidays"""
    
    current_user, org_id = auth
    
    stmt = select(HolidayCalendar).where(HolidayCalendar.organization_id == org_id)
    
    if year:
        stmt = stmt.where(HolidayCalendar.year == year)
    
    if holiday_type:
        stmt = stmt.where(HolidayCalendar.holiday_type == holiday_type)
    
    stmt = stmt.order_by(HolidayCalendar.holiday_date)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/holidays/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    holiday_data: HolidayCalendarUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update holiday"""
    
    current_user, org_id = auth
    
    stmt = select(HolidayCalendar).where(
        and_(
            HolidayCalendar.id == holiday_id,
            HolidayCalendar.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    holiday = result.scalar_one_or_none()
    
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    for field, value in holiday_data.model_dump(exclude_unset=True).items():
        setattr(holiday, field, value)
    
    await db.commit()
    await db.refresh(holiday)
    
    return holiday


@router.delete("/holidays/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    auth: tuple = Depends(require_access("hr", "delete")),
    db: AsyncSession = Depends(get_db)
):
    """Delete a holiday"""
    
    current_user, org_id = auth
    
    stmt = select(HolidayCalendar).where(
        and_(
            HolidayCalendar.id == holiday_id,
            HolidayCalendar.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    holiday = result.scalar_one_or_none()
    
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    await db.delete(holiday)
    await db.commit()
    
    return {"message": "Holiday deleted successfully"}


# ============================================================================
# Clock In/Out Endpoints
# ============================================================================

@router.post("/attendance/clock-in")
async def clock_in(
    employee_id: int,
    work_type: str = Query(default="office"),
    location: Optional[str] = Query(None),
    device: Optional[str] = Query(None),
    remarks: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Clock in an employee for attendance"""
    current_user, org_id = auth
    today = date.today()
    now = datetime.now(timezone.utc).time()
    
    # Check if attendance record already exists for today
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.organization_id == org_id,
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date == today
        )
    )
    result = await db.execute(stmt)
    existing_record = result.scalar_one_or_none()
    
    if existing_record and existing_record.check_in_time:
        raise HTTPException(
            status_code=400,
            detail="Employee has already clocked in for today"
        )
    
    if existing_record:
        # Update existing record
        existing_record.check_in_time = now
        existing_record.work_type = work_type
        existing_record.check_in_location = location
        existing_record.check_in_device = device
        existing_record.employee_remarks = remarks
        existing_record.attendance_status = "present"
        await db.commit()
        await db.refresh(existing_record)
        return existing_record
    else:
        # Create new record
        attendance_record = AttendanceRecord(
            organization_id=org_id,
            employee_id=employee_id,
            attendance_date=today,
            check_in_time=now,
            work_type=work_type,
            check_in_location=location,
            check_in_device=device,
            employee_remarks=remarks,
            attendance_status="present"
        )
        db.add(attendance_record)
        await db.commit()
        await db.refresh(attendance_record)
        return attendance_record


@router.post("/attendance/clock-out")
async def clock_out(
    employee_id: int,
    location: Optional[str] = Query(None),
    remarks: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Clock out an employee for attendance"""
    current_user, org_id = auth
    today = date.today()
    now = datetime.now(timezone.utc).time()
    
    # Find today's attendance record
    stmt = select(AttendanceRecord).where(
        and_(
            AttendanceRecord.organization_id == org_id,
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date == today
        )
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail="No clock-in record found for today"
        )
    
    if not record.check_in_time:
        raise HTTPException(
            status_code=400,
            detail="Employee has not clocked in yet"
        )
    
    if record.check_out_time:
        raise HTTPException(
            status_code=400,
            detail="Employee has already clocked out for today"
        )
    
    record.check_out_time = now
    record.check_out_location = location
    
    # Calculate total hours
    check_in_datetime = datetime.combine(today, record.check_in_time)
    check_out_datetime = datetime.combine(today, now)
    total_seconds = (check_out_datetime - check_in_datetime).total_seconds()
    total_hours = Decimal(str(total_seconds / 3600))
    
    # Subtract break hours if applicable - use explicit None check
    break_hours = record.break_hours if record.break_hours is not None else Decimal('0')
    record.total_hours = total_hours - break_hours
    
    if remarks:
        existing_remarks = record.employee_remarks or ""
        record.employee_remarks = f"{existing_remarks} | Clock-out: {remarks}" if existing_remarks else remarks
    
    await db.commit()
    await db.refresh(record)
    
    return record


# ============================================================================
# HR Phase 2: Attendance Policies, Leave Balances, Timesheets
# ============================================================================

from app.models.hr_models import (
    AttendancePolicy, LeaveBalance, Timesheet,
    PayrollArrear, StatutoryDeduction, BankPaymentExport, PayrollApproval,
    HRAnalyticsSnapshot, PositionBudget, EmployeeTransfer, IntegrationAdapter
)
from app.schemas.hr_schemas import (
    AttendancePolicyCreate, AttendancePolicyUpdate, AttendancePolicyResponse,
    LeaveBalanceCreate, LeaveBalanceUpdate, LeaveBalanceResponse,
    TimesheetCreate, TimesheetUpdate, TimesheetResponse,
    PayrollArrearCreate, PayrollArrearUpdate, PayrollArrearResponse,
    StatutoryDeductionCreate, StatutoryDeductionUpdate, StatutoryDeductionResponse,
    BankPaymentExportCreate, BankPaymentExportResponse,
    PayrollApprovalCreate, PayrollApprovalUpdate, PayrollApprovalResponse,
    HRAnalyticsSnapshotResponse,
    PositionBudgetCreate, PositionBudgetUpdate, PositionBudgetResponse,
    EmployeeTransferCreate, EmployeeTransferUpdate, EmployeeTransferResponse,
    IntegrationAdapterCreate, IntegrationAdapterUpdate, IntegrationAdapterResponse,
    PayrollExportRequest, AttendanceExportRequest, LeaveExportRequest, ExportResult
)


# ============================================================================
# Attendance Policy Management
# ============================================================================

@router.post("/attendance-policies", response_model=AttendancePolicyResponse)
async def create_attendance_policy(
    policy_data: AttendancePolicyCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new attendance policy"""
    current_user, org_id = auth
    
    # Check for unique code
    stmt = select(AttendancePolicy).where(
        and_(
            AttendancePolicy.organization_id == org_id,
            AttendancePolicy.code == policy_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Attendance policy code already exists")
    
    policy = AttendancePolicy(
        **policy_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    
    return policy


@router.get("/attendance-policies", response_model=List[AttendancePolicyResponse])
async def get_attendance_policies(
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all attendance policies"""
    current_user, org_id = auth
    
    stmt = select(AttendancePolicy).where(AttendancePolicy.organization_id == org_id)
    
    if is_active is not None:
        stmt = stmt.where(AttendancePolicy.is_active == is_active)
    
    stmt = stmt.order_by(AttendancePolicy.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/attendance-policies/{policy_id}", response_model=AttendancePolicyResponse)
async def update_attendance_policy(
    policy_id: int,
    policy_data: AttendancePolicyUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update attendance policy"""
    current_user, org_id = auth
    
    stmt = select(AttendancePolicy).where(
        and_(
            AttendancePolicy.id == policy_id,
            AttendancePolicy.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    policy = result.scalar_one_or_none()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Attendance policy not found")
    
    for field, value in policy_data.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    
    await db.commit()
    await db.refresh(policy)
    
    return policy


# ============================================================================
# Leave Balance Management
# ============================================================================

@router.get("/leave-balances", response_model=List[LeaveBalanceResponse])
async def get_leave_balances(
    employee_id: Optional[int] = Query(None),
    leave_type_id: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get leave balances for employees"""
    current_user, org_id = auth
    
    stmt = select(LeaveBalance).where(LeaveBalance.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(LeaveBalance.employee_id == employee_id)
    if leave_type_id:
        stmt = stmt.where(LeaveBalance.leave_type_id == leave_type_id)
    if year:
        stmt = stmt.where(LeaveBalance.year == year)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/leave-balances", response_model=LeaveBalanceResponse)
async def create_leave_balance(
    balance_data: LeaveBalanceCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create or update leave balance for an employee"""
    current_user, org_id = auth
    
    # Check if balance already exists
    stmt = select(LeaveBalance).where(
        and_(
            LeaveBalance.organization_id == org_id,
            LeaveBalance.employee_id == balance_data.employee_id,
            LeaveBalance.leave_type_id == balance_data.leave_type_id,
            LeaveBalance.year == balance_data.year
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing balance
        for field, value in balance_data.model_dump(exclude={'employee_id', 'leave_type_id', 'year'}).items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing
    
    balance = LeaveBalance(
        **balance_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(balance)
    await db.commit()
    await db.refresh(balance)
    
    return balance


# ============================================================================
# Timesheet Management
# ============================================================================

@router.get("/timesheets", response_model=List[TimesheetResponse])
async def get_timesheets(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get timesheets"""
    current_user, org_id = auth
    
    stmt = select(Timesheet).where(Timesheet.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(Timesheet.employee_id == employee_id)
    if status:
        stmt = stmt.where(Timesheet.status == status)
    
    stmt = stmt.order_by(desc(Timesheet.period_start)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/timesheets", response_model=TimesheetResponse)
async def create_timesheet(
    timesheet_data: TimesheetCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new timesheet"""
    current_user, org_id = auth
    
    timesheet = Timesheet(
        **timesheet_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(timesheet)
    await db.commit()
    await db.refresh(timesheet)
    
    return timesheet


@router.put("/timesheets/{timesheet_id}/submit")
async def submit_timesheet(
    timesheet_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Submit a timesheet for approval"""
    current_user, org_id = auth
    
    stmt = select(Timesheet).where(
        and_(
            Timesheet.id == timesheet_id,
            Timesheet.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft timesheets can be submitted")
    
    timesheet.status = "submitted"
    timesheet.submitted_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Timesheet submitted successfully"}


@router.put("/timesheets/{timesheet_id}/approve")
async def approve_timesheet(
    timesheet_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a submitted timesheet"""
    current_user, org_id = auth
    
    stmt = select(Timesheet).where(
        and_(
            Timesheet.id == timesheet_id,
            Timesheet.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted timesheets can be approved")
    
    timesheet.status = "approved"
    timesheet.approved_by_id = current_user.id
    timesheet.approved_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Timesheet approved successfully"}


# ============================================================================
# Statutory Deductions
# ============================================================================

@router.get("/statutory-deductions", response_model=List[StatutoryDeductionResponse])
async def get_statutory_deductions(
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get all statutory deductions"""
    current_user, org_id = auth
    
    stmt = select(StatutoryDeduction).where(StatutoryDeduction.organization_id == org_id)
    
    if is_active is not None:
        stmt = stmt.where(StatutoryDeduction.is_active == is_active)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/statutory-deductions", response_model=StatutoryDeductionResponse)
async def create_statutory_deduction(
    deduction_data: StatutoryDeductionCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new statutory deduction configuration"""
    current_user, org_id = auth
    
    # Check for unique code
    stmt = select(StatutoryDeduction).where(
        and_(
            StatutoryDeduction.organization_id == org_id,
            StatutoryDeduction.code == deduction_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Statutory deduction code already exists")
    
    deduction = StatutoryDeduction(
        **deduction_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(deduction)
    await db.commit()
    await db.refresh(deduction)
    
    return deduction


@router.put("/statutory-deductions/{deduction_id}", response_model=StatutoryDeductionResponse)
async def update_statutory_deduction(
    deduction_id: int,
    deduction_data: StatutoryDeductionUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update statutory deduction configuration"""
    current_user, org_id = auth
    
    stmt = select(StatutoryDeduction).where(
        and_(
            StatutoryDeduction.id == deduction_id,
            StatutoryDeduction.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    deduction = result.scalar_one_or_none()
    
    if not deduction:
        raise HTTPException(status_code=404, detail="Statutory deduction not found")
    
    for field, value in deduction_data.model_dump(exclude_unset=True).items():
        setattr(deduction, field, value)
    
    await db.commit()
    await db.refresh(deduction)
    
    return deduction


# ============================================================================
# Payroll Arrears
# ============================================================================

@router.get("/payroll-arrears", response_model=List[PayrollArrearResponse])
async def get_payroll_arrears(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll arrears"""
    current_user, org_id = auth
    
    stmt = select(PayrollArrear).where(PayrollArrear.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(PayrollArrear.employee_id == employee_id)
    if status:
        stmt = stmt.where(PayrollArrear.status == status)
    
    stmt = stmt.order_by(desc(PayrollArrear.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/payroll-arrears", response_model=PayrollArrearResponse)
async def create_payroll_arrear(
    arrear_data: PayrollArrearCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payroll arrear"""
    current_user, org_id = auth
    
    arrear = PayrollArrear(
        **arrear_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(arrear)
    await db.commit()
    await db.refresh(arrear)
    
    return arrear


@router.put("/payroll-arrears/{arrear_id}/approve")
async def approve_payroll_arrear(
    arrear_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a payroll arrear"""
    current_user, org_id = auth
    
    stmt = select(PayrollArrear).where(
        and_(
            PayrollArrear.id == arrear_id,
            PayrollArrear.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    arrear = result.scalar_one_or_none()
    
    if not arrear:
        raise HTTPException(status_code=404, detail="Payroll arrear not found")
    
    if arrear.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending arrears can be approved")
    
    arrear.status = "approved"
    arrear.approved_by_id = current_user.id
    arrear.approved_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Payroll arrear approved successfully"}


# ============================================================================
# Payroll Approval Workflow
# ============================================================================

@router.get("/payroll-approvals", response_model=List[PayrollApprovalResponse])
async def get_payroll_approvals(
    payroll_period_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll approvals"""
    current_user, org_id = auth
    
    stmt = select(PayrollApproval).where(PayrollApproval.organization_id == org_id)
    
    if payroll_period_id:
        stmt = stmt.where(PayrollApproval.payroll_period_id == payroll_period_id)
    if status:
        stmt = stmt.where(PayrollApproval.status == status)
    
    stmt = stmt.order_by(PayrollApproval.approval_level)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/payroll-approvals", response_model=PayrollApprovalResponse)
async def create_payroll_approval(
    approval_data: PayrollApprovalCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payroll approval request"""
    current_user, org_id = auth
    
    approval = PayrollApproval(
        **approval_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(approval)
    await db.commit()
    await db.refresh(approval)
    
    return approval


@router.put("/payroll-approvals/{approval_id}/approve")
async def approve_payroll(
    approval_id: int,
    comments: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve a payroll approval request"""
    current_user, org_id = auth
    
    stmt = select(PayrollApproval).where(
        and_(
            PayrollApproval.id == approval_id,
            PayrollApproval.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    approval = result.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Payroll approval not found")
    
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending approvals can be approved")
    
    approval.status = "approved"
    approval.approved_by_id = current_user.id
    approval.approved_at = datetime.now(timezone.utc)
    if comments:
        approval.comments = comments
    
    await db.commit()
    
    return {"message": "Payroll approval completed successfully"}


# ============================================================================
# Phase 4 Scaffolding: Analytics, Position Budgeting, Transfers
# (Feature-flagged endpoints)
# ============================================================================

@router.get("/analytics/snapshots", response_model=List[HRAnalyticsSnapshotResponse])
async def get_hr_analytics_snapshots(
    snapshot_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get HR analytics snapshots (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(HRAnalyticsSnapshot).where(HRAnalyticsSnapshot.organization_id == org_id)
    
    if snapshot_type:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_type == snapshot_type)
    if start_date:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_date >= start_date)
    if end_date:
        stmt = stmt.where(HRAnalyticsSnapshot.snapshot_date <= end_date)
    
    stmt = stmt.order_by(desc(HRAnalyticsSnapshot.snapshot_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/position-budgets", response_model=List[PositionBudgetResponse])
async def get_position_budgets(
    fiscal_year: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get position budgets (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(PositionBudget).where(PositionBudget.organization_id == org_id)
    
    if fiscal_year:
        stmt = stmt.where(PositionBudget.fiscal_year == fiscal_year)
    if department_id:
        stmt = stmt.where(PositionBudget.department_id == department_id)
    if status:
        stmt = stmt.where(PositionBudget.status == status)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/position-budgets", response_model=PositionBudgetResponse)
async def create_position_budget(
    budget_data: PositionBudgetCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new position budget (Feature-flagged)"""
    current_user, org_id = auth
    
    budget = PositionBudget(
        **budget_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    
    return budget


@router.get("/employee-transfers", response_model=List[EmployeeTransferResponse])
async def get_employee_transfers(
    employee_id: Optional[int] = Query(None),
    transfer_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get employee transfers (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(EmployeeTransfer).where(EmployeeTransfer.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(EmployeeTransfer.employee_id == employee_id)
    if transfer_type:
        stmt = stmt.where(EmployeeTransfer.transfer_type == transfer_type)
    if status:
        stmt = stmt.where(EmployeeTransfer.status == status)
    
    stmt = stmt.order_by(desc(EmployeeTransfer.effective_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/employee-transfers", response_model=EmployeeTransferResponse)
async def create_employee_transfer(
    transfer_data: EmployeeTransferCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new employee transfer (Feature-flagged)"""
    current_user, org_id = auth
    
    transfer = EmployeeTransfer(
        **transfer_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    
    return transfer


@router.put("/employee-transfers/{transfer_id}/approve")
async def approve_employee_transfer(
    transfer_id: int,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve an employee transfer (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(EmployeeTransfer).where(
        and_(
            EmployeeTransfer.id == transfer_id,
            EmployeeTransfer.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    transfer = result.scalar_one_or_none()
    
    if not transfer:
        raise HTTPException(status_code=404, detail="Employee transfer not found")
    
    if transfer.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending transfers can be approved")
    
    transfer.status = "approved"
    transfer.approved_by_id = current_user.id
    transfer.approved_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": "Employee transfer approved successfully"}


# ============================================================================
# Integration Adapters (Feature-flagged)
# ============================================================================

@router.get("/integration-adapters", response_model=List[IntegrationAdapterResponse])
async def get_integration_adapters(
    adapter_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get integration adapters (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(IntegrationAdapter).where(IntegrationAdapter.organization_id == org_id)
    
    if adapter_type:
        stmt = stmt.where(IntegrationAdapter.adapter_type == adapter_type)
    if is_active is not None:
        stmt = stmt.where(IntegrationAdapter.is_active == is_active)
    
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/integration-adapters", response_model=IntegrationAdapterResponse)
async def create_integration_adapter(
    adapter_data: IntegrationAdapterCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new integration adapter (Feature-flagged)"""
    current_user, org_id = auth
    
    # Check for unique adapter type + provider combination
    stmt = select(IntegrationAdapter).where(
        and_(
            IntegrationAdapter.organization_id == org_id,
            IntegrationAdapter.adapter_type == adapter_data.adapter_type,
            IntegrationAdapter.provider == adapter_data.provider
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Integration adapter already exists for this type and provider")
    
    adapter = IntegrationAdapter(
        **adapter_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(adapter)
    await db.commit()
    await db.refresh(adapter)
    
    return adapter


@router.put("/integration-adapters/{adapter_id}", response_model=IntegrationAdapterResponse)
async def update_integration_adapter(
    adapter_id: int,
    adapter_data: IntegrationAdapterUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update integration adapter (Feature-flagged)"""
    current_user, org_id = auth
    
    stmt = select(IntegrationAdapter).where(
        and_(
            IntegrationAdapter.id == adapter_id,
            IntegrationAdapter.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    adapter = result.scalar_one_or_none()
    
    if not adapter:
        raise HTTPException(status_code=404, detail="Integration adapter not found")
    
    for field, value in adapter_data.model_dump(exclude_unset=True).items():
        setattr(adapter, field, value)
    
    await db.commit()
    await db.refresh(adapter)
    
    return adapter


# ============================================================================
# Export Endpoints (CSV/JSON) - Scaffolding for future implementation
# ============================================================================

@router.post("/export/payroll", response_model=ExportResult)
async def export_payroll_data(
    export_request: PayrollExportRequest,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Export payroll data to CSV/JSON format.
    
    NOTE: This is a scaffolding endpoint. Full implementation will include:
    - Query payroll data from PayrollPeriod and Payslip tables
    - Generate CSV/JSON/XLSX based on export_format
    - Store file and return download URL or stream content
    
    Current behavior: Returns success with placeholder values.
    """
    current_user, org_id = auth
    
    # TODO: Implement actual export logic
    # 1. Query payroll data for the period
    # 2. Format data according to export_format
    # 3. Generate file and store/return
    return ExportResult(
        success=True,
        file_name=f"payroll_export_{export_request.payroll_period_id}.{export_request.export_format.format}",
        record_count=0,
        file_size_bytes=0
    )


@router.post("/export/attendance", response_model=ExportResult)
async def export_attendance_data(
    export_request: AttendanceExportRequest,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Export attendance data to CSV/JSON format.
    
    NOTE: This is a scaffolding endpoint. Full implementation will include:
    - Query AttendanceRecord table with date range and filters
    - Calculate overtime based on AttendancePolicy
    - Generate CSV/JSON/XLSX based on export_format
    
    Current behavior: Returns success with placeholder values.
    """
    current_user, org_id = auth
    
    # TODO: Implement actual export logic
    return ExportResult(
        success=True,
        file_name=f"attendance_export_{export_request.start_date}_{export_request.end_date}.{export_request.export_format.format}",
        record_count=0,
        file_size_bytes=0
    )


@router.post("/export/leave", response_model=ExportResult)
async def export_leave_data(
    export_request: LeaveExportRequest,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Export leave data to CSV/JSON format.
    
    NOTE: This is a scaffolding endpoint. Full implementation will include:
    - Query LeaveApplication table with date range and filters
    - Include leave type names and balance information
    - Generate CSV/JSON/XLSX based on export_format
    
    Current behavior: Returns success with placeholder values.
    """
    current_user, org_id = auth
    
    # TODO: Implement actual export logic
    return ExportResult(
        success=True,
        file_name=f"leave_export_{export_request.start_date}_{export_request.end_date}.{export_request.export_format.format}",
        record_count=0,
        file_size_bytes=0
    )