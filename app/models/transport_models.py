# app/models/transport_models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum, UniqueConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class CarrierType(enum.Enum):
    ROAD = "road"
    RAIL = "rail"
    AIR = "air"
    SEA = "sea"
    COURIER = "courier"
    MULTIMODAL = "multimodal"

class VehicleType(enum.Enum):
    TRUCK = "truck"
    VAN = "van"
    CONTAINER = "container"
    AIRCRAFT = "aircraft"
    SHIP = "ship"
    TRAIN = "train"

class ShipmentStatus(enum.Enum):
    PLANNED = "planned"
    BOOKED = "booked"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    DELAYED = "delayed"

class RouteStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SEASONAL = "seasonal"
    SUSPENDED = "suspended"

class FreightMode(enum.Enum):
    LTL = "ltl"  # Less Than Truckload
    FTL = "ftl"  # Full Truckload
    EXPRESS = "express"
    STANDARD = "standard"
    ECONOMY = "economy"

# Carrier Management
class Carrier(Base):
    __tablename__ = "carriers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Carrier Identification
    carrier_code = Column(String, nullable=False)
    carrier_name = Column(String, nullable=False)
    carrier_type = Column(Enum(CarrierType), nullable=False)
    
    # Contact Information
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    
    # Address
    address_line1 = Column(String)
    address_line2 = Column(String)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    country = Column(String)
    
    # Business Details
    license_number = Column(String)
    license_expiry_date = Column(DateTime(timezone=True))
    insurance_number = Column(String)
    insurance_expiry_date = Column(DateTime(timezone=True))
    
    # Service Areas and Capabilities
    service_areas = Column(JSON)  # List of cities/regions served
    vehicle_types = Column(JSON)  # List of vehicle types available
    special_handling = Column(JSON)  # Hazmat, refrigerated, etc.
    
    # Performance Metrics
    rating = Column(Float, default=0.0)  # 1-5 rating
    on_time_percentage = Column(Float, default=0.0)
    damage_rate = Column(Float, default=0.0)
    
    # Operational Details
    transit_time_reliability = Column(String)
    tracking_capability = Column(Boolean, default=False)
    real_time_updates = Column(Boolean, default=False)
    
    # Financial
    payment_terms = Column(String)
    credit_limit = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_preferred = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by_user = relationship("User")
    routes = relationship("Route", back_populates="carrier", cascade="all, delete-orphan")
    freight_rates = relationship("FreightRate", back_populates="carrier", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="carrier", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'carrier_code', name='uq_carrier_org_code'),
        Index('idx_carrier_org_type', 'organization_id', 'carrier_type'),
        Index('idx_carrier_org_active', 'organization_id', 'is_active'),
        Index('idx_carrier_org_name', 'organization_id', 'carrier_name'),
    )

# Route Management
class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Route Identification
    route_code = Column(String, nullable=False)
    route_name = Column(String, nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)
    
    # Route Details
    origin_city = Column(String, nullable=False)
    origin_state = Column(String)
    origin_country = Column(String)
    destination_city = Column(String, nullable=False)
    destination_state = Column(String)
    destination_country = Column(String)
    
    # Route Characteristics
    distance_km = Column(Float)
    estimated_transit_time_hours = Column(Float)
    max_transit_time_hours = Column(Float)
    
    # Operational
    vehicle_type = Column(Enum(VehicleType))
    frequency = Column(String)  # Daily, Weekly, etc.
    operating_days = Column(JSON)  # Days of week
    
    # Capacity and Restrictions
    max_weight_kg = Column(Float)
    max_volume_cbm = Column(Float)
    temperature_controlled = Column(Boolean, default=False)
    hazmat_allowed = Column(Boolean, default=False)
    
    # Performance
    average_transit_time_hours = Column(Float)
    on_time_percentage = Column(Float, default=0.0)
    
    # Cost Factors
    fuel_surcharge_applicable = Column(Boolean, default=True)
    toll_charges_applicable = Column(Boolean, default=True)
    
    # Status
    status = Column(Enum(RouteStatus), default=RouteStatus.ACTIVE, nullable=False)
    seasonal_start_date = Column(DateTime(timezone=True))
    seasonal_end_date = Column(DateTime(timezone=True))
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    carrier = relationship("Carrier", back_populates="routes")
    created_by_user = relationship("User")
    freight_rates = relationship("FreightRate", back_populates="route", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="route", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'route_code', name='uq_route_org_code'),
        Index('idx_route_org_carrier', 'organization_id', 'carrier_id'),
        Index('idx_route_org_origin', 'organization_id', 'origin_city'),
        Index('idx_route_org_dest', 'organization_id', 'destination_city'),
        Index('idx_route_org_status', 'organization_id', 'status'),
    )

