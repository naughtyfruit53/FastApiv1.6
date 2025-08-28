# app/models/hr_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date, time
from decimal import Decimal

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
    employee_type: Mapped[str] = mapped_column(String, nullable=False, default="permanent")  # permanent, contract, intern, consultant
    
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
    work_type: Mapped[str] = mapped_column(String, nullable=False, default="office")  # office, remote, hybrid
    
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
    employment_status: Mapped[str] = mapped_column(String, nullable=False, default="active")  # active, resigned, terminated, on_leave
    resignation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_working_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    resignation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Additional data
    skills: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    certifications: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    documents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {filename: {extracted_data, file_path}}
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_created_by_id"), nullable=True)
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_profile_updated_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
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
    attendance_status: Mapped[str] = mapped_column(String, nullable=False, default="present")  # present, absent, half_day, late, on_leave
    work_type: Mapped[str] = mapped_column(String, nullable=False, default="office")  # office, remote, hybrid, field_work
    
    # Location tracking
    check_in_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    check_out_location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    check_in_device: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # web, mobile, biometric
    
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
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
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
    name: Mapped[str] = mapped_column(String, nullable=False)  # Annual Leave, Sick Leave, Maternity Leave, etc.
    code: Mapped[str] = mapped_column(String, nullable=False)  # AL, SL, ML, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Leave policies
    annual_allocation: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Days per year
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
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
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
    half_day_period: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # morning, afternoon
    
    # Status and approval
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending, approved, rejected, cancelled
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
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
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
    review_type: Mapped[str] = mapped_column(String, nullable=False, default="annual")  # annual, half_yearly, quarterly, probation
    
    # Ratings and scores
    overall_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)  # e.g., 4.5 out of 5
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
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, submitted, acknowledged, finalized
    submitted_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["EmployeeProfile"] = relationship("EmployeeProfile", back_populates="performance_reviews")
    reviewer: Mapped["app.models.user_models.User"] = relationship("app.models.user_models.User")

    __table_args__ = (
        Index('idx_performance_review_org_employee', 'organization_id', 'employee_id'),
        Index('idx_performance_review_period', 'review_period_start', 'review_period_end'),
        Index('idx_performance_review_status', 'status'),
        {'extend_existing': True}
    )