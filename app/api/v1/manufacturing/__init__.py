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
"""

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
import logging
import traceback

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
from .test_router import router as test_router

# Main manufacturing router
router = APIRouter()

# Debug endpoint to verify router is mounted
@router.get("/debug")
async def debug_manufacturing():
    """Debug endpoint to verify manufacturing router is mounted"""
    logger.info("Manufacturing debug endpoint accessed")
    return {"message": "Manufacturing router is mounted"}

# Include sub-routers with error handling
try:
    router.include_router(manufacturing_orders_router, prefix="/manufacturing-orders", tags=["Manufacturing Orders"])
    for route in manufacturing_orders_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered manufacturing_orders endpoint: {methods} /manufacturing-orders{route.path}")
    logger.debug("Included manufacturing_orders_router")
except Exception as e:
    logger.error(f"Failed to include manufacturing_orders_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(bom_router, prefix="/bom", tags=["Bill of Materials"])
    for route in bom_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered bom endpoint: {methods} /bom{route.path}")
    logger.debug("Included bom_router")
except Exception as e:
    logger.error(f"Failed to include bom_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(material_issue_router, prefix="/material-issues", tags=["Material Issue"])
    for route in material_issue_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered material_issue endpoint: {methods} /material-issues{route.path}")
    logger.debug("Included material_issue_router")
except Exception as e:
    logger.error(f"Failed to include material_issue_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(manufacturing_journals_router, prefix="/manufacturing-journal-vouchers", tags=["Manufacturing Journals"])
    for route in manufacturing_journals_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered manufacturing_journals endpoint: {methods} /manufacturing-journal-vouchers{route.path}")
    logger.debug("Included manufacturing_journals_router")
except Exception as e:
    logger.error(f"Failed to include manufacturing_journals_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(material_receipt_router, prefix="/material-receipt-vouchers", tags=["Material Receipt"])
    for route in material_receipt_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered material_receipt endpoint: {methods} /material-receipt-vouchers{route.path}")
    logger.debug("Included material_receipt_router")
except Exception as e:
    logger.error(f"Failed to include material_receipt_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(job_cards_router, prefix="/job-card-vouchers", tags=["Job Cards"])
    for route in job_cards_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered job_cards endpoint: {methods} /job-card-vouchers{route.path}")
    logger.debug("Included job_cards_router")
except Exception as e:
    logger.error(f"Failed to include job_cards_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(stock_journals_router, prefix="/stock-journals", tags=["Stock Journals"])
    for route in stock_journals_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered stock_journals endpoint: {methods} /stock-journals{route.path}")
    logger.debug("Included stock_journals_router")
except Exception as e:
    logger.error(f"Failed to include stock_journals_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(mrp_router, prefix="/mrp", tags=["MRP"])
    for route in mrp_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered mrp endpoint: {methods} /mrp{route.path}")
    logger.debug("Included mrp_router")
except Exception as e:
    logger.error(f"Failed to include mrp_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(production_planning_router, prefix="/production-schedule", tags=["Production Planning"])
    for route in production_planning_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered production_planning endpoint: {methods} /production-schedule{route.path}")
    logger.debug("Included production_planning_router")
except Exception as e:
    logger.error(f"Failed to include production_planning_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(shop_floor_router, prefix="/shop-floor", tags=["Shop Floor"])
    for route in shop_floor_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered shop_floor endpoint: {methods} /shop-floor{route.path}")
    logger.debug("Included shop_floor_router")
except Exception as e:
    logger.error(f"Failed to include shop_floor_router: {str(e)}\n{traceback.format_exc()}")
    raise

try:
    router.include_router(test_router, prefix="/test", tags=["Test"])
    for route in test_router.routes:
        if isinstance(route, APIRoute):
            methods = ', '.join(sorted(route.methods)) if route.methods else 'ALL'
            logger.debug(f"Registered test endpoint: {methods} /test{route.path}")
    logger.debug("Included test_router")
except Exception as e:
    logger.error(f"Failed to include test_router: {str(e)}\n{traceback.format_exc()}")
    raise

__all__ = ["router"]