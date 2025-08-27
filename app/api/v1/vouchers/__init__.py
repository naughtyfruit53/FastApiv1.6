# app/api/v1/vouchers/__init__.py

"""
Vouchers index module - consolidates all voucher-related endpoints
This module provides a single router that includes all voucher functionality.
"""

from fastapi import APIRouter

from .sales_voucher import router as sales_voucher_router
from .sales_order import router as sales_order_router
from .delivery_challan import router as delivery_challan_router
from .sales_return import router as sales_return_router
from .purchase_order import router as purchase_order_router
from .goods_receipt_note import router as goods_receipt_note_router
from .purchase_voucher import router as purchase_voucher_router
from .purchase_return import router as purchase_return_router
from .proforma_invoice import router as proforma_invoice_router
from .quotation import router as quotation_router
from .payment_voucher import router as payment_voucher_router
from .receipt_voucher import router as receipt_voucher_router
from .contra_voucher import router as contra_voucher_router
from .journal_voucher import router as journal_voucher_router
from .inter_department_voucher import router as inter_department_voucher_router
from .credit_note import router as credit_note_router
from .debit_note import router as debit_note_router
# If email is separate
# from .email import router as email_router

# Create main vouchers router
router = APIRouter(tags=["vouchers"])

# Include all voucher sub-routers
router.include_router(sales_voucher_router, prefix="/sales-vouchers")
router.include_router(sales_order_router, prefix="/sales-orders")
router.include_router(delivery_challan_router, prefix="/delivery-challans")
router.include_router(sales_return_router, prefix="/sales-returns")
router.include_router(purchase_order_router, prefix="/purchase-orders")
router.include_router(goods_receipt_note_router, prefix="/goods-receipt-notes")
router.include_router(purchase_voucher_router, prefix="/purchase-vouchers")
router.include_router(purchase_return_router, prefix="/purchase-returns")
router.include_router(proforma_invoice_router, prefix="/proforma-invoices")
router.include_router(quotation_router, prefix="/quotations")
router.include_router(payment_voucher_router, prefix="/payment-vouchers")
router.include_router(receipt_voucher_router, prefix="/receipt-vouchers")
router.include_router(contra_voucher_router, prefix="/contra-vouchers")
router.include_router(journal_voucher_router, prefix="/journal-vouchers")
router.include_router(inter_department_voucher_router, prefix="/inter-department-vouchers")
router.include_router(credit_note_router, prefix="/credit-notes")
router.include_router(debit_note_router, prefix="/debit-notes")
# router.include_router(email_router, prefix="/email")