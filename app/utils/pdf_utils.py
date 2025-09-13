# app/utils/pdf_utils.py

"""
Unified PDF generation utility for all voucher types
"""

from typing import Dict

class VoucherPdfConfig:
    def __init__(self, voucher_type: str, voucher_title: str, show_items: bool = False, show_tax_details: bool = False, entity_type: str = None):
        self.voucher_type = voucher_type
        self.voucher_title = voucher_title
        self.show_items = show_items
        self.show_tax_details = show_tax_details
        self.entity_type = entity_type

VOUCHER_PDF_CONFIGS: Dict[str, VoucherPdfConfig] = {
    # Financial Vouchers
    "payment-voucher": VoucherPdfConfig(
        voucher_type="payment-vouchers",
        voucher_title="PAYMENT VOUCHER",
        show_items=False,
        show_tax_details=False,
        entity_type="vendor",
    ),
    "receipt-voucher": VoucherPdfConfig(
        voucher_type="receipt-vouchers",
        voucher_title="RECEIPT VOUCHER",
        show_items=False,
        show_tax_details=False,
        entity_type="customer",
    ),
    "journal-voucher": VoucherPdfConfig(
        voucher_type="journal-vouchers",
        voucher_title="JOURNAL VOUCHER",
        show_items=False,
        show_tax_details=False,
    ),
    "contra-voucher": VoucherPdfConfig(
        voucher_type="contra-vouchers",
        voucher_title="CONTRA VOUCHER",
        show_items=False,
        show_tax_details=False,
    ),
    # Purchase Vouchers
    "purchase-voucher": VoucherPdfConfig(
        voucher_type="purchase-vouchers",
        voucher_title="PURCHASE VOUCHER / BILL",
        show_items=True,
        show_tax_details=True,
        entity_type="vendor",
    ),
    "purchase-order": VoucherPdfConfig(
        voucher_type="purchase-orders",
        voucher_title="PURCHASE ORDER",
        show_items=True,
        show_tax_details=True,
        entity_type="vendor",
    ),
    "grn": VoucherPdfConfig(
        voucher_type="grns",
        voucher_title="GOODS RECEIPT NOTE",
        show_items=True,
        show_tax_details=False,
        entity_type="vendor",
    ),
    "purchase-return": VoucherPdfConfig(
        voucher_type="purchase-returns",
        voucher_title="PURCHASE RETURN",
        show_items=True,
        show_tax_details=True,
        entity_type="vendor",
    ),
    # Sales Vouchers
    "sales-voucher": VoucherPdfConfig(
        voucher_type="sales-vouchers",
        voucher_title="SALES INVOICE",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "quotation": VoucherPdfConfig(
        voucher_type="quotations",
        voucher_title="QUOTATION",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "proforma-invoice": VoucherPdfConfig(
        voucher_type="proforma-invoices",
        voucher_title="PROFORMA INVOICE",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "sales-order": VoucherPdfConfig(
        voucher_type="sales-orders",
        voucher_title="SALES ORDER",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "delivery-challan": VoucherPdfConfig(
        voucher_type="delivery-challans",
        voucher_title="DELIVERY CHALLAN",
        show_items=True,
        show_tax_details=False,
        entity_type="customer",
    ),
    "sales-return": VoucherPdfConfig(
        voucher_type="sales-returns",
        voucher_title="SALES RETURN",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "credit-note": VoucherPdfConfig(
        voucher_type="credit-notes",
        voucher_title="CREDIT NOTE",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    "debit-note": VoucherPdfConfig(
        voucher_type="debit-notes",
        voucher_title="DEBIT NOTE",
        show_items=True,
        show_tax_details=True,
        entity_type="vendor",
    ),
    "non-sales-credit-note": VoucherPdfConfig(
        voucher_type="non-sales-credit-notes",
        voucher_title="NON-SALES CREDIT NOTE",
        show_items=True,
        show_tax_details=True,
        entity_type="customer",
    ),
    # Manufacturing Vouchers
    "job-card": VoucherPdfConfig(
        voucher_type="job-cards",
        voucher_title="JOB CARD",
        show_items=True,
        show_tax_details=True,
        entity_type="vendor",
    ),
    "production-order": VoucherPdfConfig(
        voucher_type="production-orders",
        voucher_title="PRODUCTION ORDER",
        show_items=True,
        show_tax_details=False,
    ),
    "work-order": VoucherPdfConfig(
        voucher_type="work-orders",
        voucher_title="WORK ORDER",
        show_items=True,
        show_tax_details=False,
    ),
    "material-receipt": VoucherPdfConfig(
        voucher_type="material-receipts",
        voucher_title="MATERIAL RECEIPT",
        show_items=True,
        show_tax_details=False,
    ),
    "material-requisition": VoucherPdfConfig(
        voucher_type="material-requisitions",
        voucher_title="MATERIAL REQUISITION",
        show_items=True,
        show_tax_details=False,
    ),
    "finished-good-receipt": VoucherPdfConfig(
        voucher_type="finished-good-receipts",
        voucher_title="FINISHED GOODS RECEIPT",
        show_items=True,
        show_tax_details=False,
    ),
    "manufacturing-journal": VoucherPdfConfig(
        voucher_type="manufacturing-journals",
        voucher_title="MANUFACTURING JOURNAL",
        show_items=False,
        show_tax_details=False,
    ),
    "stock-journal": VoucherPdfConfig(
        voucher_type="stock-journals",
        voucher_title="STOCK JOURNAL",
        show_items=True,
        show_tax_details=False,
    ),
}

def get_voucher_pdf_config(voucher_type: str) -> VoucherPdfConfig:
    config = VOUCHER_PDF_CONFIGS.get(voucher_type)
    if not config:
        logger.warning(f"No PDF configuration found for voucher type: {voucher_type}")
        return VoucherPdfConfig(
            voucher_type=voucher_type,
            voucher_title=voucher_type.upper().replace("-", " "),
            show_items=False,
            show_tax_details=False,
        )
    return config

def generate_standalone_pdf(voucher_id: int, voucher_type: str) -> None:
    logger.info(f"[PDF] Generating standalone PDF for: {voucher_type} {voucher_id}")
    # Check authorization
    token = "dummy_token"  # Replace with actual token retrieval
    if not token:
        raise ValueError("You must be logged in to generate PDFs")
    # Get PDF configuration
    pdf_config = get_voucher_pdf_config(voucher_type)
    # Generate PDF via backend
    generate_voucher_pdf(voucher_id, pdf_config)  # Assuming this function exists