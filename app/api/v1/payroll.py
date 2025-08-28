# app/api/v1/payroll.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user_models import User
from app.models.hr_models import EmployeeProfile, AttendanceRecord
from app.models.payroll_models import (
    SalaryStructure, PayrollPeriod, Payslip, TaxSlab, 
    EmployeeLoan, PayrollSettings
)
from app.schemas.payroll_schemas import (
    SalaryStructureCreate, SalaryStructureUpdate, SalaryStructureResponse,
    PayrollPeriodCreate, PayrollPeriodUpdate, PayrollPeriodResponse,
    PayslipCreate, PayslipUpdate, PayslipResponse,
    TaxSlabCreate, TaxSlabUpdate, TaxSlabResponse,
    EmployeeLoanCreate, EmployeeLoanUpdate, EmployeeLoanResponse,
    PayrollSettingsCreate, PayrollSettingsUpdate, PayrollSettingsResponse,
    PayrollDashboard, PayrollSummary,
    BulkPayslipGeneration, PayslipGenerationResult,
    BulkSalaryUpdate, SalaryUpdateResult
)

router = APIRouter(prefix="/payroll", tags=["Payroll"])

# Salary Structure Management
@router.post("/salary-structures", response_model=SalaryStructureResponse)
async def create_salary_structure(
    salary_data: SalaryStructureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new salary structure for an employee"""
    
    # Verify employee exists and belongs to organization
    employee = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.id == salary_data.employee_id,
            EmployeeProfile.organization_id == current_user.organization_id
        )
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check for overlapping active salary structures
    overlapping_structure = db.query(SalaryStructure).filter(
        and_(
            SalaryStructure.organization_id == current_user.organization_id,
            SalaryStructure.employee_id == salary_data.employee_id,
            SalaryStructure.is_active == True,
            or_(
                SalaryStructure.effective_to.is_(None),
                SalaryStructure.effective_to >= salary_data.effective_from
            ),
            SalaryStructure.effective_from <= salary_data.effective_to if salary_data.effective_to else True
        )
    ).first()
    
    if overlapping_structure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping salary structure exists for this period"
        )
    
    salary_structure = SalaryStructure(
        **salary_data.model_dump(),
        organization_id=current_user.organization_id,
        created_by_id=current_user.id
    )
    
    db.add(salary_structure)
    db.commit()
    db.refresh(salary_structure)
    
    return salary_structure

@router.get("/salary-structures", response_model=List[SalaryStructureResponse])
async def get_salary_structures(
    employee_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get salary structures with filtering"""
    
    query = db.query(SalaryStructure).filter(
        SalaryStructure.organization_id == current_user.organization_id
    )
    
    if employee_id:
        query = query.filter(SalaryStructure.employee_id == employee_id)
    
    if is_active is not None:
        query = query.filter(SalaryStructure.is_active == is_active)
    
    query = query.order_by(desc(SalaryStructure.effective_from))
    
    structures = query.offset(skip).limit(limit).all()
    return structures

@router.put("/salary-structures/{structure_id}", response_model=SalaryStructureResponse)
async def update_salary_structure(
    structure_id: int,
    salary_data: SalaryStructureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update salary structure"""
    
    structure = db.query(SalaryStructure).filter(
        and_(
            SalaryStructure.id == structure_id,
            SalaryStructure.organization_id == current_user.organization_id
        )
    ).first()
    
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary structure not found"
        )
    
    # Update fields
    for field, value in salary_data.model_dump(exclude_unset=True).items():
        setattr(structure, field, value)
    
    db.commit()
    db.refresh(structure)
    
    return structure

@router.put("/salary-structures/{structure_id}/approve")
async def approve_salary_structure(
    structure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve salary structure"""
    
    structure = db.query(SalaryStructure).filter(
        and_(
            SalaryStructure.id == structure_id,
            SalaryStructure.organization_id == current_user.organization_id
        )
    ).first()
    
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary structure not found"
        )
    
    structure.is_approved = True
    structure.approved_by_id = current_user.id
    structure.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Salary structure approved successfully"}

# Payroll Period Management
@router.post("/periods", response_model=PayrollPeriodResponse)
async def create_payroll_period(
    period_data: PayrollPeriodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payroll period"""
    
    # Check for overlapping periods
    overlapping_period = db.query(PayrollPeriod).filter(
        and_(
            PayrollPeriod.organization_id == current_user.organization_id,
            or_(
                and_(
                    PayrollPeriod.period_start <= period_data.period_start,
                    PayrollPeriod.period_end >= period_data.period_start
                ),
                and_(
                    PayrollPeriod.period_start <= period_data.period_end,
                    PayrollPeriod.period_end >= period_data.period_end
                )
            )
        )
    ).first()
    
    if overlapping_period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping payroll period exists"
        )
    
    payroll_period = PayrollPeriod(
        **period_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(payroll_period)
    db.commit()
    db.refresh(payroll_period)
    
    return payroll_period

@router.get("/periods", response_model=List[PayrollPeriodResponse])
async def get_payroll_periods(
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payroll periods with filtering"""
    
    query = db.query(PayrollPeriod).filter(
        PayrollPeriod.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(PayrollPeriod.status == status)
    
    if year:
        query = query.filter(extract('year', PayrollPeriod.period_start) == year)
    
    query = query.order_by(desc(PayrollPeriod.period_start))
    
    periods = query.offset(skip).limit(limit).all()
    return periods

@router.put("/periods/{period_id}/process")
async def process_payroll_period(
    period_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payroll for a period"""
    
    period = db.query(PayrollPeriod).filter(
        and_(
            PayrollPeriod.id == period_id,
            PayrollPeriod.organization_id == current_user.organization_id
        )
    ).first()
    
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll period not found"
        )
    
    if period.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft periods can be processed"
        )
    
    # Count eligible employees
    employees = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employment_status == "active"
        )
    ).all()
    
    period.status = "processing"
    period.total_employees = len(employees)
    period.processed_by_id = current_user.id
    period.processed_date = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Payroll processing started for {len(employees)} employees"}

# Payslip Management
@router.post("/payslips", response_model=PayslipResponse)
async def create_payslip(
    payslip_data: PayslipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new payslip"""
    
    # Check if payslip already exists for this employee and period
    existing_payslip = db.query(Payslip).filter(
        and_(
            Payslip.organization_id == current_user.organization_id,
            Payslip.employee_id == payslip_data.employee_id,
            Payslip.payroll_period_id == payslip_data.payroll_period_id
        )
    ).first()
    
    if existing_payslip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payslip already exists for this employee and period"
        )
    
    payslip = Payslip(
        **payslip_data.model_dump(),
        organization_id=current_user.organization_id
    )
    
    db.add(payslip)
    db.commit()
    db.refresh(payslip)
    
    return payslip

@router.get("/payslips", response_model=List[PayslipResponse])
async def get_payslips(
    employee_id: Optional[int] = Query(None),
    payroll_period_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payslips with filtering"""
    
    query = db.query(Payslip).filter(
        Payslip.organization_id == current_user.organization_id
    )
    
    if employee_id:
        query = query.filter(Payslip.employee_id == employee_id)
    
    if payroll_period_id:
        query = query.filter(Payslip.payroll_period_id == payroll_period_id)
    
    if status:
        query = query.filter(Payslip.status == status)
    
    query = query.order_by(desc(Payslip.pay_date))
    
    payslips = query.offset(skip).limit(limit).all()
    return payslips

@router.post("/payslips/bulk-generate", response_model=PayslipGenerationResult)
async def bulk_generate_payslips(
    generation_data: BulkPayslipGeneration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk generate payslips for a payroll period"""
    
    # Verify payroll period exists
    period = db.query(PayrollPeriod).filter(
        and_(
            PayrollPeriod.id == generation_data.payroll_period_id,
            PayrollPeriod.organization_id == current_user.organization_id
        )
    ).first()
    
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll period not found"
        )
    
    # Get employees to process
    query = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employment_status == "active"
        )
    )
    
    if generation_data.employee_ids:
        query = query.filter(EmployeeProfile.id.in_(generation_data.employee_ids))
    
    employees = query.all()
    
    successful = 0
    failed = 0
    errors = []
    
    for employee in employees:
        try:
            # Check if payslip already exists
            existing_payslip = db.query(Payslip).filter(
                and_(
                    Payslip.organization_id == current_user.organization_id,
                    Payslip.employee_id == employee.id,
                    Payslip.payroll_period_id == generation_data.payroll_period_id
                )
            ).first()
            
            if existing_payslip:
                errors.append(f"Payslip already exists for employee {employee.employee_code}")
                failed += 1
                continue
            
            # Get latest salary structure
            salary_structure = db.query(SalaryStructure).filter(
                and_(
                    SalaryStructure.organization_id == current_user.organization_id,
                    SalaryStructure.employee_id == employee.id,
                    SalaryStructure.is_active == True,
                    SalaryStructure.is_approved == True,
                    SalaryStructure.effective_from <= period.period_end
                )
            ).order_by(desc(SalaryStructure.effective_from)).first()
            
            if not salary_structure:
                errors.append(f"No approved salary structure found for employee {employee.employee_code}")
                failed += 1
                continue
            
            # Calculate attendance data
            attendance_records = db.query(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.organization_id == current_user.organization_id,
                    AttendanceRecord.employee_id == employee.id,
                    AttendanceRecord.attendance_date >= period.period_start,
                    AttendanceRecord.attendance_date <= period.period_end
                )
            ).all()
            
            working_days = (period.period_end - period.period_start).days + 1
            present_days = len([r for r in attendance_records if r.attendance_status == "present"])
            absent_days = len([r for r in attendance_records if r.attendance_status == "absent"])
            leave_days = len([r for r in attendance_records if r.attendance_status == "on_leave"])
            overtime_hours = sum([r.overtime_hours or Decimal('0') for r in attendance_records])
            
            # Generate unique payslip number
            payslip_number = f"PS-{period.period_name.replace(' ', '')}-{employee.employee_code}"
            
            # Create payslip
            payslip = Payslip(
                organization_id=current_user.organization_id,
                employee_id=employee.id,
                payroll_period_id=generation_data.payroll_period_id,
                salary_structure_id=salary_structure.id,
                payslip_number=payslip_number,
                pay_date=period.payroll_date,
                working_days=working_days,
                present_days=present_days,
                absent_days=absent_days,
                leave_days=leave_days,
                overtime_hours=overtime_hours,
                basic_salary=salary_structure.basic_salary,
                hra=salary_structure.hra,
                transport_allowance=salary_structure.transport_allowance,
                medical_allowance=salary_structure.medical_allowance,
                special_allowance=salary_structure.special_allowance,
                other_allowances=salary_structure.other_allowances,
                provident_fund=salary_structure.provident_fund,
                professional_tax=salary_structure.professional_tax,
                income_tax=salary_structure.income_tax,
                other_deductions=salary_structure.other_deductions,
                gross_pay=salary_structure.gross_salary,
                total_deductions=salary_structure.total_deductions,
                net_pay=salary_structure.net_salary,
                status="generated",
                generated_date=datetime.utcnow()
            )
            
            db.add(payslip)
            successful += 1
            
        except Exception as e:
            errors.append(f"Error generating payslip for employee {employee.employee_code}: {str(e)}")
            failed += 1
    
    # Update period statistics
    period.processed_employees = successful
    period.total_gross_amount = db.query(func.sum(Payslip.gross_pay)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ).scalar() or Decimal('0')
    period.total_deductions = db.query(func.sum(Payslip.total_deductions)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ).scalar() or Decimal('0')
    period.total_net_amount = db.query(func.sum(Payslip.net_pay)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ).scalar() or Decimal('0')
    
    if successful > 0:
        period.status = "processed"
    
    db.commit()
    
    return PayslipGenerationResult(
        total_employees=len(employees),
        successful=successful,
        failed=failed,
        errors=errors
    )

