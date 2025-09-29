# app/services/pdf_generation_service.py

"""
Comprehensive PDF generation service for vouchers with Indian formatting
"""

import os
import uuid
from datetime import datetime, date  # Added date import for type checking
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
import pdfkit  # Replaced xhtml2pdf with pdfkit
from io import BytesIO
from num2words import num2words
from sqlalchemy.ext.asyncio import AsyncSession  # Changed to AsyncSession
from sqlalchemy import select  # Added for select
from app.models import Company, User, Vendor  # Added Vendor import
from app.models.erp_models import BankAccount  # Added for bank details in PDFs
import logging
import base64
import re  # Added for sanitizing filenames

# Import settings for dynamic wkhtmltopdf path
from app.core.config import settings

# Import voucher PDF configs for titles
from app.utils.pdf_utils import VOUCHER_PDF_CONFIGS, get_voucher_pdf_config  # Corrected import to pdf_utils

logger = logging.getLogger(__name__)

class IndianNumberFormatter:
    """Utility class for Indian number formatting and conversion"""
    
    @staticmethod
    def amount_to_words(amount: float) -> str:
        """Convert amount to Indian words format"""
        try:
            # Convert to integer for words (paise handling)
            rupees = int(amount)
            paise = int((amount - rupees) * 100)
            
            if rupees == 0 and paise == 0:
                return "Zero Rupees Only"
            
            rupees_words = ""
            if rupees > 0:
                rupees_words = num2words(rupees, lang='en_IN')
                rupees_words = f"{rupees_words.title()} Rupee{'s' if rupees != 1 else ''}"
            
            paise_words = ""
            if paise > 0:
                paise_words = num2words(paise, lang='en_IN')
                paise_words = f"{paise_words.title()} Paise"
            
            if rupees_words and paise_words:
                return f"{rupees_words} and {paise_words} Only"
            elif rupees_words:
                return f"{rupees_words} Only"
            else:
                return f"{paise_words} Only"
                
        except Exception as e:
            logger.error(f"Error converting amount to words: {e}")
            return f"Amount: {amount:.2f}"
    
    @staticmethod
    def format_indian_currency(amount: float, show_symbol: bool = True) -> str:
        """Format amount in Indian currency format format (₹1,23,456.78)"""
        try:
            # Handle negative amounts
            is_negative = amount < 0
            amount = abs(amount)
            
            # Split into rupees and paise
            rupees = int(amount)
            paise = int((amount - rupees) * 100)
            
            # Convert to string and add commas in Indian format
            rupees_str = str(rupees)
            if len(rupees_str) > 3:
                # Last 3 digits
                last_three = rupees_str[-3:]
                # Remaining digits in groups of 2
                remaining = rupees_str[:-3]
                
                # Add commas every 2 digits from right
                formatted_remaining = ""
                for i, digit in enumerate(reversed(remaining)):
                    if i > 0 and i % 2 == 0:
                        formatted_remaining = "," + formatted_remaining
                    formatted_remaining = digit + formatted_remaining
                
                formatted_amount = f"{formatted_remaining},{last_three}"
            else:
                formatted_amount = rupees_str
            
            # Add paise if non-zero
            if paise > 0:
                formatted_amount += f".{paise:02d}"
            
            # Add currency symbol and negative sign if needed
            result = f"{formatted_amount}"
            if show_symbol:
                result = f"₹ {result}"
            if is_negative:
                result = f"-{result}"
                
            return result
            
        except Exception as e:
            logger.error(f"Error formatting Indian currency: {e}")
            return f"₹ {amount:.2f}"

