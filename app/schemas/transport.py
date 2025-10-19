# app/schemas/transport.py (New File)
"""
Transport schemas for API validation and responses
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.transport_models import (
    CarrierType, RouteStatus, FreightMode, ShipmentStatus, VehicleType
)

# Courier Schema
class CourierResponse(BaseModel):
    name: str
    trackingLink: str

# Carrier Schemas
class CarrierCreate(BaseModel):
    carrier_code: str
    carrier_name: str
    carrier_type: CarrierType
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry_date: Optional[datetime] = None
    insurance_number: Optional[str] = None
    insurance_expiry_date: Optional[datetime] = None
    service_areas: Optional[List[str]] = []
    vehicle_types: Optional[List[str]] = []
    special_handling: Optional[List[str]] = []
    payment_terms: Optional[str] = None
    credit_limit: Optional[float] = 0.0
    tracking_capability: bool = False
    real_time_updates: bool = False
    is_preferred: bool = False
    notes: Optional[str] = None

class CarrierUpdate(BaseModel):
    carrier_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    rating: Optional[float] = None
    on_time_percentage: Optional[float] = None
    damage_rate: Optional[float] = None
    is_active: Optional[bool] = None
    is_preferred: Optional[bool] = None
    notes: Optional[str] = None

class CarrierResponse(BaseModel):
    id: int
    carrier_code: str
    carrier_name: str
    carrier_type: CarrierType
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    rating: float
    on_time_percentage: float
    tracking_capability: bool
    is_active: bool
    is_preferred: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Route Schemas
class RouteCreate(BaseModel):
    route_code: str
    route_name: str
    carrier_id: int
    origin_city: str
    origin_state: Optional[str] = None
    origin_country: Optional[str] = None
    destination_city: str
    destination_state: Optional[str] = None
    destination_country: Optional[str] = None
    distance_km: Optional[float] = None
    estimated_transit_time_hours: Optional[float] = None
    max_transit_time_hours: Optional[float] = None
    vehicle_type: Optional[VehicleType] = None
    frequency: Optional[str] = None
    operating_days: Optional[List[str]] = []
    max_weight_kg: Optional[float] = None
    max_volume_cbm: Optional[float] = None
    temperature_controlled: bool = False
    hazmat_allowed: bool = False
    fuel_surcharge_applicable: bool = True
    toll_charges_applicable: bool = True
    notes: Optional[str] = None

class RouteResponse(BaseModel):
    id: int
    route_code: str
    route_name: str
    carrier_id: int
    origin_city: str
    destination_city: str
    distance_km: Optional[float] = None
    estimated_transit_time_hours: Optional[float] = None
    status: RouteStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Freight Rate Schemas
class FreightRateCreate(BaseModel):
    rate_code: str
    carrier_id: int
    route_id: Optional[int] = None
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    freight_mode: FreightMode
    service_type: Optional[str] = None
    rate_basis: str
    minimum_charge: Optional[float] = 0.0
    rate_per_kg: Optional[float] = 0.0
    minimum_weight_kg: Optional[float] = 0.0
    maximum_weight_kg: Optional[float] = None
    rate_per_cbm: Optional[float] = 0.0
    minimum_volume_cbm: Optional[float] = 0.0
    maximum_volume_cbm: Optional[float] = None
    rate_per_km: Optional[float] = 0.0
    fixed_rate: Optional[float] = 0.0
    fuel_surcharge_percentage: Optional[float] = 0.0
    handling_charge: Optional[float] = 0.0
    documentation_charge: Optional[float] = 0.0
    insurance_percentage: Optional[float] = 0.0
    standard_transit_days: Optional[int] = None
    currency: str = "USD"
    tax_applicable: bool = True
    tax_percentage: Optional[float] = 0.0
    is_negotiated: bool = False
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None

class FreightRateResponse(BaseModel):
    id: int
    rate_code: str
    carrier_id: int
    route_id: Optional[int] = None
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    freight_mode: FreightMode
    rate_basis: str
    minimum_charge: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Shipment Schemas
class ShipmentItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit: str
    weight_per_unit_kg: Optional[float] = 0.0
    volume_per_unit_cbm: Optional[float] = 0.0
    packaging_type: Optional[str] = None
    number_of_packages: int = 1
    package_dimensions: Optional[str] = None
    batch_number: Optional[str] = None
    unit_value: Optional[float] = 0.0
    handling_instructions: Optional[str] = None
    notes: Optional[str] = None

class ShipmentCreate(BaseModel):
    carrier_id: int
    route_id: Optional[int] = None
    sales_order_id: Optional[int] = None
    purchase_order_id: Optional[int] = None
    manufacturing_order_id: Optional[int] = None
    freight_mode: FreightMode
    service_type: Optional[str] = None
    origin_name: str
    origin_address: Optional[str] = None
    origin_city: str
    origin_state: Optional[str] = None
    origin_postal_code: Optional[str] = None
    origin_country: Optional[str] = None
    destination_name: str
    destination_address: Optional[str] = None
    destination_city: str
    destination_state: Optional[str] = None
    destination_postal_code: Optional[str] = None
    destination_country: Optional[str] = None
    declared_value: Optional[float] = 0.0
    is_fragile: bool = False
    is_hazardous: bool = False
    temperature_controlled: bool = False
    signature_required: bool = False
    pickup_date: Optional[datetime] = None
    pickup_time_from: Optional[str] = None
    pickup_time_to: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    payment_terms: Optional[str] = None
    cod_amount: Optional[float] = 0.0
    special_instructions: Optional[str] = None
    notes: Optional[str] = None
    items: List[ShipmentItemCreate] = []

class ShipmentResponse(BaseModel):
    id: int
    shipment_number: str
    carrier_id: int
    tracking_number: Optional[str] = None
    freight_mode: FreightMode
    origin_city: str
    destination_city: str
    total_weight_kg: float
    total_volume_cbm: float
    total_pieces: int
    declared_value: float
    status: ShipmentStatus
    pickup_date: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    total_charges: float
    created_at: datetime

    class Config:
        from_attributes = True