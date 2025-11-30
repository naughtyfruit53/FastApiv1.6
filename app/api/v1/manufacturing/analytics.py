# app/api/v1/manufacturing/analytics.py
"""
Manufacturing Analytics API endpoints - Material consumption, efficiency reports, production summaries
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.vouchers.manufacturing_operations import (
    MaterialIssue, MaterialIssueItem, ManufacturingJournalVoucher,
    ProductionEntry, ProductionEntryConsumption
)
from app.models.vouchers.manufacturing_planning import ManufacturingOrder

logger = logging.getLogger(__name__)

router = APIRouter(tags=["manufacturing-analytics"])


# ============================================================================
# Pydantic Response Schemas
# ============================================================================

class MaterialConsumptionItem(BaseModel):
    """Individual material consumption record"""
    material_id: int
    material_name: Optional[str] = None
    quantity_consumed: float
    unit: Optional[str] = None
    date: date
    department: Optional[str] = None

class MaterialConsumptionSummary(BaseModel):
    """Summary of material consumption by material"""
    material_id: int
    material_name: Optional[str] = None
    total_quantity: float
    unit: Optional[str] = None
    issue_count: int

class MaterialConsumptionResponse(BaseModel):
    """Response schema for material consumption endpoint"""
    organization_id: int
    period: Dict[str, Any]
    summary: List[MaterialConsumptionSummary]
    details: Optional[List[MaterialConsumptionItem]] = None
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class EfficiencyMetrics(BaseModel):
    """OEE-like efficiency metrics"""
    availability: float = Field(description="Availability percentage (0-100)")
    performance: float = Field(description="Performance percentage (0-100)")
    quality: float = Field(description="Quality percentage (0-100)")
    oee: float = Field(description="Overall Equipment Effectiveness (0-100)")

class MachineEfficiency(BaseModel):
    """Efficiency metrics for a specific machine"""
    machine_id: Optional[str] = None
    machine_name: Optional[str] = None
    metrics: EfficiencyMetrics
    total_runtime_hours: float
    total_downtime_hours: float
    total_produced: float
    total_rejected: float

class EfficiencyReportResponse(BaseModel):
    """Response schema for efficiency report endpoint"""
    organization_id: int
    period: Dict[str, Any]
    overall_metrics: EfficiencyMetrics
    machines: List[MachineEfficiency]
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class ProductionSummaryItem(BaseModel):
    """Summary for a specific product"""
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    total_good_units: float
    total_rejected_units: float
    total_planned: float
    completion_rate: float
    downtime_hours: float

class ProductionSummaryResponse(BaseModel):
    """Response schema for production summary endpoint"""
    organization_id: int
    period: Dict[str, Any]
    totals: Dict[str, float]
    products: List[ProductionSummaryItem]
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

def parse_date_range(range_param: Optional[str]) -> tuple:
    """Parse range parameter into start and end dates"""
    end_date = date.today()
    
    if not range_param:
        start_date = end_date - timedelta(days=30)
    elif range_param == "7d":
        start_date = end_date - timedelta(days=7)
    elif range_param == "30d":
        start_date = end_date - timedelta(days=30)
    elif range_param == "90d":
        start_date = end_date - timedelta(days=90)
    elif range_param == "365d" or range_param == "1y":
        start_date = end_date - timedelta(days=365)
    elif range_param == "ytd":
        start_date = date(end_date.year, 1, 1)
    else:
        # Try to parse as days
        try:
            days = int(range_param.rstrip('d'))
            start_date = end_date - timedelta(days=days)
        except ValueError:
            start_date = end_date - timedelta(days=30)
    
    return start_date, end_date


# ============================================================================
# Material Consumption Endpoint
# ============================================================================

@router.get("/material-consumption", response_model=MaterialConsumptionResponse)
async def get_material_consumption(
    range: Optional[str] = Query("30d", description="Date range: 7d, 30d, 90d, 365d, 1y, ytd"),
    material: Optional[int] = Query(None, description="Filter by specific material ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    include_details: bool = Query(False, description="Include detailed consumption records"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get material consumption analytics with aggregation by organization, date range, and material filters.
    
    Provides summary of materials consumed in manufacturing operations.
    """
    current_user, org_id = auth
    start_date, end_date = parse_date_range(range)
    
    try:
        # Build base query for material issues
        base_conditions = [
            MaterialIssue.organization_id == org_id,
            MaterialIssue.date >= start_date,
            MaterialIssue.date <= end_date,
            MaterialIssue.is_deleted == False
        ]
        
        if department:
            base_conditions.append(MaterialIssue.issued_to_department == department)
        
        # Query for aggregated consumption by material
        summary_stmt = (
            select(
                MaterialIssueItem.product_id.label('material_id'),
                func.sum(MaterialIssueItem.quantity).label('total_quantity'),
                func.count(MaterialIssueItem.id).label('issue_count'),
                MaterialIssueItem.unit
            )
            .join(MaterialIssue, MaterialIssueItem.material_issue_id == MaterialIssue.id)
            .where(and_(*base_conditions))
        )
        
        if material:
            summary_stmt = summary_stmt.where(MaterialIssueItem.product_id == material)
        
        summary_stmt = summary_stmt.group_by(
            MaterialIssueItem.product_id,
            MaterialIssueItem.unit
        )
        
        summary_result = await db.execute(summary_stmt)
        summary_rows = summary_result.fetchall()
        
        # Build summary list
        summary_list = []
        for row in summary_rows:
            summary_list.append(MaterialConsumptionSummary(
                material_id=row.material_id,
                material_name=None,  # Would need to join with products table
                total_quantity=float(row.total_quantity or 0),
                unit=row.unit,
                issue_count=row.issue_count
            ))
        
        # Get details if requested
        details_list = None
        if include_details:
            details_stmt = (
                select(
                    MaterialIssueItem.product_id.label('material_id'),
                    MaterialIssueItem.quantity,
                    MaterialIssueItem.unit,
                    MaterialIssue.date,
                    MaterialIssue.issued_to_department
                )
                .join(MaterialIssue, MaterialIssueItem.material_issue_id == MaterialIssue.id)
                .where(and_(*base_conditions))
                .order_by(MaterialIssue.date.desc())
                .limit(1000)
            )
            
            if material:
                details_stmt = details_stmt.where(MaterialIssueItem.product_id == material)
            
            details_result = await db.execute(details_stmt)
            details_rows = details_result.fetchall()
            
            details_list = [
                MaterialConsumptionItem(
                    material_id=row.material_id,
                    quantity_consumed=float(row.quantity or 0),
                    unit=row.unit,
                    date=row.date,
                    department=row.issued_to_department
                )
                for row in details_rows
            ]
        
        return MaterialConsumptionResponse(
            organization_id=org_id,
            period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "range": range
            },
            summary=summary_list,
            details=details_list,
            metadata={
                "total_materials": len(summary_list),
                "filters_applied": {
                    "material": material,
                    "department": department
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching material consumption: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch material consumption data: {str(e)}"
        )


# ============================================================================
# Efficiency Report Endpoint
# ============================================================================

@router.get("/efficiency-report", response_model=EfficiencyReportResponse)
async def get_efficiency_report(
    range: Optional[str] = Query("30d", description="Date range: 7d, 30d, 90d, 365d, 1y, ytd"),
    machine: Optional[str] = Query(None, description="Filter by specific machine ID"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get efficiency report with OEE-like metrics (availability, performance, quality).
    
    Returns metrics per machine and overall aggregates.
    """
    current_user, org_id = auth
    start_date, end_date = parse_date_range(range)
    
    try:
        # Build base query for production entries
        base_conditions = [
            ProductionEntry.organization_id == org_id,
            ProductionEntry.date >= start_date,
            ProductionEntry.date <= end_date,
            ProductionEntry.is_deleted == False
        ]
        
        if machine:
            base_conditions.append(ProductionEntry.machine == machine)
        
        # Query aggregated metrics grouped by machine
        metrics_stmt = (
            select(
                ProductionEntry.machine.label('machine_id'),
                func.sum(ProductionEntry.machine_hours).label('total_runtime'),
                func.sum(ProductionEntry.actual_quantity).label('total_produced'),
                func.sum(ProductionEntry.rejected_quantity).label('total_rejected'),
                func.sum(ProductionEntry.time_taken).label('total_time'),
                func.count(ProductionEntry.id).label('entry_count')
            )
            .where(and_(*base_conditions))
            .group_by(ProductionEntry.machine)
        )
        
        result = await db.execute(metrics_stmt)
        rows = result.fetchall()
        
        machines_list = []
        total_runtime = 0.0
        total_produced = 0.0
        total_rejected = 0.0
        total_downtime = 0.0
        
        # Calculate planned hours (assuming 8 hours per day * number of working days)
        working_days = (end_date - start_date).days
        planned_hours_per_machine = working_days * 8  # 8 hours per day assumption
        
        for row in rows:
            runtime = float(row.total_runtime or 0)
            produced = float(row.total_produced or 0)
            rejected = float(row.total_rejected or 0)
            
            # Calculate downtime (planned hours - actual runtime)
            downtime = max(0, planned_hours_per_machine - runtime)
            
            # Calculate OEE components
            # Availability = Actual Runtime / Planned Runtime
            availability = (runtime / planned_hours_per_machine * 100) if planned_hours_per_machine > 0 else 0
            availability = min(100, availability)  # Cap at 100%
            
            # Performance = Actual Output / Expected Output at actual runtime
            # Assume expected output rate is 10 units per hour
            expected_output = runtime * 10
            performance = (produced / expected_output * 100) if expected_output > 0 else 0
            performance = min(100, performance)
            
            # Quality = Good Units / Total Units
            total_units = produced + rejected
            quality = ((produced - rejected) / produced * 100) if produced > 0 else 100
            quality = max(0, min(100, quality))
            
            # OEE = Availability × Performance × Quality
            oee = (availability * performance * quality) / 10000
            
            machines_list.append(MachineEfficiency(
                machine_id=row.machine_id,
                machine_name=row.machine_id,
                metrics=EfficiencyMetrics(
                    availability=round(availability, 2),
                    performance=round(performance, 2),
                    quality=round(quality, 2),
                    oee=round(oee, 2)
                ),
                total_runtime_hours=round(runtime, 2),
                total_downtime_hours=round(downtime, 2),
                total_produced=produced,
                total_rejected=rejected
            ))
            
            total_runtime += runtime
            total_produced += produced
            total_rejected += rejected
            total_downtime += downtime
        
        # Calculate overall metrics
        total_planned = planned_hours_per_machine * len(machines_list) if machines_list else planned_hours_per_machine
        overall_availability = (total_runtime / total_planned * 100) if total_planned > 0 else 0
        overall_availability = min(100, overall_availability)
        
        expected_total_output = total_runtime * 10
        overall_performance = (total_produced / expected_total_output * 100) if expected_total_output > 0 else 0
        overall_performance = min(100, overall_performance)
        
        overall_quality = ((total_produced - total_rejected) / total_produced * 100) if total_produced > 0 else 100
        overall_quality = max(0, min(100, overall_quality))
        
        overall_oee = (overall_availability * overall_performance * overall_quality) / 10000
        
        return EfficiencyReportResponse(
            organization_id=org_id,
            period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "range": range
            },
            overall_metrics=EfficiencyMetrics(
                availability=round(overall_availability, 2),
                performance=round(overall_performance, 2),
                quality=round(overall_quality, 2),
                oee=round(overall_oee, 2)
            ),
            machines=machines_list,
            metadata={
                "total_machines": len(machines_list),
                "filters_applied": {
                    "machine": machine
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching efficiency report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch efficiency report: {str(e)}"
        )


# ============================================================================
# Production Summary Endpoint
# ============================================================================

@router.get("/production-summary", response_model=ProductionSummaryResponse)
async def get_production_summary(
    range: Optional[str] = Query("30d", description="Date range: 7d, 30d, 90d, 365d, 1y, ytd"),
    product: Optional[int] = Query(None, description="Filter by specific product ID"),
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """
    Get production summary with aggregated totals (good units, rejects, downtime) per organization.
    
    Provides overview of production performance.
    """
    current_user, org_id = auth
    start_date, end_date = parse_date_range(range)
    
    try:
        # Query production entries aggregated
        base_conditions = [
            ProductionEntry.organization_id == org_id,
            ProductionEntry.date >= start_date,
            ProductionEntry.date <= end_date,
            ProductionEntry.is_deleted == False
        ]
        
        # Get production entry totals
        totals_stmt = (
            select(
                func.sum(ProductionEntry.actual_quantity).label('total_good'),
                func.sum(ProductionEntry.rejected_quantity).label('total_rejected'),
                func.sum(ProductionEntry.time_taken).label('total_time'),
                func.sum(ProductionEntry.machine_hours).label('total_machine_hours'),
                func.count(ProductionEntry.id).label('entry_count')
            )
            .where(and_(*base_conditions))
        )
        
        totals_result = await db.execute(totals_stmt)
        totals_row = totals_result.fetchone()
        
        total_good = float(totals_row.total_good or 0) if totals_row else 0
        total_rejected = float(totals_row.total_rejected or 0) if totals_row else 0
        total_time = float(totals_row.total_time or 0) if totals_row else 0
        total_machine_hours = float(totals_row.total_machine_hours or 0) if totals_row else 0
        entry_count = totals_row.entry_count if totals_row else 0
        
        # Get manufacturing orders to calculate planned quantities
        orders_stmt = (
            select(
                ManufacturingOrder.bom_id,
                func.sum(ManufacturingOrder.planned_quantity).label('total_planned'),
                func.sum(ManufacturingOrder.produced_quantity).label('total_produced')
            )
            .where(
                ManufacturingOrder.organization_id == org_id,
                ManufacturingOrder.planned_start_date >= start_date,
                ManufacturingOrder.planned_end_date <= end_date,
                ManufacturingOrder.is_deleted == False
            )
            .group_by(ManufacturingOrder.bom_id)
        )
        
        if product:
            # Would need to join with BOM to filter by product
            pass
        
        orders_result = await db.execute(orders_stmt)
        orders_rows = orders_result.fetchall()
        
        products_list = []
        total_planned = 0.0
        
        for row in orders_rows:
            planned = float(row.total_planned or 0)
            produced = float(row.total_produced or 0)
            completion_rate = (produced / planned * 100) if planned > 0 else 0
            
            products_list.append(ProductionSummaryItem(
                product_id=row.bom_id,  # Using BOM ID as product reference
                product_name=None,
                total_good_units=produced,
                total_rejected_units=0,  # Would need more detailed tracking
                total_planned=planned,
                completion_rate=round(completion_rate, 2),
                downtime_hours=0  # Would need more detailed tracking per product
            ))
            
            total_planned += planned
        
        # Calculate estimated downtime
        working_days = (end_date - start_date).days
        available_hours = working_days * 8 * max(1, entry_count // 10)  # Rough estimate
        downtime_hours = max(0, available_hours - total_machine_hours)
        
        completion_rate = (total_good / total_planned * 100) if total_planned > 0 else 0
        
        return ProductionSummaryResponse(
            organization_id=org_id,
            period={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "range": range
            },
            totals={
                "good_units": total_good,
                "rejected_units": total_rejected,
                "total_units": total_good + total_rejected,
                "planned_units": total_planned,
                "completion_rate": round(completion_rate, 2),
                "downtime_hours": round(downtime_hours, 2),
                "machine_hours": total_machine_hours,
                "production_entries": entry_count
            },
            products=products_list,
            metadata={
                "total_products": len(products_list),
                "filters_applied": {
                    "product": product
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error fetching production summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch production summary: {str(e)}"
        )
