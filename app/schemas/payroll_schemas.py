# app/schemas/payroll_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

# Salary Structure Schemas
class SalaryStructureBase(BaseModel):
    structure_name: str = Field(..., description="Salary structure name")
    effective_from: date = Field(..., description="Effective from date")
    effective_to: Optional[date] = None
    is_active: bool = Field(default=True)
    
    # Basic salary components
    basic_salary: Decimal = Field(..., description="Basic salary amount")
    hra: Optional[Decimal] = Field(default=Decimal('0'))
    transport_allowance: Optional[Decimal] = Field(default=Decimal('0'))
    medical_allowance: Optional[Decimal] = Field(default=Decimal('0'))
    special_allowance: Optional[Decimal] = Field(default=Decimal('0'))
    other_allowances: Optional[Decimal] = Field(default=Decimal('0'))
    
    # Deductions
    provident_fund: Optional[Decimal] = Field(default=Decimal('0'))
    professional_tax: Optional[Decimal] = Field(default=Decimal('0'))
    income_tax: Optional[Decimal] = Field(default=Decimal('0'))
    other_deductions: Optional[Decimal] = Field(default=Decimal('0'))
    
    # Calculated totals
    gross_salary: Decimal = Field(..., description="Gross salary amount")
    total_deductions: Decimal = Field(default=Decimal('0'))
    net_salary: Decimal = Field(..., description="Net salary amount")
    
    # Variable components
    variable_components: Optional[Dict[str, Any]] = Field(None, description="Dynamic salary components and calculations. Contains allowances, bonuses, overtime rates, incentives, performance-based pay, reimbursements, statutory deductions (PF, ESI, TDS), and custom pay components with calculation rules.")

