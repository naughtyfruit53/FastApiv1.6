# app/api/v1/hr.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
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

router = APIRouter(prefix="/hr", tags=["Human Resources"])

# Employee Profile Management
@router.post("/employees", response_model=EmployeeProfileResponse)
async def create_employee_profile(
    employee_data: EmployeeProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new employee profile"""
    
    # Check if employee profile already exists for this user
    existing_profile = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.user_id == employee_data.user_id
        )
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user"
        )
    
    # Check if employee code is unique within organization
    existing_code = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employee_code == employee_data.employee_code
        )
    ).first()
    
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee code already exists"
        )
    
    employee_profile = EmployeeProfile(
        **employee_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by_id=current_user.id
    )
    
    db.add(employee_profile)
    db.commit()
    db.refresh(employee_profile)
    
    return employee_profile

@router.get("/employees", response_model=List[EmployeeProfileResponse])
async def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    employment_status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of employees with filtering and pagination"""
    
    query = db.query(EmployeeProfile).filter(
        EmployeeProfile.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if search:
        query = query.join(User).filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                EmployeeProfile.employee_code.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )
    
    if department:
        query = query.join(User).filter(User.department == department)
    
    if employment_status:
        query = query.filter(EmployeeProfile.employment_status == employment_status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(EmployeeProfile.created_at))
    
    employees = query.offset(skip).limit(limit).all()
    return employees

@router.get("/employees/{employee_id}", response_model=EmployeeProfileResponse)
async def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee profile by ID"""
    
    employee = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.organization_id == current_user.organization_id
        )
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return employee

@router.put("/employees/{employee_id}", response_model=EmployeeProfileResponse)
async def update_employee(
    employee_id: int,
    employee_data: EmployeeProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update employee profile"""
    
    employee = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.id == employee_id,
            EmployeeProfile.organization_id == current_user.organization_id
        )
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if employee code is unique (if being updated)
    if employee_data.employee_code and employee_data.employee_code != employee.employee_code:
        existing_code = db.query(EmployeeProfile).filter(
            and_(
                EmployeeProfile.organization_id == current_user.organization_id,
                EmployeeProfile.employee_code == employee_data.employee_code,
                EmployeeProfile.id != employee_id
            )
        ).first()
        
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee code already exists"
            )
    
    # Update fields
    for field, value in employee_data.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    employee.updated_by_id = current_user.id
    
    db.commit()
    db.refresh(employee)
    
    return employee