# Employee Loan Management
@router.post("/loans", response_model=EmployeeLoanResponse)
async def create_employee_loan(
    loan_data: EmployeeLoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new employee loan application"""
    
    loan = EmployeeLoan(
        **loan_data.model_dump(),
        organization_id=current_user.organization_id,
        outstanding_amount=loan_data.loan_amount,
        applied_date=date.today()
    )
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    return loan

@router.get("/loans", response_model=List[EmployeeLoanResponse])
async def get_employee_loans(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    loan_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee loans with filtering"""
    
    query = db.query(EmployeeLoan).filter(
        EmployeeLoan.organization_id == current_user.organization_id
    )
    
    if employee_id:
        query = query.filter(EmployeeLoan.employee_id == employee_id)
    
    if status:
        query = query.filter(EmployeeLoan.status == status)
    
    if loan_type:
        query = query.filter(EmployeeLoan.loan_type == loan_type)
    
    query = query.order_by(desc(EmployeeLoan.applied_date))
    
    loans = query.offset(skip).limit(limit).all()
    return loans

@router.put("/loans/{loan_id}/approve")
async def approve_employee_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve an employee loan"""
    
    loan = db.query(EmployeeLoan).filter(
        and_(
            EmployeeLoan.id == loan_id,
            EmployeeLoan.organization_id == current_user.organization_id
        )
    ).first()
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    if loan.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending loans can be approved"
        )
    
    loan.status = "approved"
    loan.approved_by_id = current_user.id
    loan.approved_date = date.today()
    
    db.commit()
    
    return {"message": "Loan approved successfully"}

# Payroll Settings Management
@router.get("/settings", response_model=PayrollSettingsResponse)
async def get_payroll_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization payroll settings"""
    
    settings = db.query(PayrollSettings).filter(
        PayrollSettings.organization_id == current_user.organization_id
    ).first()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll settings not found"
        )
    
    return settings

