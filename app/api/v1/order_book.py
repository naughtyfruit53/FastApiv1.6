# app/api/v1/order_book.py
"""
Order Book API endpoints - Order management and workflow tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models import User, Organization, Customer
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/order-book", tags=["Order Book"])

# Order workflow stages
WORKFLOW_STAGES = [
    "order_received",
    "in_production",
    "quality_check",
    "ready_to_dispatch",
    "dispatched",
    "completed"
]

# Order statuses
ORDER_STATUSES = [
    "pending",
    "confirmed",
    "in_production",
    "ready_to_dispatch",
    "dispatched",
    "completed",
    "cancelled"
]


@router.get("/orders")
async def get_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    workflow_stage: Optional[str] = Query(None, description="Filter by workflow stage"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    start_date: Optional[date] = Query(None, description="Filter by order date (start)"),
    end_date: Optional[date] = Query(None, description="Filter by order date (end)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get all orders with optional filters"""
    try:
        # For now, return demo data until database models are created
        # This allows the frontend to function while backend is being developed
        demo_orders = [
            {
                "id": 1,
                "order_number": "ORD-2025-001",
                "customer_name": "ABC Manufacturing Ltd",
                "customer_id": 1,
                "order_date": "2025-01-15",
                "due_date": "2025-02-15",
                "status": "in_production",
                "workflow_stage": "in_production",
                "total_amount": 125000.00,
                "items": [
                    {"product": "Product A", "quantity": 100, "unit_price": 1000, "amount": 100000},
                    {"product": "Product B", "quantity": 50, "unit_price": 500, "amount": 25000}
                ]
            },
            {
                "id": 2,
                "order_number": "ORD-2025-002",
                "customer_name": "XYZ Industries",
                "customer_id": 2,
                "order_date": "2025-01-20",
                "due_date": "2025-03-01",
                "status": "confirmed",
                "workflow_stage": "order_received",
                "total_amount": 85000.00,
                "items": [
                    {"product": "Product C", "quantity": 200, "unit_price": 425, "amount": 85000}
                ]
            },
            {
                "id": 3,
                "order_number": "ORD-2025-003",
                "customer_name": "Global Exports Inc",
                "customer_id": 3,
                "order_date": "2025-01-10",
                "due_date": "2025-02-05",
                "status": "ready_to_dispatch",
                "workflow_stage": "ready_to_dispatch",
                "total_amount": 250000.00,
                "items": [
                    {"product": "Product D", "quantity": 500, "unit_price": 500, "amount": 250000}
                ]
            }
        ]
        
        # Apply filters if provided
        filtered_orders = demo_orders
        
        if status:
            filtered_orders = [o for o in filtered_orders if o["status"] == status]
        
        if workflow_stage:
            filtered_orders = [o for o in filtered_orders if o["workflow_stage"] == workflow_stage]
        
        if customer_id:
            filtered_orders = [o for o in filtered_orders if o["customer_id"] == customer_id]
        
        return {
            "orders": filtered_orders,
            "total_count": len(filtered_orders),
            "summary": {
                "total_value": sum(o["total_amount"] for o in filtered_orders),
                "by_stage": {
                    stage: len([o for o in filtered_orders if o["workflow_stage"] == stage])
                    for stage in WORKFLOW_STAGES
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get order details by ID"""
    try:
        # Demo data for specific order
        demo_order = {
            "id": order_id,
            "order_number": f"ORD-2025-{str(order_id).zfill(3)}",
            "customer_name": "Demo Customer",
            "customer_id": 1,
            "order_date": "2025-01-15",
            "due_date": "2025-02-15",
            "status": "in_production",
            "workflow_stage": "in_production",
            "total_amount": 125000.00,
            "items": [
                {"product": "Product A", "quantity": 100, "unit_price": 1000, "amount": 100000},
                {"product": "Product B", "quantity": 50, "unit_price": 500, "amount": 25000}
            ],
            "workflow_history": [
                {"stage": "order_received", "timestamp": "2025-01-15T10:00:00", "user": "Admin"},
                {"stage": "in_production", "timestamp": "2025-01-16T09:00:00", "user": "Production Manager"}
            ],
            "notes": "Customer requires special packaging"
        }
        
        return demo_order
    
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders")
async def create_order(
    order_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Create a new order"""
    try:
        # For demo purposes, return the created order
        new_order = {
            "id": 999,
            "order_number": "ORD-2025-999",
            "customer_name": order_data.get("customer_name", "New Customer"),
            "customer_id": order_data.get("customer_id", 0),
            "order_date": order_data.get("order_date", str(date.today())),
            "due_date": order_data.get("due_date", str(date.today())),
            "status": "pending",
            "workflow_stage": "order_received",
            "total_amount": order_data.get("total_amount", 0),
            "items": order_data.get("items", [])
        }
        
        logger.info(f"Order created: {new_order['order_number']}")
        return new_order
    
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/orders/{order_id}/workflow")
async def update_workflow_stage(
    order_id: int,
    stage_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update order workflow stage"""
    try:
        new_stage = stage_data.get("workflow_stage")
        
        if new_stage not in WORKFLOW_STAGES:
            raise HTTPException(status_code=400, detail=f"Invalid workflow stage: {new_stage}")
        
        # For demo purposes, return success
        return {
            "order_id": order_id,
            "workflow_stage": new_stage,
            "updated_at": datetime.now().isoformat(),
            "updated_by": current_user.username
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update order status"""
    try:
        new_status = status_data.get("status")
        
        if new_status not in ORDER_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid order status: {new_status}")
        
        # For demo purposes, return success
        return {
            "order_id": order_id,
            "status": new_status,
            "updated_at": datetime.now().isoformat(),
            "updated_by": current_user.username
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow-stages")
async def get_workflow_stages(
    current_user: User = Depends(get_current_active_user)
):
    """Get available workflow stages"""
    return {
        "stages": [
            {"value": "order_received", "label": "Order Received", "order": 1},
            {"value": "in_production", "label": "In Production", "order": 2},
            {"value": "quality_check", "label": "Quality Check", "order": 3},
            {"value": "ready_to_dispatch", "label": "Ready to Dispatch", "order": 4},
            {"value": "dispatched", "label": "Dispatched", "order": 5},
            {"value": "completed", "label": "Completed", "order": 6}
        ]
    }


@router.get("/order-statuses")
async def get_order_statuses(
    current_user: User = Depends(get_current_active_user)
):
    """Get available order statuses"""
    return {
        "statuses": [
            {"value": "pending", "label": "Pending"},
            {"value": "confirmed", "label": "Confirmed"},
            {"value": "in_production", "label": "In Production"},
            {"value": "ready_to_dispatch", "label": "Ready to Dispatch"},
            {"value": "dispatched", "label": "Dispatched"},
            {"value": "completed", "label": "Completed"},
            {"value": "cancelled", "label": "Cancelled"}
        ]
    }


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get order book dashboard statistics"""
    try:
        # Demo statistics
        return {
            "total_orders": 45,
            "active_orders": 28,
            "completed_orders": 15,
            "cancelled_orders": 2,
            "total_value": 2500000.00,
            "by_stage": {
                "order_received": 5,
                "in_production": 12,
                "quality_check": 6,
                "ready_to_dispatch": 3,
                "dispatched": 2,
                "completed": 15
            },
            "overdue_orders": 3,
            "due_this_week": 7
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
