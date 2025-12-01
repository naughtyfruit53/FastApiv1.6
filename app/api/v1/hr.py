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


# ============================================================================
# HR Phase 3: Performance Management (Goals/OKRs, Review Cycles, 360 Feedback)
# ============================================================================

from app.models.hr_models import (
    Goal, ReviewCycle, FeedbackForm,
    JobPosting, Candidate, Interview, JobOffer, OnboardingTask,
    PolicyDocument, PolicyAcknowledgment, TrainingProgram, TrainingAssignment,
    ComplianceAuditExport
)
from app.schemas.hr_schemas import (
    GoalCreate, GoalUpdate, GoalResponse,
    ReviewCycleCreate, ReviewCycleUpdate, ReviewCycleResponse,
    FeedbackFormCreate, FeedbackFormUpdate, FeedbackFormResponse,
    JobPostingCreate, JobPostingUpdate, JobPostingResponse,
    CandidateCreate, CandidateUpdate, CandidateResponse,
    InterviewCreate, InterviewUpdate, InterviewResponse,
    JobOfferCreate, JobOfferUpdate, JobOfferResponse,
    OnboardingTaskCreate, OnboardingTaskUpdate, OnboardingTaskResponse,
    PolicyDocumentCreate, PolicyDocumentUpdate, PolicyDocumentResponse,
    PolicyAcknowledgmentCreate, PolicyAcknowledgmentUpdate, PolicyAcknowledgmentResponse,
    TrainingProgramCreate, TrainingProgramUpdate, TrainingProgramResponse,
    TrainingAssignmentCreate, TrainingAssignmentUpdate, TrainingAssignmentResponse,
    ComplianceAuditExportCreate, ComplianceAuditExportResponse
)


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
        stmt = stmt.where(FeedbackForm.reviewee_id == reviewee_id)
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


# ============================================================================
# Recruitment Module
# ============================================================================

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


