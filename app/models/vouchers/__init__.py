# app/models/vouchers/__init__.py

# Convenience imports for easier access to models
# Example: from app.models.vouchers import BaseVoucher, PurchaseOrder

from .base import (
    BaseVoucher,
    VoucherItemBase,
    SimpleVoucherItemBase
)

from .financial import (
    CreditNote,
    CreditNoteItem,
    DebitNote,
    DebitNoteItem,
    PaymentVoucher,
    ReceiptVoucher,
    ContraVoucher,
    JournalVoucher,
    InterDepartmentVoucher,
    InterDepartmentVoucherItem
)

from .purchase import (
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceiptNote,
    GoodsReceiptNoteItem,
    PurchaseVoucher,
    PurchaseVoucherItem,
    PurchaseReturn,
    PurchaseReturnItem
)

from .presales import (
    Quotation,
    QuotationItem,
    ProformaInvoice,
    ProformaInvoiceItem,
    SalesOrder,
    SalesOrderItem
)

from .sales import (
    DeliveryChallan,
    DeliveryChallanItem,
    SalesVoucher,
    SalesVoucherItem,
    SalesReturn,
    SalesReturnItem
)

from .manufacturing_planning import (
    BillOfMaterials,
    BOMComponent,
    ManufacturingOrder,
    Machine,
    PreventiveMaintenanceSchedule,
    BreakdownMaintenance,
    MachinePerformanceLog,
    SparePart,
    QCTemplate,
    QCInspection,
    Rejection,
    InventoryAdjustment
)

from .manufacturing_operations import (
    MaterialIssue,
    MaterialIssueItem,
    ManufacturingJournalVoucher,
    ManufacturingJournalFinishedProduct,
    ManufacturingJournalMaterial,
    ManufacturingJournalByproduct,
    MaterialReceiptVoucher,
    MaterialReceiptItem,
    JobCardVoucher,
    JobCardSuppliedMaterial,
    JobCardReceivedOutput,
    StockJournal,
    StockJournalEntry,
    ProductionEntry,
    FinishedGoodReceipt,
    FinishedGoodReceiptItem,
    FGReceiptCostDetail,
    FGReceiptAudit
)