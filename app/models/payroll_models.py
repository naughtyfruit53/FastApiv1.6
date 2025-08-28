# app/models/payroll_models.py

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Index, UniqueConstraint, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

# Salary Structure Management
class SalaryStructure(Base):
    """Employee salary structure and components"""
    __tablename__ = "salary_structures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_salary_structure_organization_id"), nullable=False, index=True)
    
    # Employee reference
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_salary_structure_employee_id"), nullable=False, index=True)
    
    # Structure details
    structure_name: Mapped[str] = mapped_column(String, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Basic salary components
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    hra: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    transport_allowance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    medical_allowance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    special_allowance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    other_allowances: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    
    # Deductions
    provident_fund: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    professional_tax: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    income_tax: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    other_deductions: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True, default=0)
    
    # Calculated totals
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Variable components
    variable_components: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Flexible allowances/deductions
    
    # Approval workflow
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_salary_structure_approved_by_id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_salary_structure_created_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile", back_populates="salary_records")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[approved_by_id])
    created_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[created_by_id])
    
    # Payroll relationships
    payslips: Mapped[List["Payslip"]] = relationship("Payslip", back_populates="salary_structure")

    __table_args__ = (
        Index('idx_salary_structure_org_employee', 'organization_id', 'employee_id'),
        Index('idx_salary_structure_effective', 'effective_from', 'effective_to'),
        Index('idx_salary_structure_active', 'is_active'),
        {'extend_existing': True}
    )

# Payroll Processing
class PayrollPeriod(Base):
    """Monthly payroll processing periods"""
    __tablename__ = "payroll_periods"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_payroll_period_organization_id"), nullable=False, index=True)
    
    # Period details
    period_name: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "January 2024"
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    payroll_date: Mapped[date] = mapped_column(Date, nullable=False)  # Actual pay date
    
    # Processing status
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, processing, processed, finalized
    total_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_employees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Financial totals
    total_gross_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total_net_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Processing details
    processed_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_payroll_period_processed_by_id"), nullable=True)
    processed_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finalized_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_payroll_period_finalized_by_id"), nullable=True)
    finalized_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Notes and comments
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    processed_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[processed_by_id])
    finalized_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User", foreign_keys=[finalized_by_id])
    
    # Payroll relationships
    payslips: Mapped[List["Payslip"]] = relationship("Payslip", back_populates="payroll_period")

    __table_args__ = (
        UniqueConstraint('organization_id', 'period_start', 'period_end', name='uq_payroll_period_org_dates'),
        Index('idx_payroll_period_org_status', 'organization_id', 'status'),
        Index('idx_payroll_period_dates', 'period_start', 'period_end'),
        {'extend_existing': True}
    )

# Payslip Generation
class Payslip(Base):
    """Individual employee payslips"""
    __tablename__ = "payslips"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_payslip_organization_id"), nullable=False, index=True)
    
    # References
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_payslip_employee_id"), nullable=False, index=True)
    payroll_period_id: Mapped[int] = mapped_column(Integer, ForeignKey("payroll_periods.id", name="fk_payslip_payroll_period_id"), nullable=False, index=True)
    salary_structure_id: Mapped[int] = mapped_column(Integer, ForeignKey("salary_structures.id", name="fk_payslip_salary_structure_id"), nullable=False, index=True)
    
    # Payslip details
    payslip_number: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    pay_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Attendance summary
    working_days: Mapped[int] = mapped_column(Integer, nullable=False)
    present_days: Mapped[int] = mapped_column(Integer, nullable=False)
    absent_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leave_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    
    # Earnings
    basic_salary: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    hra: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    transport_allowance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    medical_allowance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    special_allowance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    overtime_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    other_allowances: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Deductions
    provident_fund: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    professional_tax: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    income_tax: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    loan_deduction: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    other_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Calculated totals
    gross_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    net_pay: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Variable components (JSON for flexibility)
    variable_earnings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    variable_deductions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status and processing
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")  # draft, generated, sent, acknowledged
    generated_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Document management
    pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile")
    payroll_period: Mapped["PayrollPeriod"] = relationship("PayrollPeriod", back_populates="payslips")
    salary_structure: Mapped["SalaryStructure"] = relationship("SalaryStructure", back_populates="payslips")

    __table_args__ = (
        UniqueConstraint('organization_id', 'employee_id', 'payroll_period_id', name='uq_payslip_org_emp_period'),
        Index('idx_payslip_org_employee', 'organization_id', 'employee_id'),
        Index('idx_payslip_period', 'payroll_period_id'),
        Index('idx_payslip_status', 'status'),
        {'extend_existing': True}
    )

