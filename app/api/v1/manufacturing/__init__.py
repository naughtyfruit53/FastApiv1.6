# app/api/v1/manufacturing/__init__.py
"""
Manufacturing module - Refactored from monolithic manufacturing.py
This module is organized into logical submodules for better maintainability:
- manufacturing_orders.py: Manufacturing order CRUD operations
- material_issue.py: Material issue vouchers
- manufacturing_journals.py: Manufacturing journal vouchers
- material_receipt.py: Material receipt vouchers
- job_cards.py: Job card vouchers
- stock_journals.py: Stock journal operations
- bom.py: Bill of Materials operations
- mrp.py: Material Requirements Planning
- production_planning.py: Production scheduling and planning
- shop_floor.py: Shop floor operations and barcode scanning
- production_entries.py: Production entry operations  # NEW: Added
"""

from fastapi import APIRouter, FastAPI, Depends, Query
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import logging
import traceback

from app.core.database import get_db
from app.core.enforcement import require_access

logger = logging.getLogger(__name__)

from .manufacturing_orders import router as manufacturing_orders_router
from .material_issue import router as material_issue_router
from .manufacturing_journals import router as manufacturing_journals_router
from .material_receipt import router as material_receipt_router
from .job_cards import router as job_cards_router
from .stock_journals import router as stock_journals_router
from .bom import router as bom_router
from .mrp import router as mrp_router
from .production_planning import router as production_planning_router
from .shop_floor import router as shop_floor_router
from .maintenance import router as maintenance_router
from .quality_control import router as quality_control_router
from .inventory_adjustment import router as inventory_adjustment_router
from .production_entries import router as production_entries_router  # NEW: Added import
from .fg_receipts import router as fg_receipts_router  # NEW: Added FG Receipts router
# Comment out the test_router import and inclusion to avoid ModuleNotFoundError in deployment
# from .test_router import router as test_router

# Main manufacturing router
router = APIRouter()

# Debug endpoint to verify router is mounted
@router.get("/debug")
async def debug_manufacturing():
    """Debug endpoint to verify manufacturing router is mounted"""
    logger.info("Manufacturing debug endpoint accessed")
    return {"message": "Manufacturing router is mounted"}

