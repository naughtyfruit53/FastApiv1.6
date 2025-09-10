# app/services/pdf_generation_service.py

"""
Comprehensive PDF generation service for vouchers with Indian formatting
"""

import os
import uuid
from datetime import datetime, date  # Added date import for type checking
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
from xhtml2pdf import pisa
from io import BytesIO
from num2words import num2words
from sqlalchemy.orm import Session
from app.models import Company, User
import logging
import base64
import re  # Added for sanitizing filenames

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
    def format_indian_currency(amount: float) -> str:
        """Format amount in Indian currency format (₹1,23,456.78)"""
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
            result = f"₹{formatted_amount}"
            if is_negative:
                result = f"-{result}"
                
            return result
            
        except Exception as e:
            logger.error(f"Error formatting Indian currency: {e}")
            return f"₹{amount:.2f}"

class TaxCalculator:
    """GST and tax calculation utilities"""
    
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
        return f"{value:.2f}%"
    
    def _get_company_branding(self, db: Session, organization_id: int) -> Dict[str, Any]:
        """Get company branding information"""
        try:
            company = db.query(Company).filter(
                Company.organization_id == organization_id
            ).first()
            
            if company:
                logo_url = None
                logo_path = os.path.join('uploads/company_logos', f"{organization_id}.png")
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as f:
                        logo_data = base64.b64encode(f.read()).decode('utf-8')
                    logo_url = f"data:image/png;base64,{logo_data}"
                
                return {
                    'name': company.name,
                    'address1': company.address1,
                    'address2': company.address2 or '',
                    'city': company.city,
                    'state': company.state,
                    'pin_code': company.pin_code,
                    'state_code': company.state_code,
                    'gst_number': company.gst_number or '',
                    'pan_number': company.pan_number or '',
                    'contact_number': company.contact_number,
                    'email': company.email or '',
                    'website': company.website or '',
                    'logo_url': logo_url
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
                    'logo_url': None
                }
                
        except Exception as e:
            logger.error(f"Error getting company branding: {e}")
            return {
                'name': 'Your Company Name',
                'address1': 'Company Address',
                'city': 'City', 'state': 'State', 'pin_code': '123456',
                'contact_number': '+91-1234567890',
                'logo_url': None
            }
    
    def _prepare_voucher_data(self, voucher_data: Dict[str, Any], 
                            db: Session, organization_id: int) -> Dict[str, Any]:
        """Prepare voucher data for template rendering"""
        
        # Get company branding
        company = self._get_company_branding(db, organization_id)
        
        # Calculate totals and taxes for items
        items = voucher_data.get('items', [])
        processed_items = []
        
        subtotal = 0.0
        total_discount = voucher_data.get('total_discount', 0.0)
        total_taxable = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_igst = 0.0
        is_interstate = voucher_data.get('is_interstate', False)
        
        for item in items:
            # Calculate item totals
            quantity = float(item.get('quantity', 0))
            unit_price = float(item.get('unit_price', 0))
            discount_percentage = float(item.get('discount_percentage', 0))
            discount_amount = float(item.get('discount_amount', 0))
            gst_rate = float(item.get('gst_rate', 0))
            
            item_subtotal = quantity * unit_price
            if discount_percentage > 0:
              discount_amount = item_subtotal * (discount_percentage / 100)
            taxable_amount = item_subtotal - discount_amount
            
            # Calculate GST (assuming intrastate for now - enhance with actual check)
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
                'total_amount': item_total
            }
            
            processed_items.append(processed_item)
            
            subtotal += item_subtotal
            total_taxable += taxable_amount
            total_cgst += gst_calc['cgst_amount']
            total_sgst += gst_calc['sgst_amount']
            total_igst += gst_calc['igst_amount']
        
        grand_total = subtotal - total_discount + total_cgst + total_sgst + total_igst
        
        # Calculate round off
        decimal_part = grand_total - int(grand_total)
        round_off = 0.0
        if decimal_part < 0.5:
            round_off = -decimal_part
        else:
            round_off = 1 - decimal_part
        grand_total += round_off
        
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
            'is_interstate': is_interstate,
            'amount_in_words': IndianNumberFormatter.amount_to_words(grand_total),
            'generated_at': datetime.now(),
            'page_count': 1  # Will be updated for multi-page
        }
        
        return template_data
    
    def generate_voucher_pdf(self, voucher_type: str, voucher_data: Dict[str, Any],
                           db: Session, organization_id: int, 
                           current_user: User) -> str:
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
            template_data = self._prepare_voucher_data(voucher_data, db, organization_id)
            
            # Get template for voucher type
            template_name = f"{voucher_type}_voucher.html"
            
            if voucher_type == 'purchase-orders':
                template_name = 'purchase_voucher.html'
            
            try:
                template = self.jinja_env.get_template(template_name)
            except Exception:
                # Fallback to base template
                template = self.jinja_env.get_template('base_voucher.html')
                logger.warning(f"Template {template_name} not found, using base template")
            
            # Render HTML
            html_content = template.render(**template_data)
            
            # Generate unique filename
            voucher_number = voucher_data.get('voucher_number', 'unknown')
            voucher_number = re.sub(r'[^\w\-]', '_', voucher_number)  # Sanitize voucher_number
            filename = f"{voucher_type}_{voucher_number}_{uuid.uuid4().hex[:8]}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Convert to PDF using xhtml2pdf
            pdf_buffer = BytesIO()
            pisa.CreatePDF(html_content, dest=pdf_buffer)
            pdf_buffer.seek(0)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            logger.info(f"PDF generated successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating PDF for {voucher_type}: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def generate_purchase_voucher_pdf(self, voucher_data: Dict[str, Any],
                                    db: Session, organization_id: int,
                                    current_user: User) -> str:
        """Generate Purchase Voucher PDF"""
        return self.generate_voucher_pdf('purchase', voucher_data, db, organization_id, current_user)
    
    def generate_sales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                 db: Session, organization_id: int,
                                 current_user: User) -> str:
        """Generate Sales Voucher PDF"""
        return self.generate_voucher_pdf('sales', voucher_data, db, organization_id, current_user)
    
    def generate_presales_voucher_pdf(self, voucher_data: Dict[str, Any],
                                    db: Session, organization_id: int,
                                    current_user: User) -> str:
        """Generate Pre-Sales Voucher PDF"""
        return self.generate_voucher_pdf('presales', voucher_data, db, organization_id, current_user)

# Create singleton instance
pdf_generator = VoucherPDFGenerator()