# app/services/org_reset_service.py

"""
Organization-level reset service for business data reset operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import delete
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
    def reset_organization_business_data(db: Session, organization_id: int) -> Dict[str, Any]:
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
            org = db.query(Organization).filter(Organization.id == organization_id).first()
            if not org:
                raise ValueError(f"Organization with ID {organization_id} not found")
            
            result = {"message": "Organization business data reset completed", "deleted": {}}
            
            # Delete in reverse dependency order to avoid foreign key constraints
            # First delete all dependent child records (items, history, etc.) using subqueries where necessary
            # Then delete parent records
            
            # Service models dependencies
            # Delete Ticket children
            deleted_ticket_history = db.execute(
                delete(TicketHistory).where(
                    TicketHistory.ticket_id.in_(
                        db.query(Ticket.id).filter(Ticket.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["ticket_history"] = deleted_ticket_history
            
            deleted_ticket_attachments = db.execute(
                delete(TicketAttachment).where(
                    TicketAttachment.ticket_id.in_(
                        db.query(Ticket.id).filter(Ticket.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["ticket_attachments"] = deleted_ticket_attachments
            
            deleted_sla_tracking = db.execute(
                delete(SLATracking).where(
                    SLATracking.ticket_id.in_(
                        db.query(Ticket.id).filter(Ticket.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["sla_tracking"] = deleted_sla_tracking
            
            # Delete Tickets
            deleted_tickets = db.query(Ticket).filter(Ticket.organization_id == organization_id).delete()
            result["deleted"]["tickets"] = deleted_tickets
            
            # Delete SLA Policies (after tracking deleted)
            deleted_sla_policies = db.query(SLAPolicy).filter(SLAPolicy.organization_id == organization_id).delete()
            result["deleted"]["sla_policies"] = deleted_sla_policies
            
            # Delete Dispatch Items
            deleted_dispatch_items = db.execute(
                delete(DispatchItem).where(
                    DispatchItem.dispatch_order_id.in_(
                        db.query(DispatchOrder.id).filter(DispatchOrder.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["dispatch_items"] = deleted_dispatch_items
            
            # Delete Dispatch Orders
            deleted_dispatch_orders = db.query(DispatchOrder).filter(DispatchOrder.organization_id == organization_id).delete()
            result["deleted"]["dispatch_orders"] = deleted_dispatch_orders
            
            # Delete Installation Job children
            deleted_installation_tasks = db.execute(
                delete(InstallationTask).where(
                    InstallationTask.installation_job_id.in_(
                        db.query(InstallationJob.id).filter(InstallationJob.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["installation_tasks"] = deleted_installation_tasks
            
            deleted_completion_records = db.execute(
                delete(CompletionRecord).where(
                    CompletionRecord.installation_job_id.in_(
                        db.query(InstallationJob.id).filter(InstallationJob.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["completion_records"] = deleted_completion_records
            
            deleted_customer_feedback = db.execute(
                delete(CustomerFeedback).where(
                    CustomerFeedback.installation_job_id.in_(
                        db.query(InstallationJob.id).filter(InstallationJob.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["customer_feedback"] = deleted_customer_feedback
            
            deleted_service_closures = db.execute(
                delete(ServiceClosure).where(
                    ServiceClosure.installation_job_id.in_(
                        db.query(InstallationJob.id).filter(InstallationJob.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["service_closures"] = deleted_service_closures
            
            # JobParts has org_id, delete directly
            deleted_job_parts = db.query(JobParts).filter(JobParts.organization_id == organization_id).delete()
            result["deleted"]["job_parts"] = deleted_job_parts
            
            # Delete Installation Jobs
            deleted_installation_jobs = db.query(InstallationJob).filter(InstallationJob.organization_id == organization_id).delete()
            result["deleted"]["installation_jobs"] = deleted_installation_jobs
            
            # Voucher dependencies - delete items first, then parents
            
            # Financial vouchers
            deleted_cn_items = db.execute(
                delete(CreditNoteItem).where(
                    CreditNoteItem.credit_note_id.in_(
                        db.query(CreditNote.id).filter(CreditNote.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["credit_note_items"] = deleted_cn_items
            deleted_credit_notes = db.query(CreditNote).filter(CreditNote.organization_id == organization_id).delete()
            result["deleted"]["credit_notes"] = deleted_credit_notes
            
            deleted_dn_items = db.execute(
                delete(DebitNoteItem).where(
                    DebitNoteItem.debit_note_id.in_(
                        db.query(DebitNote.id).filter(DebitNote.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["debit_note_items"] = deleted_dn_items
            deleted_debit_notes = db.query(DebitNote).filter(DebitNote.organization_id == organization_id).delete()
            result["deleted"]["debit_notes"] = deleted_debit_notes
            
            deleted_idv_items = db.execute(
                delete(InterDepartmentVoucherItem).where(
                    InterDepartmentVoucherItem.inter_department_voucher_id.in_(
                        db.query(InterDepartmentVoucher.id).filter(InterDepartmentVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["inter_department_voucher_items"] = deleted_idv_items
            deleted_idvs = db.query(InterDepartmentVoucher).filter(InterDepartmentVoucher.organization_id == organization_id).delete()
            result["deleted"]["inter_department_vouchers"] = deleted_idvs
            
            # Delete vouchers without items
            deleted_payment_vouchers = db.query(PaymentVoucher).filter(PaymentVoucher.organization_id == organization_id).delete()
            result["deleted"]["payment_vouchers"] = deleted_payment_vouchers
            
            deleted_receipt_vouchers = db.query(ReceiptVoucher).filter(ReceiptVoucher.organization_id == organization_id).delete()
            result["deleted"]["receipt_vouchers"] = deleted_receipt_vouchers
            
            deleted_contra_vouchers = db.query(ContraVoucher).filter(ContraVoucher.organization_id == organization_id).delete()
            result["deleted"]["contra_vouchers"] = deleted_contra_vouchers
            
            deleted_journal_vouchers = db.query(JournalVoucher).filter(JournalVoucher.organization_id == organization_id).delete()
            result["deleted"]["journal_vouchers"] = deleted_journal_vouchers
            
            # Manufacturing operations
            deleted_mi_items = db.execute(
                delete(MaterialIssueItem).where(
                    MaterialIssueItem.material_issue_id.in_(
                        db.query(MaterialIssue.id).filter(MaterialIssue.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["material_issue_items"] = deleted_mi_items
            deleted_material_issues = db.query(MaterialIssue).filter(MaterialIssue.organization_id == organization_id).delete()
            result["deleted"]["material_issues"] = deleted_material_issues
            
            deleted_pe_items = db.execute(
                delete(ProductionEntryItem).where(
                    ProductionEntryItem.production_entry_id.in_(
                        db.query(ProductionEntry.id).filter(ProductionEntry.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["production_entry_items"] = deleted_pe_items
            deleted_production_entries = db.query(ProductionEntry).filter(ProductionEntry.organization_id == organization_id).delete()
            result["deleted"]["production_entries"] = deleted_production_entries
            
            # Manufacturing Journal
            deleted_mj_finished = db.execute(
                delete(ManufacturingJournalFinishedProduct).where(
                    ManufacturingJournalFinishedProduct.journal_id.in_(
                        db.query(ManufacturingJournalVoucher.id).filter(ManufacturingJournalVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["manufacturing_journal_finished_products"] = deleted_mj_finished
            
            deleted_mj_materials = db.execute(
                delete(ManufacturingJournalMaterial).where(
                    ManufacturingJournalMaterial.journal_id.in_(
                        db.query(ManufacturingJournalVoucher.id).filter(ManufacturingJournalVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["manufacturing_journal_materials"] = deleted_mj_materials
            
            deleted_mj_byproducts = db.execute(
                delete(ManufacturingJournalByproduct).where(
                    ManufacturingJournalByproduct.journal_id.in_(
                        db.query(ManufacturingJournalVoucher.id).filter(ManufacturingJournalVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["manufacturing_journal_byproducts"] = deleted_mj_byproducts
            
            deleted_mj_vouchers = db.query(ManufacturingJournalVoucher).filter(ManufacturingJournalVoucher.organization_id == organization_id).delete()
            result["deleted"]["manufacturing_journal_vouchers"] = deleted_mj_vouchers
            
            deleted_mr_items = db.execute(
                delete(MaterialReceiptItem).where(
                    MaterialReceiptItem.receipt_id.in_(
                        db.query(MaterialReceiptVoucher.id).filter(MaterialReceiptVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["material_receipt_items"] = deleted_mr_items
            deleted_material_receipts = db.query(MaterialReceiptVoucher).filter(MaterialReceiptVoucher.organization_id == organization_id).delete()
            result["deleted"]["material_receipt_vouchers"] = deleted_material_receipts
            
            deleted_jc_supplied = db.execute(
                delete(JobCardSuppliedMaterial).where(
                    JobCardSuppliedMaterial.job_card_id.in_(
                        db.query(JobCardVoucher.id).filter(JobCardVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["job_card_supplied_materials"] = deleted_jc_supplied
            
            deleted_jc_received = db.execute(
                delete(JobCardReceivedOutput).where(
                    JobCardReceivedOutput.job_card_id.in_(
                        db.query(JobCardVoucher.id).filter(JobCardVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["job_card_received_outputs"] = deleted_jc_received
            
            deleted_job_cards = db.query(JobCardVoucher).filter(JobCardVoucher.organization_id == organization_id).delete()
            result["deleted"]["job_card_vouchers"] = deleted_job_cards
            
            deleted_sj_entries = db.execute(
                delete(StockJournalEntry).where(
                    StockJournalEntry.stock_journal_id.in_(
                        db.query(StockJournal.id).filter(StockJournal.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["stock_journal_entries"] = deleted_sj_entries
            deleted_stock_journals = db.query(StockJournal).filter(StockJournal.organization_id == organization_id).delete()
            result["deleted"]["stock_journals"] = deleted_stock_journals
            
            # Manufacturing planning
            deleted_bom_components = db.query(BOMComponent).filter(BOMComponent.organization_id == organization_id).delete()
            result["deleted"]["bom_components"] = deleted_bom_components
            
            deleted_boms = db.query(BillOfMaterials).filter(BillOfMaterials.organization_id == organization_id).delete()
            result["deleted"]["bill_of_materials"] = deleted_boms
            
            deleted_manufacturing_orders = db.query(ManufacturingOrder).filter(ManufacturingOrder.organization_id == organization_id).delete()
            result["deleted"]["manufacturing_orders"] = deleted_manufacturing_orders
            
            # Presales
            deleted_q_items = db.execute(
                delete(QuotationItem).where(
                    QuotationItem.quotation_id.in_(
                        db.query(Quotation.id).filter(Quotation.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["quotation_items"] = deleted_q_items
            deleted_quotations = db.query(Quotation).filter(Quotation.organization_id == organization_id).delete()
            result["deleted"]["quotations"] = deleted_quotations
            
            deleted_pi_items = db.execute(
                delete(ProformaInvoiceItem).where(
                    ProformaInvoiceItem.proforma_invoice_id.in_(
                        db.query(ProformaInvoice.id).filter(ProformaInvoice.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["proforma_invoice_items"] = deleted_pi_items
            deleted_proforma_invoices = db.query(ProformaInvoice).filter(ProformaInvoice.organization_id == organization_id).delete()
            result["deleted"]["proforma_invoices"] = deleted_proforma_invoices
            
            deleted_so_items = db.execute(
                delete(SalesOrderItem).where(
                    SalesOrderItem.sales_order_id.in_(
                        db.query(SalesOrder.id).filter(SalesOrder.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["sales_order_items"] = deleted_so_items
            deleted_sales_orders = db.query(SalesOrder).filter(SalesOrder.organization_id == organization_id).delete()
            result["deleted"]["sales_orders"] = deleted_sales_orders
            
            # Purchase
            deleted_po_items = db.execute(
                delete(PurchaseOrderItem).where(
                    PurchaseOrderItem.purchase_order_id.in_(
                        db.query(PurchaseOrder.id).filter(PurchaseOrder.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["purchase_order_items"] = deleted_po_items
            deleted_purchase_orders = db.query(PurchaseOrder).filter(PurchaseOrder.organization_id == organization_id).delete()
            result["deleted"]["purchase_orders"] = deleted_purchase_orders
            
            deleted_grn_items = db.execute(
                delete(GoodsReceiptNoteItem).where(
                    GoodsReceiptNoteItem.grn_id.in_(
                        db.query(GoodsReceiptNote.id).filter(GoodsReceiptNote.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["goods_receipt_note_items"] = deleted_grn_items
            deleted_goods_receipt_notes = db.query(GoodsReceiptNote).filter(GoodsReceiptNote.organization_id == organization_id).delete()
            result["deleted"]["goods_receipt_notes"] = deleted_goods_receipt_notes
            
            deleted_pv_items = db.execute(
                delete(PurchaseVoucherItem).where(
                    PurchaseVoucherItem.purchase_voucher_id.in_(
                        db.query(PurchaseVoucher.id).filter(PurchaseVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["purchase_voucher_items"] = deleted_pv_items
            deleted_purchase_vouchers = db.query(PurchaseVoucher).filter(PurchaseVoucher.organization_id == organization_id).delete()
            result["deleted"]["purchase_vouchers"] = deleted_purchase_vouchers
            
            deleted_pr_items = db.execute(
                delete(PurchaseReturnItem).where(
                    PurchaseReturnItem.purchase_return_id.in_(
                        db.query(PurchaseReturn.id).filter(PurchaseReturn.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["purchase_return_items"] = deleted_pr_items
            deleted_purchase_returns = db.query(PurchaseReturn).filter(PurchaseReturn.organization_id == organization_id).delete()
            result["deleted"]["purchase_returns"] = deleted_purchase_returns
            
            # Sales
            deleted_dc_items = db.execute(
                delete(DeliveryChallanItem).where(
                    DeliveryChallanItem.delivery_challan_id.in_(
                        db.query(DeliveryChallan.id).filter(DeliveryChallan.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["delivery_challan_items"] = deleted_dc_items
            deleted_delivery_challans = db.query(DeliveryChallan).filter(DeliveryChallan.organization_id == organization_id).delete()
            result["deleted"]["delivery_challans"] = deleted_delivery_challans
            
            deleted_sv_items = db.execute(
                delete(SalesVoucherItem).where(
                    SalesVoucherItem.sales_voucher_id.in_(
                        db.query(SalesVoucher.id).filter(SalesVoucher.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["sales_voucher_items"] = deleted_sv_items
            deleted_sales_vouchers = db.query(SalesVoucher).filter(SalesVoucher.organization_id == organization_id).delete()
            result["deleted"]["sales_vouchers"] = deleted_sales_vouchers
            
            deleted_sr_items = db.execute(
                delete(SalesReturnItem).where(
                    SalesReturnItem.sales_return_id.in_(
                        db.query(SalesReturn.id).filter(SalesReturn.organization_id == organization_id).subquery()
                    )
                )
            ).rowcount
            result["deleted"]["sales_return_items"] = deleted_sr_items
            deleted_sales_returns = db.query(SalesReturn).filter(SalesReturn.organization_id == organization_id).delete()
            result["deleted"]["sales_returns"] = deleted_sales_returns
            
            # Additional product dependencies
            deleted_product_files = db.query(ProductFile).filter(ProductFile.organization_id == organization_id).delete()
            result["deleted"]["product_files"] = deleted_product_files
            
            deleted_inventory_transactions = db.query(InventoryTransaction).filter(InventoryTransaction.organization_id == organization_id).delete()
            result["deleted"]["inventory_transactions"] = deleted_inventory_transactions
            
            deleted_inventory_alerts = db.query(InventoryAlert).filter(InventoryAlert.organization_id == organization_id).delete()
            result["deleted"]["inventory_alerts"] = deleted_inventory_alerts
            
            # Customer and Vendor dependencies
            deleted_customer_files = db.query(CustomerFile).filter(CustomerFile.organization_id == organization_id).delete()
            result["deleted"]["customer_files"] = deleted_customer_files
            
            deleted_vendor_files = db.query(VendorFile).filter(VendorFile.organization_id == organization_id).delete()
            result["deleted"]["vendor_files"] = deleted_vendor_files
            
            deleted_customer_interactions = db.query(CustomerInteraction).filter(CustomerInteraction.organization_id == organization_id).delete()
            result["deleted"]["customer_interactions"] = deleted_customer_interactions
            
            deleted_customer_segments = db.query(CustomerSegment).filter(CustomerSegment.organization_id == organization_id).delete()
            result["deleted"]["customer_segments"] = deleted_customer_segments
            
            # Notification and analytics
            deleted_notification_templates = db.query(NotificationTemplate).filter(NotificationTemplate.organization_id == organization_id).delete()
            result["deleted"]["notification_templates"] = deleted_notification_templates
            
            deleted_notification_logs = db.query(NotificationLog).filter(NotificationLog.organization_id == organization_id).delete()
            result["deleted"]["notification_logs"] = deleted_notification_logs
            
            deleted_notification_preferences = db.query(NotificationPreference).filter(NotificationPreference.organization_id == organization_id).delete()
            result["deleted"]["notification_preferences"] = deleted_notification_preferences
            
            deleted_service_analytics_events = db.query(ServiceAnalyticsEvent).filter(ServiceAnalyticsEvent.organization_id == organization_id).delete()
            result["deleted"]["service_analytics_events"] = deleted_service_analytics_events
            
            deleted_report_configurations = db.query(ReportConfiguration).filter(ReportConfiguration.organization_id == organization_id).delete()
            result["deleted"]["report_configurations"] = deleted_report_configurations
            
            deleted_analytics_summaries = db.query(AnalyticsSummary).filter(AnalyticsSummary.organization_id == organization_id).delete()
            result["deleted"]["analytics_summaries"] = deleted_analytics_summaries
            
            # Existing deletions
            deleted_notifications = db.query(EmailNotification).filter(EmailNotification.organization_id == organization_id).delete()
            result["deleted"]["email_notifications"] = deleted_notifications
            
            deleted_stock = db.query(Stock).filter(Stock.organization_id == organization_id).delete()
            result["deleted"]["stock"] = deleted_stock
            
            deleted_payment_terms = db.query(PaymentTerm).filter(PaymentTerm.organization_id == organization_id).delete()
            result["deleted"]["payment_terms"] = deleted_payment_terms
            
            deleted_products = db.query(Product).filter(Product.organization_id == organization_id).delete()
            result["deleted"]["products"] = deleted_products
            
            deleted_customers = db.query(Customer).filter(Customer.organization_id == organization_id).delete()
            result["deleted"]["customers"] = deleted_customers
            
            deleted_vendors = db.query(Vendor).filter(Vendor.organization_id == organization_id).delete()
            result["deleted"]["vendors"] = deleted_vendors
            
            deleted_companies = db.query(Company).filter(Company.organization_id == organization_id).delete()
            result["deleted"]["companies"] = deleted_companies
            
            # Delete OTP verifications for this organization
            deleted_otps = db.query(OTPVerification).filter(OTPVerification.organization_id == organization_id).delete()
            result["deleted"]["otp_verifications"] = deleted_otps
            
            # Reset organization status to indicate incomplete setup
            org.company_details_completed = False
            
            db.commit()
            logger.info(f"Business data reset completed for organization {organization_id}")
            
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during business data reset for organization {organization_id}: {str(e)}")
            raise e