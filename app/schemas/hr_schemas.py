# app/schemas/hr_schemas.py
# 
# NOTE: SkipValidation is used for date fields to allow flexible date input formats
# (strings, date objects, etc.) that will be parsed by Pydantic. This is necessary
# because dates may come from various sources (JSON, form data, etc.) with different
# formats and direct validation would be too strict for these use cases.

from pydantic import BaseModel, Field, ConfigDict, SkipValidation
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from decimal import Decimal

# Employee Profile Schemas
class EmployeeProfileBase(BaseModel):
    employee_code: str = Field(..., description="Unique employee code")
    employee_type: str = Field(default="permanent", description="Employment type")
    date_of_birth: Optional[SkipValidation[date]] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: str = Field(default="Indian")
    
    personal_email: Optional[str] = None
    personal_phone: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    country: Optional[str] = Field(default="India")
    
    hire_date: Optional[SkipValidation[date]] = None
    confirmation_date: Optional[SkipValidation[date]] = None
    probation_period_months: Optional[int] = Field(default=6)
    reporting_manager_id: Optional[int] = None
    
    job_title: Optional[str] = None
    job_level: Optional[str] = None
    work_location: Optional[str] = None
    work_type: str = Field(default="office")
    
    salary_currency: str = Field(default="INR")
    
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license: Optional[str] = None
    
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    
    employment_status: str = Field(default="active")
    resignation_date: Optional[SkipValidation[date]] = None
    last_working_date: Optional[SkipValidation[date]] = None
    resignation_reason: Optional[str] = None
    
    skills: Optional[Dict[str, Any]] = Field(None, description="Employee skills and competencies data. Contains skill categories, proficiency levels, certifications, training history, assessment scores, and skill development plans with timestamps.")
    certifications: Optional[Dict[str, Any]] = Field(None, description="Professional certifications and qualifications. Includes certification names, issuing bodies, issue/expiry dates, certification IDs, renewal requirements, and verification status.")
    documents: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class EmployeeProfileCreate(EmployeeProfileBase):
    user_id: int = Field(..., description="Reference to User table")

class EmployeeProfileUpdate(EmployeeProfileBase):
    pass

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
    attendance_date: SkipValidation[date] = Field(..., description="Date of attendance")
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
    start_date: SkipValidation[date] = Field(..., description="Leave start date")
    end_date: SkipValidation[date] = Field(..., description="Leave end date")
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
    start_date: Optional[SkipValidation[date]] = None
    end_date: Optional[SkipValidation[date]] = None
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
    review_period_start: SkipValidation[date] = Field(..., description="Review period start")
    review_period_end: SkipValidation[date] = Field(..., description="Review period end")
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
    review_period_start: Optional[SkipValidation[date]] = None
    review_period_end: Optional[SkipValidation[date]] = None
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


# Department Schemas
class DepartmentBase(BaseModel):
    name: str = Field(..., description="Department name")
    code: str = Field(..., description="Department code")
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: bool = Field(default=True)
    cost_center_code: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    cost_center_code: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Position Schemas
class PositionBase(BaseModel):
    title: str = Field(..., description="Position title")
    code: str = Field(..., description="Position code")
    description: Optional[str] = None
    department_id: Optional[int] = None
    level: Optional[str] = None
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    is_active: bool = Field(default=True)
    headcount: Optional[int] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None
    level: Optional[str] = None
    grade: Optional[str] = None
    min_salary: Optional[Decimal] = None
    max_salary: Optional[Decimal] = None
    is_active: Optional[bool] = None
    headcount: Optional[int] = None


class PositionResponse(PositionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Work Shift Schemas
class WorkShiftBase(BaseModel):
    name: str = Field(..., description="Shift name")
    code: str = Field(..., description="Shift code")
    description: Optional[str] = None
    start_time: time = Field(..., description="Shift start time")
    end_time: time = Field(..., description="Shift end time")
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    working_hours: Decimal = Field(default=Decimal("8"), description="Working hours per day")
    break_duration_minutes: int = Field(default=60)
    shift_type: str = Field(default="general")
    grace_period_minutes: int = Field(default=15)
    overtime_threshold_minutes: int = Field(default=30)
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)


class WorkShiftCreate(WorkShiftBase):
    pass


class WorkShiftUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    working_hours: Optional[Decimal] = None
    break_duration_minutes: Optional[int] = None
    shift_type: Optional[str] = None
    grace_period_minutes: Optional[int] = None
    overtime_threshold_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class WorkShiftResponse(WorkShiftBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Holiday Calendar Schemas
class HolidayCalendarBase(BaseModel):
    name: str = Field(..., description="Holiday name")
    holiday_date: SkipValidation[date] = Field(..., description="Date of the holiday")
    description: Optional[str] = None
    holiday_type: str = Field(default="public", description="Type: public, restricted, optional, company")
    is_mandatory: bool = Field(default=True)
    applicable_departments: Optional[Dict[str, Any]] = None
    year: int = Field(..., description="Year of the holiday")


class HolidayCalendarCreate(HolidayCalendarBase):
    pass


class HolidayCalendarUpdate(BaseModel):
    name: Optional[str] = None
    holiday_date: Optional[SkipValidation[date]] = None
    description: Optional[str] = None
    holiday_type: Optional[str] = None
    is_mandatory: Optional[bool] = None
    applicable_departments: Optional[Dict[str, Any]] = None
    year: Optional[int] = None


class HolidayCalendarResponse(HolidayCalendarBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============================================================================
# HR Phase 2 Schemas - Advanced Attendance, Leave Balance, Timesheets
# =============================================================================

# Attendance Policy Schemas
class AttendancePolicyBase(BaseModel):
    name: str = Field(..., description="Policy name")
    code: str = Field(..., description="Policy code")
    description: Optional[str] = None
    
    # Accrual settings
    accrual_type: str = Field(default="monthly", description="Accrual type: monthly, annual, pay_period")
    accrual_rate: Decimal = Field(default=Decimal("0"), description="Days accrued per period")
    max_accrual: Optional[Decimal] = None
    
    # Carry forward rules
    carry_forward_enabled: bool = Field(default=False)
    max_carry_forward_days: int = Field(default=0)
    carry_forward_expiry_months: int = Field(default=12)
    
    # Overtime calculation rules
    overtime_enabled: bool = Field(default=True)
    overtime_threshold_hours: Decimal = Field(default=Decimal("8"))
    overtime_multiplier: Decimal = Field(default=Decimal("1.5"))
    weekend_overtime_multiplier: Decimal = Field(default=Decimal("2.0"))
    holiday_overtime_multiplier: Decimal = Field(default=Decimal("2.5"))
    
    # Late/Early rules
    late_threshold_minutes: int = Field(default=15)
    early_leave_threshold_minutes: int = Field(default=30)
    half_day_threshold_hours: Decimal = Field(default=Decimal("4"))
    
    # Status
    is_active: bool = Field(default=True)
    is_default: bool = Field(default=False)
    applicable_departments: Optional[Dict[str, Any]] = None


class AttendancePolicyCreate(AttendancePolicyBase):
    pass


class AttendancePolicyUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    accrual_type: Optional[str] = None
    accrual_rate: Optional[Decimal] = None
    max_accrual: Optional[Decimal] = None
    carry_forward_enabled: Optional[bool] = None
    max_carry_forward_days: Optional[int] = None
    carry_forward_expiry_months: Optional[int] = None
    overtime_enabled: Optional[bool] = None
    overtime_threshold_hours: Optional[Decimal] = None
    overtime_multiplier: Optional[Decimal] = None
    weekend_overtime_multiplier: Optional[Decimal] = None
    holiday_overtime_multiplier: Optional[Decimal] = None
    late_threshold_minutes: Optional[int] = None
    early_leave_threshold_minutes: Optional[int] = None
    half_day_threshold_hours: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    applicable_departments: Optional[Dict[str, Any]] = None


class AttendancePolicyResponse(AttendancePolicyBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# Leave Balance Schemas
class LeaveBalanceBase(BaseModel):
    year: int = Field(..., description="Leave balance year")
    allocated_days: Decimal = Field(default=Decimal("0"))
    accrued_days: Decimal = Field(default=Decimal("0"))
    carried_forward_days: Decimal = Field(default=Decimal("0"))
    used_days: Decimal = Field(default=Decimal("0"))
    pending_days: Decimal = Field(default=Decimal("0"))
    encashed_days: Decimal = Field(default=Decimal("0"))
    available_days: Decimal = Field(default=Decimal("0"))


class LeaveBalanceCreate(LeaveBalanceBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")
    leave_type_id: int = Field(..., description="Reference to LeaveType")


class LeaveBalanceUpdate(BaseModel):
    allocated_days: Optional[Decimal] = None
    accrued_days: Optional[Decimal] = None
    carried_forward_days: Optional[Decimal] = None
    used_days: Optional[Decimal] = None
    pending_days: Optional[Decimal] = None
    encashed_days: Optional[Decimal] = None
    available_days: Optional[Decimal] = None


class LeaveBalanceResponse(LeaveBalanceBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: int
    leave_type_id: int
    last_accrual_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Timesheet Schemas
class TimesheetBase(BaseModel):
    period_start: SkipValidation[date] = Field(..., description="Timesheet period start")
    period_end: SkipValidation[date] = Field(..., description="Timesheet period end")
    total_regular_hours: Decimal = Field(default=Decimal("0"))
    total_overtime_hours: Decimal = Field(default=Decimal("0"))
    total_leave_hours: Decimal = Field(default=Decimal("0"))
    daily_entries: Optional[Dict[str, Any]] = Field(None, description="Daily time entries")


class TimesheetCreate(TimesheetBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")


class TimesheetUpdate(BaseModel):
    total_regular_hours: Optional[Decimal] = None
    total_overtime_hours: Optional[Decimal] = None
    total_leave_hours: Optional[Decimal] = None
    daily_entries: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class TimesheetResponse(TimesheetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: int
    status: str
    submitted_at: Optional[datetime] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============================================================================
# Payroll Arrears and Statutory Deductions
# =============================================================================

class PayrollArrearBase(BaseModel):
    arrear_type: str = Field(..., description="Type: salary_revision, bonus, allowance, deduction")
    description: str = Field(..., description="Arrear description")
    from_period: SkipValidation[date] = Field(..., description="Arrear from period")
    to_period: SkipValidation[date] = Field(..., description="Arrear to period")
    arrear_amount: Decimal = Field(..., description="Arrear amount")
    tax_amount: Decimal = Field(default=Decimal("0"))
    net_arrear_amount: Decimal = Field(..., description="Net arrear amount")
    reference_document: Optional[str] = None


class PayrollArrearCreate(PayrollArrearBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")


class PayrollArrearUpdate(BaseModel):
    arrear_type: Optional[str] = None
    description: Optional[str] = None
    from_period: Optional[SkipValidation[date]] = None
    to_period: Optional[SkipValidation[date]] = None
    arrear_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    net_arrear_amount: Optional[Decimal] = None
    status: Optional[str] = None
    reference_document: Optional[str] = None


class PayrollArrearResponse(PayrollArrearBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: int
    status: str
    process_in_period_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


class StatutoryDeductionBase(BaseModel):
    code: str = Field(..., description="Deduction code like PF, ESI, TDS")
    name: str = Field(..., description="Deduction name")
    description: Optional[str] = None
    calculation_type: str = Field(..., description="Type: percentage, fixed, slab_based")
    employee_contribution: Decimal = Field(default=Decimal("0"))
    employer_contribution: Decimal = Field(default=Decimal("0"))
    ceiling_amount: Optional[Decimal] = None
    minimum_wage_threshold: Optional[Decimal] = None
    maximum_wage_threshold: Optional[Decimal] = None
    slabs: Optional[Dict[str, Any]] = None
    applicable_from: SkipValidation[date] = Field(..., description="Applicable from date")
    applicable_to: Optional[SkipValidation[date]] = None
    is_active: bool = Field(default=True)


class StatutoryDeductionCreate(StatutoryDeductionBase):
    pass


class StatutoryDeductionUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    calculation_type: Optional[str] = None
    employee_contribution: Optional[Decimal] = None
    employer_contribution: Optional[Decimal] = None
    ceiling_amount: Optional[Decimal] = None
    minimum_wage_threshold: Optional[Decimal] = None
    maximum_wage_threshold: Optional[Decimal] = None
    slabs: Optional[Dict[str, Any]] = None
    applicable_from: Optional[SkipValidation[date]] = None
    applicable_to: Optional[SkipValidation[date]] = None
    is_active: Optional[bool] = None


class StatutoryDeductionResponse(StatutoryDeductionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============================================================================
# Bank Payment Export and Payroll Approval
# =============================================================================

class BankPaymentExportBase(BaseModel):
    export_type: str = Field(..., description="Export type: bank_transfer, neft, rtgs, imps")
    bank_name: str = Field(..., description="Bank name")
    file_format: str = Field(..., description="File format: csv, txt, xlsx")
    file_name: str = Field(..., description="Export file name")


class BankPaymentExportCreate(BankPaymentExportBase):
    payroll_period_id: int = Field(..., description="Reference to PayrollPeriod")


class BankPaymentExportResponse(BankPaymentExportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    payroll_period_id: int
    file_path: Optional[str] = None
    total_records: int
    total_amount: Decimal
    status: str
    error_message: Optional[str] = None
    generated_at: datetime
    generated_by_id: int


class PayrollApprovalBase(BaseModel):
    approval_level: int = Field(..., description="Approval level: 1, 2, 3...")
    approver_role: str = Field(..., description="Approver role: hr_manager, finance_head, cfo")
    comments: Optional[str] = None


class PayrollApprovalCreate(PayrollApprovalBase):
    payroll_period_id: int = Field(..., description="Reference to PayrollPeriod")


class PayrollApprovalUpdate(BaseModel):
    status: Optional[str] = None
    comments: Optional[str] = None


class PayrollApprovalResponse(PayrollApprovalBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    payroll_period_id: int
    status: str
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============================================================================
# Phase 4 Scaffolding Schemas (Feature-flagged)
# =============================================================================

class HRAnalyticsSnapshotBase(BaseModel):
    snapshot_date: SkipValidation[date] = Field(..., description="Snapshot date")
    snapshot_type: str = Field(..., description="Type: daily, weekly, monthly, quarterly")
    total_headcount: int = Field(default=0)
    active_employees: int = Field(default=0)
    new_hires: int = Field(default=0)
    terminations: int = Field(default=0)
    attrition_rate: Decimal = Field(default=Decimal("0"))
    voluntary_attrition: int = Field(default=0)
    involuntary_attrition: int = Field(default=0)
    avg_tenure_months: Decimal = Field(default=Decimal("0"))
    tenure_distribution: Optional[Dict[str, Any]] = None
    total_payroll_cost: Decimal = Field(default=Decimal("0"))
    avg_salary: Decimal = Field(default=Decimal("0"))
    cost_per_employee: Decimal = Field(default=Decimal("0"))
    department_breakdown: Optional[Dict[str, Any]] = None
    is_feature_enabled: bool = Field(default=False)


class HRAnalyticsSnapshotResponse(HRAnalyticsSnapshotBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime


class PositionBudgetBase(BaseModel):
    fiscal_year: str = Field(..., description="Fiscal year like 2024-25")
    quarter: Optional[str] = Field(None, description="Quarter: Q1, Q2, Q3, Q4")
    budgeted_headcount: int = Field(default=0)
    filled_headcount: int = Field(default=0)
    open_positions: int = Field(default=0)
    budgeted_salary_cost: Decimal = Field(default=Decimal("0"))
    actual_salary_cost: Decimal = Field(default=Decimal("0"))
    variance: Decimal = Field(default=Decimal("0"))
    status: str = Field(default="draft")
    is_feature_enabled: bool = Field(default=False)


class PositionBudgetCreate(PositionBudgetBase):
    position_id: int = Field(..., description="Reference to Position")
    department_id: Optional[int] = None


class PositionBudgetUpdate(BaseModel):
    budgeted_headcount: Optional[int] = None
    filled_headcount: Optional[int] = None
    open_positions: Optional[int] = None
    budgeted_salary_cost: Optional[Decimal] = None
    actual_salary_cost: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    status: Optional[str] = None


class PositionBudgetResponse(PositionBudgetBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    position_id: int
    department_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class EmployeeTransferBase(BaseModel):
    transfer_type: str = Field(..., description="Type: department, location, position, promotion")
    effective_date: SkipValidation[date] = Field(..., description="Effective date")
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    salary_change_amount: Optional[Decimal] = None
    salary_change_percentage: Optional[Decimal] = None
    reason: str = Field(..., description="Transfer reason")
    is_feature_enabled: bool = Field(default=False)


class EmployeeTransferCreate(EmployeeTransferBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")
    from_department_id: Optional[int] = None
    from_position_id: Optional[int] = None
    from_manager_id: Optional[int] = None
    to_department_id: Optional[int] = None
    to_position_id: Optional[int] = None
    to_manager_id: Optional[int] = None


class EmployeeTransferUpdate(BaseModel):
    transfer_type: Optional[str] = None
    effective_date: Optional[SkipValidation[date]] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    salary_change_amount: Optional[Decimal] = None
    salary_change_percentage: Optional[Decimal] = None
    status: Optional[str] = None
    reason: Optional[str] = None


class EmployeeTransferResponse(EmployeeTransferBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: int
    from_department_id: Optional[int] = None
    from_position_id: Optional[int] = None
    from_manager_id: Optional[int] = None
    to_department_id: Optional[int] = None
    to_position_id: Optional[int] = None
    to_manager_id: Optional[int] = None
    status: str
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


class IntegrationAdapterBase(BaseModel):
    adapter_type: str = Field(..., description="Type: sso, payroll_provider, attendance_hardware, erp")
    adapter_name: str = Field(..., description="Adapter name")
    provider: str = Field(..., description="Provider: okta, azure_ad, adp, sap, etc.")
    config: Dict[str, Any] = Field(..., description="Adapter configuration")
    is_active: bool = Field(default=False)
    is_feature_enabled: bool = Field(default=False)


class IntegrationAdapterCreate(IntegrationAdapterBase):
    pass


class IntegrationAdapterUpdate(BaseModel):
    adapter_type: Optional[str] = None
    adapter_name: Optional[str] = None
    provider: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IntegrationAdapterResponse(IntegrationAdapterBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    last_sync_at: Optional[datetime] = None
    sync_status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# =============================================================================
# Export Contract Formats (CSV/JSON)
# =============================================================================

class ExportFormat(BaseModel):
    format: str = Field(default="csv", description="Export format: csv, json, xlsx")
    include_headers: bool = Field(default=True)
    date_format: str = Field(default="%Y-%m-%d")
    decimal_places: int = Field(default=2)


class PayrollExportRequest(BaseModel):
    payroll_period_id: int = Field(..., description="Payroll period to export")
    export_format: ExportFormat = Field(default_factory=ExportFormat)
    include_components: bool = Field(default=True)
    include_deductions: bool = Field(default=True)
    department_ids: Optional[List[int]] = None


class AttendanceExportRequest(BaseModel):
    start_date: SkipValidation[date] = Field(..., description="Start date")
    end_date: SkipValidation[date] = Field(..., description="End date")
    export_format: ExportFormat = Field(default_factory=ExportFormat)
    employee_ids: Optional[List[int]] = None
    department_ids: Optional[List[int]] = None
    include_overtime: bool = Field(default=True)


class LeaveExportRequest(BaseModel):
    start_date: SkipValidation[date] = Field(..., description="Start date")
    end_date: SkipValidation[date] = Field(..., description="End date")
    export_format: ExportFormat = Field(default_factory=ExportFormat)
    employee_ids: Optional[List[int]] = None
    leave_type_ids: Optional[List[int]] = None
    status: Optional[str] = None


class ExportResult(BaseModel):
    success: bool
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    record_count: int = 0
    file_size_bytes: int = 0
    error_message: Optional[str] = None


# =============================================================================
# HR Phase 3 Schemas - Goals/OKRs, Review Cycles, 360 Feedback
# =============================================================================

# Goal Schemas
class GoalBase(BaseModel):
    title: str = Field(..., description="Goal title")
    description: Optional[str] = None
    goal_type: str = Field(default="individual", description="Type: individual, team, department, company")
    category: Optional[str] = None
    is_okr: bool = Field(default=False)
    parent_goal_id: Optional[int] = None
    key_results: Optional[Dict[str, Any]] = None
    start_date: SkipValidation[date] = Field(..., description="Goal start date")
    end_date: SkipValidation[date] = Field(..., description="Goal end date")
    review_cycle_id: Optional[int] = None
    progress_percentage: Decimal = Field(default=Decimal("0"))
    status: str = Field(default="not_started")
    priority: str = Field(default="medium")
    weight: Decimal = Field(default=Decimal("1.0"))
    score: Optional[Decimal] = None
    aligned_to_company_goal: Optional[str] = None
    is_private: bool = Field(default=False)
    shared_with: Optional[Dict[str, Any]] = None


class GoalCreate(GoalBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    goal_type: Optional[str] = None
    category: Optional[str] = None
    key_results: Optional[Dict[str, Any]] = None
    start_date: Optional[SkipValidation[date]] = None
    end_date: Optional[SkipValidation[date]] = None
    progress_percentage: Optional[Decimal] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    weight: Optional[Decimal] = None
    score: Optional[Decimal] = None
    is_private: Optional[bool] = None
    shared_with: Optional[Dict[str, Any]] = None


class GoalResponse(GoalBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Review Cycle Schemas
class ReviewCycleBase(BaseModel):
    name: str = Field(..., description="Review cycle name")
    description: Optional[str] = None
    cycle_type: str = Field(..., description="Type: annual, semi_annual, quarterly, monthly, probation")
    start_date: SkipValidation[date] = Field(..., description="Cycle start date")
    end_date: SkipValidation[date] = Field(..., description="Cycle end date")
    self_review_start: Optional[SkipValidation[date]] = None
    self_review_end: Optional[SkipValidation[date]] = None
    manager_review_start: Optional[SkipValidation[date]] = None
    manager_review_end: Optional[SkipValidation[date]] = None
    peer_review_start: Optional[SkipValidation[date]] = None
    peer_review_end: Optional[SkipValidation[date]] = None
    calibration_start: Optional[SkipValidation[date]] = None
    calibration_end: Optional[SkipValidation[date]] = None
    include_goals: bool = Field(default=True)
    include_competencies: bool = Field(default=True)
    include_360_feedback: bool = Field(default=False)
    allow_self_review: bool = Field(default=True)
    require_manager_approval: bool = Field(default=True)
    rating_scale: Optional[Dict[str, Any]] = None
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    status: str = Field(default="draft")
    is_active: bool = Field(default=True)


class ReviewCycleCreate(ReviewCycleBase):
    pass


class ReviewCycleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cycle_type: Optional[str] = None
    start_date: Optional[SkipValidation[date]] = None
    end_date: Optional[SkipValidation[date]] = None
    self_review_start: Optional[SkipValidation[date]] = None
    self_review_end: Optional[SkipValidation[date]] = None
    manager_review_start: Optional[SkipValidation[date]] = None
    manager_review_end: Optional[SkipValidation[date]] = None
    peer_review_start: Optional[SkipValidation[date]] = None
    peer_review_end: Optional[SkipValidation[date]] = None
    calibration_start: Optional[SkipValidation[date]] = None
    calibration_end: Optional[SkipValidation[date]] = None
    include_goals: Optional[bool] = None
    include_competencies: Optional[bool] = None
    include_360_feedback: Optional[bool] = None
    allow_self_review: Optional[bool] = None
    require_manager_approval: Optional[bool] = None
    rating_scale: Optional[Dict[str, Any]] = None
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class ReviewCycleResponse(ReviewCycleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Feedback Form Schemas
class FeedbackFormBase(BaseModel):
    name: str = Field(..., description="Feedback form name")
    description: Optional[str] = None
    feedback_type: str = Field(..., description="Type: self, manager, peer, subordinate, external")
    is_template: bool = Field(default=False)
    template_id: Optional[int] = None
    review_cycle_id: Optional[int] = None
    questions: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    overall_score: Optional[Decimal] = None
    category_scores: Optional[Dict[str, Any]] = None
    is_anonymous: bool = Field(default=False)
    status: str = Field(default="pending")
    due_date: Optional[SkipValidation[date]] = None


class FeedbackFormCreate(FeedbackFormBase):
    reviewee_id: Optional[int] = None
    reviewer_id: Optional[int] = None


class FeedbackFormUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    feedback_type: Optional[str] = None
    questions: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    overall_score: Optional[Decimal] = None
    category_scores: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    due_date: Optional[SkipValidation[date]] = None


class FeedbackFormResponse(FeedbackFormBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    reviewee_id: Optional[int] = None
    reviewer_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# =============================================================================
# Recruitment Schemas
# =============================================================================

# Job Posting Schemas
class JobPostingBase(BaseModel):
    title: str = Field(..., description="Job title")
    job_code: str = Field(..., description="Unique job code")
    description: str = Field(..., description="Job description")
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    position_id: Optional[int] = None
    department_id: Optional[int] = None
    employment_type: str = Field(default="full_time")
    experience_level: str = Field(default="mid")
    location: Optional[str] = None
    is_remote: bool = Field(default=False)
    work_mode: str = Field(default="onsite")
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: str = Field(default="INR")
    show_salary: bool = Field(default=False)
    num_openings: int = Field(default=1)
    hiring_manager_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    posted_date: Optional[SkipValidation[date]] = None
    closing_date: Optional[SkipValidation[date]] = None
    target_hire_date: Optional[SkipValidation[date]] = None
    status: str = Field(default="draft")
    is_internal: bool = Field(default=False)
    is_confidential: bool = Field(default=False)
    application_form_config: Optional[Dict[str, Any]] = None
    required_documents: Optional[Dict[str, Any]] = None
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None
    qualifications: Optional[Dict[str, Any]] = None


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    title: Optional[str] = None
    job_code: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    position_id: Optional[int] = None
    department_id: Optional[int] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    work_mode: Optional[str] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    show_salary: Optional[bool] = None
    num_openings: Optional[int] = None
    hiring_manager_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    posted_date: Optional[SkipValidation[date]] = None
    closing_date: Optional[SkipValidation[date]] = None
    target_hire_date: Optional[SkipValidation[date]] = None
    status: Optional[str] = None
    is_internal: Optional[bool] = None
    is_confidential: Optional[bool] = None
    required_skills: Optional[Dict[str, Any]] = None
    preferred_skills: Optional[Dict[str, Any]] = None
    qualifications: Optional[Dict[str, Any]] = None


class JobPostingResponse(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Candidate Schemas
class CandidateBase(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = None
    source: Optional[str] = None
    referral_employee_id: Optional[int] = None
    experience_years: Optional[Decimal] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    notice_period_days: Optional[int] = None
    available_from: Optional[SkipValidation[date]] = None
    skills: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    stage: str = Field(default="new")
    overall_rating: Optional[Decimal] = None
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    assigned_recruiter_id: Optional[int] = None
    status: str = Field(default="active")


class CandidateCreate(CandidateBase):
    job_posting_id: int = Field(..., description="Reference to JobPosting")


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    experience_years: Optional[Decimal] = None
    current_company: Optional[str] = None
    current_title: Optional[str] = None
    current_salary: Optional[Decimal] = None
    expected_salary: Optional[Decimal] = None
    notice_period_days: Optional[int] = None
    available_from: Optional[SkipValidation[date]] = None
    skills: Optional[Dict[str, Any]] = None
    education: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    stage: Optional[str] = None
    overall_rating: Optional[Decimal] = None
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    assigned_recruiter_id: Optional[int] = None
    status: Optional[str] = None


class CandidateResponse(CandidateBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    job_posting_id: int
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    documents: Optional[Dict[str, Any]] = None
    application_date: datetime
    stage_updated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Interview Schemas
class InterviewBase(BaseModel):
    interview_type: str = Field(..., description="Type: phone, video, in_person, technical, hr, panel")
    round_number: int = Field(default=1)
    title: str = Field(..., description="Interview title")
    description: Optional[str] = None
    scheduled_date: SkipValidation[date] = Field(..., description="Interview date")
    scheduled_time: time = Field(..., description="Interview time")
    duration_minutes: int = Field(default=60)
    timezone: str = Field(default="Asia/Kolkata")
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    meeting_id: Optional[str] = None
    interviewers: Optional[Dict[str, Any]] = None
    primary_interviewer_id: Optional[int] = None
    feedback: Optional[Dict[str, Any]] = None
    overall_rating: Optional[Decimal] = None
    recommendation: Optional[str] = None
    status: str = Field(default="scheduled")
    candidate_confirmed: bool = Field(default=False)
    calendar_event_id: Optional[str] = None


class InterviewCreate(InterviewBase):
    candidate_id: int = Field(..., description="Reference to Candidate")


class InterviewUpdate(BaseModel):
    interview_type: Optional[str] = None
    round_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_date: Optional[SkipValidation[date]] = None
    scheduled_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewers: Optional[Dict[str, Any]] = None
    primary_interviewer_id: Optional[int] = None
    feedback: Optional[Dict[str, Any]] = None
    overall_rating: Optional[Decimal] = None
    recommendation: Optional[str] = None
    status: Optional[str] = None
    candidate_confirmed: Optional[bool] = None


class InterviewResponse(InterviewBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    candidate_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Job Offer Schemas
class JobOfferBase(BaseModel):
    offer_number: str = Field(..., description="Unique offer number")
    position_title: str = Field(..., description="Position title")
    department_id: Optional[int] = None
    reporting_to_id: Optional[int] = None
    base_salary: Decimal = Field(..., description="Base salary")
    salary_currency: str = Field(default="INR")
    variable_pay: Optional[Decimal] = None
    signing_bonus: Optional[Decimal] = None
    other_benefits: Optional[Dict[str, Any]] = None
    employment_type: str = Field(..., description="Employment type")
    work_location: Optional[str] = None
    work_mode: str = Field(default="onsite")
    probation_months: int = Field(default=6)
    notice_period_days: int = Field(default=30)
    offer_date: SkipValidation[date] = Field(..., description="Offer date")
    expiry_date: SkipValidation[date] = Field(..., description="Offer expiry date")
    proposed_join_date: SkipValidation[date] = Field(..., description="Proposed join date")
    actual_join_date: Optional[SkipValidation[date]] = None
    status: str = Field(default="draft")
    rejection_reason: Optional[str] = None


class JobOfferCreate(JobOfferBase):
    candidate_id: int = Field(..., description="Reference to Candidate")
    job_posting_id: int = Field(..., description="Reference to JobPosting")


class JobOfferUpdate(BaseModel):
    position_title: Optional[str] = None
    department_id: Optional[int] = None
    reporting_to_id: Optional[int] = None
    base_salary: Optional[Decimal] = None
    variable_pay: Optional[Decimal] = None
    signing_bonus: Optional[Decimal] = None
    other_benefits: Optional[Dict[str, Any]] = None
    work_location: Optional[str] = None
    work_mode: Optional[str] = None
    probation_months: Optional[int] = None
    notice_period_days: Optional[int] = None
    expiry_date: Optional[SkipValidation[date]] = None
    proposed_join_date: Optional[SkipValidation[date]] = None
    actual_join_date: Optional[SkipValidation[date]] = None
    status: Optional[str] = None
    rejection_reason: Optional[str] = None


class JobOfferResponse(JobOfferBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    candidate_id: int
    job_posting_id: int
    offer_letter_path: Optional[str] = None
    signed_letter_path: Optional[str] = None
    candidate_response_date: Optional[datetime] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Onboarding Task Schemas
class OnboardingTaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = None
    category: str = Field(default="general")
    is_template: bool = Field(default=False)
    template_id: Optional[int] = None
    due_days_from_joining: int = Field(default=7)
    due_date: Optional[SkipValidation[date]] = None
    completed_date: Optional[SkipValidation[date]] = None
    sequence_order: int = Field(default=0)
    depends_on_task_id: Optional[int] = None
    status: str = Field(default="pending")
    is_mandatory: bool = Field(default=True)
    checklist: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class OnboardingTaskCreate(OnboardingTaskBase):
    employee_id: Optional[int] = None
    assignee_id: Optional[int] = None


class OnboardingTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[SkipValidation[date]] = None
    completed_date: Optional[SkipValidation[date]] = None
    sequence_order: Optional[int] = None
    status: Optional[str] = None
    checklist: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    assignee_id: Optional[int] = None


class OnboardingTaskResponse(OnboardingTaskBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    employee_id: Optional[int] = None
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# =============================================================================
# Compliance & Policies Schemas
# =============================================================================

# Policy Document Schemas
class PolicyDocumentBase(BaseModel):
    title: str = Field(..., description="Policy title")
    code: str = Field(..., description="Policy code")
    description: Optional[str] = None
    category: str = Field(..., description="Category: hr, it, security, compliance, general")
    version: str = Field(default="1.0")
    effective_date: SkipValidation[date] = Field(..., description="Effective date")
    review_date: Optional[SkipValidation[date]] = None
    content: Optional[str] = None
    applicable_to: str = Field(default="all")
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    requires_acknowledgment: bool = Field(default=True)
    acknowledgment_deadline_days: int = Field(default=7)
    re_acknowledgment_period_months: Optional[int] = None
    status: str = Field(default="draft")
    is_active: bool = Field(default=True)


class PolicyDocumentCreate(PolicyDocumentBase):
    pass


class PolicyDocumentUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[SkipValidation[date]] = None
    review_date: Optional[SkipValidation[date]] = None
    content: Optional[str] = None
    applicable_to: Optional[str] = None
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    requires_acknowledgment: Optional[bool] = None
    acknowledgment_deadline_days: Optional[int] = None
    re_acknowledgment_period_months: Optional[int] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class PolicyDocumentResponse(PolicyDocumentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Policy Acknowledgment Schemas
class PolicyAcknowledgmentBase(BaseModel):
    acknowledged_version: str = Field(..., description="Version being acknowledged")
    due_date: SkipValidation[date] = Field(..., description="Acknowledgment due date")
    status: str = Field(default="pending")
    notes: Optional[str] = None


class PolicyAcknowledgmentCreate(PolicyAcknowledgmentBase):
    policy_document_id: int = Field(..., description="Reference to PolicyDocument")
    employee_id: int = Field(..., description="Reference to EmployeeProfile")


class PolicyAcknowledgmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class PolicyAcknowledgmentResponse(PolicyAcknowledgmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    policy_document_id: int
    employee_id: int
    acknowledged_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    digital_signature: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Training Program Schemas
class TrainingProgramBase(BaseModel):
    title: str = Field(..., description="Training title")
    code: str = Field(..., description="Training code")
    description: Optional[str] = None
    category: str = Field(..., description="Category: compliance, technical, soft_skills, leadership, safety")
    training_type: str = Field(default="online")
    duration_hours: Optional[Decimal] = None
    content_url: Optional[str] = None
    materials: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    instructor: Optional[str] = None
    scheduled_date: Optional[SkipValidation[date]] = None
    scheduled_time: Optional[time] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    is_mandatory: bool = Field(default=False)
    applicable_to: str = Field(default="all")
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    provides_certificate: bool = Field(default=False)
    certificate_validity_months: Optional[int] = None
    passing_score: Optional[int] = None
    requires_assessment: bool = Field(default=False)
    status: str = Field(default="draft")
    is_active: bool = Field(default=True)


class TrainingProgramCreate(TrainingProgramBase):
    pass


class TrainingProgramUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    training_type: Optional[str] = None
    duration_hours: Optional[Decimal] = None
    content_url: Optional[str] = None
    materials: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None
    instructor: Optional[str] = None
    scheduled_date: Optional[SkipValidation[date]] = None
    scheduled_time: Optional[time] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None
    is_mandatory: Optional[bool] = None
    applicable_to: Optional[str] = None
    applicable_departments: Optional[Dict[str, Any]] = None
    applicable_positions: Optional[Dict[str, Any]] = None
    provides_certificate: Optional[bool] = None
    certificate_validity_months: Optional[int] = None
    passing_score: Optional[int] = None
    requires_assessment: Optional[bool] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class TrainingProgramResponse(TrainingProgramBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None


# Training Assignment Schemas
class TrainingAssignmentBase(BaseModel):
    assigned_date: SkipValidation[date] = Field(..., description="Assignment date")
    due_date: SkipValidation[date] = Field(..., description="Due date")
    status: str = Field(default="assigned")
    progress_percentage: Decimal = Field(default=Decimal("0"))
    assessment_score: Optional[int] = None
    assessment_attempts: int = Field(default=0)
    passed: Optional[bool] = None
    certificate_issued: bool = Field(default=False)
    certificate_expiry: Optional[SkipValidation[date]] = None
    notes: Optional[str] = None
    exemption_reason: Optional[str] = None


class TrainingAssignmentCreate(TrainingAssignmentBase):
    training_program_id: int = Field(..., description="Reference to TrainingProgram")
    employee_id: int = Field(..., description="Reference to EmployeeProfile")
    assigned_by_id: Optional[int] = None


class TrainingAssignmentUpdate(BaseModel):
    due_date: Optional[SkipValidation[date]] = None
    status: Optional[str] = None
    progress_percentage: Optional[Decimal] = None
    assessment_score: Optional[int] = None
    assessment_attempts: Optional[int] = None
    passed: Optional[bool] = None
    certificate_issued: Optional[bool] = None
    certificate_expiry: Optional[SkipValidation[date]] = None
    notes: Optional[str] = None
    exemption_reason: Optional[str] = None


class TrainingAssignmentResponse(TrainingAssignmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    training_program_id: int
    employee_id: int
    assigned_by_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    certificate_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Compliance Audit Export Schemas
class ComplianceAuditExportBase(BaseModel):
    export_type: str = Field(..., description="Export type")
    export_name: str = Field(..., description="Export name")
    description: Optional[str] = None
    date_from: Optional[SkipValidation[date]] = None
    date_to: Optional[SkipValidation[date]] = None
    filters: Optional[Dict[str, Any]] = None
    file_format: str = Field(default="csv")


class ComplianceAuditExportCreate(ComplianceAuditExportBase):
    pass


class ComplianceAuditExportResponse(ComplianceAuditExportBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    record_count: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    created_by_id: int