# Attendance Management
@router.post("/attendance", response_model=AttendanceRecordResponse)
async def create_attendance_record(
    attendance_data: AttendanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create attendance record"""
    
    # Check if attendance record already exists for this date
    existing_record = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.organization_id == current_user.organization_id,
            AttendanceRecord.employee_id == attendance_data.employee_id,
            AttendanceRecord.attendance_date == attendance_data.attendance_date
        )
    ).first()
    
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this date"
        )
    
    attendance_record = AttendanceRecord(
        **attendance_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(attendance_record)
    db.commit()
    db.refresh(attendance_record)
    
    return attendance_record

@router.get("/attendance", response_model=List[AttendanceRecordResponse])
async def get_attendance_records(
    employee_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attendance records with filtering"""
    
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if employee_id:
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    
    if start_date:
        query = query.filter(AttendanceRecord.attendance_date >= start_date)
    
    if end_date:
        query = query.filter(AttendanceRecord.attendance_date <= end_date)
    
    if status:
        query = query.filter(AttendanceRecord.attendance_status == status)
    
    # Order by date (newest first)
    query = query.order_by(desc(AttendanceRecord.attendance_date))
    
    records = query.offset(skip).limit(limit).all()
    return records

@router.put("/attendance/{attendance_id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    attendance_id: int,
    attendance_data: AttendanceRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update attendance record"""
    
    record = db.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.id == attendance_id,
            AttendanceRecord.organization_id == current_user.organization_id
        )
    ).first()
    
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
    
    db.commit()
    db.refresh(record)
    
    return record

# Leave Type Management
@router.post("/leave-types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type_data: LeaveTypeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new leave type"""
    
    # Check if leave type code is unique within organization
    existing_code = db.query(LeaveType).filter(
        and_(
            LeaveType.organization_id == current_user.organization_id,
            LeaveType.code == leave_type_data.code
        )
    ).first()
    
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type code already exists"
        )
    
    leave_type = LeaveType(
        **leave_type_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)
    
    return leave_type

@router.get("/leave-types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leave types"""
    
    query = db.query(LeaveType).filter(
        LeaveType.organization_id == current_user.organization_id
    )
    
    if is_active is not None:
        query = query.filter(LeaveType.is_active == is_active)
    
    leave_types = query.order_by(LeaveType.name).all()
    return leave_types

# Leave Application Management
@router.post("/leave-applications", response_model=LeaveApplicationResponse)
async def create_leave_application(
    leave_data: LeaveApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new leave application"""
    
    leave_application = LeaveApplication(
        **leave_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(leave_application)
    db.commit()
    db.refresh(leave_application)
    
    return leave_application

@router.get("/leave-applications", response_model=List[LeaveApplicationResponse])
async def get_leave_applications(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get leave applications with filtering"""
    
    query = db.query(LeaveApplication).filter(
        LeaveApplication.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if employee_id:
        query = query.filter(LeaveApplication.employee_id == employee_id)
    
    if status:
        query = query.filter(LeaveApplication.status == status)
    
    if start_date:
        query = query.filter(LeaveApplication.start_date >= start_date)
    
    if end_date:
        query = query.filter(LeaveApplication.end_date <= end_date)
    
    # Order by application date (newest first)
    query = query.order_by(desc(LeaveApplication.applied_date))
    
    applications = query.offset(skip).limit(limit).all()
    return applications

@router.put("/leave-applications/{application_id}/approve")
async def approve_leave_application(
    application_id: int,
    approval_remarks: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a leave application"""
    
    application = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == current_user.organization_id
        )
    ).first()
    
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
    
    db.commit()
    
    return {"message": "Leave application approved successfully"}

@router.put("/leave-applications/{application_id}/reject")
async def reject_leave_application(
    application_id: int,
    approval_remarks: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a leave application"""
    
    application = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.id == application_id,
            LeaveApplication.organization_id == current_user.organization_id
        )
    ).first()
    
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
    
    db.commit()
    
    return {"message": "Leave application rejected successfully"}

# Performance Review Management
@router.post("/performance-reviews", response_model=PerformanceReviewResponse)
async def create_performance_review(
    review_data: PerformanceReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new performance review"""
    
    performance_review = PerformanceReview(
        **review_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(performance_review)
    db.commit()
    db.refresh(performance_review)
    
    return performance_review

@router.get("/performance-reviews", response_model=List[PerformanceReviewResponse])
async def get_performance_reviews(
    employee_id: Optional[int] = Query(None),
    reviewer_id: Optional[int] = Query(None),
    review_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance reviews with filtering"""
    
    query = db.query(PerformanceReview).filter(
        PerformanceReview.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if employee_id:
        query = query.filter(PerformanceReview.employee_id == employee_id)
    
    if reviewer_id:
        query = query.filter(PerformanceReview.reviewer_id == reviewer_id)
    
    if review_type:
        query = query.filter(PerformanceReview.review_type == review_type)
    
    if status:
        query = query.filter(PerformanceReview.status == status)
    
    # Order by review period (newest first)
    query = query.order_by(desc(PerformanceReview.review_period_start))
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews

@router.put("/performance-reviews/{review_id}", response_model=PerformanceReviewResponse)
async def update_performance_review(
    review_id: int,
    review_data: PerformanceReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update performance review"""
    
    review = db.query(PerformanceReview).filter(
        and_(
            PerformanceReview.id == review_id,
            PerformanceReview.organization_id == current_user.organization_id
        )
    ).first()
    
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
    
    db.commit()
    db.refresh(review)
    
    return review

# Dashboard APIs
@router.get("/dashboard", response_model=HRDashboard)
async def get_hr_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get HR dashboard summary"""
    
    # Total employees
    total_employees = db.query(EmployeeProfile).filter(
        EmployeeProfile.organization_id == current_user.organization_id
    ).count()
    
    # Active employees
    active_employees = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employment_status == "active"
        )
    ).count()
    
    # Employees on leave today
    today = date.today()
    employees_on_leave = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.organization_id == current_user.organization_id,
            LeaveApplication.status == "approved",
            LeaveApplication.start_date <= today,
            LeaveApplication.end_date >= today
        )
    ).count()
    
    # Pending leave approvals
    pending_leave_approvals = db.query(LeaveApplication).filter(
        and_(
            LeaveApplication.organization_id == current_user.organization_id,
            LeaveApplication.status == "pending"
        )
    ).count()
    
    # Upcoming performance reviews (next 30 days)
    next_month = today + timedelta(days=30)
    upcoming_performance_reviews = db.query(PerformanceReview).filter(
        and_(
            PerformanceReview.organization_id == current_user.organization_id,
            PerformanceReview.status.in_(["draft", "submitted"]),
            PerformanceReview.review_period_end.between(today, next_month)
        )
    ).count()
    
    # Recent joiners (last 30 days)
    last_month = today - timedelta(days=30)
    recent_joiners = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.hire_date >= last_month
        )
    ).count()
    
    # Employees in probation
    employees_in_probation = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employment_status == "active",
            EmployeeProfile.confirmation_date.is_(None),
            EmployeeProfile.hire_date.isnot(None)
        )
    ).count()
    
    # Calculate average attendance rate for current month
    current_month = today.replace(day=1)
    attendance_stats = db.query(
        func.avg(AttendanceRecord.total_hours).label('avg_hours')
    ).filter(
        and_(
            AttendanceRecord.organization_id == current_user.organization_id,
            AttendanceRecord.attendance_date >= current_month,
            AttendanceRecord.attendance_status == "present"
        )
    ).first()
    
    average_attendance_rate = attendance_stats.avg_hours if attendance_stats.avg_hours else None
    
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