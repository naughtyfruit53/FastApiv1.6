"""
Comprehensive PDF generation service for vouchers with Indian formatting
"""

import os
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader
import pdfkit
from io import BytesIO
from num2words import num2words
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Company, User, Vendor, Organization
from app.models.erp_models import BankAccount
import logging
import base64
import re
import json
import traceback

from app.core.config import settings
from app.utils.pdf_utils import VOUCHER_PDF_CONFIGS, get_voucher_pdf_config

logger = logging.getLogger(__name__)

class IndianNumberFormatter:
    """Utility class for Indian number formatting and conversion"""
    
    @staticmethod
    def amount_to_words(amount: float) -> str:
        """Convert amount to Indian words format"""
        try:
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
        """Format amount in Indian currency format (₹1,23,456.78)"""
        try:
            is_negative = amount < 0
            amount = abs(amount)
            
            rupees = int(amount)
            paise = int((amount - rupees) * 100)
            
            rupees_str = str(rupees)
            if len(rupees_str) > 3:
                last_three = rupees_str[-3:]
                remaining = rupees_str[:-3]
                
                formatted_remaining = ""
                for i, digit in enumerate(reversed(remaining)):
                    if i > 0 and i % 2 == 0:
                        formatted_remaining = "," + formatted_remaining
                    formatted_remaining = digit + formatted_remaining
                
                formatted_amount = f"{formatted_remaining},{last_three}"
            else:
                formatted_amount = rupees_str
            
            if paise > 0:
                formatted_amount += f".{paise:02d}"
            
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
    """GST calculation utilities"""
    
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
        self.output_dir = './Uploads/voucher_pdfs'
        
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        self._add_custom_filters()
        
        # Use configurable path from settings
        wkhtmltopdf_path = settings.WKHTMLTOPDF_PATH
        if os.path.exists(wkhtmltopdf_path):
            self.pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            logger.info(f"wkhtmltopdf found at {wkhtmltopdf_path}")
        else:
            self.pdfkit_config = None
            logger.error(f"wkhtmltopdf not found at {wkhtmltopdf_path}. PDF generation will fail until installed.")
            raise RuntimeError(f"wkhtmltopdf not found at {wkhtmltopdf_path}. Please install wkhtmltopdf to enable PDF generation.")
    
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
    
    async def _get_company_branding(self, db: AsyncSession, organization_id: int) -> Dict[str, Any]:
        """Get company branding information"""
        try:
            stmt = select(Company).filter(
                Company.organization_id == organization_id
            )
            result = await db.execute(stmt)
            company = result.scalars().first()
            
            if company:
                logo_url = None
                logo_path = os.path.join('Uploads/company_logos', f"{organization_id}.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = base64.b64encode(f.read()).decode('utf-8')
                    logo_url = f"data:image/png;base64,{logo_data}"
                
                state_code = company.state_code
                if not state_code and company.gst_number:
                    state_code = company.gst_number[:2]
                
                logger.info(f"Company GST: {company.gst_number}, state_code (final): {state_code}")
                
                bank_details = None
                
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
                                  db: AsyncSession, organization_id: int) -> Dict[str, Any]:
        """Prepare voucher data for template rendering"""
        
        company = await self._get_company_branding(db, organization_id)
        
        stmt_org = select(Organization).where(Organization.id == organization_id)
        result_org = await db.execute(stmt_org)
        org = result_org.scalars().first()
        
        is_interstate = False
        vendor = voucher_data.get('vendor')
        customer = voucher_data.get('customer')
        employee = voucher_data.get('employee')
        party = vendor or customer or employee
        
        if party and isinstance(party, dict):
            address1 = party.get('address1', '') or party.get('address', '') or ''
            address2 = party.get('address2', '') or ''
            
            merged_address = address1
            if address1 and address2:
                merged_address = f"{address1}, {address2}"
            elif address2:
                merged_address = address2
            
            party = dict(party)
            party['address'] = merged_address
            
            if vendor:
                voucher_data = dict(voucher_data)
                voucher_data['vendor'] = party
            elif customer:
                voucher_data = dict(voucher_data)
                voucher_data['customer'] = party
            elif employee:
                voucher_data = dict(voucher_data)
                voucher_data['employee'] = party
        
        shipping_address = voucher_data.get('shipping_address')
        if shipping_address and isinstance(shipping_address, dict):
            shipping_addr1 = shipping_address.get('address1', '') or shipping_address.get('address', '') or ''
            shipping_addr2 = shipping_address.get('address2', '') or ''
            
            merged_shipping_address = shipping_addr1
            if shipping_addr1 and shipping_addr2:
                merged_shipping_address = f"{shipping_addr1}, {shipping_addr2}"
            elif shipping_addr2:
                merged_shipping_address = shipping_addr2
            
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
        
        items = voucher_data.get('items', [])
        processed_items = []
        
        subtotal = 0.0
        total_discount = 0.0
        total_taxable = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        total_quantity = 0.0
        grand_total = 0.0
        round_off = 0.0
        
        if voucher_type == 'grn':
            # For GRN, include only quantity-related fields
            for item in items:
                processed_item = {
                    **item,
                    'product_name': item.get('product_name', item.get('product', {}).get('product_name', '')),
                    'ordered_quantity': float(item.get('ordered_quantity', 0)),
                    'received_quantity': float(item.get('received_quantity', 0)),
                    'accepted_quantity': float(item.get('accepted_quantity', 0)),
                    'rejected_quantity': float(item.get('rejected_quantity', 0)),
                    'unit': item.get('unit', '')
                }
                processed_items.append(processed_item)
                total_quantity += processed_item['ordered_quantity']
        else:
            # Financial vouchers processing
            for item in items:
                quantity = float(item.get('quantity', 0))
                unit_price = float(item.get('unit_price', 0) or 0)
                discount_percentage = float(item.get('discount_percentage', 0) or 0)
                discount_amount = float(item.get('discount_amount', 0) or 0)
                gst_rate = float(item.get('gst_rate', 0) or 0)
                description = item.get('description', '')
                
                item_subtotal = quantity * unit_price
                if discount_percentage > 0:
                    discount_amount = item_subtotal * (discount_percentage / 100)
                taxable_amount = item_subtotal - discount_amount
                
                gst_calc = TaxCalculator.calculate_gst(taxable_amount, gst_rate, is_interstate)
                
                item_total = taxable_amount + gst_calc['total_gst']
                
                processed_item = {
                    **item,
                    'subtotal': item_subtotal,
                    'discount_percentage': discount_percentage,
                    'discount_amount': discount_amount,
                    'gst_rate': gst_rate,
                    'taxable_amount': taxable_amount,
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
                total_quantity += quantity
            
            additional_charges = voucher_data.get('additional_charges', {})
            if isinstance(additional_charges, str):
                try:
                    additional_charges = json.loads(additional_charges)
                except json.JSONDecodeError:
                    additional_charges = {}
                    logger.warning(f"Invalid JSON in additional_charges for voucher {voucher_data.get('id')}")
            if isinstance(additional_charges, dict):
                for name, amount in additional_charges.items():
                    if amount > 0:
                        gst_rate = 18.0
                        item_subtotal = float(amount)
                        discount_amount = 0
                        taxable_amount = item_subtotal - discount_amount
                        
                        gst_calc = TaxCalculator.calculate_gst(taxable_amount, gst_rate, is_interstate)
                        
                        item_total = taxable_amount + gst_calc['total_gst']
                        
                        processed_item = {
                            'product_name': name.capitalize() + ' Charge',
                            'description': '',
                            'hsn_code': '',
                            'quantity': 0,
                            'unit': '',
                            'unit_price': amount,
                            'discount_percentage': 0,
                            'discount_amount': 0,
                            'gst_rate': gst_rate,
                            'subtotal': item_subtotal,
                            'taxable_amount': taxable_amount,
                            'cgst_rate': gst_calc['cgst_rate'],
                            'sgst_rate': gst_calc['sgst_rate'],
                            'igst_rate': gst_calc['igst_rate'],
                            'cgst_amount': gst_calc['cgst_amount'],
                            'sgst_amount': gst_calc['sgst_amount'],
                            'igst_amount': gst_calc['igst_amount'],
                            'total_amount': item_total,
                            'is_charge': True
                        }
                        
                        processed_items.append(processed_item)
                        
                        subtotal += item_subtotal
                        total_taxable += taxable_amount
                        total_cgst += gst_calc['cgst_amount']
                        total_sgst += gst_calc['sgst_amount']
                        total_igst += gst_calc['igst_amount']
            
            if processed_items:
                grand_total = subtotal - total_discount + total_cgst + total_sgst + total_igst
                decimal_part = grand_total - int(grand_total)
                round_off = 0.0
                if decimal_part < 0.5:
                    round_off = -decimal_part
                else:
                    round_off = 1 - decimal_part
                grand_total += round_off
            else:
                subtotal = float(voucher_data.get('total_amount', 0.0))
                total_discount = float(voucher_data.get('total_discount', 0.0))
                total_taxable = subtotal - total_discount
                total_cgst = 0.0
                total_sgst = 0.0
                total_igst = 0.0
                round_off = float(voucher_data.get('round_off', 0.0))
                grand_total = total_taxable + round_off
        
        template_data = {
            'company': company,
            'voucher': voucher_data,
            'items': processed_items,
            'subtotal': subtotal,
            'total_discount': total_discount,
            'total_taxable': taxable_amount,
            'total_cgst': total_cgst,
            'total_sgst': total_sgst,
            'total_igst': total_igst,
            'round_off': round_off,
            'grand_total': grand_total,
            'total_quantity': total_quantity,
            'is_interstate': is_interstate,
            'line_discount_enabled': voucher_data.get('line_discount_type') is not None,
            'total_discount_enabled': voucher_data.get('total_discount_type') is not None,
            'amount_in_words': IndianNumberFormatter.amount_to_words(grand_total),
            'generated_at': datetime.now(),
            'page_count': 1,
            'party': party,
            'org': org.__dict__ if org else {}
        }
        
        return template_data
    
    async def generate_voucher_pdf(self, voucher_type: str, voucher_data: Dict[str, Any],
                                 db: AsyncSession, organization_id: int, 
                                 current_user: User) -> BytesIO:
        """
        Generate PDF for any voucher type
        """
        try:
            template_data = await self._prepare_voucher_data(voucher_type, voucher_data, db, organization_id)
            
            from app.models.organization_settings import OrganizationSettings, VoucherFormatTemplate
            stmt_settings = select(OrganizationSettings).where(
                OrganizationSettings.organization_id == organization_id
            )
            result_settings = await db.execute(stmt_settings)
            org_settings = result_settings.scalars().first()
            
            terms_conditions = None
            if org_settings:
                if voucher_type in ['purchase', 'purchase-vouchers']:
                    terms_conditions = org_settings.purchase_voucher_terms
                elif voucher_type in ['purchase_orders', 'purchase-orders']:
                    terms_conditions = org_settings.purchase_order_terms
                elif voucher_type in ['sales', 'sales-vouchers']:
                    terms_conditions = org_settings.sales_voucher_terms
                elif voucher_type in ['sales_order', 'sales-orders']:
                    terms_conditions = org_settings.sales_order_terms
                elif voucher_type == 'quotation':
                    terms_conditions = org_settings.quotation_terms
                elif voucher_type == 'proforma_invoice':
                    terms_conditions = org_settings.proforma_invoice_terms
                elif voucher_type == 'delivery-challan':
                    terms_conditions = org_settings.delivery_challan_terms
                elif voucher_type == 'grn':
                    terms_conditions = org_settings.grn_terms
                
                template_data['terms_conditions'] = (terms_conditions or '').split('\n') if terms_conditions else []
            
            base_template_name = 'base_voucher.html'
            if org_settings and org_settings.voucher_format_template_id:
                stmt_template = select(VoucherFormatTemplate).where(
                    VoucherFormatTemplate.id == org_settings.voucher_format_template_id,
                    VoucherFormatTemplate.is_active == True
                )
                result_template = await db.execute(stmt_template)
                format_template = result_template.scalars().first()
                
                if format_template and format_template.template_config:
                    template_data['format_config'] = format_template.template_config
                    logger.info(f"Using format template: {format_template.name} for voucher")
                    
                    layout_style = format_template.template_config.get('layout', 'standard')
                    if layout_style == 'modern':
                        base_template_name = 'base_voucher_modern.html'
                    elif layout_style == 'classic':
                        base_template_name = 'base_voucher_classic.html'
                    elif layout_style == 'minimal':
                        base_template_name = 'base_voucher_minimal.html'
            
            if voucher_type in ['purchase', 'purchase-vouchers']:
                template_name = 'purchase_voucher.html'
            elif voucher_type == 'purchase_orders':
                template_name = 'purchase_order.html'
            elif voucher_type == 'sales':
                template_name = 'sales_voucher.html'
            elif voucher_type == 'delivery-challan':
                template_name = 'delivery_challan.html'
            elif voucher_type == 'quotation':
                template_name = 'quotation.html'
            elif voucher_type == 'sales_order':
                template_name = 'sales_order.html'
            elif voucher_type == 'proforma_invoice':
                template_name = 'proforma_invoice.html'
            elif voucher_type == 'payment-vouchers':
                template_name = 'payment_voucher.html'
            elif voucher_type == 'receipt-vouchers':
                template_name = 'receipt_voucher.html'
            elif voucher_type == 'grn':
                template_name = 'goods_receipt_note.html'
            else:
                template_name = f"{voucher_type}_voucher.html"
            
            try:
                template = self.jinja_env.get_template(template_name)
            except Exception:
                template = self.jinja_env.get_template(base_template_name)
                logger.warning(f"Template {template_name} not found, using base template: {base_template_name}")
            
            html_content = template.render(**template_data)
            
            pdf_options = {
                'page-size': 'A4',
                'margin-top': '0mm',
                'margin-right': '0mm',
                'margin-bottom': '0mm',
                'margin-left': '0mm',
                'encoding': 'UTF-8',
                'disable-smart-shrinking': '',
                'zoom': '1.0',
                'dpi': '96',
                'header-spacing': '0',
                'footer-spacing': '0',
                'print-media-type': ''
            }
            if not self.pdfkit_config:
                raise RuntimeError("wkhtmltopdf is not installed or not found at /usr/bin/wkhtmltopdf. PDF generation cannot proceed.")
            pdf_bytes = pdfkit.from_string(html_content, False, configuration=self.pdfkit_config, options=pdf_options)
            
            logger.info(f"PDF generated successfully for {voucher_type}")
            pdf_io = BytesIO(pdf_bytes)
            pdf_io.seek(0)
            return pdf_io
            
        except Exception as e:
            logger.error(traceback.format_exc())
            raise Exception(f"PDF generation failed: {str(e)}")
    
    async def generate_purchase_voucher_pdf(self, voucher_data: Dict[str, Any],
                                          db: AsyncSession, organization_id: int,
                                          current_user: User) -> BytesIO:
        """Generate Purchase Voucher PDF"""
        return await self.generate_voucher_pdf('purchase', voucher_data, db, organization_id, current_user)
    
    async def generate_sales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                       db: AsyncSession, organization_id: int,
                                       current_user: User) -> BytesIO:
        """Generate Sales Voucher PDF"""
        return await self.generate_voucher_pdf('sales', voucher_data, db, organization_id, current_user)
    
    async def generate_presales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                          db: AsyncSession, organization_id: int,
                                          current_user: User) -> BytesIO:
        """Generate Pre-Sales Voucher PDF"""
        return await self.generate_voucher_pdf('presales', voucher_data, db, organization_id, current_user)

pdf_generator = VoucherPDFGenerator()