class SalaryStructureCreate(SalaryStructureBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")

class SalaryStructureUpdate(BaseModel):
    structure_name: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: Optional[bool] = None
    basic_salary: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    transport_allowance: Optional[Decimal] = None
    medical_allowance: Optional[Decimal] = None
    special_allowance: Optional[Decimal] = None
    other_allowances: Optional[Decimal] = None
    provident_fund: Optional[Decimal] = None
    professional_tax: Optional[Decimal] = None
    income_tax: Optional[Decimal] = None
    other_deductions: Optional[Decimal] = None
    gross_salary: Optional[Decimal] = None
    total_deductions: Optional[Decimal] = None
    net_salary: Optional[Decimal] = None
    variable_components: Optional[Dict[str, Any]] = None

class SalaryStructureResponse(SalaryStructureBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    organization_id: int
    is_approved: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

# Payroll Period Schemas
class PayrollPeriodBase(BaseModel):
    period_name: str = Field(..., description="Payroll period name")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    payroll_date: date = Field(..., description="Actual pay date")
    notes: Optional[str] = None

class PayrollPeriodCreate(PayrollPeriodBase):
    pass

class PayrollPeriodUpdate(BaseModel):
    period_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    payroll_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PayrollPeriodResponse(PayrollPeriodBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    status: str
    total_employees: int
    processed_employees: int
    total_gross_amount: Decimal
    total_deductions: Decimal
    total_net_amount: Decimal
    processed_by_id: Optional[int] = None
    processed_date: Optional[datetime] = None
    finalized_by_id: Optional[int] = None
    finalized_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Payslip Schemas
class PayslipBase(BaseModel):
    payslip_number: str = Field(..., description="Unique payslip number")
    pay_date: date = Field(..., description="Pay date")
    
    # Attendance summary
    working_days: int = Field(..., description="Total working days")
    present_days: int = Field(..., description="Days present")
    absent_days: int = Field(default=0)
    leave_days: int = Field(default=0)
    overtime_hours: Decimal = Field(default=Decimal('0'))
    
    # Earnings
    basic_salary: Decimal = Field(..., description="Basic salary")
    hra: Decimal = Field(default=Decimal('0'))
    transport_allowance: Decimal = Field(default=Decimal('0'))
    medical_allowance: Decimal = Field(default=Decimal('0'))
    special_allowance: Decimal = Field(default=Decimal('0'))
    overtime_amount: Decimal = Field(default=Decimal('0'))
    other_allowances: Decimal = Field(default=Decimal('0'))
    
    # Deductions
    provident_fund: Decimal = Field(default=Decimal('0'))
    professional_tax: Decimal = Field(default=Decimal('0'))
    income_tax: Decimal = Field(default=Decimal('0'))
    loan_deduction: Decimal = Field(default=Decimal('0'))
    other_deductions: Decimal = Field(default=Decimal('0'))
    
    # Calculated totals
    gross_pay: Decimal = Field(..., description="Gross pay amount")
    total_deductions: Decimal = Field(..., description="Total deductions")
    net_pay: Decimal = Field(..., description="Net pay amount")
    
    # Variable components
    variable_earnings: Optional[Dict[str, Any]] = None
    variable_deductions: Optional[Dict[str, Any]] = None

class PayslipCreate(PayslipBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")
    payroll_period_id: int = Field(..., description="Reference to PayrollPeriod")
    salary_structure_id: int = Field(..., description="Reference to SalaryStructure")

class PayslipUpdate(BaseModel):
    working_days: Optional[int] = None
    present_days: Optional[int] = None
    absent_days: Optional[int] = None
    leave_days: Optional[int] = None
    overtime_hours: Optional[Decimal] = None
    basic_salary: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    transport_allowance: Optional[Decimal] = None
    medical_allowance: Optional[Decimal] = None
    special_allowance: Optional[Decimal] = None
    overtime_amount: Optional[Decimal] = None
    other_allowances: Optional[Decimal] = None
    provident_fund: Optional[Decimal] = None
    professional_tax: Optional[Decimal] = None
    income_tax: Optional[Decimal] = None
    loan_deduction: Optional[Decimal] = None
    other_deductions: Optional[Decimal] = None
    gross_pay: Optional[Decimal] = None
    total_deductions: Optional[Decimal] = None
    net_pay: Optional[Decimal] = None
    variable_earnings: Optional[Dict[str, Any]] = None
    variable_deductions: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class PayslipResponse(PayslipBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    payroll_period_id: int
    salary_structure_id: int
    organization_id: int
    status: str
    generated_date: Optional[datetime] = None
    sent_date: Optional[datetime] = None
    acknowledged_date: Optional[datetime] = None
    pdf_path: Optional[str] = None
    email_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Tax Slab Schemas
class TaxSlabBase(BaseModel):
    slab_name: str = Field(..., description="Tax slab name")
    financial_year: str = Field(..., description="Financial year")
    min_amount: Decimal = Field(..., description="Minimum amount for this slab")
    max_amount: Optional[Decimal] = None
    tax_rate: Decimal = Field(..., description="Tax rate percentage")
    tax_regime: str = Field(default="old")
    is_active: bool = Field(default=True)

class TaxSlabCreate(TaxSlabBase):
    pass

class TaxSlabUpdate(BaseModel):
    slab_name: Optional[str] = None
    financial_year: Optional[str] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_regime: Optional[str] = None
    is_active: Optional[bool] = None

class TaxSlabResponse(TaxSlabBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# Employee Loan Schemas
class EmployeeLoanBase(BaseModel):
    loan_type: str = Field(..., description="Type of loan")
    loan_amount: Decimal = Field(..., description="Total loan amount")
    interest_rate: Decimal = Field(default=Decimal('0'))
    tenure_months: int = Field(..., description="Loan tenure in months")
    monthly_deduction: Decimal = Field(..., description="Monthly deduction amount")
    reason: str = Field(..., description="Reason for loan")

class EmployeeLoanCreate(EmployeeLoanBase):
    employee_id: int = Field(..., description="Reference to EmployeeProfile")

class EmployeeLoanUpdate(BaseModel):
    loan_type: Optional[str] = None
    loan_amount: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    tenure_months: Optional[int] = None
    monthly_deduction: Optional[Decimal] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class EmployeeLoanResponse(EmployeeLoanBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    employee_id: int
    organization_id: int
    status: str
    applied_date: date
    approved_date: Optional[date] = None
    disbursed_date: Optional[date] = None
    outstanding_amount: Decimal
    paid_amount: Decimal
    approved_by_id: Optional[int] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Payroll Settings Schemas
class PayrollSettingsBase(BaseModel):
    pay_frequency: str = Field(default="monthly")
    payroll_start_day: int = Field(default=1)
    payroll_cut_off_day: int = Field(default=25)
    working_days_per_month: int = Field(default=30)
    working_hours_per_day: Decimal = Field(default=Decimal('8'))
    overtime_multiplier: Decimal = Field(default=Decimal('1.5'))
    
    # Provident Fund settings
    pf_enabled: bool = Field(default=True)
    employee_pf_rate: Decimal = Field(default=Decimal('12'))
    employer_pf_rate: Decimal = Field(default=Decimal('12'))
    pf_ceiling: Decimal = Field(default=Decimal('15000'))
    
    # Professional Tax settings
    pt_enabled: bool = Field(default=True)
    pt_amount: Decimal = Field(default=Decimal('200'))
    pt_state: str = Field(default="Maharashtra")
    
    # HRA settings
    hra_enabled: bool = Field(default=True)
    hra_percentage: Decimal = Field(default=Decimal('40'))
    metro_hra_percentage: Decimal = Field(default=Decimal('50'))
    
    # Email settings
    auto_send_payslips: bool = Field(default=False)
    payslip_email_template: Optional[str] = None
    
    # Custom settings
    custom_settings: Optional[Dict[str, Any]] = None

class PayrollSettingsCreate(PayrollSettingsBase):
    pass

class PayrollSettingsUpdate(BaseModel):
    pay_frequency: Optional[str] = None
    payroll_start_day: Optional[int] = None
    payroll_cut_off_day: Optional[int] = None
    working_days_per_month: Optional[int] = None
    working_hours_per_day: Optional[Decimal] = None
    overtime_multiplier: Optional[Decimal] = None
    pf_enabled: Optional[bool] = None
    employee_pf_rate: Optional[Decimal] = None
    employer_pf_rate: Optional[Decimal] = None
    pf_ceiling: Optional[Decimal] = None
    pt_enabled: Optional[bool] = None
    pt_amount: Optional[Decimal] = None
    pt_state: Optional[str] = None
    hra_enabled: Optional[bool] = None
    hra_percentage: Optional[Decimal] = None
    metro_hra_percentage: Optional[Decimal] = None
    auto_send_payslips: Optional[bool] = None
    payslip_email_template: Optional[str] = None
    custom_settings: Optional[Dict[str, Any]] = None

class PayrollSettingsResponse(PayrollSettingsBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by_id: Optional[int] = None

# Payroll Dashboard Schemas
class PayrollSummary(BaseModel):
    total_employees: int
    payroll_processed: int
    total_gross_amount: Decimal
    total_deductions: Decimal
    total_net_amount: Decimal
    average_salary: Optional[Decimal] = None

class PayrollDashboard(BaseModel):
    current_period: Optional[PayrollPeriodResponse] = None
    payroll_summary: PayrollSummary
    pending_approvals: int
    pending_payslips: int
    loans_pending_approval: int
    recent_salary_changes: int

# Bulk Processing Schemas
class BulkPayslipGeneration(BaseModel):
    payroll_period_id: int
    employee_ids: Optional[List[int]] = None  # If None, process all employees
    
class PayslipGenerationResult(BaseModel):
    total_employees: int
    successful: int
    failed: int
    errors: List[str] = []

class BulkSalaryUpdate(BaseModel):
    employee_ids: List[int]
    increment_percentage: Optional[Decimal] = None
    increment_amount: Optional[Decimal] = None
    effective_from: date
    
class SalaryUpdateResult(BaseModel):
    total_employees: int
    successful: int
    failed: int
    errors: List[str] = []


# Chart of Accounts Integration Schemas for Payroll

# Chart Account minimal schema for references
class ChartAccountMinimal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    account_code: str
    account_name: str
    account_type: str

# Payroll Component Schemas
class PayrollComponentBase(BaseModel):
    component_name: str = Field(..., description="Component name like Basic Salary, HRA, etc.")
    component_code: str = Field(..., description="Short code like BS, HRA, etc.")
    component_type: str = Field(..., description="Type: earning, deduction, employer_contribution")
    expense_account_id: Optional[int] = Field(None, description="Chart account for expense posting")
    payable_account_id: Optional[int] = Field(None, description="Chart account for payable posting")
    is_active: bool = Field(default=True)
    is_taxable: bool = Field(default=True)
    calculation_formula: Optional[str] = Field(None, description="Formula for dynamic calculations")
    default_amount: Optional[Decimal] = Field(None, description="Default fixed amount")
    default_percentage: Optional[Decimal] = Field(None, description="Default percentage of basic salary")

class PayrollComponentCreate(PayrollComponentBase):
    pass

class PayrollComponentUpdate(BaseModel):
    component_name: Optional[str] = None
    component_code: Optional[str] = None
    component_type: Optional[str] = None
    expense_account_id: Optional[int] = None
    payable_account_id: Optional[int] = None
    is_active: Optional[bool] = None
    is_taxable: Optional[bool] = None
    calculation_formula: Optional[str] = None
    default_amount: Optional[Decimal] = None
    default_percentage: Optional[Decimal] = None

class PayrollComponentResponse(PayrollComponentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    
    # Related accounts
    expense_account: Optional[ChartAccountMinimal] = None
    payable_account: Optional[ChartAccountMinimal] = None

class PayrollComponentList(BaseModel):
    components: List[PayrollComponentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Payroll Run Schemas
class PayrollRunBase(BaseModel):
    run_name: str = Field(..., description="Payroll run name")
    run_date: date = Field(..., description="Run date")
    notes: Optional[str] = Field(None, description="Run notes")

class PayrollRunCreate(PayrollRunBase):
    period_id: int = Field(..., description="Reference to payroll period")

class PayrollRunUpdate(BaseModel):
    run_name: Optional[str] = None
    run_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class PayrollRunResponse(PayrollRunBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    period_id: int
    status: str
    total_employees: int
    processed_employees: int
    total_gross_amount: Decimal
    total_deductions: Decimal
    total_net_amount: Decimal
    gl_posted: bool
    gl_posted_at: Optional[datetime] = None
    gl_reversal_voucher_id: Optional[int] = None
    total_expense_amount: Decimal
    total_payable_amount: Decimal
    payment_vouchers_generated: bool
    payment_date: Optional[date] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[int] = None

class PayrollRunList(BaseModel):
    runs: List[PayrollRunResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

# Payroll Line Schemas
class PayrollLineBase(BaseModel):
    line_type: str = Field(..., description="Type: expense, payable")
    amount: Decimal = Field(..., description="Line amount")
    posting_type: str = Field(..., description="Posting type: debit, credit")
    description: str = Field(..., description="Line description")

class PayrollLineCreate(PayrollLineBase):
    employee_id: int = Field(..., description="Reference to employee")
    component_id: int = Field(..., description="Reference to payroll component")
    chart_account_id: int = Field(..., description="Reference to chart account")

class PayrollLineResponse(PayrollLineBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    payroll_run_id: int
    employee_id: int
    component_id: int
    chart_account_id: int
    gl_entry_id: Optional[int] = None
    journal_voucher_id: Optional[int] = None
    created_at: datetime

# GL Posting Schemas
class GLPreviewLine(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    debit_amount: Decimal
    credit_amount: Decimal
    description: str

class PayrollGLPreview(BaseModel):
    payroll_run_id: int
    total_debit: Decimal
    total_credit: Decimal
    lines: List[GLPreviewLine]
    is_balanced: bool

class PayrollGLPosting(BaseModel):
    payroll_run_id: int
    posting_date: date = Field(..., description="GL posting date")
    reference_number: Optional[str] = Field(None, description="Reference voucher number")
    narration: Optional[str] = Field(None, description="Posting narration")

class PayrollGLPostingResult(BaseModel):
    success: bool
    message: str
    journal_voucher_id: Optional[int] = None
    gl_entries_created: int
    total_amount: Decimal

# Chart Account Filtering Schemas
class PayrollEligibleAccountsFilter(BaseModel):
    account_types: Optional[List[str]] = Field(["expense", "liability"], description="Account types for payroll")
    component_type: Optional[str] = Field(None, description="Filter by component type")
    is_active: Optional[bool] = Field(True, description="Filter active accounts")

class PayrollAccountMapping(BaseModel):
    component_id: int
    expense_account_id: Optional[int] = None
    payable_account_id: Optional[int] = None