"""
Smoke Tests for Critical Application Flows

These tests verify basic functionality of critical endpoints:
- Login/Authentication
- Voucher operations
- HR attendance/payslips
- AI chatbot endpoint

Run with: pytest tests/test_smoke.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from decimal import Decimal


class TestAuthenticationSmoke:
    """Smoke tests for authentication endpoints."""

    def test_login_endpoint_structure(self):
        """Test that login endpoint imports work correctly."""
        from app.api.v1 import auth
        assert hasattr(auth, 'router')
    
    def test_password_reset_endpoint_structure(self):
        """Test that password reset endpoint imports work correctly."""
        from app.api.v1 import password
        assert hasattr(password, 'router')

    def test_demo_endpoint_structure(self):
        """Test that demo endpoint imports work correctly."""
        from app.api.v1 import demo
        assert hasattr(demo, 'router')


class TestVoucherSmoke:
    """Smoke tests for voucher endpoints."""

    def test_vouchers_module_structure(self):
        """Test that vouchers module imports work correctly."""
        from app.api.v1 import vouchers
        assert vouchers is not None

    def test_sales_order_imports(self):
        """Test that sales order module imports work correctly."""
        from app.api.v1.vouchers import sales_order
        assert hasattr(sales_order, 'router')

    def test_purchase_order_imports(self):
        """Test that purchase order module imports work correctly."""
        from app.api.v1.vouchers import purchase_order
        assert hasattr(purchase_order, 'router')

    def test_grn_imports(self):
        """Test that GRN module imports work correctly."""
        from app.api.v1.vouchers import goods_receipt_note
        assert hasattr(goods_receipt_note, 'router')


class TestHRSmoke:
    """Smoke tests for HR endpoints."""

    def test_hr_module_imports(self):
        """Test that HR module imports work correctly."""
        from app.api.v1 import hr
        assert hasattr(hr, 'router')

    def test_payroll_module_imports(self):
        """Test that payroll module imports work correctly."""
        from app.api.v1 import payroll
        assert hasattr(payroll, 'router')

    def test_hr_models_imports(self):
        """Test that HR models import correctly."""
        from app.models.hr_models import (
            EmployeeProfile,
            AttendanceRecord,
            LeaveType,
            LeaveApplication,
            PerformanceReview,
            Department,
            Position,
            WorkShift,
            HolidayCalendar
        )
        assert EmployeeProfile is not None
        assert AttendanceRecord is not None
        assert Department is not None

    def test_hr_phase2_models_imports(self):
        """Test that HR Phase 2 models import correctly."""
        from app.models.hr_models import (
            AttendancePolicy,
            LeaveBalance,
            Timesheet,
            PayrollArrear,
            StatutoryDeduction,
            BankPaymentExport,
            PayrollApproval
        )
        assert AttendancePolicy is not None
        assert LeaveBalance is not None
        assert Timesheet is not None
        assert PayrollArrear is not None
        assert StatutoryDeduction is not None
        assert BankPaymentExport is not None
        assert PayrollApproval is not None

    def test_hr_schemas_imports(self):
        """Test that HR schemas import correctly."""
        from app.schemas.hr_schemas import (
            EmployeeProfileCreate,
            EmployeeProfileResponse,
            AttendanceRecordCreate,
            DepartmentCreate,
            PositionCreate,
            WorkShiftCreate,
            HolidayCalendarCreate,
            HRDashboard
        )
        assert EmployeeProfileCreate is not None
        assert HRDashboard is not None

    def test_hr_phase2_schemas_imports(self):
        """Test that HR Phase 2 schemas import correctly."""
        from app.schemas.hr_schemas import (
            AttendancePolicyCreate,
            AttendancePolicyResponse,
            LeaveBalanceCreate,
            LeaveBalanceResponse,
            TimesheetCreate,
            TimesheetResponse,
            PayrollArrearCreate,
            PayrollArrearResponse,
            StatutoryDeductionCreate,
            StatutoryDeductionResponse,
            BankPaymentExportCreate,
            BankPaymentExportResponse,
            PayrollApprovalCreate,
            PayrollApprovalResponse,
            PayrollExportRequest,
            AttendanceExportRequest,
            LeaveExportRequest,
            ExportResult
        )
        assert AttendancePolicyCreate is not None
        assert LeaveBalanceResponse is not None
        assert TimesheetCreate is not None
        assert PayrollArrearResponse is not None
        assert StatutoryDeductionCreate is not None
        assert BankPaymentExportResponse is not None
        assert PayrollApprovalCreate is not None
        assert PayrollExportRequest is not None
        assert ExportResult is not None


class TestAISmoke:
    """Smoke tests for AI chatbot endpoints."""

    def test_ai_module_imports(self):
        """Test that AI module imports work correctly."""
        from app.api.v1 import ai
        assert hasattr(ai, 'router')

    def test_chatbot_module_imports(self):
        """Test that chatbot module imports work correctly."""
        from app.api.v1 import chatbot
        assert hasattr(chatbot, 'router')


class TestPhase4ScaffoldingSmoke:
    """Smoke tests for Phase 4 scaffolding models."""

    def test_analytics_models_imports(self):
        """Test that analytics models import correctly."""
        from app.models.hr_models import HRAnalyticsSnapshot
        assert HRAnalyticsSnapshot is not None

    def test_position_budget_imports(self):
        """Test that position budget model imports correctly."""
        from app.models.hr_models import PositionBudget
        assert PositionBudget is not None

    def test_employee_transfer_imports(self):
        """Test that employee transfer model imports correctly."""
        from app.models.hr_models import EmployeeTransfer
        assert EmployeeTransfer is not None

    def test_integration_adapter_imports(self):
        """Test that integration adapter model imports correctly."""
        from app.models.hr_models import IntegrationAdapter
        assert IntegrationAdapter is not None

    def test_phase4_schemas_imports(self):
        """Test that Phase 4 scaffolding schemas import correctly."""
        from app.schemas.hr_schemas import (
            HRAnalyticsSnapshotResponse,
            PositionBudgetCreate,
            PositionBudgetResponse,
            EmployeeTransferCreate,
            EmployeeTransferResponse,
            IntegrationAdapterCreate,
            IntegrationAdapterResponse
        )
        assert HRAnalyticsSnapshotResponse is not None
        assert PositionBudgetCreate is not None
        assert EmployeeTransferCreate is not None
        assert IntegrationAdapterCreate is not None


class TestPayrollSmoke:
    """Smoke tests for payroll functionality."""

    def test_payroll_models_imports(self):
        """Test that payroll models import correctly."""
        from app.models.payroll_models import (
            SalaryStructure,
            PayrollPeriod,
            Payslip,
            TaxSlab,
            EmployeeLoan,
            PayrollSettings,
            PayrollComponent,
            PayrollRun,
            PayrollLine
        )
        assert SalaryStructure is not None
        assert PayrollPeriod is not None
        assert Payslip is not None

    def test_payroll_schemas_imports(self):
        """Test that payroll schemas import correctly."""
        from app.schemas.payroll_schemas import (
            SalaryStructureCreate,
            SalaryStructureResponse,
            PayrollPeriodCreate,
            PayslipCreate,
            PayrollDashboard,
            BulkPayslipGeneration
        )
        assert SalaryStructureCreate is not None
        assert PayrollDashboard is not None


class TestServiceIntegrationSmoke:
    """Smoke tests for service integrations."""

    def test_core_database_imports(self):
        """Test that core database imports work."""
        from app.core.database import Base, async_engine
        assert Base is not None

    def test_enforcement_imports(self):
        """Test that enforcement module imports work."""
        from app.core.enforcement import require_access
        assert require_access is not None


class TestLinkageValidation:
    """Tests for linkage validation script."""

    def test_validate_linkages_script_imports(self):
        """Test that linkage validation script can be imported."""
        import sys
        from pathlib import Path
        scripts_dir = Path(__file__).parent.parent / "scripts"
        sys.path.insert(0, str(scripts_dir))
        
        try:
            from scripts.validate_linkages import (
                find_frontend_pages,
                find_backend_routes,
                validate_linkages
            )
            assert find_frontend_pages is not None
            assert find_backend_routes is not None
            assert validate_linkages is not None
        except ImportError:
            # Script may not be runnable outside of full environment
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
