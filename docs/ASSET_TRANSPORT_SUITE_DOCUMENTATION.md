# Asset Management and Transport Suite Documentation

## Overview

This document provides comprehensive documentation for the Asset Management and Transport/Freight modules implemented as part of PR 2: Manufacturing, Asset Lifecycle, and Transport Suite.

## Table of Contents

1. [Asset Management Module](#asset-management-module)
2. [Transport & Freight Module](#transport--freight-module)
3. [API Reference](#api-reference)
4. [Frontend Components](#frontend-components)
5. [Database Schema](#database-schema)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Integration Points](#integration-points)

## Asset Management Module

The Asset Management module provides comprehensive lifecycle management for organizational assets, including equipment, vehicles, IT hardware, and other valuable resources.

### Key Features

#### 1. Asset Master Data
- **Asset Registry**: Complete asset catalog with detailed specifications
- **Categories**: Flexible categorization system (Equipment, Vehicle, IT, Building, etc.)
- **Specifications**: Technical details, capacity, power ratings
- **Financial Data**: Purchase cost, depreciation, salvage value
- **Location Tracking**: Department, location, assigned employee

#### 2. Maintenance Management
- **Preventive Maintenance**: Scheduled maintenance based on time or usage
- **Corrective Maintenance**: Repair and emergency maintenance
- **Work Orders**: Complete work order lifecycle with parts and labor tracking
- **Maintenance Records**: Historical maintenance with cost analysis
- **Due Alerts**: Automated alerts for upcoming maintenance

#### 3. Asset Depreciation
- **Multiple Methods**: Straight-line, declining balance, units of production
- **Automated Calculation**: Period-based depreciation calculation
- **Book Value Tracking**: Real-time asset valuation
- **Reporting**: Depreciation reports for financial analysis

#### 4. Asset Dashboard
- **Key Metrics**: Total assets, active assets, maintenance due
- **Performance Indicators**: Asset utilization, maintenance costs
- **Alert Summary**: Overdue maintenance, warranty expiry

### Asset Lifecycle Workflow

```
Asset Creation → In Service → Maintenance → Condition Updates → Retirement/Disposal
     ↑              ↓           ↓              ↓                    ↓
Financial Setup → Depreciation → Work Orders → Value Updates → Final Disposition
```

## Transport & Freight Module

The Transport & Freight module manages logistics operations, carrier relationships, and shipment tracking for efficient goods movement.

### Key Features

#### 1. Carrier Management
- **Multi-Modal Support**: Road, rail, air, sea, courier services
- **Performance Tracking**: On-time delivery, damage rates, ratings
- **Service Areas**: Geographic coverage and capabilities
- **Contract Management**: Payment terms, credit limits, preferences

#### 2. Route Management
- **Origin-Destination Routes**: Defined shipping lanes
- **Capacity Planning**: Weight and volume limitations
- **Transit Times**: Estimated and actual delivery windows
- **Operational Parameters**: Temperature control, hazmat capability

#### 3. Freight Rate Management
- **Complex Rate Structures**: Weight-based, volume-based, distance-based
- **Surcharges**: Fuel, handling, documentation, insurance
- **Rate Comparison**: Automated comparison across carriers
- **Contract Rates**: Negotiated vs. standard pricing

#### 4. Shipment Management
- **End-to-End Tracking**: From booking to delivery
- **Multi-Item Shipments**: Product-level tracking within shipments
- **Real-Time Updates**: Status updates and location tracking
- **Exception Management**: Delays, damages, delivery issues

#### 5. Analytics & Reporting
- **Cost Analysis**: Freight spend analysis and optimization
- **Performance Metrics**: Carrier performance comparison
- **Trend Analysis**: Shipping volume and cost trends

### Shipment Lifecycle Workflow

```
Rate Quote → Booking → Pickup → Transit → Delivery → Invoice
    ↑           ↓        ↓        ↓         ↓         ↓
Rate Comparison → Tracking → Updates → Delivery → Cost Analysis
```

## API Reference

### Asset Management Endpoints

#### Assets
- `GET /api/v1/assets/` - List all assets
- `POST /api/v1/assets/` - Create new asset
- `GET /api/v1/assets/{id}` - Get asset details
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset
- `GET /api/v1/assets/categories/` - Get asset categories
- `GET /api/v1/assets/dashboard/summary` - Dashboard metrics

#### Maintenance
- `GET /api/v1/assets/maintenance-schedules/` - List schedules
- `POST /api/v1/assets/maintenance-schedules/` - Create schedule
- `GET /api/v1/assets/maintenance-schedules/due/` - Due maintenance
- `GET /api/v1/assets/maintenance-records/` - List records
- `POST /api/v1/assets/maintenance-records/` - Create record
- `PUT /api/v1/assets/maintenance-records/{id}/complete` - Complete work

#### Depreciation
- `GET /api/v1/assets/{id}/depreciation` - Asset depreciation history
- `POST /api/v1/assets/{id}/depreciation` - Calculate depreciation

### Transport Management Endpoints

#### Carriers
- `GET /api/v1/transport/carriers/` - List carriers
- `POST /api/v1/transport/carriers/` - Create carrier
- `GET /api/v1/transport/carriers/{id}` - Get carrier details
- `PUT /api/v1/transport/carriers/{id}` - Update carrier

#### Routes
- `GET /api/v1/transport/routes/` - List routes
- `POST /api/v1/transport/routes/` - Create route

#### Freight Rates
- `GET /api/v1/transport/freight-rates/` - List rates
- `POST /api/v1/transport/freight-rates/` - Create rate
- `POST /api/v1/transport/freight-rates/compare` - Compare rates

#### Shipments
- `GET /api/v1/transport/shipments/` - List shipments
- `POST /api/v1/transport/shipments/` - Create shipment
- `GET /api/v1/transport/shipments/{id}/tracking` - Tracking history
- `POST /api/v1/transport/shipments/{id}/tracking` - Add tracking event

#### Analytics
- `GET /api/v1/transport/dashboard/summary` - Dashboard metrics

## Frontend Components

### Asset Management UI

#### Main Page (`/assets`)
- **Tabbed Interface**: Assets, Schedules, Records, Due Maintenance, Reports
- **Dashboard Cards**: Key metrics with visual indicators
- **Asset Register**: Searchable table with filters
- **Maintenance Calendar**: Due dates and scheduling

#### Key Components
- Asset creation/edit forms
- Maintenance schedule builder
- Work order management
- Depreciation calculator
- Reports generator

### Transport Management UI

#### Main Page (`/transport`)
- **Tabbed Interface**: Carriers, Routes, Rates, Shipments, Comparison, Analytics
- **Dashboard Cards**: Transport metrics and KPIs
- **Carrier Management**: Performance tracking and preferences
- **Rate Comparison Tool**: Interactive rate shopping

#### Key Components
- Carrier profile management
- Route planning interface
- Rate calculation tools
- Shipment tracking dashboard
- Cost analysis reports

## Database Schema

### Asset Management Tables

#### `assets`
- Asset master data with specifications and financial information
- Links to vendors, users for ownership tracking
- Supports multiple depreciation methods

#### `maintenance_schedules`
- Frequency-based maintenance planning
- Time and meter-based scheduling
- Resource requirement planning

#### `maintenance_records`
- Complete work order history
- Parts usage and cost tracking
- Quality and condition updates

#### `maintenance_parts_used`
- Parts consumption tracking
- Batch and serial number tracking
- Cost allocation

#### `depreciation_records`
- Period-based depreciation calculation
- Multiple method support
- Historical value tracking

### Transport Management Tables

#### `carriers`
- Carrier master data with capabilities
- Performance metrics and ratings
- Service area definitions

#### `routes`
- Origin-destination route definitions
- Capacity and operational parameters
- Performance tracking

#### `freight_rates`
- Complex rate structures
- Multiple rate basis support
- Surcharge calculations

#### `shipments`
- Shipment master with tracking
- Multi-modal support
- Cost and performance tracking

#### `shipment_items`
- Item-level shipment details
- Packaging and handling requirements
- Value tracking

#### `shipment_tracking`
- Event-based tracking history
- Exception management
- Real-time updates

#### `freight_cost_analysis`
- Cost analysis and reporting
- Performance benchmarking
- Optimization recommendations

## Installation & Setup

### Database Setup

1. **Run Migrations**
   ```bash
   cd /path/to/FastApiv1.6
   python -m alembic upgrade head
   ```

2. **Seed Sample Data**
   ```bash
   python seed_asset_transport_data.py
   ```

### API Configuration

The modules are automatically included in the main FastAPI application. Ensure the following imports are present in `app/main.py`:

```python
from app.api.v1 import assets as v1_assets
from app.api.v1 import transport as v1_transport

app.include_router(v1_assets.router, prefix="/api/v1/assets", tags=["asset-management"])
app.include_router(v1_transport.router, prefix="/api/v1/transport", tags=["transport-freight"])
```

### Frontend Setup

The React components are ready to use. Add navigation links:

```typescript
// Add to navigation menu
{ path: '/assets', label: 'Asset Management', icon: SettingsIcon }
{ path: '/transport', label: 'Transport', icon: LocalShippingIcon }
```

## Usage Guide

### Asset Management Workflow

#### 1. Setting Up Assets
1. Navigate to Asset Management
2. Click "Add Asset" to create new assets
3. Fill in basic information (code, name, category)
4. Add financial details (cost, depreciation method)
5. Specify location and assignment

#### 2. Maintenance Planning
1. Go to Maintenance Schedules tab
2. Create schedules for each asset
3. Set frequency (time-based or meter-based)
4. Define required resources and skills
5. Set priority and advance notice

#### 3. Work Order Management
1. Monitor Due Maintenance tab
2. Create work orders for due items
3. Record actual work performed
4. Track parts usage and costs
5. Update asset condition

#### 4. Depreciation Management
1. Set up depreciation parameters for assets
2. Run periodic depreciation calculations
3. Generate depreciation reports
4. Update asset book values

### Transport Management Workflow

#### 1. Carrier Setup
1. Navigate to Transport Management
2. Add carriers with contact information
3. Define service areas and capabilities
4. Set up rate agreements
5. Configure performance tracking

#### 2. Route Planning
1. Create routes between locations
2. Define capacity and restrictions
3. Set estimated transit times
4. Link to appropriate carriers

#### 3. Rate Management
1. Set up freight rates for carriers
2. Define rate structures (weight, volume, distance)
3. Add surcharges and fees
4. Set effective dates and terms

#### 4. Shipment Processing
1. Create shipments for orders
2. Select carrier and route
3. Add shipment items
4. Generate tracking numbers
5. Monitor delivery progress

#### 5. Performance Analysis
1. Review carrier performance metrics
2. Analyze freight costs and trends
3. Identify optimization opportunities
4. Generate management reports

## Integration Points

### ERP Integration
- **Purchase Orders**: Link to asset purchases and carrier contracts
- **Inventory**: Track parts for maintenance and shipping items
- **Financial**: Asset depreciation and freight cost accounting
- **Manufacturing**: Asset utilization and product shipments

### Existing Modules
- **Manufacturing Orders**: Ship finished goods, maintain production equipment
- **Service Management**: Asset maintenance integration
- **Analytics**: Performance dashboards and reporting

### External Systems
- **Carrier APIs**: Real-time tracking integration
- **GPS Systems**: Vehicle and asset location tracking
- **ERP Systems**: Financial and operational data sync
- **IoT Sensors**: Asset condition monitoring

## Best Practices

### Asset Management
1. **Standardize Asset Codes**: Use consistent numbering schemes
2. **Regular Condition Updates**: Monitor asset health proactively
3. **Preventive Maintenance**: Prioritize scheduled over reactive maintenance
4. **Cost Tracking**: Monitor total cost of ownership
5. **Documentation**: Maintain complete maintenance records

### Transport Management
1. **Carrier Diversification**: Maintain multiple carrier relationships
2. **Rate Shopping**: Regularly compare rates for optimization
3. **Performance Monitoring**: Track carrier KPIs consistently
4. **Exception Management**: Handle delays and issues promptly
5. **Cost Analysis**: Regular freight spend analysis

## Troubleshooting

### Common Issues

#### Asset Management
- **Depreciation Errors**: Verify asset cost and useful life settings
- **Maintenance Alerts**: Check schedule frequency and advance notice
- **Permission Issues**: Ensure proper RBAC configuration

#### Transport Management
- **Rate Calculation**: Verify rate basis and surcharge settings
- **Tracking Issues**: Check carrier API connections
- **Performance Metrics**: Ensure data quality and completeness

### Support
For technical support and questions:
1. Check API documentation at `/docs`
2. Review error logs for detailed messages
3. Test endpoints with provided test scripts
4. Contact system administrators for access issues

## Future Enhancements

### Planned Features
1. **IoT Integration**: Sensor data for asset monitoring
2. **Mobile Apps**: Field maintenance and delivery apps
3. **AI Analytics**: Predictive maintenance and route optimization
4. **API Integrations**: External carrier and fleet management systems
5. **Advanced Reporting**: Custom dashboards and analytics

### Extensibility
The modular architecture supports easy extension:
- Additional asset types and categories
- New carrier types and services
- Custom rate structures
- Enhanced tracking capabilities
- Integration with external systems