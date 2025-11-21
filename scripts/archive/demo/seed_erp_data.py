# scripts/seed_erp_data.py
"""
Sample data fixtures for ERP modules - Demo/Testing data
"""

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from app.core.database import SessionLocal
from app.models import (
    Organization, ChartOfAccounts, GSTConfiguration, TaxCode,
    Warehouse, StockLocation, ProductTracking, Product,
    RequestForQuotation, RFQItem, VendorRFQ, Vendor,
    TallyConfiguration
)


def seed_chart_of_accounts(db: Session, organization_id: int):
    """Seed chart of accounts with standard Indian accounting structure"""
    print("Seeding Chart of Accounts...")
    
    accounts = [
        # Assets
        {"code": "1000", "name": "Current Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1001", "name": "Cash", "type": "cash", "is_group": False, "parent": "1000", "opening_balance": 10000.00},
        {"code": "1002", "name": "Bank Account", "type": "bank", "is_group": False, "parent": "1000", "opening_balance": 50000.00},
        {"code": "1003", "name": "Accounts Receivable", "type": "asset", "is_group": False, "parent": "1000", "opening_balance": 25000.00},
        {"code": "1004", "name": "Inventory", "type": "asset", "is_group": False, "parent": "1000", "opening_balance": 30000.00},
        
        {"code": "1100", "name": "Fixed Assets", "type": "asset", "is_group": True, "parent": None},
        {"code": "1101", "name": "Plant & Machinery", "type": "asset", "is_group": False, "parent": "1100", "opening_balance": 100000.00},
        {"code": "1102", "name": "Furniture & Fixtures", "type": "asset", "is_group": False, "parent": "1100", "opening_balance": 15000.00},
        
        # Liabilities
        {"code": "2000", "name": "Current Liabilities", "type": "liability", "is_group": True, "parent": None},
        {"code": "2001", "name": "Accounts Payable", "type": "liability", "is_group": False, "parent": "2000", "opening_balance": 20000.00},
        {"code": "2002", "name": "GST Payable", "type": "liability", "is_group": False, "parent": "2000", "opening_balance": 5000.00},
        {"code": "2003", "name": "TDS Payable", "type": "liability", "is_group": False, "parent": "2000", "opening_balance": 2000.00},
        
        # Equity
        {"code": "3000", "name": "Capital", "type": "equity", "is_group": True, "parent": None},
        {"code": "3001", "name": "Share Capital", "type": "equity", "is_group": False, "parent": "3000", "opening_balance": 100000.00},
        {"code": "3002", "name": "Retained Earnings", "type": "equity", "is_group": False, "parent": "3000", "opening_balance": 50000.00},
        
        # Income
        {"code": "4000", "name": "Revenue", "type": "income", "is_group": True, "parent": None},
        {"code": "4001", "name": "Sales Revenue", "type": "income", "is_group": False, "parent": "4000"},
        {"code": "4002", "name": "Service Revenue", "type": "income", "is_group": False, "parent": "4000"},
        {"code": "4003", "name": "Other Income", "type": "income", "is_group": False, "parent": "4000"},
        
        # Expenses
        {"code": "5000", "name": "Operating Expenses", "type": "expense", "is_group": True, "parent": None},
        {"code": "5001", "name": "Cost of Goods Sold", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5002", "name": "Salaries & Wages", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5003", "name": "Rent Expense", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5004", "name": "Utilities Expense", "type": "expense", "is_group": False, "parent": "5000"},
        {"code": "5005", "name": "Professional Fees", "type": "expense", "is_group": False, "parent": "5000"},
    ]
    
    # Create parent accounts first
    created_accounts = {}
    
    for account_data in accounts:
        if account_data["parent"] is None:
            account = ChartOfAccounts(
                organization_id=organization_id,
                account_code=account_data["code"],
                account_name=account_data["name"],
                account_type=account_data["type"],
                is_group=account_data["is_group"],
                opening_balance=Decimal(str(account_data.get("opening_balance", 0))),
                current_balance=Decimal(str(account_data.get("opening_balance", 0))),
                level=0
            )
            db.add(account)
            db.flush()
            created_accounts[account_data["code"]] = account
    
    # Create child accounts
    for account_data in accounts:
        if account_data["parent"] is not None:
            parent_account = created_accounts[account_data["parent"]]
            account = ChartOfAccounts(
                organization_id=organization_id,
                account_code=account_data["code"],
                account_name=account_data["name"],
                account_type=account_data["type"],
                parent_account_id=parent_account.id,
                is_group=account_data["is_group"],
                opening_balance=Decimal(str(account_data.get("opening_balance", 0))),
                current_balance=Decimal(str(account_data.get("opening_balance", 0))),
                level=parent_account.level + 1
            )
            db.add(account)
            created_accounts[account_data["code"]] = account
    
    db.commit()
    print(f"Created {len(accounts)} chart of accounts entries")


def seed_gst_configuration(db: Session, organization_id: int):
    """Seed GST configuration"""
    print("Seeding GST Configuration...")
    
    gst_config = GSTConfiguration(
        organization_id=organization_id,
        gstin="29AABCT1332L1ZZ",
        trade_name="TRITIQ BOS Solutions",
        legal_name="TRITIQ BOS Solutions Private Limited",
        registration_date=date(2023, 4, 1),
        constitution="Private Limited Company",
        business_type="Regular",
        address_line1="123 Tech Park",
        address_line2="Sector 5",
        city="Bangalore",
        state="Karnataka",
        pincode="560001",
        is_composition_scheme=False
    )
    
    db.add(gst_config)
    db.commit()
    
    # Seed tax codes
    tax_codes = [
        {"code": "CGST_9", "name": "CGST @ 9%", "type": "cgst", "rate": 9.00},
        {"code": "SGST_9", "name": "SGST @ 9%", "type": "sgst", "rate": 9.00},
        {"code": "IGST_18", "name": "IGST @ 18%", "type": "igst", "rate": 18.00},
        {"code": "CGST_6", "name": "CGST @ 6%", "type": "cgst", "rate": 6.00},
        {"code": "SGST_6", "name": "SGST @ 6%", "type": "sgst", "rate": 6.00},
        {"code": "IGST_12", "name": "IGST @ 12%", "type": "igst", "rate": 12.00},
        {"code": "TDS_2", "name": "TDS @ 2%", "type": "tds", "rate": 2.00},
    ]
    
    for tax_data in tax_codes:
        tax_code = TaxCode(
            organization_id=organization_id,
            gst_configuration_id=gst_config.id,
            tax_code=tax_data["code"],
            tax_name=tax_data["name"],
            tax_type=tax_data["type"],
            tax_rate=Decimal(str(tax_data["rate"])),
            hsn_sac_code="998313" if tax_data["type"] in ["cgst", "sgst", "igst"] else None
        )
        db.add(tax_code)
    
    db.commit()
    print(f"Created GST configuration and {len(tax_codes)} tax codes")


def seed_warehouses(db: Session, organization_id: int):
    """Seed warehouse and location data"""
    print("Seeding Warehouses...")
    
    warehouses = [
        {
            "code": "WH001",
            "name": "Main Warehouse",
            "type": "main",
            "address": "Industrial Area Phase 1",
            "city": "Bangalore",
            "state": "Karnataka",
            "pincode": "560058",
            "capacity": 10000.0
        },
        {
            "code": "WH002", 
            "name": "Branch Warehouse - Delhi",
            "type": "branch",
            "address": "Sector 63, Noida",
            "city": "Noida",
            "state": "Uttar Pradesh",
            "pincode": "201301",
            "capacity": 5000.0
        }
    ]
    
    created_warehouses = []
    
    for wh_data in warehouses:
        warehouse = Warehouse(
            organization_id=organization_id,
            warehouse_code=wh_data["code"],
            warehouse_name=wh_data["name"],
            warehouse_type=wh_data["type"],
            address_line1=wh_data["address"],
            city=wh_data["city"],
            state=wh_data["state"],
            pincode=wh_data["pincode"],
            country="India",
            storage_capacity_units=Decimal(str(wh_data["capacity"])),
            is_main_warehouse=(wh_data["type"] == "main")
        )
        db.add(warehouse)
        db.flush()
        created_warehouses.append(warehouse)
        
        # Create stock locations for each warehouse
        locations = [
            {"code": "A1-R1", "name": "Aisle 1 - Rack 1", "type": "Rack"},
            {"code": "A1-R2", "name": "Aisle 1 - Rack 2", "type": "Rack"},
            {"code": "A2-R1", "name": "Aisle 2 - Rack 1", "type": "Rack"},
            {"code": "FLOOR-01", "name": "Floor Storage Area 1", "type": "Floor"},
        ]
        
        for loc_data in locations:
            location = StockLocation(
                warehouse_id=warehouse.id,
                location_code=loc_data["code"],
                location_name=loc_data["name"],
                location_type=loc_data["type"],
                max_capacity_units=Decimal("500.0")
            )
            db.add(location)
    
    db.commit()
    print(f"Created {len(warehouses)} warehouses with stock locations")
    return created_warehouses


def seed_product_tracking(db: Session, organization_id: int):
    """Seed product tracking configuration"""
    print("Seeding Product Tracking...")
    
    # Get some products to configure tracking for
    products = db.query(Product).filter(
        Product.organization_id == organization_id
    ).limit(5).all()
    
    tracking_configs = [
        {"tracking_type": "batch", "valuation_method": "fifo", "batch_expiry": True},
        {"tracking_type": "serial", "valuation_method": "weighted_average", "batch_expiry": False},
        {"tracking_type": "batch_and_serial", "valuation_method": "fifo", "batch_expiry": True},
        {"tracking_type": "none", "valuation_method": "weighted_average", "batch_expiry": False},
        {"tracking_type": "batch", "valuation_method": "lifo", "batch_expiry": False},
    ]
    
    for i, product in enumerate(products):
        if i < len(tracking_configs):
            config = tracking_configs[i]
            tracking = ProductTracking(
                product_id=product.id,
                tracking_type=config["tracking_type"],
                valuation_method=config["valuation_method"],
                batch_naming_series="BATCH-.YYYY.-.####" if "batch" in config["tracking_type"] else None,
                batch_expiry_required=config["batch_expiry"],
                serial_naming_series="SRL-.YYYY.-.#####" if "serial" in config["tracking_type"] else None,
                enable_reorder_alert=True,
                reorder_level=Decimal("10.0"),
                reorder_quantity=Decimal("50.0"),
                max_stock_level=Decimal("200.0"),
                procurement_lead_time_days=7
            )
            db.add(tracking)
    
    db.commit()
    print(f"Created tracking configuration for {min(len(products), len(tracking_configs))} products")


def seed_sample_rfq(db: Session, organization_id: int):
    """Seed sample RFQ data"""
    print("Seeding Sample RFQ...")
    
    # Get some vendors
    vendors = db.query(Vendor).filter(
        Vendor.organization_id == organization_id
    ).limit(3).all()
    
    if not vendors:
        print("No vendors found, skipping RFQ seeding")
        return
    
    # Create a sample RFQ
    rfq = RequestForQuotation(
        organization_id=organization_id,
        rfq_number="RFQ-2024-0001",
        rfq_title="Office Supplies and Equipment",
        rfq_description="Procurement of office supplies and computer equipment for Q1 2024",
        issue_date=date.today(),
        submission_deadline=date.today() + timedelta(days=15),
        validity_period=30,
        terms_and_conditions="Standard terms and conditions apply",
        delivery_requirements="Delivery required within 2 weeks of order confirmation",
        payment_terms="Net 30 days",
        status="sent"
    )
    
    db.add(rfq)
    db.flush()
    
    # Create RFQ items
    items = [
        {"code": "OFF-001", "name": "Office Chairs", "qty": 20, "unit": "Nos"},
        {"code": "COMP-001", "name": "Laptops", "qty": 10, "unit": "Nos"},
        {"code": "STAT-001", "name": "Stationery Kit", "qty": 50, "unit": "Sets"},
    ]
    
    for item_data in items:
        rfq_item = RFQItem(
            rfq_id=rfq.id,
            item_code=item_data["code"],
            item_name=item_data["name"],
            item_description=f"High quality {item_data['name'].lower()}",
            quantity=Decimal(str(item_data["qty"])),
            unit=item_data["unit"],
            specifications={"quality": "premium", "warranty": "1 year"},
            required_delivery_date=date.today() + timedelta(days=20)
        )
        db.add(rfq_item)
    
    # Invite vendors
    for vendor in vendors:
        vendor_rfq = VendorRFQ(
            rfq_id=rfq.id,
            vendor_id=vendor.id,
            invited_date=date.today(),
            invitation_sent=True
        )
        db.add(vendor_rfq)
    
    db.commit()
    print(f"Created sample RFQ with {len(items)} items and invited {len(vendors)} vendors")


def seed_tally_configuration(db: Session, organization_id: int):
    """Seed sample Tally configuration"""
    print("Seeding Tally Configuration...")
    
    config = TallyConfiguration(
        organization_id=organization_id,
        tally_server_host="localhost",
        tally_server_port=9000,
        company_name_in_tally="TRITIQ BOS Solutions",
        sync_direction="bidirectional",
        auto_sync_enabled=False,
        sync_interval_minutes=30,
        sync_masters=True,
        sync_vouchers=True,
        sync_reports=False,
        field_mappings={
            "account_name": "ledger_name",
            "account_code": "ledger_alias",
            "opening_balance": "opening_balance"
        },
        ledger_mappings={
            "cash": "Cash",
            "bank": "Bank Account",
            "sales": "Sales Account"
        },
        voucher_type_mappings={
            "sales_voucher": "Sales",
            "purchase_voucher": "Purchase",
            "payment_voucher": "Payment",
            "receipt_voucher": "Receipt"
        },
        connection_status="disconnected"
    )
    
    db.add(config)
    db.commit()
    print("Created Tally configuration")


def main():
    """Main function to seed all ERP demo data"""
    print("Starting ERP data seeding...")
    
    db = SessionLocal()
    try:
        # Use the first organization (for demo purposes)
        organization = db.query(Organization).first()
        if not organization:
            print("No organization found. Please create an organization first.")
            return
        
        print(f"Seeding data for organization: {organization.name}")
        
        # Seed all modules
        seed_chart_of_accounts(db, organization.id)
        seed_gst_configuration(db, organization.id)
        seed_warehouses(db, organization.id)
        seed_product_tracking(db, organization.id)
        seed_sample_rfq(db, organization.id)
        seed_tally_configuration(db, organization.id)
        
        print("ERP data seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()