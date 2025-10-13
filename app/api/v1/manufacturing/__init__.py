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

from fastapi import APIRouter
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

# Main manufacturing router that includes all sub-routers
router = APIRouter()

# Include all sub-routers
router.include_router(manufacturing_orders_router, tags=["Manufacturing Orders"])
router.include_router(material_issue_router, tags=["Material Issue"])
router.include_router(manufacturing_journals_router, tags=["Manufacturing Journals"])
router.include_router(material_receipt_router, tags=["Material Receipt"])
router.include_router(job_cards_router, tags=["Job Cards"])
router.include_router(stock_journals_router, tags=["Stock Journals"])
router.include_router(bom_router, tags=["Bill of Materials"])
router.include_router(mrp_router, tags=["MRP"])
router.include_router(production_planning_router, tags=["Production Planning"])
router.include_router(shop_floor_router, tags=["Shop Floor"])

__all__ = ["router"]
