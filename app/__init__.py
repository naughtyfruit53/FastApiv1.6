from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import setup_logging
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_setup import router as admin_setup_router
from app.api.v1.ai_analytics import router as ai_analytics_router
from app.api.v1.api_gateway import router as api_gateway_router
from app.api.v1.app_users import router as app_users_router
from app.api.v1.assets import router as assets_router
from app.api.v1.auth import router as auth_router
from app.api.v1.bom import router as bom_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.chart_of_accounts import router as chart_of_accounts_router
from app.api.v1.chatbot import router as chatbot_router
from app.api.v1.company_branding import router as company_branding_router
from app.api.v1.crm import router as crm_router
from app.api.v1.dispatch import router as dispatch_router
from app.api.v1.email import router as email_router
from app.api.v1.erp import router as erp_router
from app.api.v1.exhibition import router as exhibition_router
from app.api.v1.external_integrations import router as external_integrations_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.finance_analytics import router as finance_analytics_router
from app.api.v1.financial_modeling import router as financial_modeling_router
from app.api.v1.forecasting import router as forecasting_router
from app.api.v1.gst import router as gst_router
from app.api.v1.gst_search import router as gst_search_router
from app.api.v1.health import router as health_router
from app.api.v1.hr import router as hr_router
from app.api.v1.integration_settings import router as integration_settings_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.ledger import router as ledger_router
from app.api.v1.login import router as login_router
from app.api.v1.mail import router as mail_router
from app.api.v1.manufacturing import router as manufacturing_router
from app.api.v1.marketing import router as marketing_router
from app.api.v1.master_auth import router as master_auth_router
from app.api.v1.master_data import router as master_data_router
from app.api.v1.migration import router as migration_router
from app.api.v1.oauth import router as oauth_router
from app.api.v1.otp import router as otp_router
from app.api.v1.password import router as password_router
from app.api.v1.payroll import router as payroll_router
from app.api.v1.payroll_components import router as payroll_components_router
from app.api.v1.payroll_components_advanced import router as payroll_components_advanced_router
from app.api.v1.payroll_gl import router as payroll_gl_router
from app.api.v1.payroll_migration import router as payroll_migration_router
from app.api.v1.payroll_monitoring import router as payroll_monitoring_router
from app.api.v1.pdf_extraction import router as pdf_extraction_router
from app.api.v1.pdf_generation import router as pdf_generation_router
from app.api.v1.procurement import router as procurement_router
from app.api.v1.project_management import router as project_management_router
from app.api.v1.rbac import router as rbac_router
from app.api.v1.reporting_hub import router as reporting_hub_router
from app.api.v1.reset import router as reset_router
from app.api.v1.seo import router as seo_router
from app.api.v1.service_analytics import router as service_analytics_router
from app.api.v1.service_desk import router as service_desk_router
from app.api.v1.sla import router as sla_router
from app.api.v1.stock import router as stock_router
from app.api.v1.tally import router as tally_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.transport import router as transport_router
from app.api.v1.user import router as user_router
from app.api.v1.voucher_email_templates import router as voucher_email_templates_router
from app.api.v1.voucher_format_templates import router as voucher_format_templates_router
from app.api.v1.warehouse import router as warehouse_router
from app.api.v1.workflow_approval import router as workflow_approval_router
from app.api.v1.organizations.routes import router as organizations_router
from app.api.v1.organizations.invitation_routes import invitation_router
from app.api.v1.organizations.license_routes import router as license_router
from app.api.v1.organizations.module_routes import router as module_router
from app.api.v1.organizations.user_routes import router as org_user_router
from app.api.v1.organizations.settings_routes import router as org_settings_router
from app.api.v1.vouchers.purchase_order import router as purchase_order_router
from app.api.v1.vouchers.purchase_voucher import router as purchase_voucher_router
from app.api.v1.vouchers.purchase_return import router as purchase_return_router
from app.api.v1.vouchers.sales_voucher import router as sales_voucher_router
from app.api.v1.vouchers.sales_return import router as sales_return_router
from app.api.v1.vouchers.delivery_challan import router as delivery_challan_router
from app.api.v1.vouchers.quotation import router as quotation_router
from app.api.v1.vouchers.proforma_invoice import router as proforma_invoice_router
from app.api.v1.vouchers.sales_order import router as sales_order_router
from app.api.v1.vouchers.payment_voucher import router as payment_voucher_router
from app.api.v1.vouchers.receipt_voucher import router as receipt_voucher_router
from app.api.v1.vouchers.journal_voucher import router as journal_voucher_router
from app.api.v1.vouchers.credit_note import router as credit_note_router
from app.api.v1.vouchers.debit_note import router as debit_note_router
from app.api.v1.vouchers.contra_voucher import router as contra_voucher_router
from app.api.v1.vouchers.inter_department_voucher import router as inter_department_voucher_router
from app.api.v1.vouchers.goods_receipt_note import router as goods_receipt_note_router

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporarily commented out to allow Alembic to run
# from app.core.rbac import RBACMiddleware
# from app.core.rbac_enhanced import EnhancedRBACMiddleware
# app.add_middleware(RBACMiddleware)
# app.add_middleware(EnhancedRBACMiddleware)

