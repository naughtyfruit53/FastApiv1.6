# app/services/voucher_service.py

"""
Voucher service for auto-population and business logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, delete
from typing import Type, Union, Any, Optional
from datetime import datetime
from decimal import Decimal
import logging
from app.models.organization_settings import OrganizationSettings, VoucherCounterResetPeriod

logger = logging.getLogger(__name__)

class VoucherNumberService:
    """Service for generating voucher numbers with org-level settings support"""
    
    @staticmethod
    async def generate_voucher_number(
        db: AsyncSession, 
        prefix: str, 
        organization_id: int, 
        model: Type[Any]
    ) -> str:
        """
        Generate a unique voucher number for the organization
        Supports:
        - Org-level prefix (Requirement 5)
        - Counter reset periods: monthly, quarterly, annually (Requirement 6)
        
        Format examples:
        - With prefix: PM-PO/2526/00001
        - Quarterly: PO/2526/Q1/00001
        - Monthly: PO/2526/APR/00001
        """
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Get organization settings
        stmt = select(OrganizationSettings).where(
            OrganizationSettings.organization_id == organization_id
        )
        result = await db.execute(stmt)
        org_settings = result.scalar_one_or_none()
        
        # Build prefix with org-level prefix if enabled
        full_prefix = prefix
        if org_settings and org_settings.voucher_prefix_enabled and org_settings.voucher_prefix:
            full_prefix = f"{org_settings.voucher_prefix}-{prefix}"
        
        # Calculate fiscal year (assuming April start)
        fiscal_year = f"{str(current_year)[-2:]}{str(current_year + 1 if current_month > 3 else current_year)[-2:]}"
        
        # Determine counter reset period and format accordingly
        reset_period = org_settings.voucher_counter_reset_period if org_settings else VoucherCounterResetPeriod.ANNUALLY
        
        period_segment = ""
        if reset_period == VoucherCounterResetPeriod.MONTHLY:
            # Format: PO/2526/JAN/00001
            month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                          'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            period_segment = month_names[current_month - 1]
        elif reset_period == VoucherCounterResetPeriod.QUARTERLY:
            # Format: PO/2526/Q1/00001
            quarter = ((current_month - 1) // 3) + 1
            period_segment = f"Q{quarter}"
        elif reset_period == VoucherCounterResetPeriod.ANNUALLY:
            # Format: PO/2526/00001 (no period segment)
            period_segment = ""
        # For NEVER, we'll use annually as default
        
        # Build pattern for search
        if period_segment:
            search_pattern = f"{full_prefix}/{fiscal_year}/{period_segment}/%"
            base_number = f"{full_prefix}/{fiscal_year}/{period_segment}"
        else:
            search_pattern = f"{full_prefix}/{fiscal_year}/%"
            base_number = f"{full_prefix}/{fiscal_year}"
        
        # Get the latest voucher number for this prefix, fiscal year, period and organization
        stmt = select(model).where(
            model.organization_id == organization_id,
            model.voucher_number.like(search_pattern)
        ).order_by(desc(model.voucher_number)).limit(1)
        result = await db.execute(stmt)
        latest_voucher = result.scalar_one_or_none()
        
        if latest_voucher:
            # Extract sequence number from the last voucher (handle revisions by ignoring Rev suffix)
            voucher_num = latest_voucher.voucher_number.split(' Rev ')[0]  # Strip revision if present
            try:
                last_sequence = int(voucher_num.split('/')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        
        # Generate new voucher number
        voucher_number = f"{base_number}/{next_sequence:05d}"
        
        # Ensure uniqueness (in case of race conditions)
        while True:
            stmt = select(model).where(model.voucher_number == voucher_number)
            result = await db.execute(stmt)
            if not result.scalar_one_or_none():
                break
            next_sequence += 1
            voucher_number = f"{base_number}/{next_sequence:05d}"
        
        return voucher_number

class VoucherValidationService:
    """Service for voucher validation logic"""
    
    @staticmethod
    def validate_purchase_order_quantities(po_items: list) -> bool:
        """Validate purchase order item quantities"""
        for item in po_items:
            if item.quantity <= 0:
                raise ValueError(f"Quantity must be positive for product {item.product_id}")
            if item.unit_price < 0:
                raise ValueError(f"Unit price cannot be negative for product {item.product_id}")
        return True
    
    @staticmethod
    def validate_grn_against_po(grn_items: list, po_items: list) -> bool:
        """Validate GRN items against Purchase Order"""
        po_items_dict = {item.id: item for item in po_items}
        
        for grn_item in grn_items:
            po_item = po_items_dict.get(grn_item.po_item_id)
            if not po_item:
                raise ValueError(f"PO item {grn_item.po_item_id} not found")
            
            if grn_item.received_quantity > po_item.pending_quantity:
                raise ValueError(
                    f"Received quantity ({grn_item.received_quantity}) exceeds "
                    f"pending quantity ({po_item.pending_quantity}) for product {po_item.product_id}"
                )
            
            if grn_item.accepted_quantity > grn_item.received_quantity:
                raise ValueError(
                    f"Accepted quantity cannot exceed received quantity for product {po_item.product_id}"
                )
        
        return True
    
    @staticmethod
    def validate_voucher_against_grn(voucher_items: list, grn_items: list) -> bool:
        """Validate Purchase Voucher items against GRN"""
        grn_items_dict = {item.id: item for item in grn_items}
        
        for voucher_item in voucher_items:
            grn_item = grn_items_dict.get(voucher_item.grn_item_id)
            if not grn_item:
                raise ValueError(f"GRN item {voucher_item.grn_item_id} not found")
            
            if voucher_item.quantity > grn_item.accepted_quantity:
                raise ValueError(
                    f"Voucher quantity ({voucher_item.quantity}) exceeds "
                    f"accepted quantity ({grn_item.accepted_quantity}) for product {grn_item.product_id}"
                )
        
        return True

class VoucherAutoPopulationService:
    """Service for auto-populating voucher data"""
    
    @staticmethod
    async def populate_grn_from_po(db: AsyncSession, purchase_order, current_user) -> dict:
        """Auto-populate GRN data from Purchase Order"""
        from app.models.vouchers.purchase import GoodsReceiptNote
        
        # Get pending PO items
        stmt = select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == purchase_order.id, PurchaseOrderItem.pending_quantity > 0)
        result = await db.execute(stmt)
        po_items = result.scalars().all()
        
        if not po_items:
            raise ValueError("No pending items in Purchase Order")
        
        # Generate GRN voucher number
        grn_voucher_number = await VoucherNumberService.generate_voucher_number(
            db, "GRN", purchase_order.organization_id, GoodsReceiptNote
        )
        
        # Prepare GRN data
        grn_data = {
            "voucher_number": grn_voucher_number,
            "purchase_order_id": purchase_order.id,
            "vendor_id": purchase_order.vendor_id,
            "grn_date": datetime.now(),
            "date": datetime.now(),
            "organization_id": purchase_order.organization_id,
            "created_by": current_user.id,
            "items": []
        }
        
        for po_item in po_items:
            grn_item = {
                "product_id": po_item.product_id,
                "po_item_id": po_item.id,
                "ordered_quantity": po_item.quantity,
                "received_quantity": po_item.pending_quantity,
                "accepted_quantity": po_item.pending_quantity,
                "rejected_quantity": 0,
                "unit": po_item.unit,
                "unit_price": po_item.unit_price,
                "total_cost": po_item.pending_quantity * po_item.unit_price
            }
            grn_data["items"].append(grn_item)
        
        return grn_data
    
    @staticmethod
    async def populate_purchase_voucher_from_grn(db: AsyncSession, grn, current_user, gst_rate: float = 18.0) -> dict:
        """Auto-populate Purchase Voucher data from GRN"""
        from app.models.vouchers.purchase import PurchaseVoucher
        
        # Get accepted GRN items
        stmt = select(GoodsReceiptNoteItem).where(GoodsReceiptNoteItem.grn_id == grn.id, GoodsReceiptNoteItem.accepted_quantity > 0)
        result = await db.execute(stmt)
        grn_items = result.scalars().all()
        
        if not grn_items:
            raise ValueError("No accepted items in GRN")
        
        # Generate voucher number
        pv_voucher_number = await VoucherNumberService.generate_voucher_number(
            db, "PV", grn.organization_id, PurchaseVoucher
        )
        
        # Prepare voucher data
        pv_data = {
            "voucher_number": pv_voucher_number,
            "vendor_id": grn.vendor_id,
            "purchase_order_id": grn.purchase_order_id,
            "grn_id": grn.id,
            "date": datetime.now(),
            "organization_id": grn.organization_id,
            "created_by": current_user.id,
            "items": []
        }
        
        total_amount = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        
        for grn_item in grn_items:
            # Calculate tax amounts
            taxable_amount = grn_item.accepted_quantity * grn_item.unit_price
            gst_amount = taxable_amount * (gst_rate / 100)
            
            # For intra-state: CGST + SGST, for inter-state: IGST
            # For simplicity, using CGST + SGST
            cgst_amount = gst_amount / 2
            sgst_amount = gst_amount / 2
            igst_amount = 0.0
            
            item_total = taxable_amount + gst_amount
            
            pv_item = {
                "product_id": grn_item.product_id,
                "grn_item_id": grn_item.id,
                "quantity": grn_item.accepted_quantity,
                "unit": grn_item.unit,
                "unit_price": grn_item.unit_price,
                "taxable_amount": taxable_amount,
                "gst_rate": gst_rate,
                "cgst_amount": cgst_amount,
                "sgst_amount": sgst_amount,
                "igst_amount": igst_amount,
                "total_amount": item_total
            }
            pv_data["items"].append(pv_item)
            
            total_amount += item_total
            total_cgst += cgst_amount
            total_sgst += sgst_amount
            total_igst += igst_amount
        
        pv_data.update({
            "total_amount": total_amount,
            "cgst_amount": total_cgst,
            "sgst_amount": total_sgst,
            "igst_amount": total_igst
        })
        
        return pv_data

class VoucherSearchService:
    """Service for voucher search and filtering"""
    
    @staticmethod
    async def search_vendors_for_dropdown(db: AsyncSession, search_term: str, organization_id: int, limit: int = 10):
        """Search vendors for dropdown with organization filtering"""
        from app.models.base import Vendor
        from app.core.tenant import TenantQueryFilter
        
        stmt = TenantQueryFilter.apply_organization_filter(
            select(Vendor), Vendor, organization_id
        ).where(
            Vendor.is_active == True,
            Vendor.name.contains(search_term)
        ).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def search_products_for_dropdown(db: AsyncSession, search_term: str, organization_id: int, limit: int = 10):
        """Search products for dropdown with organization filtering"""
        from app.models.base import Product
        from app.core.tenant import TenantQueryFilter
        
        stmt = TenantQueryFilter.apply_organization_filter(
            select(Product), Product, organization_id
        ).where(
            Product.is_active == True,
            Product.name.contains(search_term)
        ).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_pending_purchase_orders(db: AsyncSession, organization_id: int, vendor_id: int = None):
        """Get purchase orders with pending items"""
        from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem
        from app.core.tenant import TenantQueryFilter
        
        stmt = TenantQueryFilter.apply_organization_filter(
            select(PurchaseOrder), PurchaseOrder, organization_id
        ).join(PurchaseOrderItem).where(
            PurchaseOrder.status == "confirmed",
            PurchaseOrderItem.pending_quantity > 0
        )
        
        if vendor_id:
            stmt = stmt.where(PurchaseOrder.vendor_id == vendor_id)
        
        stmt = stmt.distinct()
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_pending_grns_for_invoicing(db: AsyncSession, organization_id: int, vendor_id: int = None):
        """Get GRNs that haven't been fully invoiced"""
        from app.models.vouchers.purchase import GoodsReceiptNote, GoodsReceiptNoteItem
        from app.core.tenant import TenantQueryFilter
        
        stmt = TenantQueryFilter.apply_organization_filter(
            select(GoodsReceiptNote), GoodsReceiptNote, organization_id
        ).join(GoodsReceiptNoteItem).where(
            GoodsReceiptNote.status == "confirmed",
            GoodsReceiptNoteItem.accepted_quantity > 0
        )
        
        if vendor_id:
            stmt = stmt.where(GoodsReceiptNote.vendor_id == vendor_id)
        
        stmt = stmt.distinct()
        result = await db.execute(stmt)
        return result.scalars().all()