# Onboarding Tasks
@router.post("/onboarding-tasks", response_model=OnboardingTaskResponse)
async def create_onboarding_task(
    task_data: OnboardingTaskCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create an onboarding task"""
    current_user, org_id = auth
    
    task = OnboardingTask(
        **task_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task


@router.get("/onboarding-tasks", response_model=List[OnboardingTaskResponse])
async def get_onboarding_tasks(
    employee_id: Optional[int] = Query(None),
    is_template: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get onboarding tasks"""
    current_user, org_id = auth
    
    stmt = select(OnboardingTask).where(OnboardingTask.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(OnboardingTask.employee_id == employee_id)
    if is_template is not None:
        stmt = stmt.where(OnboardingTask.is_template == is_template)
    if status:
        stmt = stmt.where(OnboardingTask.status == status)
    if category:
        stmt = stmt.where(OnboardingTask.category == category)
    
    stmt = stmt.order_by(OnboardingTask.sequence_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/onboarding-tasks/{task_id}", response_model=OnboardingTaskResponse)
async def update_onboarding_task(
    task_id: int,
    task_data: OnboardingTaskUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update an onboarding task"""
    current_user, org_id = auth
    
    stmt = select(OnboardingTask).where(
        and_(
            OnboardingTask.id == task_id,
            OnboardingTask.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Onboarding task not found")
    
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    return task


# ============================================================================
# Compliance & Policies Module
# ============================================================================

# Policy Documents
@router.post("/policy-documents", response_model=PolicyDocumentResponse)
async def create_policy_document(
    document_data: PolicyDocumentCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a policy document"""
    current_user, org_id = auth
    
    # Check for unique code + version
    stmt = select(PolicyDocument).where(
        and_(
            PolicyDocument.organization_id == org_id,
            PolicyDocument.code == document_data.code,
            PolicyDocument.version == document_data.version
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Policy with this code and version already exists")
    
    document = PolicyDocument(
        **document_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return document


@router.get("/policy-documents", response_model=List[PolicyDocumentResponse])
async def get_policy_documents(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get policy documents"""
    current_user, org_id = auth
    
    stmt = select(PolicyDocument).where(PolicyDocument.organization_id == org_id)
    
    if category:
        stmt = stmt.where(PolicyDocument.category == category)
    if status:
        stmt = stmt.where(PolicyDocument.status == status)
    if is_active is not None:
        stmt = stmt.where(PolicyDocument.is_active == is_active)
    
    stmt = stmt.order_by(PolicyDocument.code, desc(PolicyDocument.version)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/policy-documents/{document_id}", response_model=PolicyDocumentResponse)
async def update_policy_document(
    document_id: int,
    document_data: PolicyDocumentUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a policy document"""
    current_user, org_id = auth
    
    stmt = select(PolicyDocument).where(
        and_(
            PolicyDocument.id == document_id,
            PolicyDocument.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Policy document not found")
    
    for field, value in document_data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    
    # Set published timestamp
    if document_data.status == "published" and not document.published_at:
        document.published_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(document)
    
    return document


# Policy Acknowledgments
@router.post("/policy-acknowledgments", response_model=PolicyAcknowledgmentResponse)
async def create_policy_acknowledgment(
    ack_data: PolicyAcknowledgmentCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a policy acknowledgment request"""
    current_user, org_id = auth
    
    ack = PolicyAcknowledgment(
        **ack_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(ack)
    await db.commit()
    await db.refresh(ack)
    
    return ack


@router.get("/policy-acknowledgments", response_model=List[PolicyAcknowledgmentResponse])
async def get_policy_acknowledgments(
    policy_document_id: Optional[int] = Query(None),
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get policy acknowledgments"""
    current_user, org_id = auth
    
    stmt = select(PolicyAcknowledgment).where(PolicyAcknowledgment.organization_id == org_id)
    
    if policy_document_id:
        stmt = stmt.where(PolicyAcknowledgment.policy_document_id == policy_document_id)
    if employee_id:
        stmt = stmt.where(PolicyAcknowledgment.employee_id == employee_id)
    if status:
        stmt = stmt.where(PolicyAcknowledgment.status == status)
    
    stmt = stmt.order_by(desc(PolicyAcknowledgment.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/policy-acknowledgments/{ack_id}/acknowledge")
async def acknowledge_policy(
    ack_id: int,
    ip_address: Optional[str] = Query(None),
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge a policy document"""
    current_user, org_id = auth
    
    stmt = select(PolicyAcknowledgment).where(
        and_(
            PolicyAcknowledgment.id == ack_id,
            PolicyAcknowledgment.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    ack = result.scalar_one_or_none()
    
    if not ack:
        raise HTTPException(status_code=404, detail="Acknowledgment record not found")
    
    ack.status = "acknowledged"
    ack.acknowledged_at = datetime.now(timezone.utc)
    if ip_address:
        ack.ip_address = ip_address
    
    await db.commit()
    
    return {"message": "Policy acknowledged successfully"}


# Training Programs
@router.post("/training-programs", response_model=TrainingProgramResponse)
async def create_training_program(
    program_data: TrainingProgramCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a training program"""
    current_user, org_id = auth
    
    # Check for unique code
    stmt = select(TrainingProgram).where(
        and_(
            TrainingProgram.organization_id == org_id,
            TrainingProgram.code == program_data.code
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Training program code already exists")
    
    program = TrainingProgram(
        **program_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(program)
    await db.commit()
    await db.refresh(program)
    
    return program


@router.get("/training-programs", response_model=List[TrainingProgramResponse])
async def get_training_programs(
    category: Optional[str] = Query(None),
    training_type: Optional[str] = Query(None),
    is_mandatory: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get training programs"""
    current_user, org_id = auth
    
    stmt = select(TrainingProgram).where(TrainingProgram.organization_id == org_id)
    
    if category:
        stmt = stmt.where(TrainingProgram.category == category)
    if training_type:
        stmt = stmt.where(TrainingProgram.training_type == training_type)
    if is_mandatory is not None:
        stmt = stmt.where(TrainingProgram.is_mandatory == is_mandatory)
    if status:
        stmt = stmt.where(TrainingProgram.status == status)
    
    stmt = stmt.order_by(TrainingProgram.title).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/training-programs/{program_id}", response_model=TrainingProgramResponse)
async def update_training_program(
    program_id: int,
    program_data: TrainingProgramUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a training program"""
    current_user, org_id = auth
    
    stmt = select(TrainingProgram).where(
        and_(
            TrainingProgram.id == program_id,
            TrainingProgram.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Training program not found")
    
    for field, value in program_data.model_dump(exclude_unset=True).items():
        setattr(program, field, value)
    
    await db.commit()
    await db.refresh(program)
    
    return program


# Training Assignments
@router.post("/training-assignments", response_model=TrainingAssignmentResponse)
async def create_training_assignment(
    assignment_data: TrainingAssignmentCreate,
    auth: tuple = Depends(require_access("hr", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a training assignment"""
    current_user, org_id = auth
    
    # Check for existing assignment
    stmt = select(TrainingAssignment).where(
        and_(
            TrainingAssignment.organization_id == org_id,
            TrainingAssignment.training_program_id == assignment_data.training_program_id,
            TrainingAssignment.employee_id == assignment_data.employee_id
        )
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Training already assigned to this employee")
    
    assignment = TrainingAssignment(
        **assignment_data.model_dump(),
        organization_id=org_id,
        assigned_by_id=assignment_data.assigned_by_id or current_user.id
    )
    
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    
    return assignment


@router.get("/training-assignments", response_model=List[TrainingAssignmentResponse])
async def get_training_assignments(
    employee_id: Optional[int] = Query(None),
    training_program_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get training assignments"""
    current_user, org_id = auth
    
    stmt = select(TrainingAssignment).where(TrainingAssignment.organization_id == org_id)
    
    if employee_id:
        stmt = stmt.where(TrainingAssignment.employee_id == employee_id)
    if training_program_id:
        stmt = stmt.where(TrainingAssignment.training_program_id == training_program_id)
    if status:
        stmt = stmt.where(TrainingAssignment.status == status)
    
    stmt = stmt.order_by(desc(TrainingAssignment.assigned_date)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/training-assignments/{assignment_id}", response_model=TrainingAssignmentResponse)
async def update_training_assignment(
    assignment_id: int,
    assignment_data: TrainingAssignmentUpdate,
    auth: tuple = Depends(require_access("hr", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update a training assignment"""
    current_user, org_id = auth
    
    stmt = select(TrainingAssignment).where(
        and_(
            TrainingAssignment.id == assignment_id,
            TrainingAssignment.organization_id == org_id
        )
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Training assignment not found")
    
    for field, value in assignment_data.model_dump(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    # Track completion
    if assignment_data.status == "completed" and not assignment.completed_at:
        assignment.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(assignment)
    
    return assignment


# Compliance Audit Exports
@router.post("/compliance-exports", response_model=ComplianceAuditExportResponse)
async def create_compliance_export(
    export_data: ComplianceAuditExportCreate,
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Create a compliance audit export"""
    current_user, org_id = auth
    
    export = ComplianceAuditExport(
        **export_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id,
        status="pending"
    )
    
    db.add(export)
    await db.commit()
    await db.refresh(export)
    
    # TODO: Trigger async export generation
    
    return export


@router.get("/compliance-exports", response_model=List[ComplianceAuditExportResponse])
async def get_compliance_exports(
    export_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("hr", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get compliance audit exports"""
    current_user, org_id = auth
    
    stmt = select(ComplianceAuditExport).where(ComplianceAuditExport.organization_id == org_id)
    
    if export_type:
        stmt = stmt.where(ComplianceAuditExport.export_type == export_type)
    if status:
        stmt = stmt.where(ComplianceAuditExport.status == status)
    
    stmt = stmt.order_by(desc(ComplianceAuditExport.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()