# Alias endpoint for quality-inspections (frontend uses this path)
@router.get("/quality-inspections")
async def get_quality_inspections_alias(
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    overall_status: Optional[str] = None,
    auth: tuple = Depends(require_access("manufacturing", "read")),
    db: AsyncSession = Depends(get_db)
):
    """Alias for quality-control/inspections to match frontend API calls"""
    from app.models.vouchers.manufacturing_planning import QCInspection
    _, org_id = auth
    stmt = select(QCInspection).where(QCInspection.organization_id == org_id)
    if status:
        stmt = stmt.where(QCInspection.status == status)
    if overall_status:
        stmt = stmt.where(QCInspection.overall_status == overall_status)
    stmt = stmt.order_by(QCInspection.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return {"items": items, "page": page, "per_page": per_page}

# Include sub-routers with error handling
try:
    router.include_router(manufacturing_orders_router, prefix="/manufacturing-orders", tags=["Manufacturing Orders"])  # FIXED: Added back prefix="/manufacturing-orders" to match frontend API calls
    for route in manufacturing_orders_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered manufacturing_orders endpoint: {methods} {route.path}")
    logger.debug("Included manufacturing_orders_router")
except Exception as e:
    logger.error(f"Failed to include manufacturing_orders_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(bom_router, prefix="/bom", tags=["Bill of Materials"])  # FIXED: Added prefix="/bom" to match frontend API calls
    for route in bom_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered bom endpoint: {methods} {route.path}")
    logger.debug("Included bom_router")
except Exception as e:
    logger.error(f"Failed to include bom_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(material_issue_router, prefix="/material-issues", tags=["Material Issue"])
    for route in material_issue_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered material_issue endpoint: {methods} /material-issues{route.path}")
    logger.debug("Included material_issue_router")
except Exception as e:
    logger.error(f"Failed to include material_issue_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(manufacturing_journals_router, prefix="/manufacturing-journal-vouchers", tags=["Manufacturing Journals"])
    for route in manufacturing_journals_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered manufacturing_journals endpoint: {methods} /manufacturing-journal-vouchers{route.path}")
    logger.debug("Included manufacturing_journals_router")
except Exception as e:
    logger.error(f"Failed to include manufacturing_journals_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(material_receipt_router, prefix="/material-receipt-vouchers", tags=["Material Receipt"])
    for route in material_receipt_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered material_receipt endpoint: {methods} /material-receipt-vouchers{route.path}")
    logger.debug("Included material_receipt_router")
except Exception as e:
    logger.error(f"Failed to include material_receipt_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(job_cards_router, prefix="/job-card-vouchers", tags=["Job Cards"])
    for route in job_cards_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered job_cards endpoint: {methods} /job-card-vouchers{route.path}")
    logger.debug("Included job_cards_router")
except Exception as e:
    logger.error(f"Failed to include job_cards_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(stock_journals_router, prefix="/stock-journals", tags=["Stock Journals"])
    for route in stock_journals_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered stock_journals endpoint: {methods} /stock-journals{route.path}")
    logger.debug("Included stock_journals_router")
except Exception as e:
    logger.error(f"Failed to include stock_journals_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(mrp_router, prefix="/mrp", tags=["MRP"])
    for route in mrp_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered mrp endpoint: {methods} /mrp{route.path}")
    logger.debug("Included mrp_router")
except Exception as e:
    logger.error(f"Failed to include mrp_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(production_planning_router, prefix="/production-schedule", tags=["Production Planning"])
    for route in production_planning_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered production_planning endpoint: {methods} /production-schedule{route.path}")
    logger.debug("Included production_planning_router")
except Exception as e:
    logger.error(f"Failed to include production_planning_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(shop_floor_router, prefix="/shop-floor", tags=["Shop Floor"])
    for route in shop_floor_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered shop_floor endpoint: {methods} /shop-floor{route.path}")
    logger.debug("Included shop_floor_router")
except Exception as e:
    logger.error(f"Failed to include shop_floor_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(maintenance_router, prefix="/maintenance", tags=["Maintenance"])
    for route in maintenance_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered maintenance endpoint: {methods} /maintenance{route.path}")
    logger.debug("Included maintenance_router")
except Exception as e:
    logger.error(f"Failed to include maintenance_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(quality_control_router, prefix="/quality-control", tags=["Quality Control"])
    for route in quality_control_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered quality_control endpoint: {methods} /quality-control{route.path}")
    logger.debug("Included quality_control_router")
except Exception as e:
    logger.error(f"Failed to include quality_control_router: {str(e)}\n{traceback.format_exc()}")

try:
    router.include_router(inventory_adjustment_router, prefix="/inventory-adjustment", tags=["Inventory Adjustment"])
    for route in inventory_adjustment_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered inventory_adjustment endpoint: {methods} /inventory-adjustment{route.path}")
    logger.debug("Included inventory_adjustment_router")
except Exception as e:
    logger.error(f"Failed to include inventory_adjustment_router: {str(e)}\n{traceback.format_exc()}")

# NEW: Added inclusion for production_entries_router
try:
    router.include_router(production_entries_router, prefix="/production-entries", tags=["Production Entries"])
    for route in production_entries_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered production_entries endpoint: {methods} /production-entries{route.path}")
    logger.debug("Included production_entries_router")
except Exception as e:
    logger.error(f"Failed to include production_entries_router: {str(e)}\n{traceback.format_exc()}")

# NEW: Added FG Receipts router
try:
    router.include_router(fg_receipts_router, prefix="/fg-receipts", tags=["Finished Good Receipts"])
    for route in fg_receipts_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered fg_receipts endpoint: {methods} /fg-receipts{route.path}")
    logger.debug("Included fg_receipts_router")
except Exception as e:
    logger.error(f"Failed to include fg_receipts_router: {str(e)}\n{traceback.format_exc()}")

# Comment out test_router to avoid ModuleNotFoundError in deployment
# try:
#     router.include_router(test_router, prefix="/test", tags=["Test"])
#     for route in test_router.routes:
#         if isinstance(route, APIRoute):
#             methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
#             logger.debug(f"Registered test endpoint: {methods} /test{route.path}")
#     logger.debug("Included test_router")
# except Exception as e:
#     logger.error(f"Failed to include test_router: {str(e)}\n{traceback.format_exc()}")

__all__ = ["router"]