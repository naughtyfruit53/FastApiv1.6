# app/services/org_reset_service.py

"""
Organization-level reset service for business data reset operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from typing import Dict, Any
from app.models.system_models import Company, EmailNotification, PaymentTerm, NotificationTemplate, NotificationLog, NotificationPreference, OTPVerification
from app.models.customer_models import Customer, Vendor, CustomerFile, VendorFile, CustomerInteraction, CustomerSegment
from app.models.product_models import Product, Stock, ProductFile, InventoryTransaction, JobParts, InventoryAlert
from app.models.user_models import Organization
from app.models.analytics_models import ServiceAnalyticsEvent, ReportConfiguration, AnalyticsSummary
from app.models.service_models import (
    Ticket, TicketHistory, TicketAttachment, SLAPolicy, SLATracking,
    DispatchOrder, DispatchItem,
    InstallationJob, InstallationTask, CompletionRecord, CustomerFeedback, ServiceClosure
)
from app.models.vouchers.financial import (
    CreditNote, CreditNoteItem, DebitNote, DebitNoteItem, PaymentVoucher, ReceiptVoucher,
    ContraVoucher, JournalVoucher, InterDepartmentVoucher, InterDepartmentVoucherItem
)
from app.models.vouchers.manufacturing_operations import (
    MaterialIssue, MaterialIssueItem, ProductionEntry, ProductionEntryItem,
    ManufacturingJournalVoucher, ManufacturingJournalFinishedProduct, ManufacturingJournalMaterial, ManufacturingJournalByproduct,
    MaterialReceiptVoucher, MaterialReceiptItem, JobCardVoucher, JobCardSuppliedMaterial, JobCardReceivedOutput,
    StockJournal, StockJournalEntry
)
from app.models.vouchers.manufacturing_planning import BillOfMaterials, BOMComponent, ManufacturingOrder
from app.models.vouchers.presales import Quotation, QuotationItem, ProformaInvoice, ProformaInvoiceItem, SalesOrder, SalesOrderItem
from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceiptNote, GoodsReceiptNoteItem, PurchaseVoucher, PurchaseVoucherItem, PurchaseReturn, PurchaseReturnItem
from app.models.vouchers.sales import DeliveryChallan, DeliveryChallanItem, SalesVoucher, SalesVoucherItem, SalesReturn, SalesReturnItem
from app.core.audit import AuditLogger
import logging

logger = logging.getLogger(__name__)


class OrgResetService:
    """Service for organization-level reset operations"""
    
    @staticmethod
    async def reset_organization_business_data(db: AsyncSession, organization_id: int) -> Dict[str, Any]:
        """
        Reset organization business data only (for Org Super Admin "Reset All Data")
        Removes business data but keeps users and organization settings
        
        Args:
            db: Database session
            organization_id: ID of the organization to reset
            
        Returns:
            dict: Result with message and deleted counts
        """
        try:
            # Validate organization exists
            org = await db.scalar(select(Organization).where(Organization.id == organization_id))
            if not org:
                raise ValueError(f"Organization with ID {organization_id} not found")
            
            result = {"message": "Organization business data reset completed", "deleted": {}}
            
            # Delete in reverse dependency order to avoid foreign key constraints
            # First delete all dependent child records (items, history, etc.) using subqueries where necessary
            # Then delete parent records
            
            # Service models dependencies
            # Delete Ticket children
            res_ticket_history = await db.execute(
                delete(TicketHistory).where(
                    TicketHistory.ticket_id.in_(
                        select(Ticket.id).where(Ticket.organization_id == organization_id)
                    )
                )
            )
            deleted_ticket_history = res_ticket_history.rowcount
            result["deleted"]["ticket_history"] = deleted_ticket_history
            
            res_ticket_attachments = await db.execute(
                delete(TicketAttachment).where(
                    TicketAttachment.ticket_id.in_(
                        select(Ticket.id).where(Ticket.organization_id == organization_id)
                    )
                )
            )
            deleted_ticket_attachments = res_ticket_attachments.rowcount
            result["deleted"]["ticket_attachments"] = deleted_ticket_attachments
            
            res_sla_tracking = await db.execute(
                delete(SLATracking).where(
                    SLATracking.ticket_id.in_(
                        select(Ticket.id).where(Ticket.organization_id == organization_id)
                    )
                )
            )
            deleted_sla_tracking = res_sla_tracking.rowcount
            result["deleted"]["sla_tracking"] = deleted_sla_tracking
            
            # Delete Tickets
            res_tickets = await db.execute(delete(Ticket).where(Ticket.organization_id == organization_id))
            deleted_tickets = res_tickets.rowcount
            result["deleted"]["tickets"] = deleted_tickets
            
            # Delete SLA Policies (after tracking deleted)
            res_sla_policies = await db.execute(delete(SLAPolicy).where(SLAPolicy.organization_id == organization_id))
            deleted_sla_policies = res_sla_policies.rowcount
            result["deleted"]["sla_policies"] = deleted_sla_policies
            
            # Delete Dispatch Items
            res_dispatch_items = await db.execute(
                delete(DispatchItem).where(
                    DispatchItem.dispatch_order_id.in_(
                        select(DispatchOrder.id).where(DispatchOrder.organization_id == organization_id)
                    )
                )
            )
            deleted_dispatch_items = res_dispatch_items.rowcount
            result["deleted"]["dispatch_items"] = deleted_dispatch_items
            
            # Delete Dispatch Orders
            res_dispatch_orders = await db.execute(delete(DispatchOrder).where(DispatchOrder.organization_id == organization_id))
            deleted_dispatch_orders = res_dispatch_orders.rowcount
            result["deleted"]["dispatch_orders"] = deleted_dispatch_orders
            
            # Delete Installation Job children
            res_installation_tasks = await db.execute(
                delete(InstallationTask).where(
                    InstallationTask.installation_job_id.in_(
                        select(InstallationJob.id).where(InstallationJob.organization_id == organization_id)
                    )
                )
            )
            deleted_installation_tasks = res_installation_tasks.rowcount
            result["deleted"]["installation_tasks"] = deleted_installation_tasks
            
            res_completion_records = await db.execute(
                delete(CompletionRecord).where(
                    CompletionRecord.installation_job_id.in_(
                        select(InstallationJob.id).where(InstallationJob.organization_id == organization_id)
                    )
                )
            )
            deleted_completion_records = res_completion_records.rowcount
            result["deleted"]["completion_records"] = deleted_completion_records
            
            res_customer_feedback = await db.execute(
                delete(CustomerFeedback).where(
                    CustomerFeedback.installation_job_id.in_(
                        select(InstallationJob.id).where(InstallationJob.organization_id == organization_id)
                    )
                )
            )
            deleted_customer_feedback = res_customer_feedback.rowcount
            result["deleted"]["customer_feedback"] = deleted_customer_feedback
            
            res_service_closures = await db.execute(
                delete(ServiceClosure).where(
                    ServiceClosure.installation_job_id.in_(
                        select(InstallationJob.id).where(InstallationJob.organization_id == organization_id)
                    )
                )
            )
            deleted_service_closures = res_service_closures.rowcount
            result["deleted"]["service_closures"] = deleted_service_closures
            
            # JobParts has org_id, delete directly
            res_job_parts = await db.execute(delete(JobParts).where(JobParts.organization_id == organization_id))
            deleted_job_parts = res_job_parts.rowcount
            result["deleted"]["job_parts"] = deleted_job_parts
            
            # Delete Installation Jobs
            res_installation_jobs = await db.execute(delete(InstallationJob).where(InstallationJob.organization_id == organization_id))
            deleted_installation_jobs = res_installation_jobs.rowcount
            result["deleted"]["installation_jobs"] = deleted_installation_jobs
            
            # Voucher dependencies - delete items first, then parents
            
            # Financial vouchers
            res_cn_items = await db.execute(
                delete(CreditNoteItem).where(
                    CreditNoteItem.credit_note_id.in_(
                        select(CreditNote.id).where(CreditNote.organization_id == organization_id)
                    )
                )
            )
            deleted_cn_items = res_cn_items.rowcount
            result["deleted"]["credit_note_items"] = deleted_cn_items
            res_credit_notes = await db.execute(delete(CreditNote).where(CreditNote.organization_id == organization_id))
            deleted_credit_notes = res_credit_notes.rowcount
            result["deleted"]["credit_notes"] = deleted_credit_notes
            
            res_dn_items = await db.execute(
                delete(DebitNoteItem).where(
                    DebitNoteItem.debit_note_id.in_(
                        select(DebitNote.id).where(DebitNote.organization_id == organization_id)
                    )
                )
            )
            deleted_dn_items = res_dn_items.rowcount
            result["deleted"]["debit_note_items"] = deleted_dn_items
            res_debit_notes = await db.execute(delete(DebitNote).where(DebitNote.organization_id == organization_id))
            deleted_debit_notes = res_debit_notes.rowcount
            result["deleted"]["debit_notes"] = deleted_debit_notes
            
            res_idv_items = await db.execute(
                delete(InterDepartmentVoucherItem).where(
                    InterDepartmentVoucherItem.inter_department_voucher_id.in_(
                        select(InterDepartmentVoucher.id).where(InterDepartmentVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_idv_items = res_idv_items.rowcount
            result["deleted"]["inter_department_voucher_items"] = deleted_idv_items
            res_idvs = await db.execute(delete(InterDepartmentVoucher).where(InterDepartmentVoucher.organization_id == organization_id))
            deleted_idvs = res_idvs.rowcount
            result["deleted"]["inter_department_vouchers"] = deleted_idvs
            
            # Delete vouchers without items
            res_payment_vouchers = await db.execute(delete(PaymentVoucher).where(PaymentVoucher.organization_id == organization_id))
            deleted_payment_vouchers = res_payment_vouchers.rowcount
            result["deleted"]["payment_vouchers"] = deleted_payment_vouchers
            
            res_receipt_vouchers = await db.execute(delete(ReceiptVoucher).where(ReceiptVoucher.organization_id == organization_id))
            deleted_receipt_vouchers = res_receipt_vouchers.rowcount
            result["deleted"]["receipt_vouchers"] = deleted_receipt_vouchers
            
            res_contra_vouchers = await db.execute(delete(ContraVoucher).where(ContraVoucher.organization_id == organization_id))
            deleted_contra_vouchers = res_contra_vouchers.rowcount
            result["deleted"]["contra_vouchers"] = deleted_contra_vouchers
            
            res_journal_vouchers = await db.execute(delete(JournalVoucher).where(JournalVoucher.organization_id == organization_id))
            deleted_journal_vouchers = res_journal_vouchers.rowcount
            result["deleted"]["journal_vouchers"] = deleted_journal_vouchers
            
            # Manufacturing operations
            res_mi_items = await db.execute(
                delete(MaterialIssueItem).where(
                    MaterialIssueItem.material_issue_id.in_(
                        select(MaterialIssue.id).where(MaterialIssue.organization_id == organization_id)
                    )
                )
            )
            deleted_mi_items = res_mi_items.rowcount
            result["deleted"]["material_issue_items"] = deleted_mi_items
            res_material_issues = await db.execute(delete(MaterialIssue).where(MaterialIssue.organization_id == organization_id))
            deleted_material_issues = res_material_issues.rowcount
            result["deleted"]["material_issues"] = deleted_material_issues
            
            res_pe_items = await db.execute(
                delete(ProductionEntryItem).where(
                    ProductionEntryItem.production_entry_id.in_(
                        select(ProductionEntry.id).where(ProductionEntry.organization_id == organization_id)
                    )
                )
            )
            deleted_pe_items = res_pe_items.rowcount
            result["deleted"]["production_entry_items"] = deleted_pe_items
            res_production_entries = await db.execute(delete(ProductionEntry).where(ProductionEntry.organization_id == organization_id))
            deleted_production_entries = res_production_entries.rowcount
            result["deleted"]["production_entries"] = deleted_production_entries
            
            # Manufacturing Journal
            res_mj_finished = await db.execute(
                delete(ManufacturingJournalFinishedProduct).where(
                    ManufacturingJournalFinishedProduct.journal_id.in_(
                        select(ManufacturingJournalVoucher.id).where(ManufacturingJournalVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_mj_finished = res_mj_finished.rowcount
            result["deleted"]["manufacturing_journal_finished_products"] = deleted_mj_finished
            
            res_mj_materials = await db.execute(
                delete(ManufacturingJournalMaterial).where(
                    ManufacturingJournalMaterial.journal_id.in_(
                        select(ManufacturingJournalVoucher.id).where(ManufacturingJournalVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_mj_materials = res_mj_materials.rowcount
            result["deleted"]["manufacturing_journal_materials"] = deleted_mj_materials
            
            res_mj_byproducts = await db.execute(
                delete(ManufacturingJournalByproduct).where(
                    ManufacturingJournalByproduct.journal_id.in_(
                        select(ManufacturingJournalVoucher.id).where(ManufacturingJournalVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_mj_byproducts = res_mj_byproducts.rowcount
            result["deleted"]["manufacturing_journal_byproducts"] = deleted_mj_byproducts
            
            res_mj_vouchers = await db.execute(delete(ManufacturingJournalVoucher).where(ManufacturingJournalVoucher.organization_id == organization_id))
            deleted_mj_vouchers = res_mj_vouchers.rowcount
            result["deleted"]["manufacturing_journal_vouchers"] = deleted_mj_vouchers
            
            res_mr_items = await db.execute(
                delete(MaterialReceiptItem).where(
                    MaterialReceiptItem.receipt_id.in_(
                        select(MaterialReceiptVoucher.id).where(MaterialReceiptVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_mr_items = res_mr_items.rowcount
            result["deleted"]["material_receipt_items"] = deleted_mr_items
            res_material_receipts = await db.execute(delete(MaterialReceiptVoucher).where(MaterialReceiptVoucher.organization_id == organization_id))
            deleted_material_receipts = res_material_receipts.rowcount
            result["deleted"]["material_receipt_vouchers"] = deleted_material_receipts
            
            res_jc_supplied = await db.execute(
                delete(JobCardSuppliedMaterial).where(
                    JobCardSuppliedMaterial.job_card_id.in_(
                        select(JobCardVoucher.id).where(JobCardVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_jc_supplied = res_jc_supplied.rowcount
            result["deleted"]["job_card_supplied_materials"] = deleted_jc_supplied
            
            res_jc_received = await db.execute(
                delete(JobCardReceivedOutput).where(
                    JobCardReceivedOutput.job_card_id.in_(
                        select(JobCardVoucher.id).where(JobCardVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_jc_received = res_jc_received.rowcount
            result["deleted"]["job_card_received_outputs"] = deleted_jc_received
            
            res_job_cards = await db.execute(delete(JobCardVoucher).where(JobCardVoucher.organization_id == organization_id))
            deleted_job_cards = res_job_cards.rowcount
            result["deleted"]["job_card_vouchers"] = deleted_job_cards
            
            res_sj_entries = await db.execute(
                delete(StockJournalEntry).where(
                    StockJournalEntry.stock_journal_id.in_(
                        select(StockJournal.id).where(StockJournal.organization_id == organization_id)
                    )
                )
            )
            deleted_sj_entries = res_sj_entries.rowcount
            result["deleted"]["stock_journal_entries"] = deleted_sj_entries
            res_stock_journals = await db.execute(delete(StockJournal).where(StockJournal.organization_id == organization_id))
            deleted_stock_journals = res_stock_journals.rowcount
            result["deleted"]["stock_journals"] = deleted_stock_journals
            
            # Manufacturing planning
            res_bom_components = await db.execute(delete(BOMComponent).where(BOMComponent.organization_id == organization_id))
            deleted_bom_components = res_bom_components.rowcount
            result["deleted"]["bom_components"] = deleted_bom_components
            
            res_boms = await db.execute(delete(BillOfMaterials).where(BillOfMaterials.organization_id == organization_id))
            deleted_boms = res_boms.rowcount
            result["deleted"]["bill_of_materials"] = deleted_boms
            
            res_manufacturing_orders = await db.execute(delete(ManufacturingOrder).where(ManufacturingOrder.organization_id == organization_id))
            deleted_manufacturing_orders = res_manufacturing_orders.rowcount
            result["deleted"]["manufacturing_orders"] = deleted_manufacturing_orders
            
            # Presales
            res_q_items = await db.execute(
                delete(QuotationItem).where(
                    QuotationItem.quotation_id.in_(
                        select(Quotation.id).where(Quotation.organization_id == organization_id)
                    )
                )
            )
            deleted_q_items = res_q_items.rowcount
            result["deleted"]["quotation_items"] = deleted_q_items
            res_quotations = await db.execute(delete(Quotation).where(Quotation.organization_id == organization_id))
            deleted_quotations = res_quotations.rowcount
            result["deleted"]["quotations"] = deleted_quotations
            
            res_pi_items = await db.execute(
                delete(ProformaInvoiceItem).where(
                    ProformaInvoiceItem.proforma_invoice_id.in_(
                        select(ProformaInvoice.id).where(ProformaInvoice.organization_id == organization_id)
                    )
                )
            )
            deleted_pi_items = res_pi_items.rowcount
            result["deleted"]["proforma_invoice_items"] = deleted_pi_items
            res_proforma_invoices = await db.execute(delete(ProformaInvoice).where(ProformaInvoice.organization_id == organization_id))
            deleted_proforma_invoices = res_proforma_invoices.rowcount
            result["deleted"]["proforma_invoices"] = deleted_proforma_invoices
            
            res_so_items = await db.execute(
                delete(SalesOrderItem).where(
                    SalesOrderItem.sales_order_id.in_(
                        select(SalesOrder.id).where(SalesOrder.organization_id == organization_id)
                    )
                )
            )
            deleted_so_items = res_so_items.rowcount
            result["deleted"]["sales_order_items"] = deleted_so_items
            res_sales_orders = await db.execute(delete(SalesOrder).where(SalesOrder.organization_id == organization_id))
            deleted_sales_orders = res_sales_orders.rowcount
            result["deleted"]["sales_orders"] = deleted_sales_orders
            
            # Purchase - reordered to respect FK constraints: pr -> pv -> grn -> po
            res_pr_items = await db.execute(
                delete(PurchaseReturnItem).where(
                    PurchaseReturnItem.purchase_return_id.in_(
                        select(PurchaseReturn.id).where(PurchaseReturn.organization_id == organization_id)
                    )
                )
            )
            deleted_pr_items = res_pr_items.rowcount
            result["deleted"]["purchase_return_items"] = deleted_pr_items
            res_purchase_returns = await db.execute(delete(PurchaseReturn).where(PurchaseReturn.organization_id == organization_id))
            deleted_purchase_returns = res_purchase_returns.rowcount
            result["deleted"]["purchase_returns"] = deleted_purchase_returns
            
            res_pv_items = await db.execute(
                delete(PurchaseVoucherItem).where(
                    PurchaseVoucherItem.purchase_voucher_id.in_(
                        select(PurchaseVoucher.id).where(PurchaseVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_pv_items = res_pv_items.rowcount
            result["deleted"]["purchase_voucher_items"] = deleted_pv_items
            res_purchase_vouchers = await db.execute(delete(PurchaseVoucher).where(PurchaseVoucher.organization_id == organization_id))
            deleted_purchase_vouchers = res_purchase_vouchers.rowcount
            result["deleted"]["purchase_vouchers"] = deleted_purchase_vouchers
            
            res_grn_items = await db.execute(
                delete(GoodsReceiptNoteItem).where(
                    GoodsReceiptNoteItem.grn_id.in_(
                        select(GoodsReceiptNote.id).where(GoodsReceiptNote.organization_id == organization_id)
                    )
                )
            )
            deleted_grn_items = res_grn_items.rowcount
            result["deleted"]["goods_receipt_note_items"] = deleted_grn_items
            res_goods_receipt_notes = await db.execute(delete(GoodsReceiptNote).where(GoodsReceiptNote.organization_id == organization_id))
            deleted_goods_receipt_notes = res_goods_receipt_notes.rowcount
            result["deleted"]["goods_receipt_notes"] = deleted_goods_receipt_notes
            
            res_po_items = await db.execute(
                delete(PurchaseOrderItem).where(
                    PurchaseOrderItem.purchase_order_id.in_(
                        select(PurchaseOrder.id).where(PurchaseOrder.organization_id == organization_id)
                    )
                )
            )
            deleted_po_items = res_po_items.rowcount
            result["deleted"]["purchase_order_items"] = deleted_po_items
            res_purchase_orders = await db.execute(delete(PurchaseOrder).where(PurchaseOrder.organization_id == organization_id))
            deleted_purchase_orders = res_purchase_orders.rowcount
            result["deleted"]["purchase_orders"] = deleted_purchase_orders
            
            # Sales
            res_dc_items = await db.execute(
                delete(DeliveryChallanItem).where(
                    DeliveryChallanItem.delivery_challan_id.in_(
                        select(DeliveryChallan.id).where(DeliveryChallan.organization_id == organization_id)
                    )
                )
            )
            deleted_dc_items = res_dc_items.rowcount
            result["deleted"]["delivery_challan_items"] = deleted_dc_items
            res_delivery_challans = await db.execute(delete(DeliveryChallan).where(DeliveryChallan.organization_id == organization_id))
            deleted_delivery_challans = res_delivery_challans.rowcount
            result["deleted"]["delivery_challans"] = deleted_delivery_challans
            
            res_sv_items = await db.execute(
                delete(SalesVoucherItem).where(
                    SalesVoucherItem.sales_voucher_id.in_(
                        select(SalesVoucher.id).where(SalesVoucher.organization_id == organization_id)
                    )
                )
            )
            deleted_sv_items = res_sv_items.rowcount
            result["deleted"]["sales_voucher_items"] = deleted_sv_items
            res_sales_vouchers = await db.execute(delete(SalesVoucher).where(SalesVoucher.organization_id == organization_id))
            deleted_sales_vouchers = res_sales_vouchers.rowcount
            result["deleted"]["sales_vouchers"] = deleted_sales_vouchers
            
            res_sr_items = await db.execute(
                delete(SalesReturnItem).where(
                    SalesReturnItem.sales_return_id.in_(
                        select(SalesReturn.id).where(SalesReturn.organization_id == organization_id)
                    )
                )
            )
            deleted_sr_items = res_sr_items.rowcount
            result["deleted"]["sales_return_items"] = deleted_sr_items
            res_sales_returns = await db.execute(delete(SalesReturn).where(SalesReturn.organization_id == organization_id))
            deleted_sales_returns = res_sales_returns.rowcount
            result["deleted"]["sales_returns"] = deleted_sales_returns
            
            # Additional product dependencies
            res_product_files = await db.execute(delete(ProductFile).where(ProductFile.organization_id == organization_id))
            deleted_product_files = res_product_files.rowcount
            result["deleted"]["product_files"] = deleted_product_files
            
            res_inventory_transactions = await db.execute(delete(InventoryTransaction).where(InventoryTransaction.organization_id == organization_id))
            deleted_inventory_transactions = res_inventory_transactions.rowcount
            result["deleted"]["inventory_transactions"] = deleted_inventory_transactions
            
            res_inventory_alerts = await db.execute(delete(InventoryAlert).where(InventoryAlert.organization_id == organization_id))
            deleted_inventory_alerts = res_inventory_alerts.rowcount
            result["deleted"]["inventory_alerts"] = deleted_inventory_alerts
            
            # Customer and Vendor dependencies
            res_customer_files = await db.execute(delete(CustomerFile).where(CustomerFile.organization_id == organization_id))
            deleted_customer_files = res_customer_files.rowcount
            result["deleted"]["customer_files"] = deleted_customer_files
            
            res_vendor_files = await db.execute(delete(VendorFile).where(VendorFile.organization_id == organization_id))
            deleted_vendor_files = res_vendor_files.rowcount
            result["deleted"]["vendor_files"] = deleted_vendor_files
            
            res_customer_interactions = await db.execute(delete(CustomerInteraction).where(CustomerInteraction.organization_id == organization_id))
            deleted_customer_interactions = res_customer_interactions.rowcount
            result["deleted"]["customer_interactions"] = deleted_customer_interactions
            
            res_customer_segments = await db.execute(delete(CustomerSegment).where(CustomerSegment.organization_id == organization_id))
            deleted_customer_segments = res_customer_segments.rowcount
            result["deleted"]["customer_segments"] = deleted_customer_segments
            
            # Notification and analytics
            res_notification_templates = await db.execute(delete(NotificationTemplate).where(NotificationTemplate.organization_id == organization_id))
            deleted_notification_templates = res_notification_templates.rowcount
            result["deleted"]["notification_templates"] = deleted_notification_templates
            
            res_notification_logs = await db.execute(delete(NotificationLog).where(NotificationLog.organization_id == organization_id))
            deleted_notification_logs = res_notification_logs.rowcount
            result["deleted"]["notification_logs"] = deleted_notification_logs
            
            res_notification_preferences = await db.execute(delete(NotificationPreference).where(NotificationPreference.organization_id == organization_id))
            deleted_notification_preferences = res_notification_preferences.rowcount
            result["deleted"]["notification_preferences"] = deleted_notification_preferences
            
            res_service_analytics_events = await db.execute(delete(ServiceAnalyticsEvent).where(ServiceAnalyticsEvent.organization_id == organization_id))
            deleted_service_analytics_events = res_service_analytics_events.rowcount
            result["deleted"]["service_analytics_events"] = deleted_service_analytics_events
            
            res_report_configurations = await db.execute(delete(ReportConfiguration).where(ReportConfiguration.organization_id == organization_id))
            deleted_report_configurations = res_report_configurations.rowcount
            result["deleted"]["report_configurations"] = deleted_report_configurations
            
            res_analytics_summaries = await db.execute(delete(AnalyticsSummary).where(AnalyticsSummary.organization_id == organization_id))
            deleted_analytics_summaries = res_analytics_summaries.rowcount
            result["deleted"]["analytics_summaries"] = deleted_analytics_summaries
            
            # Existing deletions
            res_notifications = await db.execute(delete(EmailNotification).where(EmailNotification.organization_id == organization_id))
            deleted_notifications = res_notifications.rowcount
            result["deleted"]["email_notifications"] = deleted_notifications
            
            res_stock = await db.execute(delete(Stock).where(Stock.organization_id == organization_id))
            deleted_stock = res_stock.rowcount
            result["deleted"]["stock"] = deleted_stock
            
            res_payment_terms = await db.execute(delete(PaymentTerm).where(PaymentTerm.organization_id == organization_id))
            deleted_payment_terms = res_payment_terms.rowcount
            result["deleted"]["payment_terms"] = deleted_payment_terms
            
            res_products = await db.execute(delete(Product).where(Product.organization_id == organization_id))
            deleted_products = res_products.rowcount
            result["deleted"]["products"] = deleted_products
            
            res_customers = await db.execute(delete(Customer).where(Customer.organization_id == organization_id))
            deleted_customers = res_customers.rowcount
            result["deleted"]["customers"] = deleted_customers
            
            res_vendors = await db.execute(delete(Vendor).where(Vendor.organization_id == organization_id))
            deleted_vendors = res_vendors.rowcount
            result["deleted"]["vendors"] = deleted_vendors
            
            res_companies = await db.execute(delete(Company).where(Company.organization_id == organization_id))
            deleted_companies = res_companies.rowcount
            result["deleted"]["companies"] = deleted_companies
            
            # Delete OTP verifications for this organization
            res_otps = await db.execute(delete(OTPVerification).where(OTPVerification.organization_id == organization_id))
            deleted_otps = res_otps.rowcount
            result["deleted"]["otp_verifications"] = deleted_otps
            
            # Reset organization status to indicate incomplete setup
            org.company_details_completed = False
            
            await db.commit()
            logger.info(f"Business data reset completed for organization {organization_id}")
            
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during business data reset for organization {organization_id}: {str(e)}")
            raise e