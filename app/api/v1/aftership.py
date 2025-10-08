# app/api/v1/aftership.py

"""
AfterShip API endpoints for shipment tracking integration
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.models import User
from app.models.vouchers.purchase import PurchaseOrder, GoodsReceiptNote
from app.models.vouchers.sales import DeliveryChallan
from app.services.aftership_service import aftership_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["aftership"])


# Pydantic Models
class TrackingCreate(BaseModel):
    """Model for creating a new tracking"""
    tracking_number: str
    slug: Optional[str] = None  # Auto-detected if not provided
    title: Optional[str] = None
    order_id: Optional[str] = None
    customer_name: Optional[str] = None
    destination_country: str = "IN"


class TrackingResponse(BaseModel):
    """Response model for tracking"""
    id: str
    tracking_number: str
    slug: str
    tag: str
    tracking_link: str
    expected_delivery: Optional[str] = None
    checkpoints: List[Dict[str, Any]] = []


class BulkTrackingCreate(BaseModel):
    """Model for bulk tracking creation"""
    trackings: List[TrackingCreate]


class WebhookEvent(BaseModel):
    """AfterShip webhook event model"""
    event: str
    msg: Dict[str, Any]


# Endpoints
@router.post("/trackings", response_model=TrackingResponse)
async def create_tracking(
    tracking: TrackingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new shipment tracking in AfterShip
    
    The tracking will be monitored for status updates automatically.
    """
    try:
        # Auto-detect courier if not provided
        if not tracking.slug:
            couriers = await aftership_service.detect_courier(tracking.tracking_number)
            if couriers and len(couriers) > 0:
                tracking.slug = couriers[0]["slug"]
                logger.info(f"Auto-detected courier: {tracking.slug}")
        
        # Create tracking in AfterShip
        result = await aftership_service.create_tracking(
            tracking_number=tracking.tracking_number,
            slug=tracking.slug,
            title=tracking.title,
            order_id=tracking.order_id,
            customer_name=tracking.customer_name,
            destination_country=tracking.destination_country
        )
        
        # Update Purchase Order or Delivery Challan with tracking info in background
        if tracking.order_id:
            background_tasks.add_task(
                update_order_tracking,
                db,
                tracking.order_id,
                tracking.tracking_number,
                tracking.slug,
                result.get("tracking_link")
            )
        
        return TrackingResponse(
            id=result.get("id", ""),
            tracking_number=result.get("tracking_number", ""),
            slug=result.get("slug", ""),
            tag=result.get("tag", "Pending"),
            tracking_link=result.get("tracking_link", ""),
            expected_delivery=result.get("expected_delivery"),
            checkpoints=result.get("checkpoints", [])
        )
        
    except Exception as e:
        logger.error(f"Error creating tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trackings/{slug}/{tracking_number}", response_model=TrackingResponse)