# Freight Rate Management
class FreightRate(Base):
    __tablename__ = "freight_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Rate Identification
    rate_code = Column(String, nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"))
    
    # Rate Validity
    effective_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True))
    
    # Service Details
    freight_mode = Column(Enum(FreightMode), nullable=False)
    service_type = Column(String)  # Standard, Express, etc.
    
    # Rate Structure
    rate_basis = Column(String, nullable=False)  # per_kg, per_cbm, per_shipment, per_km
    minimum_charge = Column(Float, default=0.0)
    
    # Weight-based rates
    rate_per_kg = Column(Float, default=0.0)
    minimum_weight_kg = Column(Float, default=0.0)
    maximum_weight_kg = Column(Float)
    
    # Volume-based rates
    rate_per_cbm = Column(Float, default=0.0)
    minimum_volume_cbm = Column(Float, default=0.0)
    maximum_volume_cbm = Column(Float)
    
    # Distance-based rates
    rate_per_km = Column(Float, default=0.0)
    
    # Fixed rates
    fixed_rate = Column(Float, default=0.0)
    
    # Surcharges
    fuel_surcharge_percentage = Column(Float, default=0.0)
    handling_charge = Column(Float, default=0.0)
    documentation_charge = Column(Float, default=0.0)
    insurance_percentage = Column(Float, default=0.0)
    
    # Special Charges
    cod_charge_percentage = Column(Float, default=0.0)  # Cash on Delivery
    dangerous_goods_surcharge = Column(Float, default=0.0)
    oversized_surcharge = Column(Float, default=0.0)
    
    # Transit Time
    standard_transit_days = Column(Integer)
    express_transit_days = Column(Integer)
    
    # Currency and Tax
    currency = Column(String, default="USD")
    tax_applicable = Column(Boolean, default=True)
    tax_percentage = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_negotiated = Column(Boolean, default=False)
    
    # Chart of Accounts Integration
    freight_expense_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True, index=True)
    
    # Notes
    notes = Column(Text)
    terms_conditions = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    carrier = relationship("Carrier", back_populates="freight_rates")
    route = relationship("Route", back_populates="freight_rates")
    created_by_user = relationship("User")
    freight_expense_account = relationship("ChartOfAccounts", foreign_keys=[freight_expense_account_id])
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'rate_code', name='uq_freight_rate_org_code'),
        Index('idx_freight_rate_org_carrier', 'organization_id', 'carrier_id'),
        Index('idx_freight_rate_org_route', 'organization_id', 'route_id'),
        Index('idx_freight_rate_org_effective', 'organization_id', 'effective_date'),
        Index('idx_freight_rate_org_active', 'organization_id', 'is_active'),
    )

# Shipment Management
class Shipment(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Shipment Identification
    shipment_number = Column(String, nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"))
    
    # Reference Documents
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"))
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"))
    manufacturing_order_id = Column(Integer, ForeignKey("manufacturing_orders.id"))
    
    # Tracking
    tracking_number = Column(String)
    awb_number = Column(String)  # Air Waybill
    bol_number = Column(String)  # Bill of Lading
    
    # Shipment Details
    freight_mode = Column(Enum(FreightMode), nullable=False)
    service_type = Column(String)
    
    # Origin and Destination
    origin_name = Column(String, nullable=False)
    origin_address = Column(Text)
    origin_city = Column(String, nullable=False)
    origin_state = Column(String)
    origin_postal_code = Column(String)
    origin_country = Column(String)
    
    destination_name = Column(String, nullable=False)
    destination_address = Column(Text)
    destination_city = Column(String, nullable=False)
    destination_state = Column(String)
    destination_postal_code = Column(String)
    destination_country = Column(String)
    
    # Shipment Characteristics
    total_weight_kg = Column(Float, default=0.0)
    total_volume_cbm = Column(Float, default=0.0)
    total_pieces = Column(Integer, default=0)
    declared_value = Column(Float, default=0.0)
    
    # Special Handling
    is_fragile = Column(Boolean, default=False)
    is_hazardous = Column(Boolean, default=False)
    temperature_controlled = Column(Boolean, default=False)
    signature_required = Column(Boolean, default=False)
    
    # Timing
    pickup_date = Column(DateTime(timezone=True))
    pickup_time_from = Column(String)
    pickup_time_to = Column(String)
    expected_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    
    # Status
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PLANNED, nullable=False)
    last_location_update = Column(String)
    last_status_update = Column(DateTime(timezone=True))
    
    # Cost Information
    freight_charges = Column(Float, default=0.0)
    fuel_surcharge = Column(Float, default=0.0)
    handling_charges = Column(Float, default=0.0)
    insurance_charges = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    total_charges = Column(Float, default=0.0)
    
    # Payment
    payment_terms = Column(String)
    cod_amount = Column(Float, default=0.0)  # Cash on Delivery
    
    # Documents
    shipping_documents = Column(JSON)  # List of document paths
    
    # Notes
    special_instructions = Column(Text)
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    carrier = relationship("Carrier", back_populates="shipments")
    route = relationship("Route", back_populates="shipments")
    sales_order = relationship("SalesOrder")
    purchase_order = relationship("PurchaseOrder")
    manufacturing_order = relationship("ManufacturingOrder")
    created_by_user = relationship("User")
    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")
    tracking_events = relationship("ShipmentTracking", back_populates="shipment", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'shipment_number', name='uq_shipment_org_number'),
        Index('idx_shipment_org_carrier', 'organization_id', 'carrier_id'),
        Index('idx_shipment_org_status', 'organization_id', 'status'),
        Index('idx_shipment_org_pickup_date', 'organization_id', 'pickup_date'),
        Index('idx_shipment_org_tracking', 'organization_id', 'tracking_number'),
    )