# Include routers
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(admin_setup_router, prefix="/api/v1/admin_setup", tags=["admin-setup"])
app.include_router(ai_analytics_router, prefix="/api/v1/ai_analytics", tags=["ai-analytics"])
app.include_router(api_gateway_router, prefix="/api/v1/api_gateway", tags=["api-gateway"])
app.include_router(app_users_router, prefix="/api/v1/app_users", tags=["app-users"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(bom_router, prefix="/api/v1/bom", tags=["bom"])
app.include_router(calendar_router, prefix="/api/v1/calendar", tags=["calendar"])
app.include_router(chart_of_accounts_router, prefix="/api/v1/chart_of_accounts", tags=["chart-of-accounts"])
app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(company_branding_router, prefix="/api/v1/company_branding", tags=["company-branding"])
app.include_router(crm_router, prefix="/api/v1/crm", tags=["crm"])
app.include_router(dispatch_router, prefix="/api/v1/dispatch", tags=["dispatch"])
app.include_router(email_router, prefix="/api/v1/email", tags=["email"])
app.include_router(erp_router, prefix="/api/v1/erp", tags=["erp"])
app.include_router(exhibition_router, prefix="/api/v1/exhibition", tags=["exhibition"])
app.include_router(external_integrations_router, prefix="/api/v1/external_integrations", tags=["external-integrations"])
app.include_router(feedback_router, prefix="/api/v1/feedback", tags=["feedback"])
app.include_router(finance_analytics_router, prefix="/api/v1/finance_analytics", tags=["finance-analytics"])
app.include_router(financial_modeling_router, prefix="/api/v1/financial_modeling", tags=["financial-modeling"])
app.include_router(forecasting_router, prefix="/api/v1/forecasting", tags=["forecasting"])
app.include_router(gst_router, prefix="/api/v1/gst", tags=["gst"])
app.include_router(gst_search_router, prefix="/api/v1/gst_search", tags=["gst-search"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
app.include_router(hr_router, prefix="/api/v1/hr", tags=["hr"])
app.include_router(integration_settings_router, prefix="/api/v1/integration_settings", tags=["integration-settings"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(ledger_router, prefix="/api/v1/ledger", tags=["ledger"])
app.include_router(login_router, prefix="/api/v1/login", tags=["login"])
app.include_router(mail_router, prefix="/api/v1/mail", tags=["mail"])
app.include_router(manufacturing_router, prefix="/api/v1/manufacturing", tags=["manufacturing"])
app.include_router(marketing_router, prefix="/api/v1/marketing", tags=["marketing"])
app.include_router(master_auth_router, prefix="/api/v1/master_auth", tags=["master-auth"])
app.include_router(master_data_router, prefix="/api/v1/master_data", tags=["master-data"])
app.include_router(migration_router, prefix="/api/v1/migration", tags=["migration"])
app.include_router(oauth_router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(otp_router, prefix="/api/v1/otp", tags=["otp"])
app.include_router(password_router, prefix="/api/v1/password", tags=["password"])
app.include_router(payroll_router, prefix="/api/v1/payroll", tags=["payroll"])
app.include_router(payroll_components_router, prefix="/api/v1/payroll_components", tags=["payroll-components"])
app.include_router(payroll_components_advanced_router, prefix="/api/v1/payroll_components_advanced", tags=["payroll-components-advanced"])
app.include_router(payroll_gl_router, prefix="/api/v1/payroll_gl", tags=["payroll-gl"])
app.include_router(payroll_migration_router, prefix="/api/v1/payroll_migration", tags=["payroll-migration"])
app.include_router(payroll_monitoring_router, prefix="/api/v1/payroll_monitoring", tags=["payroll-monitoring"])
app.include_router(pdf_extraction_router, prefix="/api/v1/pdf_extraction", tags=["pdf-extraction"])
app.include_router(pdf_generation_router, prefix="/api/v1/pdf_generation", tags=["pdf-generation"])
app.include_router(procurement_router, prefix="/api/v1/procurement", tags=["procurement"])
app.include_router(project_management_router, prefix="/api/v1/project_management", tags=["project-management"])
app.include_router(rbac_router, prefix="/api/v1/rbac", tags=["rbac"])
app.include_router(reporting_hub_router, prefix="/api/v1/reporting_hub", tags=["reporting-hub"])
app.include_router(reset_router, prefix="/api/v1/reset", tags=["reset"])
app.include_router(seo_router, prefix="/api/v1/seo", tags=["seo"])
app.include_router(service_analytics_router, prefix="/api/v1/service_analytics", tags=["service-analytics"])
app.include_router(service_desk_router, prefix="/api/v1/service_desk", tags=["service-desk"])
app.include_router(sla_router, prefix="/api/v1/sla", tags=["sla"])
app.include_router(stock_router, prefix="/api/v1/stock", tags=["stock"])
app.include_router(tally_router, prefix="/api/v1/tally", tags=["tally"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(transport_router, prefix="/api/v1/transport", tags=["transport"])
app.include_router(user_router, prefix="/api/v1/user", tags=["user"])
app.include_router(voucher_email_templates_router, prefix="/api/v1/voucher_email_templates", tags=["voucher-email-templates"])
app.include_router(voucher_format_templates_router, prefix="/api/v1/voucher_format_templates", tags=["voucher-format-templates"])
app.include_router(warehouse_router, prefix="/api/v1/warehouse", tags=["warehouse"])
app.include_router(workflow_approval_router, prefix="/api/v1/workflow_approval", tags=["workflow-approval"])
app.include_router(organizations_router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(invitation_router, prefix="/api/v1/organizations/invitations", tags=["organizations-invitations"])
app.include_router(license_router, prefix="/api/v1/organizations/licenses", tags=["organizations-licenses"])
app.include_router(module_router, prefix="/api/v1/organizations/modules", tags=["organizations-modules"])
app.include_router(org_user_router, prefix="/api/v1/organizations/users", tags=["organizations-users"])
app.include_router(org_settings_router, prefix="/api/v1/organizations/settings", tags=["organizations-settings"])
app.include_router(purchase_order_router, prefix="/api/v1/vouchers/purchase_order", tags=["vouchers-purchase-order"])
app.include_router(purchase_voucher_router, prefix="/api/v1/vouchers/purchase_voucher", tags=["vouchers-purchase-voucher"])
app.include_router(purchase_return_router, prefix="/api/v1/vouchers/purchase_return", tags=["vouchers-purchase-return"])
app.include_router(sales_voucher_router, prefix="/api/v1/vouchers/sales_voucher", tags=["vouchers-sales-voucher"])
app.include_router(sales_return_router, prefix="/api/v1/vouchers/sales_return", tags=["vouchers-sales-return"])
app.include_router(delivery_challan_router, prefix="/api/v1/vouchers/delivery_challan", tags=["vouchers-delivery-challan"])
app.include_router(quotation_router, prefix="/api/v1/vouchers/quotation", tags=["vouchers-quotation"])
app.include_router(proforma_invoice_router, prefix="/api/v1/vouchers/proforma_invoice", tags=["vouchers-proforma-invoice"])
app.include_router(sales_order_router, prefix="/api/v1/vouchers/sales_order", tags=["vouchers-sales-order"])
app.include_router(payment_voucher_router, prefix="/api/v1/vouchers/payment_voucher", tags=["vouchers-payment-voucher"])
app.include_router(receipt_voucher_router, prefix="/api/v1/vouchers/receipt_voucher", tags=["vouchers-receipt-voucher"])
app.include_router(journal_voucher_router, prefix="/api/v1/vouchers/journal_voucher", tags=["vouchers-journal-voucher"])
app.include_router(credit_note_router, prefix="/api/v1/vouchers/credit_note", tags=["vouchers-credit-note"])
app.include_router(debit_note_router, prefix="/api/v1/vouchers/debit_note", tags=["vouchers-debit-note"])
app.include_router(contra_voucher_router, prefix="/api/v1/vouchers/contra_voucher", tags=["vouchers-contra-voucher"])
app.include_router(inter_department_voucher_router, prefix="/api/v1/vouchers/inter_department_voucher", tags=["vouchers-inter-department-voucher"])
app.include_router(goods_receipt_note_router, prefix="/api/v1/vouchers/goods_receipt_note", tags=["vouchers-goods-receipt-note"])

@app.on_event("startup")
async def startup():
    # Create tables if they don't exist
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            await session.rollback()
            raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Add any other init code