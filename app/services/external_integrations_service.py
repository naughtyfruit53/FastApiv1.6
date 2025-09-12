# app/services/external_integrations_service.py
"""
Enhanced External Integration Service for Payment Gateways, ERP Connectors, and Third-party Analytics
"""

import httpx
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
import asyncio

from app.models.integration_models import ExternalIntegration, IntegrationSyncJob, IntegrationLog
from app.models.master_data_models import PaymentTermsExtended
from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """Service for payment gateway integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30  # seconds
    
    async def process_payment(self, integration_id: int, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through configured gateway"""
        try:
            integration = self.db.query(ExternalIntegration).filter(
                ExternalIntegration.id == integration_id,
                ExternalIntegration.integration_type == "payment"
            ).first()
            
            if not integration:
                raise ValueError("Payment integration not found")
            
            if integration.status != "active":
                raise ValueError("Payment integration is not active")
            
            # Decrypt authentication config
            auth_config = self._decrypt_auth_config(integration.auth_config)
            
            # Route to appropriate payment processor
            if integration.provider.lower() == "stripe":
                return await self._process_stripe_payment(auth_config, payment_data)
            elif integration.provider.lower() == "razorpay":
                return await self._process_razorpay_payment(auth_config, payment_data)
            elif integration.provider.lower() == "paypal":
                return await self._process_paypal_payment(auth_config, payment_data)
            elif integration.provider.lower() == "square":
                return await self._process_square_payment(auth_config, payment_data)
            else:
                raise ValueError(f"Unsupported payment provider: {integration.provider}")
        
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            await self._log_integration_error(integration_id, "payment_processing", str(e))
            raise
    
    async def _process_stripe_payment(self, auth_config: Dict, payment_data: Dict) -> Dict[str, Any]:
        """Process Stripe payment"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {auth_config['secret_key']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            stripe_data = {
                "amount": int(payment_data["amount"] * 100),  # Convert to cents
                "currency": payment_data.get("currency", "usd").lower(),
                "source": payment_data["payment_method"],
                "description": payment_data.get("description", "Payment"),
                "metadata": payment_data.get("metadata", {})
            }
            
            response = await client.post(
                "https://api.stripe.com/v1/charges",
                headers=headers,
                data=stripe_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "transaction_id": result["id"],
                    "amount": result["amount"] / 100,
                    "currency": result["currency"],
                    "status": result["status"],
                    "created": result["created"],
                    "raw_response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("message", "Payment failed"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "raw_response": error_data
                }
    
    async def _process_razorpay_payment(self, auth_config: Dict, payment_data: Dict) -> Dict[str, Any]:
        """Process Razorpay payment"""
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(auth_config["key_id"], auth_config["key_secret"])
            headers = {"Content-Type": "application/json"}
            
            razorpay_data = {
                "amount": int(payment_data["amount"] * 100),  # Convert to paise
                "currency": payment_data.get("currency", "INR"),
                "receipt": payment_data.get("receipt", f"receipt_{datetime.now().timestamp()}"),
                "notes": payment_data.get("metadata", {})
            }
            
            response = await client.post(
                "https://api.razorpay.com/v1/orders",
                headers=headers,
                json=razorpay_data,
                auth=auth,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "order_id": result["id"],
                    "amount": result["amount"] / 100,
                    "currency": result["currency"],
                    "status": result["status"],
                    "created_at": result["created_at"],
                    "raw_response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("error", {}).get("description", "Payment failed"),
                    "error_code": error_data.get("error", {}).get("code"),
                    "raw_response": error_data
                }
    
    async def _process_paypal_payment(self, auth_config: Dict, payment_data: Dict) -> Dict[str, Any]:
        """Process PayPal payment"""
        # Get access token first
        token = await self._get_paypal_access_token(auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            paypal_data = {
                "intent": "CAPTURE",
                "purchase_units": [{
                    "amount": {
                        "currency_code": payment_data.get("currency", "USD"),
                        "value": str(payment_data["amount"])
                    },
                    "description": payment_data.get("description", "Payment")
                }]
            }
            
            base_url = "https://api.sandbox.paypal.com" if auth_config.get("sandbox", True) else "https://api.paypal.com"
            
            response = await client.post(
                f"{base_url}/v2/checkout/orders",
                headers=headers,
                json=paypal_data,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "order_id": result["id"],
                    "status": result["status"],
                    "approval_url": next(
                        (link["href"] for link in result["links"] if link["rel"] == "approve"), 
                        None
                    ),
                    "raw_response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("message", "Payment failed"),
                    "raw_response": error_data
                }
    
    async def _process_square_payment(self, auth_config: Dict, payment_data: Dict) -> Dict[str, Any]:
        """Process Square payment"""
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {auth_config['access_token']}",
                "Content-Type": "application/json",
                "Square-Version": "2023-10-18"
            }
            
            square_data = {
                "source_id": payment_data["payment_method"],
                "amount_money": {
                    "amount": int(payment_data["amount"] * 100),  # Convert to cents
                    "currency": payment_data.get("currency", "USD")
                },
                "idempotency_key": payment_data.get("idempotency_key", str(datetime.now().timestamp()))
            }
            
            base_url = "https://connect.squareupsandbox.com" if auth_config.get("sandbox", True) else "https://connect.squareup.com"
            
            response = await client.post(
                f"{base_url}/v2/payments",
                headers=headers,
                json=square_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                payment = result["payment"]
                return {
                    "success": True,
                    "payment_id": payment["id"],
                    "amount": payment["amount_money"]["amount"] / 100,
                    "currency": payment["amount_money"]["currency"],
                    "status": payment["status"],
                    "created_at": payment["created_at"],
                    "raw_response": result
                }
            else:
                error_data = response.json()
                return {
                    "success": False,
                    "error": error_data.get("errors", [{}])[0].get("detail", "Payment failed"),
                    "raw_response": error_data
                }
    
    async def _get_paypal_access_token(self, auth_config: Dict) -> str:
        """Get PayPal access token"""
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(auth_config["client_id"], auth_config["client_secret"])
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"grant_type": "client_credentials"}
            
            base_url = "https://api.sandbox.paypal.com" if auth_config.get("sandbox", True) else "https://api.paypal.com"
            
            response = await client.post(
                f"{base_url}/v1/oauth2/token",
                headers=headers,
                data=data,
                auth=auth,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["access_token"]
            else:
                raise Exception("Failed to get PayPal access token")
    
    def _decrypt_auth_config(self, encrypted_config: str) -> Dict[str, Any]:
        """Decrypt authentication configuration"""
        try:
            # In production, use proper encryption key management
            key = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_config.encode())
            return json.loads(decrypted.decode())
        except Exception:
            # Fallback to plain text for development
            return json.loads(encrypted_config) if isinstance(encrypted_config, str) else encrypted_config
    
    async def _log_integration_error(self, integration_id: int, operation: str, error_message: str):
        """Log integration error"""
        log_entry = IntegrationLog(
            integration_id=integration_id,
            log_level="error",
            operation=operation,
            message=error_message,
            timestamp=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()


class ERPConnectorService:
    """Service for ERP system integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.timeout = 60  # seconds for ERP operations
    
    async def sync_chart_of_accounts(self, integration_id: int) -> Dict[str, Any]:
        """Sync chart of accounts from ERP system"""
        try:
            integration = self.db.query(ExternalIntegration).filter(
                ExternalIntegration.id == integration_id,
                ExternalIntegration.integration_type == "erp"
            ).first()
            
            if not integration:
                raise ValueError("ERP integration not found")
            
            if integration.provider.lower() == "quickbooks":
                return await self._sync_quickbooks_accounts(integration)
            elif integration.provider.lower() == "sap":
                return await self._sync_sap_accounts(integration)
            elif integration.provider.lower() == "oracle":
                return await self._sync_oracle_accounts(integration)
            elif integration.provider.lower() == "tally":
                return await self._sync_tally_accounts(integration)
            else:
                raise ValueError(f"Unsupported ERP provider: {integration.provider}")
        
        except Exception as e:
            logger.error(f"ERP sync failed: {e}")
            await self._log_integration_error(integration_id, "chart_of_accounts_sync", str(e))
            raise
    
    async def _sync_quickbooks_accounts(self, integration: ExternalIntegration) -> Dict[str, Any]:
        """Sync QuickBooks chart of accounts"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {auth_config['access_token']}",
                "Accept": "application/json"
            }
            
            # QuickBooks API call
            company_id = auth_config['company_id']
            response = await client.get(
                f"{integration.endpoint_url}/v3/company/{company_id}/accounts",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("QueryResponse", {}).get("Account", [])
                
                # Process and transform accounts
                processed_accounts = []
                for account in accounts:
                    processed_account = {
                        "external_id": account["Id"],
                        "name": account["Name"],
                        "account_type": self._map_quickbooks_account_type(account.get("AccountType")),
                        "account_code": account.get("AcctNum", account["Id"]),
                        "description": account.get("Description"),
                        "is_active": account.get("Active", True),
                        "parent_id": account.get("ParentRef", {}).get("value"),
                        "current_balance": float(account.get("CurrentBalance", 0))
                    }
                    processed_accounts.append(processed_account)
                
                return {
                    "success": True,
                    "accounts_count": len(processed_accounts),
                    "accounts": processed_accounts
                }
            else:
                raise Exception(f"QuickBooks API error: {response.status_code}")
    
    async def _sync_sap_accounts(self, integration: ExternalIntegration) -> Dict[str, Any]:
        """Sync SAP chart of accounts"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Basic {auth_config['basic_auth']}",
                "Content-Type": "application/json"
            }
            
            # SAP OData API call
            response = await client.get(
                f"{integration.endpoint_url}/sap/opu/odata/sap/FCO_CI_UNIVERSAL_JOURNAL_ENTRY_SRV/ChartOfAccounts",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("d", {}).get("results", [])
                
                processed_accounts = []
                for account in accounts:
                    processed_account = {
                        "external_id": account["ChartOfAccounts"],
                        "name": account["ChartOfAccountsName"],
                        "account_type": self._map_sap_account_type(account.get("AccountType")),
                        "account_code": account["ChartOfAccounts"],
                        "description": account.get("ChartOfAccountsName"),
                        "is_active": True,
                        "company_code": account.get("CompanyCode")
                    }
                    processed_accounts.append(processed_account)
                
                return {
                    "success": True,
                    "accounts_count": len(processed_accounts),
                    "accounts": processed_accounts
                }
            else:
                raise Exception(f"SAP API error: {response.status_code}")
    
    async def _sync_oracle_accounts(self, integration: ExternalIntegration) -> Dict[str, Any]:
        """Sync Oracle ERP chart of accounts"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {auth_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            # Oracle REST API call
            response = await client.get(
                f"{integration.endpoint_url}/fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("items", [])
                
                processed_accounts = []
                for account in accounts:
                    processed_account = {
                        "external_id": account["AccountId"],
                        "name": account["AccountName"],
                        "account_type": self._map_oracle_account_type(account.get("AccountType")),
                        "account_code": account["AccountNumber"],
                        "description": account.get("Description"),
                        "is_active": account.get("EnabledFlag", "Y") == "Y",
                        "parent_id": account.get("ParentAccountId")
                    }
                    processed_accounts.append(processed_account)
                
                return {
                    "success": True,
                    "accounts_count": len(processed_accounts),
                    "accounts": processed_accounts
                }
            else:
                raise Exception(f"Oracle API error: {response.status_code}")
    
    async def _sync_tally_accounts(self, integration: ExternalIntegration) -> Dict[str, Any]:
        """Sync Tally ERP chart of accounts"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        # Tally XML request
        xml_request = """
        <ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Export Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <EXPORTDATA>
                    <REQUESTDESC>
                        <REPORTNAME>List of Accounts</REPORTNAME>
                        <STATICVARIABLES>
                            <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
                        </STATICVARIABLES>
                    </REQUESTDESC>
                </EXPORTDATA>
            </BODY>
        </ENVELOPE>
        """
        
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/xml"}
            
            response = await client.post(
                f"{integration.endpoint_url}:{auth_config.get('port', 9000)}",
                headers=headers,
                content=xml_request,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                # Parse Tally XML response (simplified)
                # In production, use proper XML parsing
                xml_data = response.text
                
                # Mock processing for demonstration
                processed_accounts = [
                    {
                        "external_id": "TALLY_001",
                        "name": "Cash",
                        "account_type": "cash",
                        "account_code": "CASH",
                        "is_active": True
                    }
                ]
                
                return {
                    "success": True,
                    "accounts_count": len(processed_accounts),
                    "accounts": processed_accounts,
                    "raw_xml": xml_data
                }
            else:
                raise Exception(f"Tally API error: {response.status_code}")
    
    def _map_quickbooks_account_type(self, qb_type: str) -> str:
        """Map QuickBooks account type to internal type"""
        mapping = {
            "Asset": "asset",
            "Liability": "liability",
            "Equity": "equity",
            "Income": "income",
            "Expense": "expense",
            "Bank": "bank",
            "Other Current Asset": "asset",
            "Fixed Asset": "asset",
            "Other Asset": "asset",
            "Accounts Receivable": "asset",
            "Accounts Payable": "liability",
            "Credit Card": "liability"
        }
        return mapping.get(qb_type, "asset")
    
    def _map_sap_account_type(self, sap_type: str) -> str:
        """Map SAP account type to internal type"""
        # SAP has different account type classification
        mapping = {
            "A": "asset",
            "L": "liability",
            "E": "equity",
            "R": "income",
            "X": "expense"
        }
        return mapping.get(sap_type, "asset")
    
    def _map_oracle_account_type(self, oracle_type: str) -> str:
        """Map Oracle account type to internal type"""
        mapping = {
            "ASSET": "asset",
            "LIABILITY": "liability",
            "EQUITY": "equity",
            "REVENUE": "income",
            "EXPENSE": "expense"
        }
        return mapping.get(oracle_type, "asset")
    
    def _decrypt_auth_config(self, encrypted_config: str) -> Dict[str, Any]:
        """Decrypt authentication configuration"""
        try:
            # In production, use proper encryption key management
            key = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_config.encode())
            return json.loads(decrypted.decode())
        except Exception:
            # Fallback to plain text for development
            return json.loads(encrypted_config) if isinstance(encrypted_config, str) else encrypted_config
    
    async def _log_integration_error(self, integration_id: int, operation: str, error_message: str):
        """Log integration error"""
        log_entry = IntegrationLog(
            integration_id=integration_id,
            log_level="error",
            operation=operation,
            message=error_message,
            timestamp=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()


class ThirdPartyAnalyticsService:
    """Service for third-party analytics integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.timeout = 30
    
    async def push_analytics_data(self, integration_id: int, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Push analytics data to third-party service"""
        try:
            integration = self.db.query(ExternalIntegration).filter(
                ExternalIntegration.id == integration_id,
                ExternalIntegration.integration_type == "analytics"
            ).first()
            
            if not integration:
                raise ValueError("Analytics integration not found")
            
            if integration.provider.lower() == "google_analytics":
                return await self._push_to_google_analytics(integration, analytics_data)
            elif integration.provider.lower() == "mixpanel":
                return await self._push_to_mixpanel(integration, analytics_data)
            elif integration.provider.lower() == "amplitude":
                return await self._push_to_amplitude(integration, analytics_data)
            elif integration.provider.lower() == "segment":
                return await self._push_to_segment(integration, analytics_data)
            else:
                raise ValueError(f"Unsupported analytics provider: {integration.provider}")
        
        except Exception as e:
            logger.error(f"Analytics push failed: {e}")
            await self._log_integration_error(integration_id, "analytics_push", str(e))
            raise
    
    async def _push_to_google_analytics(self, integration: ExternalIntegration, data: Dict) -> Dict[str, Any]:
        """Push data to Google Analytics"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            
            # Google Analytics 4 Measurement Protocol
            payload = {
                "client_id": data.get("client_id", "anonymous"),
                "events": [{
                    "name": data["event_name"],
                    "parameters": data.get("parameters", {})
                }]
            }
            
            response = await client.post(
                f"https://www.google-analytics.com/mp/collect?measurement_id={auth_config['measurement_id']}&api_secret={auth_config['api_secret']}",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            return {
                "success": response.status_code == 204,
                "status_code": response.status_code
            }
    
    async def _push_to_mixpanel(self, integration: ExternalIntegration, data: Dict) -> Dict[str, Any]:
        """Push data to Mixpanel"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            payload = {
                "event": data["event_name"],
                "properties": {
                    "token": auth_config["project_token"],
                    "distinct_id": data.get("user_id", "anonymous"),
                    **data.get("properties", {})
                }
            }
            
            encoded_data = base64.b64encode(json.dumps(payload).encode()).decode()
            
            response = await client.post(
                "https://api.mixpanel.com/track/",
                data={"data": encoded_data},
                timeout=self.timeout
            )
            
            return {
                "success": response.status_code == 200 and response.text == "1",
                "response": response.text
            }
    
    async def _push_to_amplitude(self, integration: ExternalIntegration, data: Dict) -> Dict[str, Any]:
        """Push data to Amplitude"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {auth_config['api_key']}"
            }
            
            payload = {
                "api_key": auth_config["api_key"],
                "events": [{
                    "user_id": data.get("user_id", "anonymous"),
                    "event_type": data["event_name"],
                    "event_properties": data.get("properties", {}),
                    "time": int(datetime.now().timestamp() * 1000)
                }]
            }
            
            response = await client.post(
                "https://api2.amplitude.com/2/httpapi",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            result = response.json()
            return {
                "success": result.get("code") == 200,
                "result": result
            }
    
    async def _push_to_segment(self, integration: ExternalIntegration, data: Dict) -> Dict[str, Any]:
        """Push data to Segment"""
        auth_config = self._decrypt_auth_config(integration.auth_config)
        
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(auth_config["write_key"], "")
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "userId": data.get("user_id", "anonymous"),
                "event": data["event_name"],
                "properties": data.get("properties", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            response = await client.post(
                "https://api.segment.io/v1/track",
                headers=headers,
                json=payload,
                auth=auth,
                timeout=self.timeout
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code
            }
    
    def _decrypt_auth_config(self, encrypted_config: str) -> Dict[str, Any]:
        """Decrypt authentication configuration"""
        try:
            # In production, use proper encryption key management
            key = settings.ENCRYPTION_KEY.encode() if hasattr(settings, 'ENCRYPTION_KEY') else Fernet.generate_key()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_config.encode())
            return json.loads(decrypted.decode())
        except Exception:
            # Fallback to plain text for development
            return json.loads(encrypted_config) if isinstance(encrypted_config, str) else encrypted_config
    
    async def _log_integration_error(self, integration_id: int, operation: str, error_message: str):
        """Log integration error"""
        log_entry = IntegrationLog(
            integration_id=integration_id,
            log_level="error",
            operation=operation,
            message=error_message,
            timestamp=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()


class IntegrationOrchestrator:
    """Orchestrator for complex integration workflows"""
    
    def __init__(self, db: Session):
        self.db = db
        self.payment_service = PaymentGatewayService(db)
        self.erp_service = ERPConnectorService(db)
        self.analytics_service = ThirdPartyAnalyticsService(db)
    
    async def execute_integration_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complex integration workflow"""
        try:
            results = {}
            
            for step in workflow_config.get("steps", []):
                step_type = step["type"]
                step_config = step["config"]
                
                if step_type == "payment":
                    result = await self.payment_service.process_payment(
                        step_config["integration_id"], 
                        step_config["payment_data"]
                    )
                elif step_type == "erp_sync":
                    result = await self.erp_service.sync_chart_of_accounts(
                        step_config["integration_id"]
                    )
                elif step_type == "analytics":
                    result = await self.analytics_service.push_analytics_data(
                        step_config["integration_id"],
                        step_config["analytics_data"]
                    )
                else:
                    result = {"success": False, "error": f"Unknown step type: {step_type}"}
                
                results[step.get("name", step_type)] = result
                
                # Stop on failure if configured
                if not result.get("success", False) and step.get("stop_on_failure", False):
                    break
            
            return {
                "success": True,
                "workflow_results": results
            }
        
        except Exception as e:
            logger.error(f"Integration workflow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }