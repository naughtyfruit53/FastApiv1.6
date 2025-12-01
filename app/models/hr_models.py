# app/models/hr_models.py
from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, date, time
from decimal import Decimal
if TYPE_CHECKING:
    from app.models.user_models import Organization, User
# Department Management
class Department(Base):
    """Organization department/division structure"""
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_department_organization_id"), nullable=False, index=True)
   
    # Department details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", name="fk_department_parent_id"), nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_department_manager_id"), nullable=True)
   
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cost_center_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_department_created_by_id"), nullable=True)
    # Relationships - use string references for cross-module relationships
    organization: Mapped["Organization"] = relationship("Organization")
    parent: Mapped[Optional["Department"]] = relationship("Department", remote_side=[id], foreign_keys=[parent_id])
    manager: Mapped[Optional["User"]] = relationship("User", foreign_keys=[manager_id])
    positions: Mapped[List["Position"]] = relationship("Position", back_populates="department")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_department_org_code'),
        Index('idx_department_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )
# Position/Designation Management
class Position(Base):
    """Job positions/designations within organization"""
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_position_organization_id"), nullable=False, index=True)
   
    # Position details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Department association
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", name="fk_position_department_id"), nullable=True)
   
    # Job level/grade
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # Junior, Mid, Senior, Lead, Manager, Director, etc.
    grade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # A, B, C, etc.
   
    # Salary range
    min_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    max_salary: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
   
    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    headcount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Budgeted headcount
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="positions")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_position_org_code'),
        Index('idx_position_org_department', 'organization_id', 'department_id'),
        Index('idx_position_active', 'is_active'),
        {'extend_existing': True}
    )
# Work Shift Management
class WorkShift(Base):
    """Work shift definitions"""
    __tablename__ = "work_shifts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_work_shift_organization_id"), nullable=False, index=True)
   
    # Shift details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Timing
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    break_start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
   
    # Working hours
    working_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=8)
    break_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
   
    # Shift type
    shift_type: Mapped[str] = mapped_column(String(50), nullable=False, default="general") # general, morning, afternoon, night, rotating
   
    # Flexibility settings
    grace_period_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    overtime_threshold_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
   
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_work_shift_org_code'),
        Index('idx_work_shift_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )
# Holiday Calendar
class HolidayCalendar(Base):
    """Organization holiday calendar"""
    __tablename__ = "holiday_calendars"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_holiday_calendar_organization_id"), nullable=False, index=True)
   
    # Holiday details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    holiday_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Holiday type
    holiday_type: Mapped[str] = mapped_column(String(50), nullable=False, default="public") # public, restricted, optional, company
   
    # Applicability
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    applicable_departments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # List of department IDs
   
    # Year reference
    year: Mapped[int] = mapped_column(Integer, nullable=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'holiday_date', name='uq_holiday_calendar_org_date'),
        Index('idx_holiday_calendar_org_year', 'organization_id', 'year'),
        Index('idx_holiday_calendar_date', 'holiday_date'),
        {'extend_existing': True}
    )
# Employee Profile - Extends User model for HR-specific data
class EmployeeProfile(Base):
    """Extended employee profile for HR management"""
    __tablename__ = "employee_profiles"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_employee_profile_organization_id"), nullable=False, index=True)
   
    # Link to User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_user_id"), nullable=False, unique=True, index=True)
   
    # Employee identification
    employee_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    employee_type: Mapped[str] = mapped_column(String, nullable=False, default="permanent") # permanent, contract, intern, consultant
   
    # Personal details
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    blood_group: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nationality: Mapped[str] = mapped_column(String, nullable=False, default="Indian")
   
    # Contact information
    personal_email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    personal_phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
   
    # Address details
    address_line1: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pin_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="India")
   
    # Employment details
    hire_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    confirmation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    probation_period_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=6)
    reporting_manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_reporting_manager_id"), nullable=True)
   
    # Job details
    job_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    job_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    work_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    work_type: Mapped[str] = mapped_column(String, nullable=False, default="office") # office, remote, hybrid, field_work
   
    # Benefits and compensation
    salary_currency: Mapped[str] = mapped_column(String, nullable=False, default="INR")
   
    # Documents
    pan_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    aadhaar_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    passport_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    driving_license: Mapped[Optional[str]] = mapped_column(String, nullable=True)
   
    # Banking details
    bank_account_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bank_branch: Mapped[Optional[str]] = mapped_column(String, nullable=True)
   
    # Status
    employment_status: Mapped[str] = mapped_column(String, nullable=False, default="active") # active, resigned, terminated, on_leave
    resignation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_working_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    resignation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Additional data
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    documents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # {filename: {extracted_data, file_path}}
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_updated_by_id"), nullable=True)
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    user: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User", foreign_keys=[user_id])
    reporting_manager: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[reporting_manager_id])
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[created_by_id])
    updated_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[updated_by_id])
   
    # HR relationships
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="employee")
    leave_applications: Mapped[List["LeaveApplication"]] = relationship("LeaveApplication", back_populates="employee")
    performance_reviews: Mapped[List["PerformanceReview"]] = relationship("PerformanceReview", back_populates="employee")
    salary_records: Mapped[List["app.models.hr_models.SalaryStructure"]] = relationship("SalaryStructure", back_populates="employee")
    __table_args__ = (
        UniqueConstraint('organization_id', 'employee_code', name='uq_employee_profile_org_code'),
        Index('idx_employee_profile_org_user', 'organization_id', 'user_id'),
        Index('idx_employee_profile_employment_status', 'employment_status'),
        Index('idx_employee_profile_hire_date', 'hire_date'),
        {'extend_existing': True}
    )
# Attendance Management
class AttendanceRecord(Base):
    """Daily attendance records for employees"""
    __tablename__ = "attendance_records"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_attendance_record_organization_id"), nullable=False, index=True)
   
    # Employee reference
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_attendance_record_employee_id"), nullable=False, index=True)
   
    # Attendance details
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    check_out_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
   
    # Calculated fields
    total_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    overtime_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True, default=0)
    break_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True, default=0)
   
    # Status and type
    attendance_status: Mapped[str] = mapped_column(String, nullable=False, default="present") # present, absent, half_day, late, on_leave
    work_type: Mapped[str] = mapped_column(String, nullable=False, default="office") # office, remote, hybrid, field_work
   
    # Location tracking
    check_in_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    check_out_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    check_in_device: Mapped[Optional[str]] = mapped_column(String, nullable=True) # web, mobile, biometric
   
    # Approval workflow
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_attendance_record_approved_by_id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Comments and notes
    employee_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="attendance_records")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    __table_args__ = (
        UniqueConstraint('organization_id', 'employee_id', 'attendance_date', name='uq_attendance_record_emp_date'),
        Index('idx_attendance_record_org_date', 'organization_id', 'attendance_date'),
        Index('idx_attendance_record_status', 'attendance_status'),
        {'extend_existing': True}
    )
# Leave Management
class LeaveType(Base):
    """Types of leaves available in the organization"""
    __tablename__ = "leave_types"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_leave_type_organization_id"), nullable=False, index=True)
   
    # Leave type details
    name: Mapped[str] = mapped_column(String, nullable=False) # Annual Leave, Sick Leave, Maternity Leave, etc.
    code: Mapped[str] = mapped_column(String, nullable=False) # AL, SL, ML, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Leave policies
    annual_allocation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # Days per year
    carry_forward_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    max_carry_forward_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cash_conversion_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Rules
    min_days_per_application: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=1)
    max_days_per_application: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    advance_notice_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    leave_applications: Mapped[List["LeaveApplication"]] = relationship("LeaveApplication", back_populates="leave_type")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_leave_type_org_code'),
        Index('idx_leave_type_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )
class LeaveApplication(Base):
    """Employee leave applications and approvals"""
    __tablename__ = "leave_applications"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_leave_application_organization_id"), nullable=False, index=True)
   
    # Employee and leave type
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_leave_application_employee_id"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id", name="fk_leave_application_leave_type_id"), nullable=False, index=True)
   
    # Leave details
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
   
    # Half day specifics
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False)
    half_day_period: Mapped[Optional[str]] = mapped_column(String, nullable=True) # morning, afternoon
   
    # Status and approval
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending") # pending, approved, rejected, cancelled
    applied_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
   
    # Approval workflow
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_leave_application_approved_by_id"), nullable=True)
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Contact details during leave
    contact_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="leave_applications")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType", back_populates="leave_applications")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")
    __table_args__ = (
        Index('idx_leave_application_org_employee', 'organization_id', 'employee_id'),
        Index('idx_leave_application_status', 'status'),
        Index('idx_leave_application_dates', 'start_date', 'end_date'),
        {'extend_existing': True}
    )
# Performance Management
class PerformanceReview(Base):
    """Employee performance reviews and evaluations"""
    __tablename__ = "performance_reviews"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
   
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_performance_review_organization_id"), nullable=False, index=True)
   
    # Employee reference
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_performance_review_employee_id"), nullable=False, index=True)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", name="fk_performance_review_reviewer_id"), nullable=False, index=True)
   
    # Review details
    review_period_start: Mapped[date] = mapped_column(Date, nullable=False)
    review_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    review_type: Mapped[str] = mapped_column(String, nullable=False, default="annual") # annual, half_yearly, quarterly, probation
   
    # Ratings and scores
    overall_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True) # e.g., 4.5 out of 5
    technical_skills_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    communication_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    leadership_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    teamwork_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
   
    # Comments and feedback
    achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    areas_of_improvement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goals_next_period: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employee_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Custom ratings (JSON for flexibility)
    custom_ratings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # Status and workflow
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft") # draft, submitted, acknowledged, finalized
    submitted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="performance_reviews")
    reviewer: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User")
    __table_args__ = (
        Index('idx_performance_review_org_employee', 'organization_id', 'employee_id'),
        Index('idx_performance_review_period', 'review_period_start', 'review_period_end'),
        Index('idx_performance_review_status', 'status'),
        {'extend_existing': True}
    )
# =============================================================================
# HR Phase 2 Models - Advanced Payroll and Attendance
# =============================================================================
# Attendance Policy Configuration
class AttendancePolicy(Base):
    """Attendance policy rules and configurations"""
    __tablename__ = "attendance_policies"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Policy identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Accrual settings
    accrual_type: Mapped[str] = mapped_column(String(50), default="monthly") # monthly, annual, pay_period
    accrual_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0")) # days per period
    max_accrual: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True) # max accrued days
   
    # Carry forward rules
    carry_forward_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    max_carry_forward_days: Mapped[int] = mapped_column(Integer, default=0)
    carry_forward_expiry_months: Mapped[int] = mapped_column(Integer, default=12) # months until carried leave expires
   
    # Overtime calculation rules
    overtime_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    overtime_threshold_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("8")) # daily hours
    overtime_multiplier: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("1.5"))
    weekend_overtime_multiplier: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("2.0"))
    holiday_overtime_multiplier: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("2.5"))
   
    # Late/Early rules
    late_threshold_minutes: Mapped[int] = mapped_column(Integer, default=15)
    early_leave_threshold_minutes: Mapped[int] = mapped_column(Integer, default=30)
    half_day_threshold_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), default=Decimal("4"))
   
    # Status and applicability
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    applicable_departments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_attendance_policy_org_code'),
        Index('idx_attendance_policy_org_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )
# Leave Balance Tracking
class LeaveBalance(Base):
    """Track leave balances for employees by leave type and year"""
    __tablename__ = "leave_balances"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
    leave_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("leave_types.id"), nullable=False, index=True)
   
    # Balance tracking
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    allocated_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    accrued_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    carried_forward_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    used_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    pending_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0")) # pending approval
    encashed_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
   
    # Calculated balance
    available_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
   
    # Metadata
    last_accrual_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    leave_type: Mapped["LeaveType"] = relationship("LeaveType")
    __table_args__ = (
        UniqueConstraint('organization_id', 'employee_id', 'leave_type_id', 'year', name='uq_leave_balance_emp_type_year'),
        Index('idx_leave_balance_org_employee', 'organization_id', 'employee_id'),
        {'extend_existing': True}
    )
# Timesheet for detailed time tracking
class Timesheet(Base):
    """Weekly/monthly timesheet entries"""
    __tablename__ = "timesheets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
   
    # Timesheet period
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
   
    # Summary hours
    total_regular_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
    total_overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
    total_leave_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
   
    # Daily breakdown (JSON for flexibility)
    daily_entries: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: { "2024-01-01": {"regular": 8, "overtime": 2, "project_id": 1, "notes": ""}, ... }
   
    # Status and approval
    status: Mapped[str] = mapped_column(String(50), default="draft") # draft, submitted, approved, rejected
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    approved_by: Mapped[Optional["User"]] = relationship("User")
    __table_args__ = (
        UniqueConstraint('organization_id', 'employee_id', 'period_start', 'period_end', name='uq_timesheet_emp_period'),
        Index('idx_timesheet_org_status', 'organization_id', 'status'),
        {'extend_existing': True}
    )
# Arrears and Retro Adjustments
class PayrollArrear(Base):
    """Track arrears and retro salary adjustments"""
    __tablename__ = "payroll_arrears"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
   
    # Arrear details
    arrear_type: Mapped[str] = mapped_column(String(50), nullable=False) # salary_revision, bonus, allowance, deduction
    description: Mapped[str] = mapped_column(Text, nullable=False)
   
    # Period for arrear calculation
    from_period: Mapped[date] = mapped_column(Date, nullable=False)
    to_period: Mapped[date] = mapped_column(Date, nullable=False)
   
    # Amounts
    arrear_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    net_arrear_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
   
    # Processing
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, approved, processed, paid
    process_in_period_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payroll_periods.id"), nullable=True)
   
    # Approval workflow
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Reference
    reference_document: Mapped[Optional[str]] = mapped_column(String(200), nullable=True) # HR letter number, etc.
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    __table_args__ = (
        Index('idx_payroll_arrear_org_status', 'organization_id', 'status'),
        Index('idx_payroll_arrear_employee', 'employee_id'),
        {'extend_existing': True}
    )
# Statutory Deduction Configuration
class StatutoryDeduction(Base):
    """Configurable statutory deductions (PF, ESI, TDS, etc.)"""
    __tablename__ = "statutory_deductions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Deduction identification
    code: Mapped[str] = mapped_column(String(50), nullable=False) # PF, ESI, TDS, PT, LWF
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Calculation type
    calculation_type: Mapped[str] = mapped_column(String(50), nullable=False) # percentage, fixed, slab_based
    employee_contribution: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    employer_contribution: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
   
    # Ceiling and limits
    ceiling_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    minimum_wage_threshold: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    maximum_wage_threshold: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
   
    # Slab configuration (if slab_based)
    slabs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: [{"min": 0, "max": 15000, "rate": 0.12}, {"min": 15001, "max": null, "rate": 0.12}]
   
    # Applicability
    applicable_from: Mapped[date] = mapped_column(Date, nullable=False)
    applicable_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', name='uq_statutory_deduction_org_code'),
        Index('idx_statutory_deduction_active', 'organization_id', 'is_active'),
        {'extend_existing': True}
    )
# Bank Payment Export Configuration
class BankPaymentExport(Base):
    """Bank payment file generation tracking"""
    __tablename__ = "bank_payment_exports"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    payroll_period_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_periods.id"), nullable=False, index=True)
   
    # Export details
    export_type: Mapped[str] = mapped_column(String(50), nullable=False) # bank_transfer, neft, rtgs, imps
    bank_name: Mapped[str] = mapped_column(String(200), nullable=False)
    file_format: Mapped[str] = mapped_column(String(50), nullable=False) # csv, txt, xlsx, bank_specific
   
    # File info
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
   
    # Summary
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="generated") # generated, uploaded, processed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    generated_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization")
    generated_by: Mapped["User"] = relationship("User")
    __table_args__ = (
        Index('idx_bank_export_org_period', 'organization_id', 'payroll_period_id'),
        {'extend_existing': True}
    )
# Payroll Approval Workflow
class PayrollApproval(Base):
    """Multi-level payroll approval workflow"""
    __tablename__ = "payroll_approvals"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    payroll_period_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_periods.id"), nullable=False, index=True)
   
    # Approval level
    approval_level: Mapped[int] = mapped_column(Integer, nullable=False) # 1, 2, 3...
    approver_role: Mapped[str] = mapped_column(String(100), nullable=False) # hr_manager, finance_head, cfo
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, approved, rejected
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    approved_by: Mapped[Optional["User"]] = relationship("User")
    __table_args__ = (
        UniqueConstraint('payroll_period_id', 'approval_level', name='uq_payroll_approval_period_level'),
        Index('idx_payroll_approval_status', 'status'),
        {'extend_existing': True}
    )
# =============================================================================
# Phase 4 Scaffolding - Analytics and Org Planning (Feature-flagged)
# =============================================================================
# HR Analytics Data Model
class HRAnalyticsSnapshot(Base):
    """Point-in-time HR analytics snapshots"""
    __tablename__ = "hr_analytics_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Snapshot details
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    snapshot_type: Mapped[str] = mapped_column(String(50), nullable=False) # daily, weekly, monthly, quarterly
   
    # Headcount metrics
    total_headcount: Mapped[int] = mapped_column(Integer, default=0)
    active_employees: Mapped[int] = mapped_column(Integer, default=0)
    new_hires: Mapped[int] = mapped_column(Integer, default=0)
    terminations: Mapped[int] = mapped_column(Integer, default=0)
   
    # Attrition metrics
    attrition_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    voluntary_attrition: Mapped[int] = mapped_column(Integer, default=0)
    involuntary_attrition: Mapped[int] = mapped_column(Integer, default=0)
   
    # Tenure metrics
    avg_tenure_months: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
    tenure_distribution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"0-6": 10, "6-12": 20, "12-24": 30, "24+": 40}
   
    # Payroll cost metrics
    total_payroll_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    avg_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    cost_per_employee: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
   
    # Department breakdown
    department_breakdown: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"dept_id": {"headcount": 10, "payroll_cost": 500000}}
   
    # Feature flag
    is_feature_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'snapshot_date', 'snapshot_type', name='uq_hr_analytics_snapshot'),
        Index('idx_hr_analytics_org_date', 'organization_id', 'snapshot_date'),
        {'extend_existing': True}
    )
# Position Budgeting
class PositionBudget(Base):
    """Position budgeting and headcount planning"""
    __tablename__ = "position_budgets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    position_id: Mapped[int] = mapped_column(Integer, ForeignKey("positions.id"), nullable=False, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
   
    # Budget period
    fiscal_year: Mapped[str] = mapped_column(String(10), nullable=False) # 2024-25
    quarter: Mapped[Optional[str]] = mapped_column(String(5), nullable=True) # Q1, Q2, Q3, Q4
   
    # Headcount budget
    budgeted_headcount: Mapped[int] = mapped_column(Integer, default=0)
    filled_headcount: Mapped[int] = mapped_column(Integer, default=0)
    open_positions: Mapped[int] = mapped_column(Integer, default=0)
   
    # Salary budget
    budgeted_salary_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    actual_salary_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    variance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
   
    # Approval status
    status: Mapped[str] = mapped_column(String(50), default="draft") # draft, submitted, approved
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Feature flag
    is_feature_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    position: Mapped["Position"] = relationship("Position")
    department: Mapped[Optional["Department"]] = relationship("Department")
    __table_args__ = (
        UniqueConstraint('organization_id', 'position_id', 'fiscal_year', 'quarter', name='uq_position_budget'),
        Index('idx_position_budget_org_year', 'organization_id', 'fiscal_year'),
        {'extend_existing': True}
    )
# Transfer History
class EmployeeTransfer(Base):
    """Track employee transfers and movements"""
    __tablename__ = "employee_transfers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
   
    # Transfer details
    transfer_type: Mapped[str] = mapped_column(String(50), nullable=False) # department, location, position, promotion
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
   
    # From
    from_department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    from_position_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("positions.id"), nullable=True)
    from_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    from_manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
   
    # To
    to_department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"), nullable=True)
    to_position_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("positions.id"), nullable=True)
    to_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    to_manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
   
    # Salary change (if any)
    salary_change_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    salary_change_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
   
    # Status and approval
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, approved, completed, cancelled
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Feature flag
    is_feature_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    __table_args__ = (
        Index('idx_employee_transfer_org_emp', 'organization_id', 'employee_id'),
        Index('idx_employee_transfer_date', 'effective_date'),
        {'extend_existing': True}
    )
# =============================================================================
# Integration Adapters Configuration
# =============================================================================
class IntegrationAdapter(Base):
    """Integration adapter configuration for external systems"""
    __tablename__ = "integration_adapters"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Adapter identification
    adapter_type: Mapped[str] = mapped_column(String(50), nullable=False) # sso, payroll_provider, attendance_hardware, erp
    adapter_name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False) # okta, azure_ad, adp, sap, etc.
   
    # Configuration (encrypted in production)
    config: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Structure varies by adapter_type:
    # SSO: {"client_id": "", "client_secret": "", "tenant_id": "", "auth_url": "", "token_url": ""}
    # Payroll: {"api_key": "", "api_url": "", "company_id": ""}
    # Attendance: {"device_ip": "", "port": "", "api_key": ""}
   
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(50), default="not_synced") # not_synced, syncing, synced, error
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Feature flag
    is_feature_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'adapter_type', 'provider', name='uq_integration_adapter'),
        Index('idx_integration_adapter_org_type', 'organization_id', 'adapter_type'),
        {'extend_existing': True}
    )
# =============================================================================
# HR Phase 3 Models - Performance Management, Compliance
# =============================================================================
# Goals and OKRs Management
class Goal(Base):
    """Employee goals and OKRs (Objectives & Key Results)"""
    __tablename__ = "hr_goals"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
   
    # Goal details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False, default="individual") # individual, team, department, company
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # performance, development, project, etc.
   
    # OKR structure
    is_okr: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_goal_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hr_goals.id"), nullable=True)
   
    # Key results (for OKRs)
    key_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: [{"id": 1, "description": "...", "target": 100, "current": 50, "unit": "%"}]
   
    # Timeline
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    review_cycle_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hr_review_cycles.id"), nullable=True)
   
    # Progress tracking
    progress_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(50), default="not_started") # not_started, in_progress, completed, cancelled
    priority: Mapped[str] = mapped_column(String(20), default="medium") # low, medium, high, critical
   
    # Weightage for scoring
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.0"))
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
   
    # Alignment
    aligned_to_company_goal: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
   
    # Visibility
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    shared_with: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # user IDs who can view
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    parent_goal: Mapped[Optional["Goal"]] = relationship("Goal", remote_side=[id])
    __table_args__ = (
        Index('idx_goal_org_employee', 'organization_id', 'employee_id'),
        Index('idx_goal_status', 'status'),
        Index('idx_goal_dates', 'start_date', 'end_date'),
        {'extend_existing': True}
    )
# Review Cycles Management
class ReviewCycle(Base):
    """Performance review cycles/periods"""
    __tablename__ = "hr_review_cycles"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Cycle details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cycle_type: Mapped[str] = mapped_column(String(50), nullable=False) # annual, semi_annual, quarterly, monthly, probation
   
    # Timeline
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
   
    # Review windows
    self_review_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    self_review_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    manager_review_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    manager_review_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    peer_review_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    peer_review_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    calibration_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    calibration_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
   
    # Configuration
    include_goals: Mapped[bool] = mapped_column(Boolean, default=True)
    include_competencies: Mapped[bool] = mapped_column(Boolean, default=True)
    include_360_feedback: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_self_review: Mapped[bool] = mapped_column(Boolean, default=True)
    require_manager_approval: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Rating scale
    rating_scale: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"min": 1, "max": 5, "labels": {"1": "Needs Improvement", "5": "Exceptional"}}
   
    # Applicable to
    applicable_departments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    applicable_positions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft") # draft, active, completed, archived
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        Index('idx_review_cycle_org_status', 'organization_id', 'status'),
        Index('idx_review_cycle_dates', 'start_date', 'end_date'),
        {'extend_existing': True}
    )
