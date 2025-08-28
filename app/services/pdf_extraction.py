"""
PDF Extraction Service for KYC and HR Documents
Handles PDF processing and data extraction for employee KYC documents and vouchers
"""

import logging
import os
import uuid
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException, status
import tempfile
import fitz  # PyMuPDF for PDF processing
import re
from datetime import datetime
import requests
import time

logger = logging.getLogger(__name__)

class PDFExtractionService:
    """Service for extracting structured data from PDF documents"""
    
    UPLOAD_DIR = "temp/pdf_uploads"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    RAPIDAPI_HOST = "powerful-gstin-tool.p.rapidapi.com"
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    
    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        if not self.RAPIDAPI_KEY:
            logger.warning("RAPIDAPI_KEY not set in environment variables")
    
    async def extract_voucher_data(self, file: UploadFile, voucher_type: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF based on voucher type
        For vendor/customer: Extract from PDF only (GSTIN at minimum), GST retrieval is separate via search endpoint
        
        Args:
            file: UploadFile object containing the PDF
            voucher_type: Type of voucher (purchase_voucher, sales_order, vendor, etc.)
            
        Returns:
            Dictionary containing extracted voucher data
        """
        
        # Validate file
        await self._validate_pdf_file(file)
        
        # Save file temporarily
        temp_file_path = await self._save_temp_file(file)
        
        try:
            # Extract text from PDF
            text_content = await self._extract_text_from_pdf(temp_file_path)
            
            # Parse text based on voucher type
            if voucher_type == "purchase_voucher":
                return await self._extract_purchase_voucher_data(text_content)
            elif voucher_type == "sales_order":
                return await self._extract_sales_order_data(text_content)
            elif voucher_type == "vendor":
                return await self._extract_vendor_data(text_content)
            elif voucher_type == "customer":
                return await self._extract_customer_data(text_content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported voucher type: {voucher_type}"
                )
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF extraction failed: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    async def extract_kyc_data(self, file: UploadFile) -> Dict[str, Any]:
        """
        Extract KYC data from uploaded PDF document
        Supports Aadhaar, PAN, Passport, etc.
        """
       
        # Validate file
        await self._validate_pdf_file(file)
       
        # Save file temporarily
        temp_file_path = await self._save_temp_file(file)
       
        try:
            # Extract text from PDF
            text_content = await self._extract_text_from_pdf(temp_file_path)
           
            # Detect document type and extract accordingly
            doc_type = self._detect_kyc_type(text_content)
           
            if doc_type == "aadhaar":
                return self._extract_aadhaar_data(text_content)
            elif doc_type == "pan":
                return self._extract_pan_data(text_content)
            elif doc_type == "passport":
                return self._extract_passport_data(text_content)
            elif doc_type == "bank":
                return self._extract_bank_data(text_content)
            else:
                return self._extract_generic_kyc_data(text_content)
               
        except Exception as e:
            logger.error(f"KYC extraction failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"KYC extraction failed: {str(e)}"
            )
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
   
    def _detect_kyc_type(self, text: str) -> str:
        """Detect KYC document type based on content"""
       
        text_lower = text.lower()
       
        if "unique identification authority" in text_lower or "aadhaar" in text_lower:
            return "aadhaar"
        elif "income tax department" in text_lower or "permanent account number" in text_lower:
            return "pan"
        elif "passport" in text_lower or "government of india" in text_lower:
            return "passport"
        elif "account number" in text_lower and ("bank" in text_lower or "ifsc" in text_lower):
            return "bank"
        else:
            return "generic"
   
    def _extract_aadhaar_data(self, text: str) -> Dict[str, Any]:
        """Extract data from Aadhaar card"""
       
        patterns = {
            'aadhaar_number': r'(\d{4}\s?\d{4}\s?\d{4})',
            'name': r'(?:Name|नाम)\s*:\s*(.+?)(?=\s*(?:Year|DOB|जन्म तिथि|Mobile|Address|$))',
            'dob': r'(?:DOB|Year of Birth|जन्म तिथि|जन्म वर्ष)\s*:\s*(\d{2}/\d{2}/\d{4})',
            'gender': r'(?:Gender|लिंग)\s*:\s*(Male|Female|Transgender|MALE|FEMALE|TRANSGENDER)',
            'address': r'(?:Address|पता)\s*:\s*(.+?)(?=\s*(?:To|Enrolment|Download|www|$))',
        }
       
        extracted = {k: self._extract_with_pattern(text, v) for k, v in patterns.items()}
       
        # Parse address
        if extracted.get('address'):
            address_parts = extracted['address'].split(',')
            if len(address_parts) > 1:
                extracted['address_line1'] = ','.join(address_parts[:-3])
                extracted['address_line2'] = address_parts[-3].strip() if len(address_parts) > 2 else None
                extracted['city'] = address_parts[-2].strip() if len(address_parts) > 1 else None
                last_part = address_parts[-1].strip().split()
                if len(last_part) >= 2:
                    extracted['state'] = ' '.join(last_part[:-1])
                    extracted['pin_code'] = last_part[-1]
       
        return {k: v for k, v in extracted.items() if v}
   
    def _extract_pan_data(self, text: str) -> Dict[str, Any]:
        """Extract data from PAN card"""
       
        patterns = {
            'pan_number': r'(?:Permanent Account Number|PAN)\s*:\s*([A-Z]{5}\d{4}[A-Z])',
            'name': r'(?:Name|नाम)\s*:\s*(.+?)(?=\s*(?:Father|Date|DOB|जन्म तिथि|$))',
            'father_name': r"(?:Father's Name|पिता का नाम)\s*:\s*(.+?)(?=\s*(?:Date|DOB|जन्म तिथि|$))",
            'dob': r'(?:Date of Birth|DOB|जन्म तिथि)\s*:\s*(\d{2}/\d{2}/\d{4})',
        }
       
        return {k: self._extract_with_pattern(text, v) for k, v in patterns.items() if self._extract_with_pattern(text, v)}
   
    def _extract_passport_data(self, text: str) -> Dict[str, Any]:
        """Extract data from Passport"""
       
        patterns = {
            'passport_number': r'(?:Passport No|पासपोर्ट संख्या)\s*:\s*([A-Z]\d{7})',
            'name': r'(?:Given Name|दिए गए नाम)\s*:\s*(.+?)(?=\s*(?:Surname|Date|DOB|$))',
            'surname': r'(?:Surname|उपनाम)\s*:\s*(.+?)(?=\s*(?:Date|DOB|Place|$))',
            'dob': r'(?:Date of Birth|DOB|जन्म तिथि)\s*:\s*(\d{2}/\d{2}/\d{4})',
            'place_of_birth': r'(?:Place of Birth|जन्म स्थान)\s*:\s*(.+?)(?=\s*(?:Date of Issue|$))',
            'date_of_issue': r'(?:Date of Issue|जारी करने की तिथि)\s*:\s*(\d{2}/\d{2}/\d{4})',
            'date_of_expiry': r'(?:Date of Expiry|समाप्ति तिथि)\s*:\s*(\d{2}/\d{2}/\d{4})',
            'address': r'(?:Address|पता)\s*:\s*(.+?)(?=\s*(?:ECR|ECNR|$))',
        }
       
        extracted = {k: self._extract_with_pattern(text, v) for k, v in patterns.items()}
        if extracted.get('name') and extracted.get('surname'):
            extracted['full_name'] = f"{extracted['name']} {extracted['surname']}"
       
        return {k: v for k, v in extracted.items() if v}
   
    def _extract_bank_data(self, text: str) -> Dict[str, Any]:
        """Extract bank details from statement or passbook"""
       
        patterns = {
            'account_number': r'(?:Account Number|Acct No|A/C No|खाता संख्या)\s*:\s*(\d{9,18})',
            'ifsc_code': r'(?:IFSC Code|IFSC|आईएफएससी कोड)\s*:\s*([A-Z]{4}0[A-Z0-9]{6})',
            'bank_name': r'(?:Bank Name|बैंक का नाम)\s*:\s*(.+?)(?=\s*(?:Branch|शाखा|$))',
            'branch': r'(?:Branch|शाखा)\s*:\s*(.+?)(?=\s*(?:Account Number|खाता संख्या|$))',
            'name': r'(?:Account Holder Name|खाता धारक का नाम|Name of the Account Holder)\s*:\s*(.+?)(?=\s*(?:Account Number|खाता संख्या|$))',
        }
       
        return {k: self._extract_with_pattern(text, v) for k, v in patterns.items() if self._extract_with_pattern(text, v)}
   
    def _extract_generic_kyc_data(self, text: str) -> Dict[str, Any]:
        """Generic extraction for unknown documents"""
       
        patterns = {
            'name': r'(?:Name|नाम|Full Name|Account Holder)\s*:\s*(.+?)(?=\s*(?:Father|Date|DOB|Address|जन्म तिथि|पता|$))',
            'dob': r'(?:Date of Birth|DOB|जन्म तिथि)\s*:\s*(\d{2}/\d{2}/\d{4})',
            'address': r'(?:Address|पता|Current Address|Permanent Address)\s*:\s*(.+?)(?=\s*(?:PIN|Pin Code|State|राज्य|$))',
            'pan_number': r'(?:PAN|Pan Number|Permanent Account Number)\s*:\s*([A-Z]{5}\d{4}[A-Z])',
            'aadhaar_number': r'(?:Aadhaar Number|आधार संख्या)\s*:\s*(\d{4}\s?\d{4}\s?\d{4})',
            'account_number': r'(?:Account Number|खाता संख्या)\s*:\s*(\d{9,18})',
            'ifsc_code': r'(?:IFSC Code|IFSC|आईएफएससी कोड)\s*:\s*([A-Z]{4}0[A-Z0-9]{6})',
        }
       
        return {k: self._extract_with_pattern(text, v) for k, v in patterns.items() if self._extract_with_pattern(text, v)}
    
    async def _validate_pdf_file(self, file: UploadFile) -> None:
        """Validate uploaded PDF file"""
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded"
            )
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB"
            )
    
    async def _save_temp_file(self, file: UploadFile) -> str:
        """Save uploaded file temporarily"""
        
        file_extension = os.path.splitext(file.filename or "")[1]
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join(self.UPLOAD_DIR, temp_filename)
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return temp_file_path
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF using PyMuPDF"""
        
        try:
            doc = fitz.open(file_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text() + "\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read PDF content"
            )
    
    async def _extract_purchase_voucher_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Purchase Voucher"""
        
        patterns = {
            'invoice_number': r'(?:invoice|bill|voucher)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'invoice_date': r'(?:date|dated)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'vendor_name': r'(?:vendor|supplier|from)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone)',
            'amount': r'(?:total|amount|sum)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+\.?\d{0,2})',
            'gst_number': r'(?:gstin|gst\s*no?)[\s:]*([0-9A-Z]{15})',
        }
        
        extracted_data = {
            "vendor_name": self._extract_with_pattern(text, patterns['vendor_name']),
            "invoice_number": self._extract_with_pattern(text, patterns['invoice_number']),
            "invoice_date": self._parse_date(self._extract_with_pattern(text, patterns['invoice_date'])),
            "payment_terms": "Net 30",
            "notes": "Extracted from PDF invoice",
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "items": self._extract_line_items(text, "purchase")
        }
        
        return extracted_data
    
    async def _extract_sales_order_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Sales Order"""
        
        patterns = {
            'order_number': r'(?:order|so|sales)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'order_date': r'(?:date|dated)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'customer_name': r'(?:customer|client|to|bill\s*to)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone)',
            'amount': r'(?:total|amount|sum)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+\.?\d{0,2})',
        }
        
        extracted_data = {
            "customer_name": self._extract_with_pattern(text, patterns['customer_name']),
            "order_number": self._extract_with_pattern(text, patterns['order_number']),
            "order_date": self._parse_date(self._extract_with_pattern(text, patterns['order_date'])),
            "payment_terms": "Net 15",
            "notes": "Extracted from PDF sales order",
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "items": self._extract_line_items(text, "sales")
        }
        
        return extracted_data
    
    async def fetch_gst_details(self, gstin: str) -> Dict[str, Any]:
        """Fetch GST details using RapidAPI GSTIN tool with retry on rate limit"""
        url = f"https://{self.RAPIDAPI_HOST}/v1/gstin/{gstin}/details"
        
        headers = {
            "x-rapidapi-key": self.RAPIDAPI_KEY,
            "x-rapidapi-host": self.RAPIDAPI_HOST
        }
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit (429), retrying after {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                
                if response.status_code != 200:
                    logger.error(f"RapidAPI error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Failed to fetch GST details from RapidAPI: {response.text}"
                    )
                
                api_response = response.json()
                api_data = api_response.get('data', api_response)
                
                legal_name = api_data.get('legal_name') or api_data.get('lgnm') or api_data.get('lgn')
                trade_name = api_data.get('trade_name') or api_data.get('tradeNam') or api_data.get('trdnm')
                
                extracted_data = {
                    "name": trade_name,
                    "legal_name": legal_name,
                    "gst_number": api_data.get('gstin') or gstin,
                    "pan_number": api_data.get('pan_number') or gstin[2:12] if len(gstin) >= 12 else None,
                    "address1": None,
                    "address2": None,
                    "city": None,
                    "state": None,
                    "pin_code": None,
                    "state_code": api_data.get('state_code') or gstin[:2] if len(gstin) >= 2 else None,
                    "contact_number": api_data.get('contact_number') or api_data.get('mobile'),
                    "email": api_data.get('email'),
                    "business_constitution": api_data.get('business_constitution') or api_data.get('ctb'),
                    "taxpayer_type": api_data.get('type') or api_data.get('dty'),
                    "registration_date": api_data.get('registration_date') or api_data.get('rgdt'),
                    "nature_of_business": api_data.get('business_activity_nature') or api_data.get('nba'),
                    "additional_places": api_data.get('place_of_business_additional') or api_data.get('adadr'),
                    "is_active": (api_data.get('status') or api_data.get('sts')) in ['Active', 'ACT', 'Provisional', 'PRO']
                }
                
                pradr = api_data.get('place_of_business_principal') or api_data.get('pradr') or {}
                addr = pradr.get('address') or pradr.get('addr') or pradr
                
                bno = addr.get('door_num') or addr.get('bno')
                flno = addr.get('floor_num') or addr.get('flno')
                bnm = addr.get('building_name') or addr.get('bnm')
                st = addr.get('street') or addr.get('st')
                loc = addr.get('location') or addr.get('loc')
                dst = addr.get('district') or addr.get('dst')
                city = addr.get('city') or dst or loc
                state = addr.get('state') or addr.get('stcd')
                pin_code = addr.get('pin_code') or addr.get('pncd')
                
                address_parts1 = list(filter(None, [bno, flno, bnm, st]))
                extracted_data["address1"] = ', '.join(address_parts1) if address_parts1 else None
                
                address_parts2 = list(filter(None, [loc]))
                extracted_data["address2"] = ', '.join(address_parts2) if address_parts2 else None
                
                extracted_data["city"] = city
                extracted_data["state"] = state
                extracted_data["pin_code"] = pin_code
                
                return {k: v for k, v in extracted_data.items() if v is not None}
                
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch from RapidAPI after {max_retries} attempts: {str(e)}")
                    raise
                else:
                    time.sleep(retry_delay)
                    retry_delay *= 2
    
    async def _extract_vendor_data(self, text: str) -> Dict[str, Any]:
        """Extract vendor data from GST certificate using PDF extraction only"""
        
        return await self._fallback_pdf_extraction(text, "vendor")
    
    async def _fallback_pdf_extraction(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extraction from PDF text"""
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        patterns = {
            'legal_name': r'(?:Legal Name of the Taxpayer|Legal Name\s*of\s*Business|Legal Name|Name of Business|Registered Name|Name of the Proprietor|Firm Name)\s*:\s*(.+?)(?=\s*(?:Trade Name|GSTIN|PAN|Address|State|Mobile|Email|$))',
            'trade_name': r'(?:Trade Name\s*of\s*Business|Trade Name, if any|Trade Name)\s*:\s*(.+?)(?=\s*(?:GSTIN|PAN|Address|State|Mobile|Email|$))',
            'gst_number': r'(?:GSTIN|Registration Number|GST Number)[\s:]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            'address_block': r'(?:Address of Principal Place of Business|Registered Address|Address|Principal Place of Business|Complete Address|Office Address)\s*:\s*(.+?)(?=\s*(?:State Code|PIN Code|Date of Liability|$))',
            'phone': r'(?:Phone|Mobile|Contact Number|Telephone|Mobile Number)[\s:]*([+]?[0-9\s\-\(\)]{10,15})',
            'email': r'(?:Email|E-mail|Mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'pan_number': r'(?:PAN|Pan Number)[\s:]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            'state_code': r'(?:State Code)[\s:]*(\d{2})',
            'pin_code': r'(?:PIN Code|Pincode|Postal Code)[\s:]*(\d{6})',
            'state': r'(?:State)[\s:]*([A-Za-z\s]+)(?:PIN|Pin Code|Code|\n)',
            'registration_date': r'(?:Registration Date|Date of Registration|Date of Issue)[\s:]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'business_constitution': r'(?:Constitution of Business|Type of Taxpayer|Business Type)[\s:]*([A-Za-z\s]+)',
            'nature_of_business': r'(?:Nature of Business|Business Activity)[\s:]*([A-Za-z\s,]+)',
        }
        
        legal_name = self._extract_with_pattern(text, patterns['legal_name'])
        trade_name = self._extract_with_pattern(text, patterns['trade_name'])
        gst_number = self._extract_with_pattern(text, patterns['gst_number'])
        address_block = self._extract_with_pattern(text, patterns['address_block'])
        pan_number = self._extract_with_pattern(text, patterns['pan_number']) or (gst_number[2:12] if gst_number else None)
        state_code = self._extract_with_pattern(text, patterns['state_code']) or (gst_number[:2] if gst_number else None)
        phone = self._extract_with_pattern(text, patterns['phone'])
        email = self._extract_with_pattern(text, patterns['email'])
        pin_code = self._extract_with_pattern(text, patterns['pin_code'])
        state = self._extract_with_pattern(text, patterns['state'])
        registration_date = self._parse_date(self._extract_with_pattern(text, patterns['registration_date']))
        business_constitution = self._extract_with_pattern(text, patterns['business_constitution'])
        nature_of_business = self._extract_with_pattern(text, patterns['nature_of_business'])
        
        extracted_data = {
            "name": trade_name or legal_name,
            "legal_name": legal_name,
            "gst_number": gst_number,
            "pan_number": pan_number,
            "address1": None,
            "address2": None,
            "city": None,
            "state": state,
            "state_code": state_code,
            "pin_code": pin_code,
            "phone": phone,
            "email": email,
            "registration_date": registration_date,
            "business_constitution": business_constitution,
            "nature_of_business": nature_of_business.split(',') if nature_of_business else None,
            "is_active": True
        }
        
        if address_block:
            address_parts = [p.strip() for p in address_block.split(',') if p.strip()]
            
            if len(address_parts) >= 4:
                extracted_data["address1"] = ', '.join(address_parts[:-3])
                extracted_data["address2"] = address_parts[-3]
                extracted_data["city"] = address_parts[-3]
                extracted_data["state"] = address_parts[-2]
                extracted_data["pin_code"] = address_parts[-1] if not extracted_data["pin_code"] else extracted_data["pin_code"]
            elif len(address_parts) >= 3:
                extracted_data["address1"] = address_parts[0]
                extracted_data["address2"] = address_parts[1]
                extracted_data["city"] = address_parts[1]
                extracted_data["state"] = address_parts[2].split()[0]
                pin_match = re.search(r'\d{6}', address_parts[2])
                if pin_match and not extracted_data["pin_code"]:
                    extracted_data["pin_code"] = pin_match.group(0)
            else:
                extracted_data["address1"] = address_block
                pin_match = re.search(r'\d{6}', address_block)
                if pin_match and not extracted_data["pin_code"]:
                    extracted_data["pin_code"] = pin_match.group(0)
        
        return {k: v for k, v in extracted_data.items() if v is not None}
    
    async def _extract_customer_data(self, text: str) -> Dict[str, Any]:
        """Extract customer data from business document"""
        
        return await extract_vendor_data(text)
    
    def _extract_with_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Extract text using regex pattern with improved cleaning"""
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s+', ' ', value)
            return value if value else None
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse and standardize date string"""
        
        if not date_str:
            return None
        
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', '%d.%m.%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str
    
    def _parse_amount(self, amount_str: Optional[str]) -> float:
        """Parse amount string to float, removing currency symbols"""
        
        if not amount_str:
            return 0.0
        
        cleaned = re.sub(r'[₹$, ]', '', amount_str).strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def _extract_line_items(self, text: str, voucher_type: str) -> List[Dict[str, Any]]:
        """Extract line items from table-like text in PDF"""
        
        lines = text.split('\n')
        items = []
        in_table = False
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'(?:Sr|Sl|No|Item)\.?', line, re.IGNORECASE):
                in_table = True
                continue
                
            if in_table:
                match = re.match(r'(\d+)\s+(.+?)\s+([0-9]{4,8})\s+([0-9.]+)\s+([A-Za-z]+)\s+([0-9.,]+)\s+([0-9.,]+)', line)
                if match:
                    items.append({
                        "sr_no": match.group(1),
                        "description": match.group(2).strip(),
                        "hsn_code": match.group(3),
                        "quantity": float(match.group(4)),
                        "unit": match.group(5),
                        "rate": self._parse_amount(match.group(6)),
                        "amount": self._parse_amount(match.group(7))
                    })
                elif 'total' in line.lower() or 'grand' in line.lower():
                    in_table = False
        
        return items

# Global service instance
pdf_extraction_service = PDFExtractionService()