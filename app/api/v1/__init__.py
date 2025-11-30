# app/api/v1/__init__.py

from fastapi import APIRouter
from fastapi.routing import APIRoute
import logging
import traceback

logger = logging.getLogger(__name__)

api_v1_router = APIRouter()

def register_subrouters():
    # Import routers lazily inside this function to avoid circular imports
    try:
        from .chart_of_accounts import router as chart_of_accounts_router
        logger.debug("Imported chart_of_accounts_router")
        api_v1_router.include_router(chart_of_accounts_router, tags=["Chart of Accounts"])
        chart_of_accounts_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in chart_of_accounts_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered chart_of_accounts endpoints: {len(chart_of_accounts_routes)} routes")
        for route_path in chart_of_accounts_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include chart_of_accounts_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .expense_account import router as expense_account_router
        logger.debug("Imported expense_account_router")
        api_v1_router.include_router(expense_account_router, tags=["Expense Accounts"])
        expense_account_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in expense_account_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered expense_account endpoints: {len(expense_account_routes)} routes")
        for route_path in expense_account_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include expense_account_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers.journal_voucher import router as journal_voucher_router
        logger.debug("Imported journal_voucher_router")
        api_v1_router.include_router(journal_voucher_router)
        journal_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in journal_voucher_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered journal_voucher endpoints: {len(journal_routes)} routes")
        for route_path in journal_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include journal_voucher_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers.contra_voucher import router as contra_voucher_router
        logger.debug("Imported contra_voucher_router")
        api_v1_router.include_router(contra_voucher_router)
        contra_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in contra_voucher_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered contra_voucher endpoints: {len(contra_routes)} routes")
        for route_path in contra_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include contra_voucher_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers.credit_note import router as credit_note_router
        logger.debug("Imported credit_note_router")
        api_v1_router.include_router(credit_note_router)
        credit_note_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in credit_note_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered credit_note endpoints: {len(credit_note_routes)} routes")
        for route_path in credit_note_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include credit_note_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers.debit_note import router as debit_note_router
        logger.debug("Imported debit_note_router")
        api_v1_router.include_router(debit_note_router)
        debit_note_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in debit_note_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered debit_note endpoints: {len(debit_note_routes)} routes")
        for route_path in debit_note_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include debit_note_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers.non_sales_credit_note import router as non_sales_credit_note_router
        logger.debug("Imported non_sales_credit_note_router")
        api_v1_router.include_router(non_sales_credit_note_router)
        non_sales_credit_note_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in non_sales_credit_note_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered non_sales_credit_note endpoints: {len(non_sales_credit_note_routes)} routes")
        for route_path in non_sales_credit_note_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include non_sales_credit_note_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .user import router as user_router
        logger.debug("Imported user_router")
        api_v1_router.include_router(user_router, prefix="/users", tags=["users"])
        user_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in user_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered user endpoints: {len(user_routes)} routes")
        for route_path in user_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include user_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .organizations.routes import router as organizations_router
        logger.debug("Imported organizations_router")
        api_v1_router.include_router(organizations_router)
        org_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in organizations_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered organizations endpoints: {len(org_routes)} routes")
        for route_path in org_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include organizations_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .hr import router as hr_router
        logger.debug("Imported hr_router")
        api_v1_router.include_router(hr_router)
        hr_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in hr_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered hr endpoints: {len(hr_routes)} routes")
        for route_path in hr_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include hr_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .payroll import router as payroll_router
        logger.debug("Imported payroll_router")
        api_v1_router.include_router(payroll_router)
        payroll_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in payroll_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered payroll endpoints: {len(payroll_routes)} routes")
        for route_path in payroll_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include payroll_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .oauth import router as oauth_router
        logger.debug("Imported oauth_router")
        api_v1_router.include_router(oauth_router, prefix="/oauth", tags=["OAuth2"])
        oauth_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /oauth{route.path}" for route in oauth_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered oauth endpoints: {len(oauth_routes)} routes")
        for route_path in oauth_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include oauth_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .ledger import router as ledger_router
        logger.debug("Imported ledger_router")
        api_v1_router.include_router(ledger_router, prefix="/ledger")
        ledger_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /ledger{route.path}" for route in ledger_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered ledger endpoints: {len(ledger_routes)} routes")
        for route_path in ledger_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include ledger_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .master_data import router as master_data_router
        logger.debug("Imported master_data_router")
        api_v1_router.include_router(master_data_router, prefix="/master-data", tags=["master-data"])
        master_data_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /master-data{route.path}" for route in master_data_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered master_data endpoints: {len(master_data_routes)} routes")
        for route_path in master_data_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include master_data_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .email import router as email_router
        logger.debug("Imported email_router")
        api_v1_router.include_router(email_router, prefix="/email", tags=["email"])
        email_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /email{route.path}" for route in email_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered email endpoints: {len(email_routes)} routes")
        for route_path in email_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include email_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .voucher_email_templates import router as voucher_email_templates_router
        logger.debug("Imported voucher_email_templates_router")
        api_v1_router.include_router(voucher_email_templates_router, prefix="/voucher-email-templates")
        voucher_email_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /voucher-email-templates{route.path}" for route in voucher_email_templates_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered voucher_email_templates endpoints: {len(voucher_email_routes)} routes")
        for route_path in voucher_email_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include voucher_email_templates_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .voucher_format_templates import router as voucher_format_templates_router
        logger.debug("Imported voucher_format_templates_router")
        api_v1_router.include_router(voucher_format_templates_router, prefix="/voucher-format-templates")
        voucher_format_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /voucher-format-templates{route.path}" for route in voucher_format_templates_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered voucher_format_templates endpoints: {len(voucher_format_routes)} routes")
        for route_path in voucher_format_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include voucher_format_templates_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .chatbot import router as chatbot_router
        logger.debug("Imported chatbot_router")
        api_v1_router.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
        chatbot_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /chatbot{route.path}" for route in chatbot_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered chatbot endpoints: {len(chatbot_routes)} routes")
        for route_path in chatbot_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include chatbot_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .ai import router as ai_router
        logger.debug("Imported ai_router")
        api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI Agent"])
        ai_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /ai{route.path}" for route in ai_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered ai_router endpoints: {len(ai_routes)} routes")
        for route_path in ai_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include ai_router: {str(e)}\n{traceback.format_exc()}")

    # THIS WAS MISSING — NOW FIXED
    try:
        from .manufacturing import router as manufacturing_router
        logger.debug("Imported manufacturing_router")
        api_v1_router.include_router(manufacturing_router, prefix="/manufacturing", tags=["Manufacturing"])
        manufacturing_routes = [
            f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /manufacturing{route.path}"
            for route in manufacturing_router.routes
            if isinstance(route, APIRoute)
        ]
        logger.debug(f"Registered manufacturing endpoints: {len(manufacturing_routes)} routes")
        for route_path in manufacturing_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include manufacturing_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .bom import router as bom_router
        logger.debug("Imported bom_router")
        api_v1_router.include_router(bom_router, prefix="/bom", tags=["BOM"])
        bom_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /bom{route.path}" for route in bom_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered bom endpoints: {len(bom_routes)} routes")
        for route_path in bom_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include bom_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .transport import router as transport_router
        logger.debug("Imported transport_router")
        api_v1_router.include_router(transport_router, prefix="/transport", tags=["Transport"])
        transport_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /transport{route.path}" for route in transport_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered transport endpoints: {len(transport_routes)} routes")
        for route_path in transport_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include transport_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .crm import router as crm_router
        logger.debug("Imported crm_router")
        api_v1_router.include_router(crm_router, tags=["CRM"])
        crm_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in crm_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered crm endpoints: {len(crm_routes)} routes")
        for route_path in crm_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include crm_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .contacts import router as contacts_router
        logger.debug("Imported contacts_router")
        api_v1_router.include_router(contacts_router, tags=["Contacts"])
        contacts_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in contacts_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered contacts endpoints: {len(contacts_routes)} routes")
        for route_path in contacts_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include contacts_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .accounts import router as accounts_router
        logger.debug("Imported accounts_router")
        api_v1_router.include_router(accounts_router, tags=["Accounts"])
        accounts_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in accounts_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered accounts endpoints: {len(accounts_routes)} routes")
        for route_path in accounts_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include accounts_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .pincode import router as pincode_router
        logger.debug("Imported pincode_router")
        api_v1_router.include_router(pincode_router, prefix="/pincode", tags=["Pincode"])
        pincode_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /pincode{route.path}" for route in pincode_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered pincode endpoints: {len(pincode_routes)} routes")
        for route_path in pincode_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include pincode_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .website_agent import router as website_agent_router
        logger.debug("Imported website_agent_router")
        api_v1_router.include_router(website_agent_router, prefix="/website-agent", tags=["Website Agent"])
        website_agent_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /website-agent{route.path}" for route in website_agent_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered website_agent endpoints: {len(website_agent_routes)} routes")
        for route_path in website_agent_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include website_agent_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .ab_testing import router as ab_testing_router
        logger.debug("Imported ab_testing_router")
        api_v1_router.include_router(ab_testing_router, prefix="/ab-testing", tags=["A/B Testing"])
        ab_testing_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /ab-testing{route.path}" for route in ab_testing_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered ab_testing endpoints: {len(ab_testing_routes)} routes")
        for route_path in ab_testing_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include ab_testing_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .streaming_analytics import router as streaming_analytics_router
        logger.debug("Imported streaming_analytics_router")
        api_v1_router.include_router(streaming_analytics_router, prefix="/streaming-analytics", tags=["Streaming Analytics"])
        streaming_analytics_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /streaming-analytics{route.path}" for route in streaming_analytics_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered streaming_analytics endpoints: {len(streaming_analytics_routes)} routes")
        for route_path in streaming_analytics_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include streaming_analytics_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .vouchers import router as vouchers_router
        logger.debug("Imported vouchers_router")
        api_v1_router.include_router(vouchers_router, prefix="/vouchers")
        vouchers_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /vouchers{route.path}" for route in vouchers_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered vouchers endpoints: {len(vouchers_routes)} routes")
        for route_path in vouchers_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include vouchers_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .products import router as products_router
        logger.debug("Imported products_router")
        api_v1_router.include_router(products_router, prefix="/products", tags=["products"])
        products_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in products_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered products endpoints: {len(products_routes)} routes")
        for route_path in products_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include products_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .finance_analytics import router as finance_analytics_router
        logger.debug("Imported finance_analytics_router")
        api_v1_router.include_router(finance_analytics_router, prefix="/finance", tags=["Finance Analytics"])
        finance_analytics_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /finance{route.path}" for route in finance_analytics_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered finance_analytics endpoints: {len(finance_analytics_routes)} routes")
        for route_path in finance_analytics_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include finance_analytics_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .order_book import router as order_book_router
        logger.debug("Imported order_book_router")
        api_v1_router.include_router(order_book_router, tags=["Order Book"])
        order_book_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in order_book_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered order_book endpoints: {len(order_book_routes)} routes")
        for route_path in order_book_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include order_book_router: {str(e)}\n{traceback.format_exc()}")

    try:
        from .exhibition import router as exhibition_router
        logger.debug("Imported exhibition_router")
        api_v1_router.include_router(exhibition_router, prefix="/exhibition", tags=["Exhibition"])
        exhibition_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /exhibition{route.path}" for route in exhibition_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered exhibition endpoints: {len(exhibition_routes)} routes")
        for route_path in exhibition_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include exhibition_router: {str(e)}\n{traceback.format_exc()}")

    # Entitlements API (app-level, read-only)
    try:
        from .entitlements import router as entitlements_router
        logger.debug("Imported entitlements_router")
        api_v1_router.include_router(entitlements_router, tags=["entitlements"])
        entitlements_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in entitlements_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered entitlements endpoints: {len(entitlements_routes)} routes")
        for route_path in entitlements_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include entitlements_router: {str(e)}\n{traceback.format_exc()}")

    # Admin Entitlements API (admin-only, write)
    try:
        from .admin_entitlements import router as admin_entitlements_router
        logger.debug("Imported admin_entitlements_router")
        api_v1_router.include_router(admin_entitlements_router, tags=["admin-entitlements"])
        admin_ent_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in admin_entitlements_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered admin_entitlements endpoints: {len(admin_ent_routes)} routes")
        for route_path in admin_ent_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include admin_entitlements_router: {str(e)}\n{traceback.format_exc()}")

    # Admin Categories API (admin-only, category-based entitlement management)
    try:
        from .admin_categories import router as admin_categories_router
        logger.debug("Imported admin_categories_router")
        api_v1_router.include_router(admin_categories_router, tags=["admin-categories"])
        admin_cat_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in admin_categories_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered admin_categories endpoints: {len(admin_cat_routes)} routes")
        for route_path in admin_cat_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include admin_categories_router: {str(e)}\n{traceback.format_exc()}")

    # Role Delegation API (org_admin and management)
    try:
        from .role_delegation import router as role_delegation_router
        logger.debug("Imported role_delegation_router")
        api_v1_router.include_router(role_delegation_router, prefix="/role-delegation", tags=["Role Delegation"])
        role_delegation_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /role-delegation{route.path}" for route in role_delegation_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered role_delegation endpoints: {len(role_delegation_routes)} routes")
        for route_path in role_delegation_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include role_delegation_router: {str(e)}\n{traceback.format_exc()}")

    # Customer Analytics API
    try:
        from .customer_analytics import router as customer_analytics_router
        logger.debug("Imported customer_analytics_router")
        api_v1_router.include_router(customer_analytics_router, prefix="/customer-analytics", tags=["Customer Analytics"])
        customer_analytics_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /customer-analytics{route.path}" for route in customer_analytics_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered customer_analytics endpoints: {len(customer_analytics_routes)} routes")
        for route_path in customer_analytics_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include customer_analytics_router: {str(e)}\n{traceback.format_exc()}")

    # Management Reports API
    try:
        from .management_reports import router as management_reports_router
        logger.debug("Imported management_reports_router")
        api_v1_router.include_router(management_reports_router, prefix="/management-reports", tags=["Management Reports"])
        management_reports_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /management-reports{route.path}" for route in management_reports_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered management_reports endpoints: {len(management_reports_routes)} routes")
        for route_path in management_reports_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include management_reports_router: {str(e)}\n{traceback.format_exc()}")

    # Notifications API
    try:
        from .notifications import router as notifications_router
        logger.debug("Imported notifications_router")
        api_v1_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
        notifications_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /notifications{route.path}" for route in notifications_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered notifications endpoints: {len(notifications_routes)} routes")
        for route_path in notifications_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include notifications_router: {str(e)}\n{traceback.format_exc()}")

    # Platform API
    try:
        from .platform import router as platform_router
        logger.debug("Imported platform_router")
        api_v1_router.include_router(platform_router, prefix="/platform", tags=["Platform"])
        platform_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /platform{route.path}" for route in platform_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered platform endpoints: {len(platform_routes)} routes")
        for route_path in platform_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include platform_router: {str(e)}\n{traceback.format_exc()}")

    # Settings API
    try:
        from .settings import router as settings_router
        logger.debug("Imported settings_router")
        api_v1_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
        settings_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /settings{route.path}" for route in settings_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered settings endpoints: {len(settings_routes)} routes")
        for route_path in settings_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include settings_router: {str(e)}\n{traceback.format_exc()}")

    # Organization User Management API (NEW 4-role system)
    try:
        from .org_user_management import router as org_user_mgmt_router
        logger.debug("Imported org_user_management_router")
        api_v1_router.include_router(org_user_mgmt_router, prefix="/org", tags=["Organization User Management"])
        org_user_mgmt_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /org{route.path}" for route in org_user_mgmt_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered org_user_management endpoints: {len(org_user_mgmt_routes)} routes")
        for route_path in org_user_mgmt_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include org_user_mgmt_router: {str(e)}\n{traceback.format_exc()}")

    # Reports API (fixed 404 on /reports)
    try:
        from .reports import router as reports_router
        logger.debug("Imported reports_router")
        api_v1_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
        reports_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /reports{route.path}" for route in reports_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered reports endpoints: {len(reports_routes)} routes")
        for route_path in reports_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include reports_router: {str(e)}\n{traceback.format_exc()}")

    # Purchase Order API (fixed 404 on /purchase-orders/next-number)
    try:
        from .vouchers.purchase_order import router as purchase_order_router
        logger.debug("Imported purchase_order_router")
        api_v1_router.include_router(purchase_order_router, tags=["purchase-orders"])
        purchase_order_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in purchase_order_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered purchase_order endpoints: {len(purchase_order_routes)} routes")
        for route_path in purchase_order_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include purchase_order_router: {str(e)}\n{traceback.format_exc()}")

    # GST Search API (fixed 404 on /gst/search/{gst_number})
    try:
        from .gst_search import router as gst_search_router
        logger.debug("Imported gst_search_router")
        api_v1_router.include_router(gst_search_router, prefix="/gst", tags=["GST Search"])
        gst_search_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /gst{route.path}" for route in gst_search_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered gst_search endpoints: {len(gst_search_routes)} routes")
        for route_path in gst_search_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include gst_search_router: {str(e)}\n{traceback.format_exc()}")

    # ERP API (fixed 404 on /erp/bank-accounts)
    try:
        from .erp import router as erp_router
        logger.debug("Imported erp_router")
        api_v1_router.include_router(erp_router, prefix="/erp", tags=["ERP"])
        erp_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /erp{route.path}" for route in erp_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered erp endpoints: {len(erp_routes)} routes")
        for route_path in erp_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include erp_router: {str(e)}\n{traceback.format_exc()}")

    # PDF Extraction API (fixed 404 on /pdf-extraction)
    try:
        from .pdf_extraction import router as pdf_extraction_router
        logger.debug("Imported pdf_extraction_router")
        api_v1_router.include_router(pdf_extraction_router, prefix="/pdf-extraction", tags=["PDF Extraction"])
        pdf_extraction_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} /pdf-extraction{route.path}" for route in pdf_extraction_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered pdf_extraction endpoints: {len(pdf_extraction_routes)} routes")
        for route_path in pdf_extraction_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include pdf_extraction_router: {str(e)}\n{traceback.format_exc()}")

    # Add quotation router (new inclusion to fix 404 on /quotations)
    try:
        from .vouchers.quotation import router as quotation_router
        logger.debug("Imported quotation_router")
        api_v1_router.include_router(quotation_router, tags=["quotations"])
        quotation_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in quotation_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered quotation endpoints: {len(quotation_routes)} routes")
        for route_path in quotation_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include quotation_router: {str(e)}\n{traceback.format_exc()}")

    # Sales Orders API unified at /api/v1/vouchers/sales-orders (removed duplicate top-level endpoint)

    # Items API for rate/description memory at /api/v1/items
    try:
        from .items import router as items_router
        logger.debug("Imported items_router")
        api_v1_router.include_router(items_router, tags=["items"])
        items_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in items_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered items endpoints: {len(items_routes)} routes")
        for route_path in items_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include items_router: {str(e)}\n{traceback.format_exc()}")

    # Demo OTP Users API at /api/v1/demo
    try:
        from .demo import router as demo_router
        logger.debug("Imported demo_router")
        api_v1_router.include_router(demo_router, tags=["Demo"])
        demo_routes = [f"{', '.join(sorted(route.methods)) if route.methods else 'ALL'} {route.path}" for route in demo_router.routes if isinstance(route, APIRoute)]
        logger.debug(f"Registered demo endpoints: {len(demo_routes)} routes")
        for route_path in demo_routes:
            logger.debug(f"  {route_path}")
    except Exception as e:
        logger.error(f"Failed to import/include demo_router: {str(e)}\n{traceback.format_exc()}")


register_subrouters()
