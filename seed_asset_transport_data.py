#!/usr/bin/env python3
"""
Seed data script for Asset Management and Transport modules
"""

import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.asset_models import Asset, AssetStatus, AssetCondition, DepreciationMethod
from app.models.transport_models import Carrier, CarrierType

def seed_asset_data():
    """Seed sample asset data"""
    db = SessionLocal()
    
    try:
        # Sample assets
        assets_data = [
            {
                "organization_id": 1,  # Assuming first organization
                "asset_code": "EQP-001",
                "asset_name": "Manufacturing Press #1",
                "description": "High-precision hydraulic press for metal forming",
                "category": "Manufacturing Equipment",
                "subcategory": "Press",
                "manufacturer": "Industrial Solutions Inc",
                "model": "HP-5000",
                "serial_number": "HP5000-2023-001",
                "year_of_manufacture": 2023,
                "purchase_cost": 125000.00,
                "purchase_date": datetime(2023, 3, 15),
                "location": "Production Floor A",
                "department": "Manufacturing",
                "status": AssetStatus.ACTIVE,
                "condition": AssetCondition.EXCELLENT,
                "specifications": "5000 ton capacity, hydraulic system, programmable controls",
                "operating_capacity": "5000 tons",
                "power_rating": "500 kW",
                "depreciation_method": DepreciationMethod.STRAIGHT_LINE,
                "useful_life_years": 15,
                "salvage_value": 12500.00,
                "depreciation_rate": 6.67,
                "created_by": 1
            },
            {
                "organization_id": 1,
                "asset_code": "VEH-001",
                "asset_name": "Delivery Truck #1",
                "description": "Medium-duty delivery truck for customer shipments",
                "category": "Vehicle",
                "subcategory": "Truck",
                "manufacturer": "Ford",
                "model": "Transit 350",
                "serial_number": "1FTBW3XM5PKA12345",
                "year_of_manufacture": 2024,
                "purchase_cost": 45000.00,
                "purchase_date": datetime(2024, 1, 10),
                "location": "Vehicle Bay 1",
                "department": "Logistics",
                "assigned_to_employee": "John Driver",
                "status": AssetStatus.ACTIVE,
                "condition": AssetCondition.EXCELLENT,
                "specifications": "3.5L V6 engine, 350 payload capacity, GPS tracking",
                "operating_capacity": "350 cu ft",
                "power_rating": "250 HP",
                "depreciation_method": DepreciationMethod.STRAIGHT_LINE,
                "useful_life_years": 8,
                "salvage_value": 9000.00,
                "depreciation_rate": 12.5,
                "insurance_provider": "Commercial Auto Insurance Co",
                "insurance_policy_number": "POL-VEH-001",
                "insurance_expiry_date": datetime(2024, 12, 31),
                "created_by": 1
            },
            {
                "organization_id": 1,
                "asset_code": "IT-001",
                "asset_name": "Server Rack #1",
                "description": "Main database server for ERP system",
                "category": "IT Equipment",
                "subcategory": "Server",
                "manufacturer": "Dell",
                "model": "PowerEdge R750",
                "serial_number": "DELL-R750-2023-001",
                "year_of_manufacture": 2023,
                "purchase_cost": 15000.00,
                "purchase_date": datetime(2023, 6, 1),
                "location": "Server Room",
                "department": "IT",
                "status": AssetStatus.ACTIVE,
                "condition": AssetCondition.GOOD,
                "specifications": "Intel Xeon processor, 64GB RAM, 2TB SSD storage",
                "operating_capacity": "24/7 uptime",
                "power_rating": "750W",
                "depreciation_method": DepreciationMethod.STRAIGHT_LINE,
                "useful_life_years": 5,
                "salvage_value": 1500.00,
                "depreciation_rate": 20.0,
                "created_by": 1
            }
        ]
        
        for asset_data in assets_data:
            # Check if asset already exists
            existing = db.query(Asset).filter(
                Asset.organization_id == asset_data["organization_id"],
                Asset.asset_code == asset_data["asset_code"]
            ).first()
            
            if not existing:
                asset = Asset(**asset_data)
                db.add(asset)
                print(f"✅ Created asset: {asset_data['asset_code']} - {asset_data['asset_name']}")
            else:
                print(f"⚠️  Asset already exists: {asset_data['asset_code']}")
        
        db.commit()
        print(f"\n🎉 Asset data seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding asset data: {e}")
        db.rollback()
    finally:
        db.close()

