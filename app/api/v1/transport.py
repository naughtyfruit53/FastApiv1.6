# app/api/v1/transport.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import pandas as pd
import os
import io
import re
from cachetools import TTLCache

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.transport_models import (
    Carrier, Route, FreightRate, Shipment, ShipmentTracking, ShipmentItem,
    CarrierType, RouteStatus, FreightMode, ShipmentStatus
)
from app.schemas.transport import (
    CourierResponse, CarrierCreate, CarrierUpdate, CarrierResponse, 
    RouteCreate, RouteResponse, FreightRateCreate, FreightRateResponse, 
    ShipmentCreate, ShipmentResponse, ShipmentItemCreate
)
from app.services.voucher_service import VoucherNumberService

logger = logging.getLogger(__name__)
router = APIRouter()

# Cache for courier list (1-hour TTL)
cache = TTLCache(maxsize=1, ttl=3600)

# Carrier Endpoints
@router.get("/carriers/", response_model=List[CarrierResponse])
async def get_carriers(
    skip: int = 0,
    limit: int = 100,
    carrier_type: Optional[CarrierType] = None,
    is_active: Optional[bool] = True,
    is_preferred: Optional[bool] = None,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(Carrier).filter(
        Carrier.organization_id == org_id
    )
    
    if carrier_type:
        stmt = stmt.filter(Carrier.carrier_type == carrier_type)
    if is_active is not None:
        stmt = stmt.filter(Carrier.is_active == is_active)
    if is_preferred is not None:
        stmt = stmt.filter(Carrier.is_preferred == is_preferred)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    carriers = result.scalars().all()
    return carriers

@router.post("/carriers/", response_model=CarrierResponse)
async def create_carrier(
    carrier_data: CarrierCreate,
    auth: tuple = Depends(require_access("transport", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Check if carrier code already exists
    result = await db.execute(select(Carrier).filter(
        Carrier.organization_id == org_id,
        Carrier.carrier_code == carrier_data.carrier_code
    ))
    existing_carrier = result.scalar_one_or_none()
    
    if existing_carrier:
        raise HTTPException(
            status_code=400, 
            detail="Carrier code already exists"
        )
    
    db_carrier = Carrier(
        organization_id=org_id,
        created_by=current_user.id,
        **carrier_data.dict()
    )
    
    db.add(db_carrier)
    await db.commit()
    await db.refresh(db_carrier)
    
    return db_carrier

@router.get("/carriers/{carrier_id}", response_model=CarrierResponse)
async def get_carrier(
    carrier_id: int,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    result = await db.execute(select(Carrier).filter(
        Carrier.id == carrier_id,
        Carrier.organization_id == org_id
    ))
    carrier = result.scalar_one_or_none()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    return carrier

@router.put("/carriers/{carrier_id}", response_model=CarrierResponse)
async def update_carrier(
    carrier_id: int,
    carrier_data: CarrierUpdate,
    auth: tuple = Depends(require_access("transport", "update")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    result = await db.execute(select(Carrier).filter(
        Carrier.id == carrier_id,
        Carrier.organization_id == org_id
    ))
    carrier = result.scalar_one_or_none()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    for field, value in carrier_data.dict(exclude_unset=True).items():
        setattr(carrier, field, value)
    
    await db.commit()
    await db.refresh(carrier)
    
    return carrier

# Route Endpoints
@router.get("/routes/", response_model=List[RouteResponse])
async def get_routes(
    skip: int = 0,
    limit: int = 100,
    carrier_id: Optional[int] = None,
    origin_city: Optional[str] = None,
    destination_city: Optional[str] = None,
    status: Optional[RouteStatus] = None,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(Route).filter(
        Route.organization_id == org_id
    )
    
    if carrier_id:
        stmt = stmt.filter(Route.carrier_id == carrier_id)
    if origin_city:
        stmt = stmt.filter(Route.origin_city.ilike(f"%{origin_city}%"))
    if destination_city:
        stmt = stmt.filter(Route.destination_city.ilike(f"%{destination_city}%"))
    if status:
        stmt = stmt.filter(Route.status == status)
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    routes = result.scalars().all()
    return routes

@router.post("/routes/", response_model=RouteResponse)
async def create_route(
    route_data: RouteCreate,
    auth: tuple = Depends(require_access("transport", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Verify carrier exists
    result = await db.execute(select(Carrier).filter(
        Carrier.id == route_data.carrier_id,
        Carrier.organization_id == org_id
    ))
    carrier = result.scalar_one_or_none()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    # Check if route code already exists
    result = await db.execute(select(Route).filter(
        Route.organization_id == org_id,
        Route.route_code == route_data.route_code
    ))
    existing_route = result.scalar_one_or_none()
    
    if existing_route:
        raise HTTPException(
            status_code=400, 
            detail="Route code already exists"
        )
    
    db_route = Route(
        organization_id=org_id,
        created_by=current_user.id,
        **route_data.dict()
    )
    
    db.add(db_route)
    await db.commit()
    await db.refresh(db_route)
    
    return db_route

# Freight Rate Endpoints
@router.get("/freight-rates/", response_model=List[FreightRateResponse])
async def get_freight_rates(
    skip: int = 0,
    limit: int = 100,
    carrier_id: Optional[int] = None,
    route_id: Optional[int] = None,
    freight_mode: Optional[FreightMode] = None,
    is_active: Optional[bool] = True,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(FreightRate).filter(
        FreightRate.organization_id == org_id
    )
    
    if carrier_id:
        stmt = stmt.filter(FreightRate.carrier_id == carrier_id)
    if route_id:
        stmt = stmt.filter(FreightRate.route_id == route_id)
    if freight_mode:
        stmt = stmt.filter(FreightRate.freight_mode == freight_mode)
    if is_active is not None:
        stmt = stmt.filter(FreightRate.is_active == is_active)
    
    # Filter by current date
    current_date = datetime.now()
    stmt = stmt.filter(
        FreightRate.effective_date <= current_date
    ).filter(
        (FreightRate.expiry_date.is_(None)) | (FreightRate.expiry_date >= current_date)
    )
    
    result = await db.execute(stmt.offset(skip).limit(limit))
    rates = result.scalars().all()
    return rates

@router.post("/freight-rates/", response_model=FreightRateResponse)
async def create_freight_rate(
    rate_data: FreightRateCreate,
    auth: tuple = Depends(require_access("transport", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Verify carrier exists
    result = await db.execute(select(Carrier).filter(
        Carrier.id == rate_data.carrier_id,
        Carrier.organization_id == org_id
    ))
    carrier = result.scalar_one_or_none()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    # Verify route exists if specified
    if rate_data.route_id:
        result = await db.execute(select(Route).filter(
            Route.id == rate_data.route_id,
            Route.organization_id == org_id
        ))
        route = result.scalar_one_or_none()
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
    
    db_rate = FreightRate(
        organization_id=org_id,
        created_by=current_user.id,
        **rate_data.dict()
    )
    
    db.add(db_rate)
    await db.commit()
    await db.refresh(db_rate)
    
    return db_rate

# Rate Comparison
@router.post("/freight-rates/compare")
async def compare_freight_rates(
    origin_city: str,
    destination_city: str,
    weight_kg: float,
    volume_cbm: Optional[float] = None,
    freight_mode: Optional[FreightMode] = None,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Find applicable routes
    result = await db.execute(select(Route).filter(
        Route.organization_id == org_id,
        Route.origin_city.ilike(f"%{origin_city}%"),
        Route.destination_city.ilike(f"%{destination_city}%"),
        Route.status == RouteStatus.ACTIVE
    ))
    routes = result.scalars().all()
    
    if not routes:
        raise HTTPException(
            status_code=404, 
            detail="No routes found for the specified origin and destination"
        )
    
    rate_comparisons = []
    current_date = datetime.now()
    
    for route in routes:
        # Find applicable rates for this route
        stmt = select(FreightRate).filter(
            FreightRate.organization_id == org_id,
            FreightRate.route_id == route.id,
            FreightRate.is_active == True,
            FreightRate.effective_date <= current_date
        ).filter(
            (FreightRate.expiry_date.is_(None)) | (FreightRate.expiry_date >= current_date)
        )
        
        if freight_mode:
            stmt = stmt.filter(FreightRate.freight_mode == freight_mode)
        
        result = await db.execute(stmt)
        rates = result.scalars().all()
        
        for rate in rates:
            # Calculate cost based on rate structure
            cost = 0.0
            
            if rate.rate_basis == "per_kg":
                if weight_kg >= rate.minimum_weight_kg:
                    cost = weight_kg * rate.rate_per_kg
                else:
                    cost = rate.minimum_charge
                    
            elif rate.rate_basis == "per_cbm" and volume_cbm:
                if volume_cbm >= rate.minimum_volume_cbm:
                    cost = volume_cbm * rate.rate_per_cbm
                else:
                    cost = rate.minimum_charge
            elif rate.rate_basis == "per_shipment":
                cost = rate.fixed_rate
                
            elif rate.rate_basis == "per_km" and route.distance_km:
                cost = route.distance_km * rate.rate_per_km
            
            # Add surcharges
            fuel_surcharge = cost * (rate.fuel_surcharge_percentage / 100)
            total_cost = cost + fuel_surcharge + rate.handling_charge + rate.documentation_charge
            
            # Add insurance if applicable
            if rate.insurance_percentage > 0:
                insurance_cost = (weight_kg * rate.rate_per_kg) * (rate.insurance_percentage / 100)
                total_cost += insurance_cost
            
            # Add tax if applicable
            if rate.tax_applicable:
                tax_amount = total_cost * (rate.tax_percentage / 100)
                total_cost += tax_amount
            
            rate_comparisons.append({
                "carrier_id": route.carrier_id,
                "carrier_name": route.carrier.carrier_name,
                "route_id": route.id,
                "route_name": route.route_name,
                "rate_id": rate.id,
                "rate_code": rate.rate_code,
                "freight_mode": rate.freight_mode.value,
                "service_type": rate.service_type,
                "base_cost": cost,
                "fuel_surcharge": fuel_surcharge,
                "handling_charge": rate.handling_charge,
                "total_cost": total_cost,
                "currency": rate.currency,
                "transit_days": rate.standard_transit_days,
                "estimated_transit_hours": route.estimated_transit_time_hours
            })
    
    # Sort by total cost
    rate_comparisons.sort(key=lambda x: x["total_cost"])
    
    return {
        "origin_city": origin_city,
        "destination_city": destination_city,
        "weight_kg": weight_kg,
        "volume_cbm": volume_cbm,
        "comparison_date": current_date,
        "rates": rate_comparisons
    }

# Shipment Endpoints
@router.get("/shipments/", response_model=List[ShipmentResponse])
async def get_shipments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ShipmentStatus] = None,
    carrier_id: Optional[int] = None,
    tracking_number: Optional[str] = None,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    stmt = select(Shipment).filter(
        Shipment.organization_id == org_id
    )
    
    if status:
        stmt = stmt.filter(Shipment.status == status)
    if carrier_id:
        stmt = stmt.filter(Shipment.carrier_id == carrier_id)
    if tracking_number:
        stmt = stmt.filter(Shipment.tracking_number.ilike(f"%{tracking_number}%"))
    
    result = await db.execute(stmt.order_by(Shipment.created_at.desc()).offset(skip).limit(limit))
    shipments = result.scalars().all()
    return shipments

@router.post("/shipments/", response_model=ShipmentResponse)
async def create_shipment(
    shipment_data: ShipmentCreate,
    auth: tuple = Depends(require_access("transport", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Verify carrier exists
    result = await db.execute(select(Carrier).filter(
        Carrier.id == shipment_data.carrier_id,
        Carrier.organization_id == org_id
    ))
    carrier = result.scalar_one_or_none()
    
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier not found")
    
    # Generate shipment number
    shipment_number = f"SH-{datetime.now().strftime('%Y%m%d')}-{org_id:04d}-{carrier.id:03d}"
    
    # Calculate totals from items
    total_weight_kg = sum(item.quantity * item.weight_per_unit_kg for item in shipment_data.items)
    total_volume_cbm = sum(item.quantity * item.volume_per_unit_cbm for item in shipment_data.items)
    total_pieces = sum(item.number_of_packages for item in shipment_data.items)
    
    db_shipment = Shipment(
        organization_id=org_id,
        shipment_number=shipment_number,
        total_weight_kg=total_weight_kg,
        total_volume_cbm=total_volume_cbm,
        total_pieces=total_pieces,
        created_by=current_user.id,
        **shipment_data.dict(exclude={'items'})
    )
    
    db.add(db_shipment)
    await db.flush()
    
    # Add shipment items
    for item_data in shipment_data.items:
        total_value = item_data.quantity * item_data.unit_value
        item = ShipmentItem(
            organization_id=org_id,
            shipment_id=db_shipment.id,
            total_value=total_value,
            **item_data.dict()
        )
        db.add(item)
    
    await db.commit()
    await db.refresh(db_shipment)
    
    return db_shipment

@router.get("/shipments/{shipment_id}/tracking")
async def get_shipment_tracking(
    shipment_id: int,
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    result = await db.execute(select(Shipment).filter(
        Shipment.id == shipment_id,
        Shipment.organization_id == org_id
    ))
    shipment = result.scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    result = await db.execute(select(ShipmentTracking).filter(
        ShipmentTracking.shipment_id == shipment_id,
        ShipmentTracking.organization_id == org_id
    ).order_by(ShipmentTracking.event_timestamp.desc()))
    tracking_events = result.scalars().all()
    
    return {
        "shipment_id": shipment_id,
        "shipment_number": shipment.shipment_number,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "tracking_events": tracking_events
    }

@router.post("/shipments/{shipment_id}/tracking")
async def add_tracking_event(
    shipment_id: int,
    event_type: str,
    status: str,
    description: str,
    location: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    is_exception: bool = False,
    exception_reason: Optional[str] = None,
    notes: Optional[str] = None,
    auth: tuple = Depends(require_access("transport", "create")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    result = await db.execute(select(Shipment).filter(
        Shipment.id == shipment_id,
        Shipment.organization_id == org_id
    ))
    shipment = result.scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    tracking_event = ShipmentTracking(
        organization_id=org_id,
        shipment_id=shipment_id,
        event_timestamp=datetime.now(),
        event_type=event_type,
        status=status,
        description=description,
        location=location,
        city=city,
        state=state,
        country=country,
        is_exception=is_exception,
        exception_reason=exception_reason,
        notes=notes,
        data_source="manual",
        created_by=current_user.id
    )
    
    db.add(tracking_event)
    
    # Update shipment status and location
    shipment.status = ShipmentStatus(status.lower()) if status.lower() in [s.value for s in ShipmentStatus] else shipment.status
    shipment.last_location_update = location or f"{city}, {state}" if city else None
    shipment.last_status_update = datetime.now()
    
    # Update delivery date if delivered
    if status.lower() == "delivered":
        shipment.actual_delivery_date = datetime.now()
    
    await db.commit()
    await db.refresh(tracking_event)
    
    return tracking_event

# Dashboard and Analytics
@router.get("/dashboard/summary")
async def get_transport_dashboard_summary(
    auth: tuple = Depends(require_access("transport", "read")),
    db: AsyncSession = Depends(get_db)
):
    current_user, org_id = auth
    
    # Total carriers
    result = await db.execute(select(func.count(Carrier.id)).filter(
        Carrier.organization_id == org_id,
        Carrier.is_active == True
    ))
    total_carriers = result.scalar()
    
    # Active shipments
    result = await db.execute(select(func.count(Shipment.id)).filter(
        Shipment.organization_id == org_id,
        Shipment.status.in_([ShipmentStatus.BOOKED, ShipmentStatus.IN_TRANSIT])
    ))
    active_shipments = result.scalar()
    
    # Delivered this month
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(select(func.count(Shipment.id)).filter(
        Shipment.organization_id == org_id,
        Shipment.status == ShipmentStatus.DELIVERED,
        Shipment.actual_delivery_date >= start_of_month
    ))
    delivered_this_month = result.scalar()
    
    # Pending pickups
    result = await db.execute(select(func.count(Shipment.id)).filter(
        Shipment.organization_id == org_id,
        Shipment.status == ShipmentStatus.BOOKED,
        Shipment.pickup_date <= datetime.now()
    ))
    pending_pickups = result.scalar()
    
    # Total freight cost this month
    result = await db.execute(select(Shipment).filter(
        Shipment.organization_id == org_id,
        Shipment.created_at >= start_of_month
    ))
    freight_cost_this_month = result.scalars().all()
    
    total_freight_cost = sum(shipment.total_charges or 0 for shipment in freight_cost_this_month)
    
    return {
        "total_carriers": total_carriers,
        "active_shipments": active_shipments,
        "delivered_this_month": delivered_this_month,
        "pending_pickups": pending_pickups,
        "total_freight_cost_this_month": total_freight_cost
    }

# Get courier list from CSV
@router.get("/couriers", response_model=List[CourierResponse])
async def get_couriers(
    auth: tuple = Depends(require_access("transport", "read"))
):
    if "couriers" in cache:
        return cache["couriers"]
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "../../static/comprehensive_courier_list_india.csv")
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="Courier list CSV not found")
        df = pd.read_csv(csv_path)
        couriers = [
            {"name": row["Name of Courier/Transporter"], "trackingLink": row["Consignment Tracking Link"]}
            for row in df.to_dict(orient="records")
        ]
        cache["couriers"] = couriers
        return couriers
    except Exception as e:
        logger.error(f"Error reading courier list: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reading courier list: {str(e)}")

# Upload new courier CSV
@router.post("/couriers/upload")
async def upload_courier_csv(
    file: UploadFile = File(...),
    auth: tuple = Depends(require_access("transport", "create"))
):
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        required_headers = ["Name of Courier/Transporter", "Consignment Tracking Link"]
        if not all(header in df.columns for header in required_headers):
            raise HTTPException(status_code=400, detail="Invalid CSV format: Missing required headers")
        if df["Name of Courier/Transporter"].duplicated().any():
            raise HTTPException(status_code=400, detail="Duplicate courier names found")
        # Validate tracking links
        url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
        invalid_urls = df[~df["Consignment Tracking Link"].str.match(url_pattern, na=False)]
        if not invalid_urls.empty:
            raise HTTPException(status_code=400, detail="Invalid tracking link URLs found")
        csv_path = os.path.join(os.path.dirname(__file__), "../../static/comprehensive_courier_list_india.csv")
        df.to_csv(csv_path, index=False)
        cache.pop("couriers", None)
        return {"message": "Courier list updated successfully"}
    except Exception as e:
        logger.error(f"Error uploading courier CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading CSV: {str(e)}")