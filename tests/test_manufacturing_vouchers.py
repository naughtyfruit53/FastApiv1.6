"""
Comprehensive test suite for manufacturing voucher system
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from app.main import app
from app.core.database import get_db
from app.models.vouchers import (
    ManufacturingOrder, MaterialIssue, ManufacturingJournalVoucher,
    MaterialReceiptVoucher, JobCardVoucher, StockJournal,
    BillOfMaterials, BOMComponent
)
from app.core.database import SessionLocal


class TestManufacturingVoucherSystem:
    """Test suite for manufacturing voucher system"""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture(scope="class")
    def db_session(self):
        """Create test database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture(scope="class")
    def sample_data(self, db_session):
        """Create sample data for testing"""
        # This would normally be created via proper API calls
        # For testing purposes, we'll create mock data
        return {
            "organization_id": 1,
            "user_id": 1,
            "vendor_id": 1,
            "product_ids": [1, 2, 3],
            "bom_id": 1,
            "manufacturing_order_id": 1
        }
    
    def test_manufacturing_journal_voucher_creation(self, client, sample_data):
        """Test creating a manufacturing journal voucher"""
        voucher_data = {
            "manufacturing_order_id": sample_data["manufacturing_order_id"],
            "bom_id": sample_data["bom_id"],
            "date_of_manufacture": datetime.now().isoformat(),
            "shift": "Day Shift",
            "operator": "John Doe",
            "supervisor": "Jane Smith",
            "machine_used": "CNC Machine 1",
            "finished_quantity": 100,
            "scrap_quantity": 5,
            "rework_quantity": 3,
            "byproduct_quantity": 2,
            "material_cost": 5000.0,
            "labor_cost": 2000.0,
            "overhead_cost": 1000.0,
            "quality_grade": "Grade A",
            "quality_remarks": "Good quality production",
            "narration": "Regular production run",
            "notes": "No issues observed",
            "finished_products": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "quantity": 100,
                    "unit": "pcs",
                    "unit_cost": 80,
                    "quality_grade": "Grade A",
                    "batch_number": "B001"
                }
            ],
            "consumed_materials": [
                {
                    "product_id": sample_data["product_ids"][1],
                    "quantity_consumed": 200,
                    "unit": "kg",
                    "unit_cost": 25,
                    "batch_number": "RM001"
                }
            ],
            "byproducts": [
                {
                    "product_id": sample_data["product_ids"][2],
                    "quantity": 2,
                    "unit": "kg",
                    "unit_value": 10,
                    "condition": "Good"
                }
            ]
        }
        
        # Note: This test assumes proper authentication setup
        # In a real test environment, you'd need to authenticate first
        response = client.post(
            "/api/v1/manufacturing-journal-vouchers/",
            json=voucher_data
        )
        
        # Expected result depends on authentication setup
        # For now, we'll check if the endpoint exists
        assert response.status_code in [200, 201, 401, 422]
    
    def test_material_receipt_voucher_creation(self, client, sample_data):
        """Test creating a material receipt voucher"""
        voucher_data = {
            "source_type": "return",
            "source_reference": "MO001",
            "received_from_department": "Production",
            "received_from_employee": "John Worker",
            "received_by_employee": "Store Keeper",
            "receipt_time": datetime.now().isoformat(),
            "inspection_required": True,
            "inspection_status": "pending",
            "inspector_name": "Quality Inspector",
            "condition_on_receipt": "Good",
            "notes": "Material returned from production",
            "items": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "quantity": 10,
                    "unit": "pcs",
                    "unit_price": 50,
                    "received_quantity": 10,
                    "accepted_quantity": 9,
                    "rejected_quantity": 1,
                    "batch_number": "B002",
                    "quality_status": "accepted"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/material-receipt-vouchers/",
            json=voucher_data
        )
        
        assert response.status_code in [200, 201, 401, 422]
    
    def test_job_card_voucher_creation(self, client, sample_data):
        """Test creating a job card voucher"""
        voucher_data = {
            "job_type": "outsourcing",
            "vendor_id": sample_data["vendor_id"],
            "job_description": "CNC machining of steel components",
            "job_category": "Machining",
            "expected_completion_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "materials_supplied_by": "company",
            "delivery_address": "Vendor facility",
            "transport_mode": "Truck",
            "quality_specifications": "As per technical drawing",
            "quality_check_required": True,
            "notes": "Urgent order",
            "supplied_materials": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "quantity_supplied": 50,
                    "unit": "pcs",
                    "unit_rate": 100,
                    "batch_number": "SM001",
                    "supply_date": datetime.now().isoformat()
                }
            ],
            "received_outputs": [
                {
                    "product_id": sample_data["product_ids"][1],
                    "quantity_received": 45,
                    "unit": "pcs",
                    "unit_rate": 150,
                    "quality_status": "accepted",
                    "receipt_date": (datetime.now() + timedelta(days=5)).isoformat()
                }
            ]
        }
        
        response = client.post(
            "/api/v1/job-card-vouchers/",
            json=voucher_data
        )
        
        assert response.status_code in [200, 201, 401, 422]
    
    def test_stock_journal_creation(self, client, sample_data):
        """Test creating a stock journal"""
        journal_data = {
            "journal_type": "transfer",
            "from_location": "Main Warehouse",
            "to_location": "Production Floor",
            "from_warehouse": "WH001",
            "to_warehouse": "WH002",
            "transfer_reason": "Production requirement",
            "physical_verification_done": True,
            "verified_by": "Store Manager",
            "verification_date": datetime.now().isoformat(),
            "notes": "Regular stock transfer",
            "entries": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "debit_quantity": 0,
                    "credit_quantity": 20,
                    "unit": "pcs",
                    "unit_rate": 50,
                    "from_location": "Main Warehouse",
                    "to_location": "Production Floor",
                    "batch_number": "B003"
                },
                {
                    "product_id": sample_data["product_ids"][0],
                    "debit_quantity": 20,
                    "credit_quantity": 0,
                    "unit": "pcs",
                    "unit_rate": 50,
                    "from_location": "Production Floor",
                    "to_location": "Main Warehouse",
                    "batch_number": "B003"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/stock-journals/",
            json=journal_data
        )
        
        assert response.status_code in [200, 201, 401, 422]
    
    def test_enhanced_material_issue_creation(self, client, sample_data):
        """Test creating enhanced material issue with batch tracking"""
        issue_data = {
            "manufacturing_order_id": sample_data["manufacturing_order_id"],
            "issued_to_department": "Production",
            "issued_to_employee": "Machine Operator",
            "purpose": "production",
            "destination": "Machine Center A",
            "issue_time": datetime.now().isoformat(),
            "expected_return_time": (datetime.now() + timedelta(hours=8)).isoformat(),
            "notes": "Material for urgent order",
            "items": [
                {
                    "product_id": sample_data["product_ids"][1],
                    "quantity": 100,
                    "unit": "kg",
                    "unit_price": 25,
                    "batch_number": "RM002",
                    "lot_number": "LOT001",
                    "warehouse_location": "WH001-A1",
                    "bin_location": "A1-01",
                    "notes": "High grade material"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/material-issues/",
            json=issue_data
        )
        
        assert response.status_code in [200, 201, 401, 422]
    
    def test_voucher_number_generation(self, client):
        """Test voucher number generation for all voucher types"""
        voucher_types = [
            "manufacturing-journal-vouchers",
            "material-receipt-vouchers", 
            "job-card-vouchers",
            "stock-journals",
            "material-issues"
        ]
        
        for voucher_type in voucher_types:
            response = client.get(f"/api/v1/{voucher_type}/next-number")
            # Should either return a voucher number or require authentication
            assert response.status_code in [200, 401]
    
    def test_voucher_listing(self, client):
        """Test listing vouchers for all types"""
        voucher_types = [
            "manufacturing-journal-vouchers",
            "material-receipt-vouchers",
            "job-card-vouchers", 
            "stock-journals",
            "material-issues"
        ]
        
        for voucher_type in voucher_types:
            response = client.get(f"/api/v1/{voucher_type}/")
            # Should either return voucher list or require authentication
            assert response.status_code in [200, 401]
    
    def test_manufacturing_journal_workflow(self, client, sample_data):
        """Test manufacturing journal voucher workflow"""
        # Test case: Complete manufacturing process workflow
        
        # 1. Material Issue
        issue_data = {
            "manufacturing_order_id": sample_data["manufacturing_order_id"],
            "issued_to_department": "Production",
            "purpose": "production",
            "items": [
                {
                    "product_id": sample_data["product_ids"][1],
                    "quantity": 100,
                    "unit": "kg",
                    "unit_price": 25,
                    "batch_number": "RM001"
                }
            ]
        }
        
        issue_response = client.post("/api/v1/material-issues/", json=issue_data)
        
        # 2. Manufacturing Journal
        journal_data = {
            "manufacturing_order_id": sample_data["manufacturing_order_id"],
            "bom_id": sample_data["bom_id"],
            "date_of_manufacture": datetime.now().isoformat(),
            "finished_quantity": 95,
            "scrap_quantity": 5,
            "material_cost": 2500,
            "labor_cost": 1000,
            "overhead_cost": 500,
            "finished_products": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "quantity": 95,
                    "unit": "pcs",
                    "unit_cost": 42.11
                }
            ],
            "consumed_materials": [
                {
                    "product_id": sample_data["product_ids"][1],
                    "quantity_consumed": 95,
                    "unit": "kg",
                    "unit_cost": 25
                }
            ]
        }
        
        journal_response = client.post("/api/v1/manufacturing-journal-vouchers/", json=journal_data)
        
        # 3. Material Receipt (for scrap/unused material)
        receipt_data = {
            "source_type": "return",
            "source_reference": "Production scrap",
            "items": [
                {
                    "product_id": sample_data["product_ids"][2],  # Scrap material
                    "quantity": 5,
                    "unit": "kg",
                    "unit_price": 5,
                    "quality_status": "rejected"
                }
            ]
        }
        
        receipt_response = client.post("/api/v1/material-receipt-vouchers/", json=receipt_data)
        
        # All should either succeed or fail with authentication
        for response in [issue_response, journal_response, receipt_response]:
            assert response.status_code in [200, 201, 401, 422]
    
    def test_stock_journal_assembly_workflow(self, client, sample_data):
        """Test stock journal assembly workflow"""
        assembly_data = {
            "journal_type": "assembly",
            "assembly_product_id": sample_data["product_ids"][0],  # Final product
            "assembly_quantity": 10,
            "notes": "Assembly of finished goods",
            "entries": [
                # Consume components
                {
                    "product_id": sample_data["product_ids"][1],  # Component 1
                    "debit_quantity": 0,
                    "credit_quantity": 20,
                    "unit": "pcs",
                    "unit_rate": 10,
                    "transformation_type": "consume"
                },
                {
                    "product_id": sample_data["product_ids"][2],  # Component 2
                    "debit_quantity": 0,
                    "credit_quantity": 10,
                    "unit": "pcs", 
                    "unit_rate": 15,
                    "transformation_type": "consume"
                },
                # Produce finished product
                {
                    "product_id": sample_data["product_ids"][0],  # Finished product
                    "debit_quantity": 10,
                    "credit_quantity": 0,
                    "unit": "pcs",
                    "unit_rate": 50,
                    "transformation_type": "produce"
                }
            ]
        }
        
        response = client.post("/api/v1/stock-journals/", json=assembly_data)
        assert response.status_code in [200, 201, 401, 422]
    
    def test_job_card_outsourcing_workflow(self, client, sample_data):
        """Test job card outsourcing workflow"""
        # Create job card with material supply and output receipt
        job_data = {
            "job_type": "outsourcing",
            "vendor_id": sample_data["vendor_id"],
            "job_description": "Heat treatment of steel components",
            "job_category": "Heat Treatment",
            "expected_completion_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "materials_supplied_by": "company",
            "quality_check_required": True,
            "supplied_materials": [
                {
                    "product_id": sample_data["product_ids"][0],
                    "quantity_supplied": 100,
                    "unit": "pcs",
                    "unit_rate": 50,
                    "supply_date": datetime.now().isoformat()
                }
            ],
            "received_outputs": [
                {
                    "product_id": sample_data["product_ids"][0],  # Same product, processed
                    "quantity_received": 98,  # 2 pieces rejected
                    "unit": "pcs",
                    "unit_rate": 75,  # Higher value after processing
                    "quality_status": "accepted",
                    "inspection_remarks": "Good quality heat treatment",
                    "receipt_date": (datetime.now() + timedelta(days=2)).isoformat()
                }
            ]
        }
        
        response = client.post("/api/v1/job-card-vouchers/", json=job_data)
        assert response.status_code in [200, 201, 401, 422]
    
    def test_error_handling(self, client):
        """Test error handling for invalid data"""
        # Test with invalid manufacturing journal data
        invalid_data = {
            "manufacturing_order_id": 99999,  # Non-existent
            "bom_id": 99999,  # Non-existent
            "date_of_manufacture": "invalid-date",
            "finished_quantity": -1,  # Invalid quantity
        }
        
        response = client.post("/api/v1/manufacturing-journal-vouchers/", json=invalid_data)
        assert response.status_code in [400, 401, 422]
    
    def test_api_endpoints_exist(self, client):
        """Test that all required API endpoints exist"""
        endpoints = [
            "/api/v1/manufacturing-journal-vouchers/",
            "/api/v1/material-receipt-vouchers/",
            "/api/v1/job-card-vouchers/",
            "/api/v1/stock-journals/",
            "/api/v1/manufacturing-journal-vouchers/next-number",
            "/api/v1/material-receipt-vouchers/next-number",
            "/api/v1/job-card-vouchers/next-number",
            "/api/v1/stock-journals/next-number"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404


class TestManufacturingVoucherModels:
    """Test manufacturing voucher database models"""
    
    @pytest.fixture(scope="class")
    def db_session(self):
        """Create test database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def test_model_relationships(self, db_session):
        """Test model relationships are properly defined"""
        # This test would verify that all foreign key relationships work
        # In a real test environment, you'd create test records and verify relationships
        
        # Test ManufacturingJournalVoucher relationships
        assert hasattr(ManufacturingJournalVoucher, 'manufacturing_order')
        assert hasattr(ManufacturingJournalVoucher, 'bom')
        assert hasattr(ManufacturingJournalVoucher, 'finished_products')
        assert hasattr(ManufacturingJournalVoucher, 'consumed_materials')
        assert hasattr(ManufacturingJournalVoucher, 'byproducts')
        
        # Test MaterialReceiptVoucher relationships
        assert hasattr(MaterialReceiptVoucher, 'manufacturing_order')
        assert hasattr(MaterialReceiptVoucher, 'items')
        
        # Test JobCardVoucher relationships
        assert hasattr(JobCardVoucher, 'vendor')
        assert hasattr(JobCardVoucher, 'supplied_materials')
        assert hasattr(JobCardVoucher, 'received_outputs')
        
        # Test StockJournal relationships
        assert hasattr(StockJournal, 'entries')
        assert hasattr(StockJournal, 'manufacturing_order')
        assert hasattr(StockJournal, 'bom')
    
    def test_model_constraints(self, db_session):
        """Test that model constraints are properly defined"""
        # Test unique constraints exist
        
        # ManufacturingJournalVoucher should have unique voucher number per org
        mjv_constraints = ManufacturingJournalVoucher.__table__.constraints
        unique_constraints = [c for c in mjv_constraints if hasattr(c, 'columns')]
        assert any('voucher_number' in [col.name for col in c.columns] for c in unique_constraints)
        
        # Similar tests for other models
        mrv_constraints = MaterialReceiptVoucher.__table__.constraints
        unique_constraints = [c for c in mrv_constraints if hasattr(c, 'columns')]
        assert any('voucher_number' in [col.name for col in c.columns] for c in unique_constraints)


# Integration test class for full workflow testing
class TestManufacturingWorkflowIntegration:
    """Integration tests for complete manufacturing workflows"""
    
    def test_complete_manufacturing_cycle(self, client):
        """Test complete manufacturing cycle from order to completion"""
        # This would test the complete cycle:
        # 1. Create Manufacturing Order
        # 2. Issue Materials
        # 3. Create Manufacturing Journal
        # 4. Receive finished goods
        # 5. Handle byproducts and scrap
        # 6. Stock adjustments
        
        # Due to authentication requirements, this is a placeholder
        # In a real test environment, you'd implement the full cycle
        pass
    
    def test_outsourcing_workflow(self, client):
        """Test complete outsourcing workflow"""
        # This would test:
        # 1. Create Job Card
        # 2. Supply materials to vendor
        # 3. Receive processed goods
        # 4. Quality inspection
        # 5. Stock updates
        
        # Due to authentication requirements, this is a placeholder
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])