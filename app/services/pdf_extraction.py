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
import re
from datetime import datetime
import requests
import time
import base64  # Added for base64 PDF encoding
from PyPDF2 import PdfReader  # Added for PDF text extraction

logger = logging.getLogger(__name__)

class PDFExtractionService:
    """Service for extracting structured data from PDF documents"""
    
    UPLOAD_DIR = "temp/pdf_uploads"
    MAX_FILE_SIZE = 5 * 1024 * 1024  # Reduced to 5MB to lower memory usage
    RAPIDAPI_HOST = "powerful-gstin-tool.p.rapidapi.com"
    RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
    
    # AI-based extraction settings (Feature 11)
    USE_AI_EXTRACTION = os.getenv('USE_AI_EXTRACTION', 'false').lower() == 'true'
    MINDEE_API_KEY = os.getenv('MINDEE_API_KEY')  # Free tier: https://mindee.com
    GOOGLE_DOCUMENT_AI_KEY = os.getenv('GOOGLE_DOCUMENT_AI_KEY')  # Free tier
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')  # New: OpenRouter key
    OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-chat-v3-0324:free')  # Updated to suggested model
    
    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        if not self.RAPIDAPI_KEY:
            logger.warning("RAPIDAPI_KEY not set in environment variables")
        if self.USE_AI_EXTRACTION and not self.OPENROUTER_API_KEY:
            logger.warning("AI extraction enabled but no OpenRouter API key configured")
    
    async def extract_voucher_data(self, file: UploadFile, voucher_type: str) -> Dict[str, Any]:
        """
        Extract structured data from PDF based on voucher type
        For vendor/customer: Extract from PDF only (GSTIN at minimum), GST retrieval is separate via search endpoint
        """
        # Validate file
        await self._validate_pdf_file(file)
        
        # Save file temporarily
        temp_file_path = await self._save_temp_file(file)
        
        try:
            logger.info(f"Starting extraction for voucher_type: {voucher_type}")
            if self.USE_AI_EXTRACTION:
                logger.info("Attempting AI extraction")
                # Try AI extraction directly with PDF
                ai_extracted = await self.extract_with_ai(None, voucher_type, temp_file_path)
                if ai_extracted:  # If AI succeeds, return it
                    logger.info("AI extraction successful")
                    return ai_extracted
                logger.warning("AI extraction failed or returned empty, falling back to regex")
            
            # Fallback to regex extraction
            text_content = self._extract_text_from_pdf(temp_file_path)  # Synchronous call
            logger.info(f"Extracted text length: {len(text_content)}")
            if len(text_content) == 0:
                logger.warning("No text extracted from PDF - may be scanned image, consider OCR")
            
            # Parse text based on voucher type
            if voucher_type == "purchase_voucher":
                extracted = self._extract_purchase_voucher_data(text_content)
            elif voucher_type == "sales_order":
                extracted = self._extract_sales_order_data(text_content)
            elif voucher_type == "vendor":
                extracted = self._extract_vendor_data(text_content)
            elif voucher_type == "customer":
                extracted = self._extract_customer_data(text_content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported voucher type: {voucher_type}"
                )
            if not extracted or len(extracted.get('items', [])) == 0:
                logger.info("Specific regex failed, trying generic fallback")
                extracted = self._generic_extract(text_content, voucher_type)
            logger.info(f"Final extraction result: {extracted}")
            return extracted
                
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
            logger.info("Starting KYC extraction")
            if self.USE_AI_EXTRACTION:
                logger.info("Attempting AI extraction for KYC")
                ai_extracted = await self.extract_with_ai(None, "kyc", temp_file_path)
                if ai_extracted:  # If AI succeeds, return it
                    logger.info("AI KYC extraction successful")
                    return ai_extracted
                logger.warning("AI KYC extraction failed or empty, falling back to regex")
            
            # Fallback to regex extraction
            text_content = self._extract_text_from_pdf(temp_file_path)  # Synchronous call
            logger.info(f"Extracted text length for KYC: {len(text_content)}")
            if len(text_content) == 0:
                logger.warning("No text extracted from KYC PDF - may be scanned image")
            
            # Detect document type and extract accordingly
            doc_type = self._detect_kyc_type(text_content)
            logger.info(f"Detected KYC type: {doc_type}")
            
            if doc_type == "aadhaar":
                extracted = self._extract_aadhaar_data(text_content)
            elif doc_type == "pan":
                extracted = self._extract_pan_data(text_content)
            elif doc_type == "passport":
                extracted = self._extract_passport_data(text_content)
            elif doc_type == "bank":
                extracted = self._extract_bank_data(text_content)
            else:
                extracted = self._extract_generic_kyc_data(text_content)
            logger.info(f"KYC regex extraction result: {extracted}")
            return extracted
                
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
            'pan_number': r'(?:PAN|Pan Number)[\s:]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
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
                detail=f"File size must be less than {self.MAX_FILE_SIZE // (1024 * 1024)}MB"
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
    
    def _extract_purchase_voucher_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Purchase Voucher"""
        patterns = {
            'invoice_number': r'(?:invoice|bill|voucher|purchase order|po|no|number|ref no)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'invoice_date': r'(?:date|dated|issue date|order date)[\s:]*(\d{1,2}[\/\- ]\d{1,2}[\/\- ]\d{2,4})',
            'vendor_name': r'(?:vendor|supplier|from|sold by|seller|ship from)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone|gstin)',
            'amount': r'(?:total|grand total|amount|sum|payable|net amount)[\s:]*(?:rs\.?|₹|inr)?\s*([0-9,]+\.?\d{0,2})',
            'gst_number': r'(?:gstin|gst\s*no?|gst number)[\s:]*([0-9A-Z]{15})',
        }
        extracted_data = {
            "vendor_name": self._extract_with_pattern(text, patterns['vendor_name']),
            "invoice_number": self._extract_with_pattern(text, patterns['invoice_number']),
            "invoice_date": self._parse_date(self._extract_with_pattern(text, patterns['invoice_date'])),
            "payment_terms": "Net 30",
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "items": self._extract_line_items(text, "purchase")
        }
        return extracted_data
    
    def _extract_sales_order_data(self, text: str) -> Dict[str, Any]:
        """Extract data specific to Sales Order - Treat as received PO, extract supplier as customer"""
        patterns = {
            'order_number': r'(?:order|po|purchase order|sales|no|number|ref no|reference)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'order_date': r'(?:date|dated|order date|issue date|po date)[\s:]*(\d{1,2}[\/\- ]\d{1,2}[\/\- ]\d{2,4})',
            'customer_name': r'(?:supplier|vendor|from|sold by|seller|letterhead|company name)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone|gstin)',
            'amount': r'(?:total|grand total|amount|sum|payable|net amount)[\s:]*(?:rs\.?|₹|inr)?\s*([0-9,]+\.?\d{0,2})',
            'reference_number': r'(?:reference|ref|so|customer ref)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'delivery_date': r'(?:delivery date|due date|ship date|expected delivery)[\s:]*(\d{1,2}[\/\- ]\d{1,2}[\/\- ]\d{2,4})',
            'gst_terms': r'(?:gst terms|tax terms|terms of payment)[\s:]*(.+?)(?=\s*(?:freight|warranty|$))',
            'freight': r'(?:freight|shipping|transport)[\s:]*(?:rs\.?|₹|inr)?\s*([0-9,]+\.?\d{0,2})',
            'warranty': r'(?:warranty)[\s:]*(.+?)(?=\s*(?:installation|$))',
            'installation_charges': r'(?:installation charges|setup fee|installation)[\s:]*(?:rs\.?|₹|inr)?\s*([0-9,]+\.?\d{0,2})',
            'signer': r'(?:authorized signatory|signed by|prepared by)[\s:]*([A-Za-z\s&\.]+)',
            'signer_role': r'(?:position|role|designation)[\s:]*([A-Za-z\s&\.]+)',
        }
        extracted_data = {
            "customer_name": self._extract_with_pattern(text, patterns['customer_name']),
            "order_number": self._extract_with_pattern(text, patterns['order_number']),
            "order_date": self._parse_date(self._extract_with_pattern(text, patterns['order_date'])),
            "reference_number": self._extract_with_pattern(text, patterns['reference_number']),
            "delivery_date": self._parse_date(self._extract_with_pattern(text, patterns['delivery_date'])),
            "payment_terms": "Net 15",
            "gst_terms": self._extract_with_pattern(text, patterns['gst_terms']),
            "freight": self._parse_amount(self._extract_with_pattern(text, patterns['freight'])),
            "warranty": self._extract_with_pattern(text, patterns['warranty']),
            "installation_charges": self._parse_amount(self._extract_with_pattern(text, patterns['installation_charges'])),
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['amount'])),
            "signer": self._extract_with_pattern(text, patterns['signer']),
            "signer_role": self._extract_with_pattern(text, patterns['signer_role']),
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
                response = requests.get(url, headers=headers, timeout=10)  # Reduced timeout
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
                time.sleep(retry_delay)
                retry_delay *= 2
    
    def _extract_vendor_data(self, text: str) -> Dict[str, Any]:
        """Extract vendor data from GST certificate using PDF extraction only"""
        return self._fallback_pdf_extraction(text, "vendor")
    
    def _fallback_pdf_extraction(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Extraction from PDF text"""
        text = re.sub(r'\s+', ' ', text).strip()
        patterns = {
            'legal_name': r'(?:Legal Name of the Taxpayer|Legal Name\s*of\s*Business|Legal Name|Name of Business|Registered Name|Name of the Proprietor|Firm Name|Name)\s*:\s*(.+?)(?=\s*(?:Trade Name|GSTIN|PAN|Address|State|Mobile|Email|$))',
            'trade_name': r'(?:Trade Name\s*of\s*Business|Trade Name, if any|Trade Name)\s*:\s*(.+?)(?=\s*(?:GSTIN|PAN|Address|State|Mobile|Email|$))',
            'gst_number': r'(?:GSTIN|Registration Number|GST Number|GST)[\s:]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            'address_block': r'(?:Address of Principal Place of Business|Registered Address|Address|Principal Place of Business|Complete Address|Office Address|Address)\s*:\s*(.+?)(?=\s*(?:State Code|PIN Code|Date of Liability|$))',
            'phone': r'(?:Phone|Mobile|Contact Number|Telephone|Mobile Number|Contact)[\s:]*([+]?[0-9\s\-\(\)]{10,15})',
            'email': r'(?:Email|E-mail|Mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            'pan_number': r'(?:PAN|Pan Number)[\s:]*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            'state_code': r'(?:State Code)[\s:]*(\d{2})',
            'pin_code': r'(?:PIN Code|Pincode|Postal Code|PIN)[\s:]*(\d{6})',
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
            address_parts = [p.strip() for p in re.split(r',|\n', address_block) if p.strip()]  # Split on comma or newline
            if len(address_parts) >= 4:
                extracted_data["address1"] = ', '.join(address_parts[:-3])
                extracted_data["address2"] = address_parts[-3]
                extracted_data["city"] = address_parts[-2]
                extracted_data["state"] = address_parts[-2].split()[0] if ' ' in address_parts[-2] else address_parts[-2]
                extracted_data["pin_code"] = address_parts[-1] if not extracted_data["pin_code"] else extracted_data["pin_code"]
            elif len(address_parts) >= 3:
                extracted_data["address1"] = address_parts[0]
                extracted_data["address2"] = address_parts[1]
                extracted_data["city"] = address_parts[1]
                last = address_parts[2]
                extracted_data["state"] = ' '.join(last.split()[:-1]) if ' ' in last else last
                pin_match = re.search(r'\d{6}', last)
                if pin_match and not extracted_data["pin_code"]:
                    extracted_data["pin_code"] = pin_match.group(0)
            else:
                extracted_data["address1"] = address_block
                pin_match = re.search(r'\d{6}', address_block)
                if pin_match and not extracted_data["pin_code"]:
                    extracted_data["pin_code"] = pin_match.group(0)
                    extracted_data["address1"] = re.sub(r'\d{6}', '', address_block).strip()
        return {k: v for k, v in extracted_data.items() if v is not None}
    
    def _extract_customer_data(self, text: str) -> Dict[str, Any]:
        """Extract customer data from business document"""
        return self._extract_vendor_data(text)
    
    def _extract_with_pattern(self, text: str, pattern: str) -> Optional[str]:
        """Extract text using regex pattern with improved cleaning"""
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s+', ' ', value)
            return value if value else None
        return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse and standardize date string"""
        if not date_str:
            return None
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d', '%d.%m.%Y', '%d %b %Y', '%b %d, %Y', '%d %B %Y', '%B %d, %Y']
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
        lines = re.split(r'\n|\r', text)  # Better split
        items = []
        in_table = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.search(r'(?:sr|sl|no|item|desc|product|qty|unit|rate|amount|hsn|sac|particulars)', line, re.IGNORECASE):
                in_table = True
                continue
            if in_table:
                # More flexible: Optional groups, any order-ish
                parts = re.split(r'\s{2,}', line)  # Split on multiple spaces
                if len(parts) >= 4:  # Min sr, desc, qty, amount
                    item = {}
                    try:
                        item['sr_no'] = int(parts[0]) if parts[0].isdigit() else None
                        item['description'] = parts[1]
                        idx = 2
                        if re.match(r'\d{4,8}', parts[idx]):  # HSN
                            item['hsn_code'] = parts[idx]
                            idx += 1
                        item['quantity'] = float(re.sub(r'[^\d.]', '', parts[idx])) if re.search(r'\d', parts[idx]) else None
                        idx += 1
                        if idx < len(parts) and re.match(r'[A-Za-z]+', parts[idx]):  # Unit
                            item['unit'] = parts[idx]
                            idx += 1
                        item['rate'] = self._parse_amount(parts[idx]) if idx < len(parts) else None
                        idx += 1
                        item['amount'] = self._parse_amount(parts[idx]) if idx < len(parts) else None
                        items.append(item)
                    except:
                        pass
                if re.search(r'total|grand|subtotal|tax|gst', line, re.IGNORECASE):
                    in_table = False
        logger.info(f"Extracted {len(items)} line items")
        return items[:10]  # Limit to 10 items to reduce memory
    
    def _generic_extract(self, text: str, voucher_type: str) -> Dict[str, Any]:
        """Generic fallback extraction if specific fails"""
        patterns = {
            'number': r'(?:no|number|ref|order|invoice|so|po)[\s#]*:?\s*([A-Z0-9\-\/]+)',
            'date': r'(?:date|dated)[\s:]*(\d{1,2}[\/\- ]\d{1,2}[\/\- ]\d{2,4})',
            'name': r'(?:to|from|buyer|seller|customer|vendor)[\s:]*([A-Za-z\s&\.,]+?)(?:\n|address|phone)',
            'total': r'(?:total|amount)[\s:]*(?:rs\.?|₹)?\s*([0-9,]+\.?\d{0,2})',
        }
        extracted_data = {
            "name": self._extract_with_pattern(text, patterns['name']),
            "number": self._extract_with_pattern(text, patterns['number']),
            "date": self._parse_date(self._extract_with_pattern(text, patterns['date'])),
            "total_amount": self._parse_amount(self._extract_with_pattern(text, patterns['total'])),
            "items": self._extract_line_items(text, voucher_type)
        }
        if voucher_type == "sales_order":
            extracted_data["customer_name"] = extracted_data.pop("name", None)
            extracted_data["order_number"] = extracted_data.pop("number", None)
            extracted_data["order_date"] = extracted_data.pop("date", None)
            extracted_data["payment_terms"] = "Net 15"
        elif voucher_type == "purchase_voucher":
            extracted_data["vendor_name"] = extracted_data.pop("name", None)
            extracted_data["invoice_number"] = extracted_data.pop("number", None)
            extracted_data["invoice_date"] = extracted_data.pop("date", None)
            extracted_data["payment_terms"] = "Net 30"
        logger.info(f"Generic extraction result: {extracted_data}")
        return extracted_data
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract raw text from PDF file using PyPDF2"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            text = text.strip()
            logger.info(f"PDF text extraction successful, length: {len(text)}")
            if len(text) < 50:
                logger.warning("Extracted text is very short - PDF may contain images or non-extractable text")
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {str(e)}")
            raise ValueError(f"PDF text extraction failed: {str(e)}")
    
    async def extract_with_ai(self, text_content: Optional[str], document_type: str, file_path: str) -> Dict[str, Any]:
        """
        AI-based PDF extraction using OpenRouter with direct PDF
        """
        if not self.USE_AI_EXTRACTION:
            logger.info("AI extraction disabled, using fallback regex extraction")
            return {}
        # Always extract text if not provided (for text-based models like OpenRouter)
        if text_content is None:
            text_content = self._extract_text_from_pdf(file_path)
        try:
            if self.OPENROUTER_API_KEY:
                return await self._extract_with_openrouter(text_content, document_type, file_path)
            elif self.MINDEE_API_KEY:
                return await self._extract_with_mindee(file_path, document_type)
            elif self.GOOGLE_DOCUMENT_AI_KEY:
                return await self._extract_with_google_doc_ai(file_path, document_type)
            else:
                logger.warning("No AI API keys configured, using fallback extraction")
                return {}
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return {}
    
    async def _extract_with_openrouter(self, text_content: str, document_type: str, file_path: str) -> Dict[str, Any]:
        """
        Extract data using OpenRouter API with extracted text (since model is text-based)
        """
        try:
            # Improved prompt to force strict JSON output
            prompt = f"Extract structured data from this {document_type} document as JSON only. Keys: customer_name, customer_address, customer_email, customer_phone, customer_website, order_number, order_date, reference_number, reference_date, delivery_date, items (array of objects with sl_no, description, hsn_code, quantity, unit, rate, amount), subtotal, gst_terms, freight, warranty, installation_charges, total_amount, signer, signer_role. Use null for missing. Output pure JSON, no text."
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt + "\n\nExtracted document text:\n" + text_content[:4000]  # Limit text to avoid token limits
                    }
                ]
            }
            
            logger.info(f"Sending request to OpenRouter with model: {self.OPENROUTER_MODEL}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Extract from AI response (assume it's JSON in content)
            ai_content = result['choices'][0]['message']['content']
            logger.info(f"OpenRouter raw response: {ai_content[:500]}")  # Log snippet for debug
            try:
                import json
                # Clean potential markdown
                ai_content = re.sub(r'^```json\n|\n```$', '', ai_content).strip()
                extracted = json.loads(ai_content)
                if not isinstance(extracted, dict):
                    raise ValueError("Parsed but not a dict")
                logger.info(f"OpenRouter extraction successful: {len(extracted.get('items', []))} items extracted")
                return extracted
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse OpenRouter JSON response: {str(e)}")
                return {}
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error in OpenRouter: {str(http_err)}")
            if "402" in str(http_err):
                logger.error("Payment required - check OpenRouter credits")
            return {}
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            return {}
    
    async def _extract_with_mindee(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """
        Extract data using Mindee API
        """
        try:
            url = "https://api.mindee.net/v1/products/mindee/invoices/v4/predict"
            with open(file_path, 'rb') as f:
                files = {'document': f}
                headers = {'Authorization': f'Token {self.MINDEE_API_KEY}'}
                response = requests.post(url, files=files, headers=headers, timeout=10)  # Reduced timeout
                response.raise_for_status()
                data = response.json()
                if data.get('document') and data['document'].get('inference'):
                    inference = data['document']['inference']
                    prediction = inference.get('prediction', {})
                    extracted = {
                        'vendor_name': prediction.get('supplier_name', {}).get('value'),
                        'invoice_number': prediction.get('invoice_number', {}).get('value'),
                        'invoice_date': prediction.get('date', {}).get('value'),
                        'total_amount': prediction.get('total_amount', {}).get('value'),
                        'tax_amount': prediction.get('total_tax', {}).get('value'),
                        'items': []
                    }
                    for item in prediction.get('line_items', [])[:10]:  # Limit to 10 items
                        extracted['items'].append({
                            'description': item.get('description'),
                            'quantity': item.get('quantity'),
                            'unit_price': item.get('unit_price'),
                            'total_amount': item.get('total_amount')
                        })
                    logger.info(f"Mindee extraction successful: {len(extracted.get('items', []))} items extracted")
                    return extracted
            return {}
        except Exception as e:
            logger.error(f"Mindee API error: {str(e)}")
            return {}
    
    async def _extract_with_google_doc_ai(self, file_path: str, document_type: str) -> Dict[str, Any]:
        """
        Extract data using Google Document AI
        """
        logger.info("Google Document AI extraction not yet implemented")
        logger.info("To use Google Document AI:")
        logger.info("1. Enable Document AI API in Google Cloud Console")
        logger.info("2. Create an Invoice Parser processor")
        logger.info("3. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        return {}

# Global service instance
pdf_extraction_service = PDFExtractionService()