@router.put("/settings", response_model=PayrollSettingsResponse)
async def update_payroll_settings(
    settings_data: PayrollSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization payroll settings"""
    
    settings = db.query(PayrollSettings).filter(
        PayrollSettings.organization_id == current_user.organization_id
    ).first()
    
    if not settings:
        # Create new settings if not exist
        settings = PayrollSettings(
            organization_id=current_user.organization_id,
            **settings_data.model_dump(exclude_unset=True)
        )
        db.add(settings)
    else:
        # Update existing settings
        for field, value in settings_data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
    
    settings.updated_by_id = current_user.id
    
    db.commit()
    db.refresh(settings)
    
    return settings

# Dashboard
@router.get("/dashboard", response_model=PayrollDashboard)
async def get_payroll_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payroll dashboard summary"""
    
    # Get current/latest payroll period
    current_period = db.query(PayrollPeriod).filter(
        PayrollPeriod.organization_id == current_user.organization_id
    ).order_by(desc(PayrollPeriod.period_start)).first()
    
    # Payroll summary
    total_employees = db.query(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == current_user.organization_id,
            EmployeeProfile.employment_status == "active"
        )
    ).count()
    
    if current_period:
        payroll_processed = db.query(Payslip).filter(
            and_(
                Payslip.organization_id == current_user.organization_id,
                Payslip.payroll_period_id == current_period.id
            )
        ).count()
        
        totals = db.query(
            func.sum(Payslip.gross_pay).label('total_gross'),
            func.sum(Payslip.total_deductions).label('total_deductions'),
            func.sum(Payslip.net_pay).label('total_net'),
            func.avg(Payslip.net_pay).label('avg_salary')
        ).filter(
            and_(
                Payslip.organization_id == current_user.organization_id,
                Payslip.payroll_period_id == current_period.id
            )
        ).first()
    else:
        payroll_processed = 0
        totals = type('obj', (object,), {
            'total_gross': Decimal('0'),
            'total_deductions': Decimal('0'),
            'total_net': Decimal('0'),
            'avg_salary': None
        })
    
    # Pending items
    pending_approvals = db.query(SalaryStructure).filter(
        and_(
            SalaryStructure.organization_id == current_user.organization_id,
            SalaryStructure.is_approved == False
        )
    ).count()
    
    pending_payslips = db.query(Payslip).filter(
        and_(
            Payslip.organization_id == current_user.organization_id,
            Payslip.status == "draft"
        )
    ).count()
    
    loans_pending_approval = db.query(EmployeeLoan).filter(
        and_(
            EmployeeLoan.organization_id == current_user.organization_id,
            EmployeeLoan.status == "pending"
        )
    ).count()
    
    # Recent salary changes (last 30 days)
    last_month = date.today() - timedelta(days=30)
    recent_salary_changes = db.query(SalaryStructure).filter(
        and_(
            SalaryStructure.organization_id == current_user.organization_id,
            SalaryStructure.created_at >= last_month
        )
    ).count()
    
    payroll_summary = PayrollSummary(
        total_employees=total_employees,
        payroll_processed=payroll_processed,
        total_gross_amount=totals.total_gross or Decimal('0'),
        total_deductions=totals.total_deductions or Decimal('0'),
        total_net_amount=totals.total_net or Decimal('0'),
        average_salary=totals.avg_salary
    )
    
    return PayrollDashboard(
        current_period=current_period,
        payroll_summary=payroll_summary,
        pending_approvals=pending_approvals,
        pending_payslips=pending_payslips,
        loans_pending_approval=loans_pending_approval,
        recent_salary_changes=recent_salary_changes
    )