# app/api/v1/payroll.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, func, extract
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.enforcement import require_access
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
    auth: tuple = Depends(require_access("payroll", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new salary structure for an employee"""
    current_user, org_id = auth
    
    # Verify employee exists and belongs to organization
    result = await db.execute(select(EmployeeProfile).filter(
        and_(
            EmployeeProfile.id == salary_data.employee_id,
            EmployeeProfile.organization_id == org_id
        )
    ))
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check for overlapping active salary structures
    result = await db.execute(select(SalaryStructure).filter(
        and_(
            SalaryStructure.organization_id == org_id,
            SalaryStructure.employee_id == salary_data.employee_id,
            SalaryStructure.is_active == True,
            or_(
                SalaryStructure.effective_to.is_(None),
                SalaryStructure.effective_to >= salary_data.effective_from
            ),
            SalaryStructure.effective_from <= salary_data.effective_to if salary_data.effective_to else True
        )
    ))
    overlapping_structure = result.scalar_one_or_none()
    
    if overlapping_structure:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping salary structure exists for this period"
        )
    
    salary_structure = SalaryStructure(
        **salary_data.model_dump(),
        organization_id=org_id,
        created_by_id=current_user.id
    )
    
    db.add(salary_structure)
    await db.commit()
    await db.refresh(salary_structure)
    
    return salary_structure

@router.get("/salary-structures", response_model=List[SalaryStructureResponse])
async def get_salary_structures(
    employee_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get salary structures with filtering"""
    current_user, org_id = auth
    
    stmt = select(SalaryStructure).filter(
        SalaryStructure.organization_id == org_id
    )
    
    if employee_id:
        stmt = stmt.filter(SalaryStructure.employee_id == employee_id)
    
    if is_active is not None:
        stmt = stmt.filter(SalaryStructure.is_active == is_active)
    
    stmt = stmt.order_by(desc(SalaryStructure.effective_from))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    structures = result.scalars().all()
    return structures

@router.put("/salary-structures/{structure_id}", response_model=SalaryStructureResponse)
async def update_salary_structure(
    structure_id: int,
    salary_data: SalaryStructureUpdate,
    auth: tuple = Depends(require_access("payroll", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update salary structure"""
    current_user, org_id = auth
    
    result = await db.execute(select(SalaryStructure).filter(
        and_(
            SalaryStructure.id == structure_id,
            SalaryStructure.organization_id == org_id
        )
    ))
    structure = result.scalar_one_or_none()
    
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary structure not found"
        )
    
    # Update fields
    for field, value in salary_data.model_dump(exclude_unset=True).items():
        setattr(structure, field, value)
    
    await db.commit()
    await db.refresh(structure)
    
    return structure

@router.put("/salary-structures/{structure_id}/approve")
async def approve_salary_structure(
    structure_id: int,
    auth: tuple = Depends(require_access("payroll", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve salary structure"""
    current_user, org_id = auth
    
    result = await db.execute(select(SalaryStructure).filter(
        and_(
            SalaryStructure.id == structure_id,
            SalaryStructure.organization_id == org_id
        )
    ))
    structure = result.scalar_one_or_none()
    
    if not structure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary structure not found"
        )
    
    structure.is_approved = True
    structure.approved_by_id = current_user.id
    structure.approved_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Salary structure approved successfully"}

# Payroll Period Management
@router.post("/periods", response_model=PayrollPeriodResponse)
async def create_payroll_period(
    period_data: PayrollPeriodCreate,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payroll period"""
    current_user, org_id = auth
    
    # Check for overlapping periods
    result = await db.execute(select(PayrollPeriod).filter(
        and_(
            PayrollPeriod.organization_id == org_id,
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
    ))
    overlapping_period = result.scalar_one_or_none()
    
    if overlapping_period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping payroll period exists"
        )
    
    payroll_period = PayrollPeriod(
        **period_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(payroll_period)
    await db.commit()
    await db.refresh(payroll_period)
    
    return payroll_period

@router.get("/periods", response_model=List[PayrollPeriodResponse])
async def get_payroll_periods(
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll periods with filtering"""
    current_user, org_id = auth
    
    stmt = select(PayrollPeriod).filter(
        PayrollPeriod.organization_id == org_id
    )
    
    if status:
        stmt = stmt.filter(PayrollPeriod.status == status)
    
    if year:
        stmt = stmt.filter(extract('year', PayrollPeriod.period_start) == year)
    
    stmt = stmt.order_by(desc(PayrollPeriod.period_start))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    periods = result.scalars().all()
    return periods

@router.put("/periods/{period_id}/process")
async def process_payroll_period(
    period_id: int,
    auth: tuple = Depends(require_access("payroll", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Process payroll for a period"""
    current_user, org_id = auth
    
    result = await db.execute(select(PayrollPeriod).filter(
        and_(
            PayrollPeriod.id == period_id,
            PayrollPeriod.organization_id == org_id
        )
    ))
    period = result.scalar_one_or_none()
    
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
    result = await db.execute(select(func.count(EmployeeProfile.id)).filter(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employment_status == "active"
        )
    ))
    total_employees = result.scalar()
    
    period.status = "processing"
    period.total_employees = total_employees
    period.processed_by_id = current_user.id
    period.processed_date = datetime.utcnow()
    
    await db.commit()
    
    return {"message": f"Payroll processing started for {total_employees} employees"}

# Payslip Management
@router.post("/payslips", response_model=PayslipResponse)
async def create_payslip(
    payslip_data: PayslipCreate,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new payslip"""
    current_user, org_id = auth
    
    # Check if payslip already exists for this employee and period
    result = await db.execute(select(Payslip).filter(
        and_(
            Payslip.organization_id == org_id,
            Payslip.employee_id == payslip_data.employee_id,
            Payslip.payroll_period_id == payslip_data.payroll_period_id
        )
    ))
    existing_payslip = result.scalar_one_or_none()
    
    if existing_payslip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payslip already exists for this employee and period"
        )
    
    payslip = Payslip(
        **payslip_data.model_dump(),
        organization_id=org_id
    )
    
    db.add(payslip)
    await db.commit()
    await db.refresh(payslip)
    
    return payslip

@router.get("/payslips", response_model=List[PayslipResponse])
async def get_payslips(
    employee_id: Optional[int] = Query(None),
    payroll_period_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payslips with filtering"""
    current_user, org_id = auth
    
    stmt = select(Payslip).filter(
        Payslip.organization_id == org_id
    )
    
    if employee_id:
        stmt = stmt.filter(Payslip.employee_id == employee_id)
    
    if payroll_period_id:
        stmt = stmt.filter(Payslip.payroll_period_id == payroll_period_id)
    
    if status:
        stmt = stmt.filter(Payslip.status == status)
    
    stmt = stmt.order_by(desc(Payslip.pay_date))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    payslips = result.scalars().all()
    return payslips

@router.post("/payslips/bulk-generate", response_model=PayslipGenerationResult)
async def bulk_generate_payslips(
    generation_data: BulkPayslipGeneration,
    auth: tuple = Depends(require_access("payroll", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Bulk generate payslips for a payroll period"""
    current_user, org_id = auth
    
    # Verify payroll period exists
    result = await db.execute(select(PayrollPeriod).filter(
        and_(
            PayrollPeriod.id == generation_data.payroll_period_id,
            PayrollPeriod.organization_id == org_id
        )
    ))
    period = result.scalar_one_or_none()
    
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll period not found"
        )
    
    # Get employees to process
    stmt = select(EmployeeProfile).filter(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employment_status == "active"
        )
    )
    
    if generation_data.employee_ids:
        stmt = stmt.filter(EmployeeProfile.id.in_(generation_data.employee_ids))
    
    result = await db.execute(stmt)
    employees = result.scalars().all()
    
    successful = 0
    failed = 0
    errors = []
    
    for employee in employees:
        try:
            # Check if payslip already exists
            res = await db.execute(select(Payslip).filter(
                and_(
                    Payslip.organization_id == org_id,
                    Payslip.employee_id == employee.id,
                    Payslip.payroll_period_id == generation_data.payroll_period_id
                )
            ))
            existing_payslip = res.scalar_one_or_none()
            
            if existing_payslip:
                errors.append(f"Payslip already exists for employee {employee.employee_code}")
                failed += 1
                continue
            
            # Get latest salary structure
            res = await db.execute(select(SalaryStructure).filter(
                and_(
                    SalaryStructure.organization_id == org_id,
                    SalaryStructure.employee_id == employee.id,
                    SalaryStructure.is_active == True,
                    SalaryStructure.is_approved == True,
                    SalaryStructure.effective_from <= period.period_end
                )
            ).order_by(desc(SalaryStructure.effective_from)))
            salary_structure = res.scalar_one_or_none()
            
            if not salary_structure:
                errors.append(f"No approved salary structure found for employee {employee.employee_code}")
                failed += 1
                continue
            
            # Calculate attendance data
            res = await db.execute(select(AttendanceRecord).filter(
                and_(
                    AttendanceRecord.organization_id == org_id,
                    AttendanceRecord.employee_id == employee.id,
                    AttendanceRecord.attendance_date >= period.period_start,
                    AttendanceRecord.attendance_date <= period.period_end
                )
            ))
            attendance_records = res.scalars().all()
            
            working_days = (period.period_end - period.period_start).days + 1
            present_days = len([r for r in attendance_records if r.attendance_status == "present"])
            absent_days = len([r for r in attendance_records if r.attendance_status == "absent"])
            leave_days = len([r for r in attendance_records if r.attendance_status == "on_leave"])
            overtime_hours = sum([r.overtime_hours or Decimal('0') for r in attendance_records])
            
            # Generate unique payslip number
            payslip_number = f"PS-{period.period_name.replace(' ', '')}-{employee.employee_code}"
            
            # Create payslip
            payslip = Payslip(
                organization_id=org_id,
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
    
    await db.commit()
    
    # Update period statistics
    res = await db.execute(select(func.sum(Payslip.gross_pay)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ))
    total_gross = res.scalar() or Decimal('0')
    
    res = await db.execute(select(func.sum(Payslip.total_deductions)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ))
    total_deductions = res.scalar() or Decimal('0')
    
    res = await db.execute(select(func.sum(Payslip.net_pay)).filter(
        Payslip.payroll_period_id == generation_data.payroll_period_id
    ))
    total_net = res.scalar() or Decimal('0')
    
    period.processed_employees = successful
    period.total_gross_amount = total_gross
    period.total_deductions = total_deductions
    period.total_net_amount = total_net
    
    if successful > 0:
        period.status = "processed"
    
    await db.commit()
    
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
    auth: tuple = Depends(require_access("payroll", "create")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new employee loan application"""
    current_user, org_id = auth
    
    loan = EmployeeLoan(
        **loan_data.model_dump(),
        organization_id=org_id,
        outstanding_amount=loan_data.loan_amount,
        applied_date=date.today()
    )
    
    db.add(loan)
    await db.commit()
    await db.refresh(loan)
    
    return loan

@router.get("/loans", response_model=List[EmployeeLoanResponse])
async def get_employee_loans(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    loan_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get employee loans with filtering"""
    current_user, org_id = auth
    
    stmt = select(EmployeeLoan).filter(
        EmployeeLoan.organization_id == org_id
    )
    
    if employee_id:
        stmt = stmt.filter(EmployeeLoan.employee_id == employee_id)
    
    if status:
        stmt = stmt.filter(EmployeeLoan.status == status)
    
    if loan_type:
        stmt = stmt.filter(EmployeeLoan.loan_type == loan_type)
    
    stmt = stmt.order_by(desc(EmployeeLoan.applied_date))
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    loans = result.scalars().all()
    return loans

@router.put("/loans/{loan_id}/approve")
async def approve_employee_loan(
    loan_id: int,
    auth: tuple = Depends(require_access("payroll", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Approve an employee loan"""
    current_user, org_id = auth
    
    result = await db.execute(select(EmployeeLoan).filter(
        and_(
            EmployeeLoan.id == loan_id,
            EmployeeLoan.organization_id == org_id
        )
    ))
    loan = result.scalar_one_or_none()
    
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
    
    await db.commit()
    
    return {"message": "Loan approved successfully"}

# Payroll Settings Management
@router.get("/settings", response_model=PayrollSettingsResponse)
async def get_payroll_settings(
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get organization payroll settings"""
    current_user, org_id = auth
    
    result = await db.execute(select(PayrollSettings).filter(
        PayrollSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll settings not found"
        )
    
    return settings

@router.put("/settings", response_model=PayrollSettingsResponse)
async def update_payroll_settings(
    settings_data: PayrollSettingsUpdate,
    auth: tuple = Depends(require_access("payroll", "update")),
    db: AsyncSession = Depends(get_db)
):
    """Update organization payroll settings"""
    current_user, org_id = auth
    
    result = await db.execute(select(PayrollSettings).filter(
        PayrollSettings.organization_id == org_id
    ))
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create new settings if not exist
        settings = PayrollSettings(
            organization_id=org_id,
            **settings_data.model_dump(exclude_unset=True)
        )
        db.add(settings)
    else:
        # Update existing settings
        for field, value in settings_data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
    
    settings.updated_by_id = current_user.id
    
    await db.commit()
    await db.refresh(settings)
    
    return settings

# Dashboard
@router.get("/dashboard", response_model=PayrollDashboard)
async def get_payroll_dashboard(
    auth: tuple = Depends(require_access("payroll", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Get payroll dashboard summary"""
    current_user, org_id = auth
    
    # Get current/latest payroll period
    result = await db.execute(select(PayrollPeriod).filter(
        PayrollPeriod.organization_id == org_id
    ).order_by(desc(PayrollPeriod.period_start)))
    current_period = result.scalar_one_or_none()
    
    # Payroll summary
    result = await db.execute(select(func.count(EmployeeProfile.id)).filter(
        and_(
            EmployeeProfile.organization_id == org_id,
            EmployeeProfile.employment_status == "active"
        )
    ))
    total_employees = result.scalar()
    
    if current_period:
        result = await db.execute(select(func.count(Payslip.id)).filter(
            and_(
                Payslip.organization_id == org_id,
                Payslip.payroll_period_id == current_period.id
            )
        ))
        payroll_processed = result.scalar()
        
        result = await db.execute(select(
            func.sum(Payslip.gross_pay).label('total_gross'),
            func.sum(Payslip.total_deductions).label('total_deductions'),
            func.sum(Payslip.net_pay).label('total_net'),
            func.avg(Payslip.net_pay).label('avg_salary')
        ).filter(
            and_(
                Payslip.organization_id == org_id,
                Payslip.payroll_period_id == current_period.id
            )
        ))
        totals = result.one()
    else:
        payroll_processed = 0
        totals = type('obj', (object,), {
            'total_gross': Decimal('0'),
            'total_deductions': Decimal('0'),
            'total_net': Decimal('0'),
            'avg_salary': None
        })
    
    # Pending items
    result = await db.execute(select(func.count(SalaryStructure.id)).filter(
        and_(
            SalaryStructure.organization_id == org_id,
            SalaryStructure.is_approved == False
        )
    ))
    pending_approvals = result.scalar()
    
    result = await db.execute(select(func.count(Payslip.id)).filter(
        and_(
            Payslip.organization_id == org_id,
            Payslip.status == "draft"
        )
    ))
    pending_payslips = result.scalar()
    
    result = await db.execute(select(func.count(EmployeeLoan.id)).filter(
        and_(
            EmployeeLoan.organization_id == org_id,
            EmployeeLoan.status == "pending"
        )
    ))
    loans_pending_approval = result.scalar()
    
    # Recent salary changes (last 30 days)
    last_month = date.today() - timedelta(days=30)
    result = await db.execute(select(func.count(SalaryStructure.id)).filter(
        and_(
            SalaryStructure.organization_id == org_id,
            SalaryStructure.created_at >= last_month
        )
    ))
    recent_salary_changes = result.scalar()
    
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