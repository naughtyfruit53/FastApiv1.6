from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.hr_models import (
    StatutoryDeduction, PayrollArrear, PayrollApproval,
    PolicyDocument, PolicyAcknowledgment,
    ComplianceAuditExport
)
from app.schemas.hr_schemas import (
    StatutoryDeductionCreate, StatutoryDeductionUpdate, StatutoryDeductionResponse,
    PayrollArrearCreate, PayrollArrearUpdate, PayrollArrearResponse,
    PayrollApprovalCreate, PayrollApprovalUpdate, PayrollApprovalResponse,
    PolicyDocumentCreate, PolicyDocumentUpdate, PolicyDocumentResponse,
    PolicyAcknowledgmentCreate, PolicyAcknowledgmentUpdate, PolicyAcknowledgmentResponse,
    ComplianceAuditExportCreate, ComplianceAuditExportResponse
)

router = APIRouter(prefix="/hr", tags=["Human Resources - Compliance"])

# ============================================================================
# Statutory Deductions
# ============================================================================
@router.get("/statutory-deductions", response_model=List[StatutoryDeductionResponse])
async def get_statutory_deductions(
    is_active: Optional[bool] = Query(default=None),
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
