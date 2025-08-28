# app/schemas/hr_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal

# Employee Profile Schemas
class EmployeeProfileBase(BaseModel):
    employee_code: str = Field(..., description="Unique employee code")
    employee_type: str = Field(default="permanent", description="Employment type")
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: str = Field(default="Indian")
    
    # Contact information
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    # Address details
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    
    # Employment details
    hire_date: Optional[date] = None
    confirmation_date: Optional[date] = None
    probation_period_months: Optional[int] = Field(default=6)
    reporting_manager_id: Optional[int] = None
    
    # Job details
    job_title: Optional[str] = None
    job_level: Optional[str] = None
    work_location: Optional[str] = None
    work_type: str = Field(default="office")
    
    # Benefits and compensation
    salary_currency: str = Field(default="INR")
    
    # Documents
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license: Optional[str] = None
    
    # Banking details
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    
    # Status
    employment_status: str = Field(default="active")
    resignation_date: Optional[date] = None
    last_working_date: Optional[date] = None
    resignation_reason: Optional[str] = None
    
    # Additional data
    skills: Optional[Dict[str, Any]] = Field(None, description="Employee skills and competencies data. Contains skill categories, proficiency levels, certifications, training history, assessment scores, and skill development plans with timestamps.")
    certifications: Optional[Dict[str, Any]] = Field(None, description="Professional certifications and qualifications. Includes certification names, issuing bodies, issue/expiry dates, certification IDs, renewal requirements, and verification status.")
    notes: Optional[str] = None

class EmployeeProfileCreate(EmployeeProfileBase):
    user_id: int = Field(..., description="Reference to User table")