# Shipment Items
class ShipmentItem(Base):
    __tablename__ = "shipment_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # References
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item Details
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    weight_per_unit_kg = Column(Float, default=0.0)
    volume_per_unit_cbm = Column(Float, default=0.0)
    
    # Packaging
    packaging_type = Column(String)  # Box, Pallet, etc.
    number_of_packages = Column(Integer, default=1)
    package_dimensions = Column(String)  # LxWxH
    
    # Tracking
    batch_number = Column(String)
    serial_numbers = Column(JSON)  # List of serial numbers
    
    # Value
    unit_value = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    
    # Special Handling
    handling_instructions = Column(Text)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    shipment = relationship("Shipment", back_populates="items")
    product = relationship("Product")
    
    __table_args__ = (
        Index('idx_shipment_items_org_shipment', 'organization_id', 'shipment_id'),
        Index('idx_shipment_items_org_product', 'organization_id', 'product_id'),
    )

# Shipment Tracking
class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # References
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)
    
    # Tracking Event
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String, nullable=False)  # pickup, transit, delivery, exception
    status = Column(String, nullable=False)
    description = Column(Text)
    
    # Location
    location = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    
    # Additional Details
    facility_name = Column(String)  # Sorting facility, depot, etc.
    vehicle_number = Column(String)
    driver_name = Column(String)
    
    # Exceptions
    is_exception = Column(Boolean, default=False)
    exception_reason = Column(String)
    resolution_required = Column(Boolean, default=False)
    
    # Source
    data_source = Column(String)  # manual, api, gps, etc.
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    shipment = relationship("Shipment", back_populates="tracking_events")
    created_by_user = relationship("User")
    
    __table_args__ = (
        Index('idx_shipment_tracking_org_shipment', 'organization_id', 'shipment_id'),
        Index('idx_shipment_tracking_org_timestamp', 'organization_id', 'event_timestamp'),
        Index('idx_shipment_tracking_org_status', 'organization_id', 'status'),
    )

# Freight Cost Analysis
class FreightCostAnalysis(Base):
    __tablename__ = "freight_cost_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Multi-tenant field - REQUIRED
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Analysis Period
    analysis_name = Column(String, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Scope
    carrier_id = Column(Integer, ForeignKey("carriers.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))
    
    # Cost Breakdown
    total_freight_cost = Column(Float, default=0.0)
    base_freight_cost = Column(Float, default=0.0)
    fuel_surcharges = Column(Float, default=0.0)
    handling_charges = Column(Float, default=0.0)
    insurance_costs = Column(Float, default=0.0)
    other_charges = Column(Float, default=0.0)
    
    # Volume Analysis
    total_shipments = Column(Integer, default=0)
    total_weight_kg = Column(Float, default=0.0)
    total_volume_cbm = Column(Float, default=0.0)
    
    # Performance Metrics
    average_cost_per_kg = Column(Float, default=0.0)
    average_cost_per_cbm = Column(Float, default=0.0)
    average_cost_per_shipment = Column(Float, default=0.0)
    on_time_delivery_percentage = Column(Float, default=0.0)
    damage_incidents = Column(Integer, default=0)
    
    # Comparison
    previous_period_cost = Column(Float, default=0.0)
    cost_variance = Column(Float, default=0.0)
    cost_variance_percentage = Column(Float, default=0.0)
    
    # Recommendations
    cost_optimization_opportunities = Column(Text)
    recommended_actions = Column(Text)
    
    # Notes
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    carrier = relationship("Carrier")
    route = relationship("Route")
    created_by_user = relationship("User")
    
    __table_args__ = (
        Index('idx_freight_analysis_org_period', 'organization_id', 'period_start'),
        Index('idx_freight_analysis_org_carrier', 'organization_id', 'carrier_id'),
        Index('idx_freight_analysis_org_route', 'organization_id', 'route_id'),
    )