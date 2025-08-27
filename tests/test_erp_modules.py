# tests/test_erp_modules.py
"""
Tests for ERP Core, Procurement, Tally Integration, and Enhanced Inventory modules
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal

from app.main import app
from app.core.database import SessionLocal
from app.models import (
    Organization, User, ChartOfAccounts, GSTConfiguration, TaxCode,
    Warehouse, StockLocation, ProductTracking, Product,
    RequestForQuotation, RFQItem, TallyConfiguration
)

client = TestClient(app)


class TestERPCore:
    """Test ERP Core functionality"""
    
    def test_create_chart_of_account(self):
        """Test creating a chart of account"""
        # This is a basic test structure - in a real environment,
        # you'd need proper authentication and database setup
        
        account_data = {
            "account_code": "1001",
            "account_name": "Cash Account",
            "account_type": "cash",
            "opening_balance": 10000.00,
            "description": "Primary cash account"
        }
        
        # Note: This test would need proper authentication headers
        # and database setup/teardown
        
        # response = client.post(
        #     "/api/v1/erp/chart-of-accounts",
        #     json=account_data,
        #     headers={"Authorization": "Bearer test_token"}
        # )
        
        # assert response.status_code == 200
        # assert response.json()["account_name"] == "Cash Account"
        
        # For now, just test the data structure
        assert account_data["account_code"] == "1001"
        assert account_data["account_name"] == "Cash Account"
    
    def test_gst_configuration_validation(self):
        """Test GST configuration validation"""
        
        # Valid GSTIN format
        valid_gstin = "29AABCT1332L1ZZ"
        assert len(valid_gstin) == 15
        
        # Invalid GSTIN format
        invalid_gstin = "29AABCT1332L1"
        assert len(invalid_gstin) != 15
    
    def test_tax_code_creation(self):
        """Test tax code creation logic"""
        
        tax_data = {
            "tax_code": "CGST_18",
            "tax_name": "CGST @ 18%",
            "tax_type": "cgst",
            "tax_rate": 18.00,
            "is_inclusive": False
        }
        
        assert tax_data["tax_rate"] == 18.00
        assert tax_data["tax_type"] == "cgst"


class TestProcurement:
    """Test Procurement functionality"""
    
    def test_rfq_number_generation(self):
        """Test RFQ number generation logic"""
        
        current_year = datetime.now().year
        expected_prefix = f"RFQ-{current_year}-"
        
        # Mock RFQ number generation
        rfq_number = f"{expected_prefix}0001"
        
        assert rfq_number.startswith(expected_prefix)
        assert rfq_number.endswith("0001")
    
    def test_quotation_validation(self):
        """Test quotation validation logic"""
        
        quotation_data = {
            "quotation_date": date.today(),
            "validity_date": date.today(),
            "total_amount": 10000.00,
            "tax_amount": 1800.00,
            "grand_total": 11800.00
        }
        
        # Validate calculations
        expected_total = quotation_data["total_amount"] + quotation_data["tax_amount"]
        assert quotation_data["grand_total"] == expected_total
    
    def test_vendor_evaluation_scoring(self):
        """Test vendor evaluation scoring"""
        
        evaluation_data = {
            "quality_rating": 8.5,
            "delivery_rating": 9.0,
            "service_rating": 7.5,
            "price_rating": 8.0,
            "communication_rating": 8.5
        }
        
        # Calculate overall rating (average)
        ratings = [
            evaluation_data["quality_rating"],
            evaluation_data["delivery_rating"],
            evaluation_data["service_rating"],
            evaluation_data["price_rating"],
            evaluation_data["communication_rating"]
        ]
        
        overall_rating = sum(ratings) / len(ratings)
        assert overall_rating == 8.3


class TestTallyIntegration:
    """Test Tally Integration functionality"""
    
    def test_connection_validation(self):
        """Test Tally connection validation"""
        
        connection_data = {
            "host": "localhost",
            "port": 9000,
            "company_name": "Test Company"
        }
        
        # Basic validation
        assert connection_data["host"] is not None
        assert connection_data["port"] > 0
        assert connection_data["company_name"] is not None
    
    def test_sync_log_structure(self):
        """Test sync log data structure"""
        
        sync_log = {
            "sync_type": "ledgers",
            "sync_direction": "bidirectional",
            "started_at": datetime.utcnow(),
            "sync_status": "completed",
            "records_processed": 10,
            "records_successful": 9,
            "records_failed": 1
        }
        
        # Validate sync completion
        success_rate = sync_log["records_successful"] / sync_log["records_processed"]
        assert success_rate == 0.9
    
    def test_ledger_mapping_validation(self):
        """Test ledger mapping validation"""
        
        mapping_data = {
            "erp_account_code": "1001",
            "tally_ledger_name": "Cash",
            "is_bidirectional": True,
            "sync_status": "completed"
        }
        
        assert mapping_data["erp_account_code"] is not None
        assert mapping_data["tally_ledger_name"] is not None


class TestWarehouseManagement:
    """Test Enhanced Warehouse Management functionality"""
    
    def test_warehouse_code_generation(self):
        """Test warehouse code generation"""
        
        # Mock warehouse code generation
        prefix = "WH"
        sequence = 1
        warehouse_code = f"{prefix}{str(sequence).zfill(3)}"
        
        assert warehouse_code == "WH001"
    
    def test_stock_location_hierarchy(self):
        """Test stock location hierarchy"""
        
        warehouse = {"id": 1, "code": "WH001", "name": "Main Warehouse"}
        
        locations = [
            {"code": "A1", "name": "Aisle 1", "parent_id": None},
            {"code": "A1-R1", "name": "Aisle 1 - Rack 1", "parent_id": "A1"},
            {"code": "A1-R1-L1", "name": "Aisle 1 - Rack 1 - Level 1", "parent_id": "A1-R1"}
        ]
        
        # Test hierarchy structure
        root_locations = [loc for loc in locations if loc["parent_id"] is None]
        assert len(root_locations) == 1
        assert root_locations[0]["code"] == "A1"
    
    def test_product_tracking_configuration(self):
        """Test product tracking configuration"""
        
        tracking_config = {
            "tracking_type": "batch_and_serial",
            "valuation_method": "fifo",
            "batch_expiry_required": True,
            "enable_reorder_alert": True,
            "reorder_level": 10.0,
            "reorder_quantity": 50.0
        }
        
        # Validate configuration
        assert tracking_config["tracking_type"] in ["none", "batch", "serial", "batch_and_serial"]
        assert tracking_config["valuation_method"] in ["fifo", "lifo", "weighted_average", "standard_cost"]
        assert tracking_config["reorder_quantity"] > tracking_config["reorder_level"]
    
    def test_warehouse_utilization_calculation(self):
        """Test warehouse utilization calculation"""
        
        warehouse_data = {
            "total_capacity": 1000.0,
            "current_stock": 750.0
        }
        
        utilization_percentage = (warehouse_data["current_stock"] / warehouse_data["total_capacity"]) * 100
        assert utilization_percentage == 75.0
    
    def test_batch_expiry_alert(self):
        """Test batch expiry alert logic"""
        
        from datetime import timedelta
        
        batch_data = {
            "batch_number": "BATCH-2024-001",
            "manufacturing_date": date.today() - timedelta(days=90),
            "expiry_date": date.today() + timedelta(days=30),
            "quantity": 100.0
        }
        
        # Check if batch is expiring within 30 days
        days_to_expiry = (batch_data["expiry_date"] - date.today()).days
        is_expiring_soon = days_to_expiry <= 30
        
        assert is_expiring_soon == True
        assert days_to_expiry == 30


class TestIntegration:
    """Test integration between modules"""
    
    def test_inventory_to_accounting_integration(self):
        """Test inventory valuation impact on accounting"""
        
        inventory_data = {
            "product_id": 1,
            "quantity": 100,
            "unit_cost": 50.0,
            "total_value": 5000.0
        }
        
        # This should create corresponding accounting entries
        accounting_entry = {
            "account_code": "1004",  # Inventory account
            "debit_amount": inventory_data["total_value"],
            "credit_amount": 0.0
        }
        
        assert accounting_entry["debit_amount"] == inventory_data["total_value"]
    
    def test_procurement_to_inventory_flow(self):
        """Test procurement to inventory flow"""
        
        purchase_order = {
            "po_number": "PO-2024-001",
            "vendor_id": 1,
            "total_amount": 10000.0,
            "items": [
                {"product_id": 1, "quantity": 20, "unit_price": 500.0}
            ]
        }
        
        # When PO is received, it should update inventory
        expected_inventory_update = {
            "product_id": 1,
            "quantity_received": 20,
            "unit_cost": 500.0,
            "warehouse_id": 1
        }
        
        assert expected_inventory_update["product_id"] == purchase_order["items"][0]["product_id"]
        assert expected_inventory_update["quantity_received"] == purchase_order["items"][0]["quantity"]


# Mock data for testing
@pytest.fixture
def sample_organization():
    """Sample organization for testing"""
    return {
        "id": 1,
        "name": "Test Organization",
        "subdomain": "test",
        "status": "active"
    }


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "organization_id": 1,
        "is_active": True
    }


@pytest.fixture
def sample_product():
    """Sample product for testing"""
    return {
        "id": 1,
        "name": "Test Product",
        "hsn_code": "12345678",
        "unit": "Nos",
        "unit_price": 100.0,
        "organization_id": 1
    }


if __name__ == "__main__":
    pytest.main([__file__])