class TaxCalculator:
    """GST GST calculation utilities"""
    
    @staticmethod
    def calculate_gst(taxable_amount: float, gst_rate: float, 
                     is_interstate: bool = False) -> Dict[str, float]:
        """
        Calculate GST amounts
        For intrastate: CGST + SGST
        For interstate: IGST
        """
        total_gst = (taxable_amount * gst_rate) / 100
        
        if is_interstate:
            return {
                'cgst_rate': 0.0,
                'sgst_rate': 0.0,
                'igst_rate': gst_rate,
                'cgst_amount': 0.0,
                'sgst_amount': 0.0,
                'igst_amount': total_gst,
                'total_gst': total_gst
            }
        else:
            half_rate = gst_rate / 2
            half_amount = total_gst / 2
            return {
                'cgst_rate': half_rate,
                'sgst_rate': half_rate,
                'igst_rate': 0.0,
                'cgst_amount': half_amount,
                'sgst_amount': half_amount,
                'igst_amount': 0.0,
                'total_gst': total_gst
            }

class VoucherPDFGenerator:
    """Main PDF generation service for vouchers"""
    
    def __init__(self):
        self.templates_dir = os.path.join(os.path.dirname(__file__), '../templates/pdf')
        self.static_dir = os.path.join(os.path.dirname(__file__), '../static')
        self.output_dir = './uploads/voucher_pdfs'
        
        # Ensure directories exist
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        # Add custom filters
        self._add_custom_filters()
        
        # pdfkit config using dynamic path from settings (works for Windows local and Linux deploy)
        wkhtmltopdf_path = settings.WKHTMLTOPDF_PATH
        if not os.path.exists(wkhtmltopdf_path):
            raise FileNotFoundError(f"wkhtmltopdf not found at {wkhtmltopdf_path}. Please install it and set WKHTMLTOPDF_PATH in .env.")
        self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    
    def _add_custom_filters(self):
        """Add custom Jinja2 filters"""
        self.jinja_env.filters['amount_to_words'] = IndianNumberFormatter.amount_to_words
        self.jinja_env.filters['format_currency'] = IndianNumberFormatter.format_indian_currency
        self.jinja_env.filters['format_date'] = self._format_date
        self.jinja_env.filters['format_percentage'] = self._format_percentage
    
    def _format_date(self, date_obj, format_str='%d/%m/%Y') -> str:
        """Format date object"""
        if not date_obj:
            return ""
        if isinstance(date_obj, str):
            return date_obj
        if isinstance(date_obj, datetime):
            return date_obj.strftime(format_str)
        if isinstance(date_obj, date):
            return date_obj.strftime(format_str)
        return str(date_obj)
    
    def _format_percentage(self, value: float) -> str:
        """Format percentage value"""
        return f"{value:.2f}"
    
    async def _get_company_branding(self, db: AsyncSession, organization_id: int) -> Dict[str, Any]:  # Changed to async and AsyncSession
        """Get company branding information"""
        try:
            stmt = select(Company).filter(  # Changed to select
                Company.organization_id == organization_id
            )
            result = await db.execute(stmt)  # Await execute
            company = result.scalars().first()  # scalars().first()
            
            if company:
                logo_url = None
                logo_path = os.path.join('uploads/company_logos', f"{organization_id}.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = base64.b64encode(f.read()).decode('utf-8')
                    logo_url = f"data:image/png;base64,{logo_data}"
                
                state_code = company.state_code
                if not state_code and company.gst_number:
                    state_code = company.gst_number[:2]  # Fallback to GST prefix
                
                logger.info(f"Company Company GST: {company.gst_number}, state_code (final): {state_code}")
                
                # Get bank account details (default bank account or first active one)
                bank_details = None
                stmt_bank = select(BankAccount).filter(  # Changed to select
                    BankAccount.organization_id == organization_id,
                    BankAccount.is_active == True
                ).filter(
                    (BankAccount.is_default == True)  # Prefer default account
                )
                result_bank = await db.execute(stmt_bank)  # Await
                bank_account = result_bank.scalars().first()
                
                # If no default, get any active bank account
                if not bank_account:
                    stmt_any = select(BankAccount).filter(
                        BankAccount.organization_id == organization_id,
                        BankAccount.is_active == True
                    )
                    result_any = await db.execute(stmt_any)  # Await
                    bank_account = result_any.scalars().first()
                
                if bank_account:
                    bank_details = {
                        'holder_name': company.name,  # Use company name as account holder
                        'bank_name': bank_account.bank_name,
                        'account_number': bank_account.account_number,
                        'branch': bank_account.branch_name or '',
                        'ifsc': bank_account.ifsc_code or ''
                    }
                
                return {
                    'name': company.name,
                    'address1': company.address1,
                    'address2': company.address2 or '',
                    'city': company.city,
                    'state': company.state,
                    'pin_code': company.pin_code,
                    'state_code': state_code,
                    'gst_number': company.gst_number or '',
                    'pan_number': company.pan_number or '',
                    'contact_number': company.contact_number,
                    'email': company.email or '',
                    'website': company.website or '',
                    'logo_url': logo_url,
                    'bank_details': bank_details
                }
            else:
                # Fallback company data
                return {
                    'name': 'Your Company Name',
                    'address1': 'Company Address Line 1',
                    'address2': 'Company Address Line 2',
                    'city': 'City',
                    'state': 'State',
                    'pin_code': '123456',
                    'state_code': '12',
                    'gst_number': '',
                    'pan_number': '',
                    'contact_number': '+91-1234567890',
                    'email': 'contact@company.com',
                    'website': 'www.company.com',
                    'logo_url': None,
                    'bank_details': None
                }
                
        except Exception as e:
            logger.error(f"Error getting company branding: {e}")
            return {
                'name': 'Your Company Name',
                'address1': 'Company Address',
                'city': 'City', 'state': 'State', 'pin_code': '123456',
                'contact_number': '+91-1234567890',
                'logo_url': None,
                'bank_details': None
            }
    
    async def _prepare_voucher_data(self, voucher_type: str, voucher_data: Dict[str, Any], 
                                  db: AsyncSession, organization_id: int) -> Dict[str, Any]:  # Changed db to AsyncSession
        """Prepare voucher data for template rendering"""
        
        # Get company branding - await since now async
        company = await self._get_company_branding(db, organization_id)
        
        # Get vendor/party details and determine interstate
        is_interstate = False
        vendor = voucher_data.get('vendor')
        customer = voucher_data.get('customer')
        employee = voucher_data.get('employee')
        party = vendor or customer or employee
        
        # Merge address lines for party if it exists
        if party and isinstance(party, dict):
            address1 = party.get('address1', '') or party.get('address', '') or ''
            address2 = party.get('address2', '') or ''
            
            # Merge address lines with comma separation if both exist
            merged_address = address1
            if address1 and address2:
                merged_address = f"{address1}, {address2}"
            elif address2:  # Only address2 exists
                merged_address = address2
            
            # Update party data with merged address
            party = dict(party)  # Create a copy to avoid modifying original
            party['address'] = merged_address
            
            # Update the specific party type in voucher_data for template
            if vendor:
                voucher_data = dict(voucher_data)
                voucher_data['vendor'] = party
            elif customer:
                voucher_data = dict(voucher_data)
                voucher_data['customer'] = party
            elif employee:
                voucher_data = dict(voucher_data)
                voucher_data['employee'] = party
        
        # Merge address lines for shipping address if it exists
        shipping_address = voucher_data.get('shipping_address')
        if shipping_address and isinstance(shipping_address, dict):
            shipping_addr1 = shipping_address.get('address1', '') or shipping_address.get('address', '') or ''
            shipping_addr2 = shipping_address.get('address2', '') or ''
            
            # Merge shipping address lines
            merged_shipping_address = shipping_addr1
            if shipping_addr1 and shipping_addr2:
                merged_shipping_address = f"{shipping_addr1}, {shipping_addr2}"
            elif shipping_addr2:  # Only address2 exists
                merged_shipping_address = shipping_addr2
            
            # Update shipping address data
            voucher_data = dict(voucher_data)
            shipping_address = dict(shipping_address)
            shipping_address['address'] = merged_shipping_address
            voucher_data['shipping_address'] = shipping_address
        
        party_state_code = None
        if party and company['state_code']:
            party_state_code = party.get('state_code')
            logger.info(f"Party initial state_code: {party_state_code}, gst_number: {party.get('gst_number')}")
            if not party_state_code and party.get('gst_number'):
                party_state_code = party['gst_number'][:2]
            if party_state_code:
                is_interstate = company['state_code'] != party_state_code
        
        logger.info(f"Company state_code: {company['state_code']}, Party state_code: {party_state_code if party_state_code else 'None'}, is_interstate: {is_interstate}")
        
        # Calculate totals and taxes for items
        items = voucher_data.get('items', [])
        processed_items = []
        
        subtotal = 0.0
        total_discount = voucher_data.get('total_discount', 0.0)
        total_taxable = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_quantity = 0.0  # Added for totals row
        
        if items:
            for item in items:
                # Calculate item totals
                quantity = float(item.get('quantity', 0))
                unit_price = float(item.get('unit_price', 0) or 0)  # Handle None
                discount_percentage = float(item.get('discount_percentage', 0) or 0)
                discount_amount = float(item.get('discount_amount', 0) or 0)
                gst_rate = float(item.get('gst_rate', 0) or 0)
                description = item.get('description', '')
                
                item_subtotal = quantity * unit_price
                if discount_percentage > 0:
                  discount_amount = item_subtotal * (discount_percentage / 100)
                taxable_amount = item_subtotal - discount_amount
                
                # Calculate GST with updated interstate check
                gst_calc = TaxCalculator.calculate_gst(taxable_amount, gst_rate, is_interstate)
                
                item_total = taxable_amount + gst_calc['total_gst']
                
                processed_item = {
                    **item,  # Unpack original item dict to include all its fields
                    'subtotal': item_subtotal,
                    'discount_percentage': discount_percentage,
                    'discount_amount': discount_amount,
                    'taxable_amount': taxable_amount,
                    'gst_rate': gst_rate,
                    'cgst_rate': gst_calc['cgst_rate'],
                    'sgst_rate': gst_calc['sgst_rate'],
                    'igst_rate': gst_calc['igst_rate'],
                    'cgst_amount': gst_calc['cgst_amount'],
                    'sgst_amount': gst_calc['sgst_amount'],
                    'igst_amount': gst_calc['igst_amount'],
                    'total_amount': item_total,
                    'description': description
                }
                
                processed_items.append(processed_item)
                
                subtotal += item_subtotal
                total_taxable += taxable_amount
                total_cgst += gst_calc['cgst_amount']
                total_sgst += gst_calc['sgst_amount']
                total_igst += gst_calc['igst_amount']
                total_quantity += quantity  # Accumulate quantity
            
            grand_total = subtotal - total_discount + total_cgst + total_sgst + total_igst
            
            # Calculate round off
            decimal_part = grand_total - int(grand_total)
            round_off = 0.0
            if decimal_part < 0.5:
                round_off = -decimal_part
            else:
                round_off = 1 - decimal_part
            grand_total += round_off
        else:
            # For non-item vouchers like payments
            subtotal = float(voucher_data.get('total_amount', 0.0))
            total_discount = float(voucher_data.get('total_discount', 0.0))
            total_taxable = subtotal - total_discount
            total_cgst = 0.0
            total_sgst = 0.0
            total_igst = 0.0
            round_off = float(voucher_data.get('round_off', 0.0))
            grand_total = total_taxable + round_off  # No taxes for financial vouchers
        
        # Prepare template data
        template_data = {
            'company': company,
            'voucher': voucher_data,
            'items': processed_items,
            'subtotal': subtotal,
            'total_discount': total_discount,
            'total_taxable': total_taxable,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
            'total_igst': total_igst,
            'round_off': round_off,
            'grand_total': grand_total,
            'total_quantity': total_quantity,  # Added for items table totals
            'is_interstate': is_interstate,
            'line_discount_enabled': voucher_data.get('line_discount_type') is not None,  # Flag for line discount
            'total_discount_enabled': voucher_data.get('total_discount_type') is not None,  # Flag for total discount
            'amount_in_words': IndianNumberFormatter.amount_to_words(grand_total),
            'generated_at': datetime.now(),
            'page_count': 1,  # Will be updated for multi-page
            'party': party
        }
        
        return template_data
    
    async def generate_voucher_pdf(self, voucher_type: str, voucher_data: Dict[str, Any],
                                 db: AsyncSession, organization_id: int, 
                                 current_user: User) -> str:  # Changed to async and AsyncSession
        """
        Generate PDF for any voucher type
        
        Args:
            voucher_type: Type of voucher (purchase, sales, pre_sales)
            voucher_data: Voucher data including items
            db: Database session
            organization_id: Organization ID for tenant isolation
            current_user: Current user for audit logging
            
        Returns:
            File path of generated PDF
        """
        try:
            # Prepare data for template
            template_data = await self._prepare_voucher_data(voucher_type, voucher_data, db, organization_id)  # Await since now async
            
            # Get template for voucher type
            if voucher_type in ['purchase', 'purchase-vouchers']:
                template_name = 'purchase_voucher.html'
            elif voucher_type == 'purchase-orders':
                template_name = 'purchase_order.html'
            elif voucher_type == 'sales':
                template_name = 'sales_voucher.html'
            elif voucher_type == 'delivery-challan':
                template_name = 'delivery_challan.html'
            elif voucher_type in ['quotation', 'sales_order', 'sales-orders', 'proforma_invoice']:
                template_name = 'presales_voucher.html'
            elif voucher_type == 'payment-vouchers':
                template_name = 'payment_voucher.html'
            elif voucher_type == 'receipt-vouchers':
                template_name = 'receipt_voucher.html'
            else:
                template_name = f"{voucher_type}_voucher.html"
            
            try:
                template = self.jinja_env.get_template(template_name)
            except Exception:
                # Fallback to base template
                template = self.jinja_env.get_template('base_voucher.html')
                logger.warning(f"Template {template_name} not found at at {template.filename}, using base template")
            
            # Render HTML
            html_content = template.render(**template_data)
            
            # Generate unique filename
            voucher_number = voucher_data.get('voucher_number', 'unknown')
            voucher_number = re.sub(r'[^\w\-]', '_', voucher_number)  # Sanitize voucher_number
            filename = f"{voucher_type}_{voucher_number}_{uuid.uuid4().hex[:8]}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Convert to PDF using pdfkit (replaced pisa)
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': 'UTF-8',
                'disable-smart-shrinking': '',
                'zoom': '1.0',
                'dpi': '96'
            }
            pdfkit.from_string(html_content, filepath, configuration=self.pdfkit_config, options=pdf_options)
            
            logger.info(f"PDF generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF for {voucher_type}: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    async def generate_purchase_voucher_pdf(self, voucher_data: Dict[str, Any],
                                          db: AsyncSession, organization_id: int,
                                          current_user: User) -> str:  # Changed to async
        """Generate Purchase Voucher PDF"""
        return await self.generate_voucher_pdf('purchase', voucher_data, db, organization_id, current_user)  # Await
    
    async def generate_sales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                       db: AsyncSession, organization_id: int,
                                       current_user: User) -> str:  # Changed to async
        """Generate Sales Voucher PDF"""
        return await self.generate_voucher_pdf('sales', voucher_data, db, organization_id, current_user)  # Await
    
    async def generate_presales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                          db: AsyncSession, organization_id: int,
                                          current_user: User) -> str:  # Changed to async
        """Generate Pre-Sales Voucher PDF"""
        return await self.generate_voucher_pdf('presales', voucher_data, db, organization_id, current_user)  # Await

# Create singleton instance
pdf_generator = VoucherPDFGenerator()