async def get_tracking(
    slug: str,
    tracking_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed tracking information for a shipment
    
    Returns current status, location, expected delivery, and checkpoint history.
    """
    try:
        result = await aftership_service.get_tracking(slug, tracking_number)
        
        return TrackingResponse(
            id=result.get("id", ""),
            tracking_number=result.get("tracking_number", ""),
            slug=result.get("slug", ""),
            tag=result.get("tag", "Pending"),
            tracking_link=result.get("tracking_link", ""),
            expected_delivery=result.get("expected_delivery"),
            checkpoints=result.get("checkpoints", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trackings", response_model=Dict[str, Any])
async def list_trackings(
    tag: Optional[str] = Query(None, description="Filter by status tag"),
    keyword: Optional[str] = Query(None, description="Search keyword"),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all trackings with optional filters
    
    Tag options: Pending, InfoReceived, InTransit, OutForDelivery, 
                 AttemptFail, Delivered, Exception, Expired
    """
    try:
        result = await aftership_service.get_trackings(
            tag=tag,
            keyword=keyword,
            limit=limit
        )
        return result
        
    except Exception as e:
        logger.error(f"Error listing trackings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trackings/{slug}/{tracking_number}")
async def delete_tracking(
    slug: str,
    tracking_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a tracking from AfterShip
    
    Note: This only removes it from tracking system, not from carrier.
    """
    try:
        success = await aftership_service.delete_tracking(slug, tracking_number)
        if success:
            return {"message": "Tracking deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete tracking")
            
    except Exception as e:
        logger.error(f"Error deleting tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trackings/bulk", response_model=Dict[str, Any])
async def bulk_create_trackings(
    bulk_data: BulkTrackingCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create multiple trackings in bulk
    
    Useful for importing tracking numbers from CSV or processing multiple shipments.
    Returns summary with success/failure counts.
    """
    try:
        trackings_data = [
            {
                "tracking_number": t.tracking_number,
                "slug": t.slug,
                "title": t.title,
                "order_id": t.order_id,
                "customer_name": t.customer_name,
                "destination_country": t.destination_country
            }
            for t in bulk_data.trackings
        ]
        
        result = await aftership_service.bulk_create_trackings(trackings_data)
        
        # Update orders in background
        for tracking in bulk_data.trackings:
            if tracking.order_id:
                background_tasks.add_task(
                    update_order_tracking,
                    db,
                    tracking.order_id,
                    tracking.tracking_number,
                    tracking.slug,
                    None
                )
        
        return result
        
    except Exception as e:
        logger.error(f"Error bulk creating trackings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/couriers/detect")
async def detect_courier(
    tracking_number: str = Query(..., description="Tracking number to detect courier"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Auto-detect courier from tracking number
    
    Returns list of possible couriers based on tracking number pattern.
    """
    try:
        couriers = await aftership_service.detect_courier(tracking_number)
        return {"couriers": couriers}
        
    except Exception as e:
        logger.error(f"Error detecting courier: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/couriers")
async def list_couriers(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all supported couriers
    
    Returns information about all couriers supported by AfterShip.
    """
    try:
        couriers = await aftership_service.get_couriers()
        return {"couriers": couriers, "count": len(couriers)}
        
    except Exception as e:
        logger.error(f"Error fetching couriers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks")
async def aftership_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint for AfterShip tracking updates
    
    AfterShip will send POST requests to this endpoint when tracking status changes.
    This endpoint verifies the webhook signature and processes the update.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get signature from header
        signature = request.headers.get("aftership-hmac-sha256", "")
        
        # Verify webhook signature
        if not aftership_service.verify_webhook_signature(body, signature):
            logger.warning("Invalid webhook signature received")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse webhook data
        event_data = await request.json()
        event_type = event_data.get("event")
        msg = event_data.get("msg", {})
        
        tracking_number = msg.get("tracking_number")
        slug = msg.get("slug")
        tag = msg.get("tag")
        order_id = msg.get("order_id")
        
        logger.info(f"Webhook received: {event_type} for tracking {tracking_number}")
        
        # Process webhook in background
        background_tasks.add_task(
            process_webhook_event,
            db,
            event_type,
            tracking_number,
            slug,
            tag,
            order_id,
            msg
        )
        
        return {"status": "received"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Return 200 to prevent AfterShip from retrying
        return {"status": "error", "message": str(e)}


# Background task functions
async def update_order_tracking(
    db: AsyncSession,
    order_id: str,
    tracking_number: str,
    slug: Optional[str],
    tracking_link: Optional[str]
):
    """Update Purchase Order or Delivery Challan with tracking information"""
    try:
        # Try Purchase Order first
        stmt = select(PurchaseOrder).where(PurchaseOrder.voucher_number == order_id)
        result = await db.execute(stmt)
        po = result.scalar_one_or_none()
        
        if po:
            po.tracking_number = tracking_number
            if tracking_link:
                po.tracking_link = tracking_link
            po.transporter_name = slug or po.transporter_name
            await db.commit()
            logger.info(f"Updated PO {order_id} with tracking {tracking_number}")
            return
        
        # Try Delivery Challan
        stmt = select(DeliveryChallan).where(DeliveryChallan.voucher_number == order_id)
        result = await db.execute(stmt)
        dc = result.scalar_one_or_none()
        
        if dc:
            dc.tracking_number = tracking_number
            if tracking_link:
                dc.tracking_link = tracking_link
            dc.transporter_name = slug or dc.transporter_name
            await db.commit()
            logger.info(f"Updated DC {order_id} with tracking {tracking_number}")
            return
        
        logger.warning(f"Order {order_id} not found for tracking update")
        
    except Exception as e:
        logger.error(f"Error updating order tracking: {e}")
        await db.rollback()


async def process_webhook_event(
    db: AsyncSession,
    event_type: str,
    tracking_number: str,
    slug: str,
    tag: str,
    order_id: Optional[str],
    msg: Dict[str, Any]
):
    """Process AfterShip webhook event"""
    try:
        logger.info(f"Processing {event_type} for {tracking_number}, status: {tag}")
        
        # Update order status based on tracking status
        if order_id:
            # Find the order
            stmt = select(PurchaseOrder).where(PurchaseOrder.voucher_number == order_id)
            result = await db.execute(stmt)
            po = result.scalar_one_or_none()
            
            if po:
                # Update tracking status
                po.tracking_status = tag
                po.tracking_last_update = datetime.now()
                
                # Update expected delivery if available
                expected_delivery = msg.get("expected_delivery")
                if expected_delivery:
                    po.expected_delivery_date = datetime.fromisoformat(expected_delivery)
                
                # If delivered, update status
                if tag == "Delivered":
                    # Could auto-create GRN or send notification
                    logger.info(f"PO {order_id} delivered, consider creating GRN")
                
                # If exception, create alert
                elif tag == "Exception":
                    subtag = msg.get("subtag", "")
                    logger.warning(f"Exception for PO {order_id}: {subtag}")
                    # Could create a notification or alert here
                
                await db.commit()
                logger.info(f"Updated PO {order_id} status to {tag}")
        
        # Additional processing based on event type
        if event_type == "tracking.delivered":
            # Send delivery confirmation email
            logger.info(f"Shipment {tracking_number} delivered")
            
        elif event_type == "tracking.exception":
            # Send alert email
            logger.info(f"Exception for shipment {tracking_number}")
        
    except Exception as e:
        logger.error(f"Error processing webhook event: {e}")
        await db.rollback()