class EmployeeProfileUpdate(BaseModel):
    employee_code: Optional[str] = None
    employee_type: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    current_address: Optional[str] = None
    permanent_address: Optional[str] = None
    hire_date: Optional[date] = None
    confirmation_date: Optional[date] = None
    probation_period_months: Optional[int] = None
    reporting_manager_id: Optional[int] = None
    job_title: Optional[str] = None
    job_level: Optional[str] = None
    work_location: Optional[str] = None
    work_type: Optional[str] = None
    salary_currency: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    employment_status: Optional[str] = None
    resignation_date: Optional[date] = None
    last_working_date: Optional[date] = None
    resignation_reason: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class EmployeeProfileResponse(EmployeeProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None

# Attendance Record Schemas
class AttendanceRecordBase(BaseModel):
    attendance_date: date = Field(..., description="Date of attendance")
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    total_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = Field(default=Decimal('0'))
    break_hours: Optional[Decimal] = Field(default=Decimal('0'))
    attendance_status: str = Field(default="present")
    work_type: str = Field(default="office")
    check_in_location: Optional[str] = None
    check_out_location: Optional[str] = None
    check_in_device: Optional[str] = None
    employee_remarks: Optional[str] = None
    manager_remarks: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")

class AttendanceRecordUpdate(BaseModel):
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    total_hours: Optional[Decimal] = None
    overtime_hours: Optional[Decimal] = None
    break_hours: Optional[Decimal] = None
    attendance_status: Optional[str] = None
    work_type: Optional[str] = None
    check_in_location: Optional[str] = None
    check_out_location: Optional[str] = None
    check_in_device: Optional[str] = None
    employee_remarks: Optional[str] = None
    manager_remarks: Optional[str] = None
    is_approved: Optional[bool] = None

class AttendanceRecordResponse(AttendanceRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    organization_id: int
    is_approved: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Leave Type Schemas
class LeaveTypeBase(BaseModel):
    name: str = Field(..., description="Leave type name")
    code: str = Field(..., description="Leave type code")
    description: Optional[str] = None
    annual_allocation: Optional[int] = None
    carry_forward_allowed: bool = Field(default=False)
    max_carry_forward_days: Optional[int] = None
    cash_conversion_allowed: bool = Field(default=False)
    min_days_per_application: Optional[int] = Field(default=1)
    max_days_per_application: Optional[int] = None
    advance_notice_days: Optional[int] = None
    requires_approval: bool = Field(default=True)
    is_active: bool = Field(default=True)

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    annual_allocation: Optional[int] = None
    carry_forward_allowed: Optional[bool] = None
    max_carry_forward_days: Optional[int] = None
    cash_conversion_allowed: Optional[bool] = None
    min_days_per_application: Optional[int] = None
    max_days_per_application: Optional[int] = None
    advance_notice_days: Optional[int] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None

class LeaveTypeResponse(LeaveTypeBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Leave Application Schemas
class LeaveApplicationBase(BaseModel):
    leave_type_id: int = Field(..., description="Reference to LeaveType")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    total_days: int = Field(..., description="Total leave days")
    reason: str = Field(..., description="Reason for leave")
    is_half_day: bool = Field(default=False)
    half_day_period: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None

class LeaveApplicationCreate(LeaveApplicationBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")

class LeaveApplicationUpdate(BaseModel):
    leave_type_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None
    reason: Optional[str] = None
    is_half_day: Optional[bool] = None
    half_day_period: Optional[str] = None
    contact_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: Optional[str] = None
    approval_remarks: Optional[str] = None

class LeaveApplicationResponse(LeaveApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    organization_id: int
    status: str
    applied_date: datetime
    approved_by_id: Optional[int] = None
    approved_date: Optional[datetime] = None
    approval_remarks: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Performance Review Schemas
class PerformanceReviewBase(BaseModel):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")
    reviewer_id: int = Field(..., description="Reference to User (reviewer)")
    review_period_start: date = Field(..., description="Review period start")
    review_period_end: date = Field(..., description="Review period end")
    review_type: str = Field(default="annual")
    overall_rating: Optional[Decimal] = None
    technical_skills_rating: Optional[Decimal] = None
    communication_rating: Optional[Decimal] = None
    leadership_rating: Optional[Decimal] = None
    teamwork_rating: Optional[Decimal] = None
    achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    goals_next_period: Optional[str] = None
    employee_comments: Optional[str] = None
    reviewer_comments: Optional[str] = None
    custom_ratings: Optional[Dict[str, Any]] = None

class PerformanceReviewCreate(PerformanceReviewBase):
    pass

class PerformanceReviewUpdate(BaseModel):
    reviewer_id: Optional[int] = None
    review_period_start: Optional[date] = None
    review_period_end: Optional[date] = None
    review_type: Optional[str] = None
    overall_rating: Optional[Decimal] = None
    technical_skills_rating: Optional[Decimal] = None
    communication_rating: Optional[Decimal] = None
    leadership_rating: Optional[Decimal] = None
    teamwork_rating: Optional[Decimal] = None
    achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    goals_next_period: Optional[str] = None
    employee_comments: Optional[str] = None
    reviewer_comments: Optional[str] = None
    custom_ratings: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class PerformanceReviewResponse(PerformanceReviewBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    status: str
    submitted_date: Optional[datetime] = None
    acknowledged_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Dashboard and Summary Schemas
class AttendanceSummary(BaseModel):
    total_working_days: int
    present_days: int
    absent_days: int
    late_days: int
    leave_days: int
    average_hours: Optional[Decimal] = None
    total_overtime_hours: Optional[Decimal] = None

class EmployeeDashboard(BaseModel):
    employee_id: int
    full_name: str
    department: Optional[str] = None
    designation: Optional[str] = None
    attendance_summary: AttendanceSummary
    pending_leave_applications: int
    upcoming_reviews: int
    active_training_programs: int

class HRDashboard(BaseModel):
    total_employees: int
    active_employees: int
    employees_on_leave: int
    pending_leave_approvals: int
    upcoming_performance_reviews: int
    recent_joiners: int
    employees_in_probation: int
    average_attendance_rate: Optional[Decimal] = None