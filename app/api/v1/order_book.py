# app/api/v1/order_book.py
"""
Order Book API endpoints - Order management and workflow tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.core.database import get_db

from app.core.enforcement import require_access
from app.models import User, Organization, Customer
from app.models.order_book_models import Order, OrderItem, WorkflowHistory  # Import new models
from app.schemas.order_book import OrderSchema, OrderCreateSchema, WorkflowUpdateSchema, StatusUpdateSchema  # Assume schemas exist or create them
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

@router.get("/orders", response_model=List[OrderSchema])
async def get_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    workflow_stage: Optional[str] = Query(None, description="Filter by workflow stage"),
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    start_date: Optional[date] = Query(None, description="Filter by order date (start)"),
    end_date: Optional[date] = Query(None, description="Filter by order date (end)"),
    auth: tuple = Depends(require_access("order", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get all orders with optional filters"""

    current_user, organization_id = auth
    try:
        stmt = select(Order).where(Order.organization_id == organization_id)
        
        if status:
            stmt = stmt.where(Order.status == status)
        
        if workflow_stage:
            stmt = stmt.where(Order.workflow_stage == workflow_stage)
        
        if customer_id:
            stmt = stmt.where(Order.customer_id == customer_id)
        
        if start_date:
            stmt = stmt.where(Order.order_date >= start_date)
        
        if end_date:
            stmt = stmt.where(Order.order_date <= end_date)
        
        stmt = stmt.order_by(desc(Order.order_date))
        
        result = await db.execute(stmt)
        orders = result.scalars().all()
        
        # Convert to schema if needed, but assuming OrderSchema.from_orm works
        return orders
    
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    auth: tuple = Depends(require_access("order", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get order details by ID"""

    current_user, organization_id = auth
    try:
        stmt = select(Order).where(
            and_(Order.id == order_id, Order.organization_id == organization_id)
        )
        
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/orders", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreateSchema,
    auth: tuple = Depends(require_access("order", "create")),

    db: AsyncSession = Depends(get_db)
):

    """Create a new order"""

    current_user, organization_id = auth
    try:
        # Generate unique order number (simple example, improve as needed)
        stmt = select(Order).where(Order.organization_id == organization_id).order_by(desc(Order.id))
        result = await db.execute(stmt)
        last_order = result.scalars().first()
        order_number = f"ORD-{organization_id}-{ (last_order.id + 1) if last_order else 1 }"
        
        new_order = Order(
            organization_id=organization_id,
            order_number=order_number,
            customer_id=order_data.customer_id,
            order_date=order_data.order_date,
            due_date=order_data.due_date,
            status="pending",
            workflow_stage="order_received",
            total_amount=order_data.total_amount,
            created_by_id=current_user.id
        )
        
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        
        # Add items
        for item in order_data.items:
            new_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.quantity * item.unit_price
            )
            db.add(new_item)
        
        # Add initial workflow history
        initial_history = WorkflowHistory(
            order_id=new_order.id,
            from_stage=None,
            to_stage="order_received",
            changed_by_id=current_user.id,
            notes="Order created"
        )
        db.add(initial_history)
        
        await db.commit()
        await db.refresh(new_order)
        
        logger.info(f"Order created: {new_order.order_number}")
        return new_order
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/orders/{order_id}/workflow", response_model=OrderSchema)
async def update_workflow_stage(
    order_id: int,
    stage_data: WorkflowUpdateSchema,
    auth: tuple = Depends(require_access("order", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Update order workflow stage"""

    current_user, organization_id = auth
    try:
        stmt = select(Order).where(
            and_(Order.id == order_id, Order.organization_id == organization_id)
        )
        
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if stage_data.workflow_stage not in WORKFLOW_STAGES:
            raise HTTPException(status_code=400, detail=f"Invalid workflow stage: {stage_data.workflow_stage}")
        
        # Record history
        history = WorkflowHistory(
            order_id=order_id,
            from_stage=order.workflow_stage,
            to_stage=stage_data.workflow_stage,
            changed_by_id=current_user.id,
            notes=stage_data.notes
        )
        db.add(history)
        
        order.workflow_stage = stage_data.workflow_stage
        order.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(order)
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating workflow for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/orders/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    status_data: StatusUpdateSchema,
    auth: tuple = Depends(require_access("order", "update")),

    db: AsyncSession = Depends(get_db)
):

    """Update order status"""

    current_user, organization_id = auth
    try:
        stmt = select(Order).where(
            and_(Order.id == order_id, Order.organization_id == organization_id)
        )
        
        result = await db.execute(stmt)
        order = result.scalars().first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if status_data.status not in ORDER_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid order status: {status_data.status}")
        
        order.status = status_data.status
        order.updated_at = datetime.now()
        
        await db.commit()
        await db.refresh(order)
        
        return order
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating status for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow-stages")
async def get_workflow_stages(
    auth: tuple = Depends(require_access("order", "read"))
):
    """Get available workflow stages"""
    current_user, organization_id = auth
    
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
    auth: tuple = Depends(require_access("order", "read"))
):
    """Get available order statuses"""
    current_user, organization_id = auth
    
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
    auth: tuple = Depends(require_access("order", "read")),

    db: AsyncSession = Depends(get_db)
):

    """Get order book dashboard statistics"""

    current_user, organization_id = auth
    try:
        # Total orders
        stmt = select(func.count(Order.id)).where(Order.organization_id == organization_id)
        result = await db.execute(stmt)
        total_orders = result.scalar()
        
        # Active orders
        stmt = select(func.count(Order.id)).where(
            and_(Order.organization_id == organization_id, ~Order.status.in_(["completed", "cancelled"]))
        )
        result = await db.execute(stmt)
        active_orders = result.scalar()
        
        # Completed orders
        stmt = select(func.count(Order.id)).where(
            and_(Order.organization_id == organization_id, Order.status == "completed")
        )
        result = await db.execute(stmt)
        completed_orders = result.scalar()
        
        # Cancelled orders
        stmt = select(func.count(Order.id)).where(
            and_(Order.organization_id == organization_id, Order.status == "cancelled")
        )
        result = await db.execute(stmt)
        cancelled_orders = result.scalar()
        
        # Total value
        stmt = select(func.sum(Order.total_amount)).where(Order.organization_id == organization_id)
        result = await db.execute(stmt)
        total_value = result.scalar() or 0
        
        # By stage
        by_stage = {}
        for stage in WORKFLOW_STAGES:
            stmt = select(func.count(Order.id)).where(
                and_(Order.organization_id == organization_id, Order.workflow_stage == stage)
            )
            result = await db.execute(stmt)
            by_stage[stage] = result.scalar()
        
        # Overdue orders
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.organization_id == organization_id,
                Order.due_date < date.today(),
                Order.status != "completed"
            )
        )
        result = await db.execute(stmt)
        overdue_orders = result.scalar()
        
        # Due this week
        this_week_end = date.today() + timedelta(days=7)
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.organization_id == organization_id,
                Order.due_date >= date.today(),
                Order.due_date <= this_week_end,
                Order.status != "completed"
            )
        )
        result = await db.execute(stmt)
        due_this_week = result.scalar()
        
        return {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "cancelled_orders": cancelled_orders,
            "total_value": float(total_value),
            "by_stage": by_stage,
            "overdue_orders": overdue_orders,
            "due_this_week": due_this_week
        }
    
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))