# Tax Configuration
class TaxSlab(Base):
    """Income tax slabs configuration"""
    __tablename__ = "tax_slabs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_tax_slab_organization_id"), nullable=False, index=True)
    
    # Tax slab details
    slab_name: Mapped[str] = mapped_column(String, nullable=False)
    financial_year: Mapped[str] = mapped_column(String, nullable=False)  # e.g., "2023-24"
    min_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    max_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)  # NULL for highest slab
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # Percentage
    
    # Slab type
    tax_regime: Mapped[str] = mapped_column(String, nullable=False, default="old")  # old, new
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")

    __table_args__ = (
        Index('idx_tax_slab_org_year', 'organization_id', 'financial_year'),
        Index('idx_tax_slab_regime', 'tax_regime'),
        {'extend_existing': True}
    )

# Loan and Advance Management
class EmployeeLoan(Base):
    """Employee loans and advances"""
    __tablename__ = "employee_loans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_employee_loan_organization_id"), nullable=False, index=True)
    
    # Employee reference
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employee_profiles.id", name="fk_employee_loan_employee_id"), nullable=False, index=True)
    
    # Loan details
    loan_type: Mapped[str] = mapped_column(String, nullable=False)  # salary_advance, personal_loan, emergency_loan
    loan_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)  # Annual percentage
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_deduction: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Loan status
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")  # pending, approved, disbursed, closed
    applied_date: Mapped[date] = mapped_column(Date, nullable=False)
    approved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    disbursed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Outstanding details
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    
    # Approval workflow
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_employee_loan_approved_by_id"), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    employee: Mapped["app.models.hr_models.EmployeeProfile"] = relationship("app.models.hr_models.EmployeeProfile")
    approved_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")

    __table_args__ = (
        Index('idx_employee_loan_org_employee', 'organization_id', 'employee_id'),
        Index('idx_employee_loan_status', 'status'),
        Index('idx_employee_loan_dates', 'applied_date', 'disbursed_date'),
        {'extend_existing': True}
    )

# Payroll Integration Settings
class PayrollSettings(Base):
    """Organization-wide payroll configuration"""
    __tablename__ = "payroll_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Multi-tenant field (one record per organization)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id", name="fk_payroll_settings_organization_id"), nullable=False, unique=True, index=True)
    
    # General settings
    pay_frequency: Mapped[str] = mapped_column(String, nullable=False, default="monthly")  # monthly, bi_weekly, weekly
    payroll_start_day: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # Day of month for payroll start
    payroll_cut_off_day: Mapped[int] = mapped_column(Integer, nullable=False, default=25)  # Cut-off day for attendance
    
    # Default calculations
    working_days_per_month: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    working_hours_per_day: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False, default=8)
    overtime_multiplier: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False, default=1.5)
    
    # Provident Fund settings
    pf_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    employee_pf_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=12)  # Percentage
    employer_pf_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=12)
    pf_ceiling: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False, default=15000)  # Monthly ceiling
    
    # Professional Tax settings
    pt_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    pt_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=200)  # Fixed amount
    pt_state: Mapped[str] = mapped_column(String, nullable=False, default="Maharashtra")
    
    # HRA settings
    hra_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    hra_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=40)  # Percentage of basic
    metro_hra_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=50)
    
    # Email settings
    auto_send_payslips: Mapped[bool] = mapped_column(Boolean, default=False)
    payslip_email_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Custom settings (JSON for flexibility)
    custom_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    updated_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", name="fk_payroll_settings_updated_by_id"), nullable=True)

    # Relationships
    organization: Mapped["app.models.user_models.Organization"] = relationship("app.models.user_models.Organization")
    updated_by: Mapped[Optional["app.models.user_models.User"]] = relationship("app.models.user_models.User")

    __table_args__ = (
        {'extend_existing': True}
    )