# 360 Feedback Forms
class FeedbackForm(Base):
    """360 degree feedback form templates and responses"""
    __tablename__ = "hr_feedback_forms"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Form template or response
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hr_feedback_forms.id"), nullable=True)
   
    # Form details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False) # self, manager, peer, subordinate, external
   
    # Review cycle association
    review_cycle_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("hr_review_cycles.id"), nullable=True)
   
    # For responses: who is being reviewed and by whom
    review_reviewee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=True)
    reviewer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
   
    # Form structure
    questions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: [{"id": 1, "category": "Leadership", "question": "...", "type": "rating", "required": true}]
   
    # Responses
    responses: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Structure: {"1": {"rating": 4, "comment": "..."}, "2": {...}}
   
    # Scoring
    overall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    category_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # Anonymity
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, in_progress, completed, expired
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    template: Mapped[Optional["FeedbackForm"]] = relationship("FeedbackForm", remote_side=[id])
    reviewee: Mapped[Optional["EmployeeProfile"]] = relationship("EmployeeProfile")
    __table_args__ = (
        Index('idx_feedback_form_org_type', 'organization_id', 'feedback_type'),
        Index('idx_feedback_form_reviewee', 'review_reviewee_id'),
        Index('idx_feedback_form_status', 'status'),
        {'extend_existing': True}
    )
# =============================================================================
# Compliance & Policies Module
# =============================================================================
# Policy Documents
class PolicyDocument(Base):
    """Company policy documents for distribution and acknowledgment"""
    __tablename__ = "hr_policy_documents"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Document details
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False) # hr, it, security, compliance, general, etc.
   
    # Version management
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
   
    # Content
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # pdf, docx, etc.
   
    # Distribution
    applicable_to: Mapped[str] = mapped_column(String(50), default="all") # all, departments, positions, new_hires
    applicable_departments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    applicable_positions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # Acknowledgment settings
    requires_acknowledgment: Mapped[bool] = mapped_column(Boolean, default=True)
    acknowledgment_deadline_days: Mapped[int] = mapped_column(Integer, default=7)
    re_acknowledgment_period_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # For periodic re-ack
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft") # draft, published, archived
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        UniqueConstraint('organization_id', 'code', 'version', name='uq_policy_document_code_version'),
        Index('idx_policy_document_org_status', 'organization_id', 'status'),
        Index('idx_policy_document_category', 'category'),
        {'extend_existing': True}
    )
# Policy Acknowledgments
class PolicyAcknowledgment(Base):
    """Employee acknowledgments of policy documents"""
    __tablename__ = "hr_policy_acknowledgments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    policy_document_id: Mapped[int] = mapped_column(Integer, ForeignKey("hr_policy_documents.id"), nullable=False, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id"), nullable=False, index=True)
   
    # Acknowledgment details
    acknowledged_version: Mapped[str] = mapped_column(String(20), nullable=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, acknowledged, overdue
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
   
    # IP and signature
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    digital_signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
   
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    organization: Mapped["Organization"] = relationship("Organization")
    policy_document: Mapped["PolicyDocument"] = relationship("PolicyDocument")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile")
    __table_args__ = (
        UniqueConstraint('policy_document_id', 'employee_id', 'acknowledged_version', name='uq_policy_ack_emp_version'),
        Index('idx_policy_ack_org_status', 'organization_id', 'status'),
        Index('idx_policy_ack_employee', 'employee_id'),
        {'extend_existing': True}
    )
# Compliance Audit Export
class ComplianceAuditExport(Base):
    """Compliance audit export tracking"""
    __tablename__ = "hr_compliance_audit_exports"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
   
    # Export details
    export_type: Mapped[str] = mapped_column(String(100), nullable=False) # policy_acknowledgments, training_compliance, employee_documents, etc.
    export_name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Date range
    date_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
   
    # Filters applied
    filters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
   
    # File details
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_format: Mapped[str] = mapped_column(String(20), default="csv") # csv, xlsx, pdf
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    record_count: Mapped[int] = mapped_column(Integer, default=0)
   
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
   
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    organization: Mapped["Organization"] = relationship("Organization")
    __table_args__ = (
        Index('idx_compliance_export_org_type', 'organization_id', 'export_type'),
        Index('idx_compliance_export_status', 'status'),
        {'extend_existing': True}
    )
    