def seed_transport_data():
    """Seed sample transport data"""
    db = SessionLocal()
    
    try:
        # Sample carriers
        carriers_data = [
            {
                "organization_id": 1,
                "carrier_code": "FDX-001",
                "carrier_name": "Federal Express",
                "carrier_type": CarrierType.COURIER,
                "contact_person": "John Smith",
                "phone": "+1-800-463-3339",
                "email": "corporate@fedex.com",
                "website": "https://www.fedex.com",
                "city": "Memphis",
                "state": "TN",
                "country": "USA",
                "license_number": "DOT-123456",
                "license_expiry_date": datetime(2025, 12, 31),
                "service_areas": ["USA", "Canada", "International"],
                "vehicle_types": ["Van", "Truck", "Aircraft"],
                "special_handling": ["Express", "Overnight", "International"],
                "rating": 4.5,
                "on_time_percentage": 95.2,
                "tracking_capability": True,
                "real_time_updates": True,
                "payment_terms": "Net 30",
                "credit_limit": 50000.00,
                "is_active": True,
                "is_preferred": True,
                "created_by": 1
            },
            {
                "organization_id": 1,
                "carrier_code": "UPS-001",
                "carrier_name": "United Parcel Service",
                "carrier_type": CarrierType.COURIER,
                "contact_person": "Jane Doe",
                "phone": "+1-800-742-5877",
                "email": "corporate@ups.com",
                "website": "https://www.ups.com",
                "city": "Atlanta",
                "state": "GA",
                "country": "USA",
                "license_number": "DOT-789012",
                "license_expiry_date": datetime(2025, 6, 30),
                "service_areas": ["USA", "Canada", "International"],
                "vehicle_types": ["Van", "Truck", "Aircraft"],
                "special_handling": ["Express", "Ground", "International"],
                "rating": 4.3,
                "on_time_percentage": 94.8,
                "tracking_capability": True,
                "real_time_updates": True,
                "payment_terms": "Net 30",
                "credit_limit": 45000.00,
                "is_active": True,
                "is_preferred": True,
                "created_by": 1
            },
            {
                "organization_id": 1,
                "carrier_code": "LOC-001",
                "carrier_name": "Local Transport LLC",
                "carrier_type": CarrierType.ROAD,
                "contact_person": "Mike Johnson",
                "phone": "+1-555-0123",
                "email": "dispatch@localtransport.com",
                "city": "Local City",
                "state": "Local State",
                "country": "USA",
                "license_number": "DOT-345678",
                "license_expiry_date": datetime(2024, 12, 31),
                "service_areas": ["Local Metro Area"],
                "vehicle_types": ["Truck", "Van"],
                "special_handling": ["Local Delivery", "Same Day"],
                "rating": 4.0,
                "on_time_percentage": 92.5,
                "tracking_capability": False,
                "real_time_updates": False,
                "payment_terms": "Net 15",
                "credit_limit": 10000.00,
                "is_active": True,
                "is_preferred": False,
                "created_by": 1
            }
        ]
        
        for carrier_data in carriers_data:
            # Check if carrier already exists
            existing = db.query(Carrier).filter(
                Carrier.organization_id == carrier_data["organization_id"],
                Carrier.carrier_code == carrier_data["carrier_code"]
            ).first()
            
            if not existing:
                carrier = Carrier(**carrier_data)
                db.add(carrier)
                print(f"✅ Created carrier: {carrier_data['carrier_code']} - {carrier_data['carrier_name']}")
            else:
                print(f"⚠️  Carrier already exists: {carrier_data['carrier_code']}")
        
        db.commit()
        print(f"\n🎉 Transport data seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding transport data: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main seeding function"""
    print("🌱 Starting Asset Management and Transport Data Seeding")
    print("=" * 60)
    
    print("\n📊 Seeding Asset Management Data...")
    seed_asset_data()
    
    print("\n🚛 Seeding Transport Management Data...")
    seed_transport_data()
    
    print("\n🎉 All seeding completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()