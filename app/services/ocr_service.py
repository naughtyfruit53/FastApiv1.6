# app/services/ocr_service.py

import os
import re
import uuid
import shutil
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)


class BusinessCardOCRService:
    """Service for OCR extraction from business cards"""
    
    def __init__(self):
        self.UPLOAD_DIR = "uploads/business_cards"
        self.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        self.ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
        
        # Ensure upload directory exists
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        
        # Configure tesseract if needed
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Adjust path as needed
    
    async def process_business_card(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process uploaded business card image and extract contact information
        
        Args:
            file: Uploaded image file
            
        Returns:
            Dict containing extracted information and metadata
        """
        try:
            # Validate file
            await self._validate_image_file(file)
            
            # Save temporary file
            temp_file_path = await self._save_temp_file(file)
            
            try:
                # Extract text using OCR
                raw_text = await self._extract_text_from_image(temp_file_path)
                
                # Parse extracted text into structured data
                extracted_data = self._parse_business_card_text(raw_text)
                
                # Calculate confidence score
                confidence_score = self._calculate_confidence_score(extracted_data, raw_text)
                
                return {
                    "raw_text": raw_text,
                    "extracted_data": extracted_data,
                    "confidence_score": confidence_score,
                    "image_path": temp_file_path,
                    **extracted_data  # Flatten extracted fields to top level
                }
                
            except Exception as e:
                # Clean up temp file if processing fails
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise
                
        except Exception as e:
            logger.error(f"Error processing business card: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process business card: {str(e)}"
            )
    
    async def _validate_image_file(self, file: UploadFile) -> None:
        """Validate uploaded image file"""
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file uploaded"
            )
        
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Supported types: {', '.join(self.ALLOWED_EXTENSIONS)}"
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
    
    async def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        
        try:
            # Open and preprocess image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use pytesseract to extract text
            # Using multiple PSM modes for better accuracy
            psm_modes = [6, 8, 13]  # Block, single word, raw line
            extracted_texts = []
            
            for psm in psm_modes:
                try:
                    config = f'--oem 3 --psm {psm}'
                    text = pytesseract.image_to_string(image, config=config)
                    if text.strip():
                        extracted_texts.append(text.strip())
                except Exception as e:
                    logger.warning(f"OCR with PSM {psm} failed: {str(e)}")
                    continue
            
            # Return the longest extracted text (usually most complete)
            if extracted_texts:
                return max(extracted_texts, key=len)
            else:
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {str(e)}")
            raise
    
    def _parse_business_card_text(self, text: str) -> Dict[str, Any]:
        """Parse raw OCR text into structured contact information"""
        
        # Clean up text
        text = text.strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Initialize extracted data
        extracted = {
            "full_name": None,
            "company_name": None,
            "designation": None,
            "email": None,
            "phone": None,
            "mobile": None,
            "website": None,
            "address": None
        }
        
        # Patterns for different types of information
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(?:\+91[\s\-]?)?(?:\d{3}[\s\-]?\d{3}[\s\-]?\d{4}|\d{10})',
            "website": r'(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]*\.(?:com|org|net|edu|gov|mil|biz|info|mobi|name|aero|jobs|museum)',
            "mobile": r'(?:\+91[\s\-]?)?(?:9|8|7|6)\d{9}',
        }
        
        # Extract email
        email_matches = re.findall(patterns["email"], text, re.IGNORECASE)
        if email_matches:
            extracted["email"] = email_matches[0].lower()
        
        # Extract phone numbers
        phone_matches = re.findall(patterns["phone"], text)
        mobile_matches = re.findall(patterns["mobile"], text)
        
        if phone_matches:
            extracted["phone"] = phone_matches[0]
        if mobile_matches:
            extracted["mobile"] = mobile_matches[0]
        
        # Extract website
        website_matches = re.findall(patterns["website"], text, re.IGNORECASE)
        if website_matches:
            website = website_matches[0]
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            extracted["website"] = website
        
        # Extract name, company, and designation using heuristics
        self._extract_name_company_designation(lines, extracted)
        
        # Extract address (remaining lines that don't match other patterns)
        address_lines = self._extract_address(lines, extracted)
        if address_lines:
            extracted["address"] = ", ".join(address_lines)
        
        return extracted
    
    def _extract_name_company_designation(self, lines: List[str], extracted: Dict[str, Any]) -> None:
        """Extract name, company, and designation using heuristics"""
        
        # Common designation patterns
        designation_patterns = [
            r'\b(?:CEO|CTO|CFO|COO|VP|President|Director|Manager|Engineer|Developer|Analyst|Consultant|Executive|Officer|Head|Lead|Senior|Junior|Assistant)\b',
            r'\b(?:Chief|Senior|Lead|Principal|Associate|Executive|Regional|National|International)\s+\w+',
        ]
        
        # Company indicators
        company_indicators = [
            r'\b(?:Ltd|Limited|Inc|Incorporated|Corp|Corporation|LLC|LLP|Pvt|Private|Co|Company|Group|Solutions|Technologies|Tech|Software|Systems|Services|Enterprises|Industries)\b',
            r'\b(?:& Co|and Co|& Sons|and Sons|& Associates|and Associates)\b'
        ]
        
        name_line = None
        company_line = None
        designation_line = None
        
        for i, line in enumerate(lines):
            # Skip lines that are clearly not names (contain email, phone, website)
            if any(pattern in line.lower() for pattern in ['@', 'www.', '.com', '+91']):
                continue
            
            # Check for designation patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in designation_patterns):
                designation_line = line
                continue
            
            # Check for company patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in company_indicators):
                company_line = line
                continue
            
            # First non-matching line is likely the name (if it looks like a name)
            if name_line is None and self._looks_like_name(line):
                name_line = line
                continue
            
            # Second non-matching line might be company if not already found
            if company_line is None and name_line is not None:
                company_line = line
        
        # Assign extracted values
        if name_line:
            extracted["full_name"] = name_line.strip()
        if company_line:
            extracted["company_name"] = company_line.strip()
        if designation_line:
            extracted["designation"] = designation_line.strip()
    
    def _looks_like_name(self, line: str) -> bool:
        """Check if a line looks like a person's name"""
        
        # Basic heuristics for name detection
        words = line.split()
        
        # Should have 1-4 words
        if len(words) < 1 or len(words) > 4:
            return False
        
        # Should be mostly alphabetic
        if not all(word.replace('.', '').isalpha() for word in words):
            return False
        
        # Should not contain common non-name words
        non_name_words = {'the', 'and', 'or', 'of', 'in', 'at', 'to', 'for', 'with', 'by'}
        if any(word.lower() in non_name_words for word in words):
            return False
        
        return True
    
    def _extract_address(self, lines: List[str], extracted: Dict[str, Any]) -> List[str]:
        """Extract address lines from remaining text"""
        
        address_lines = []
        
        for line in lines:
            # Skip lines that are already identified
            if line == extracted.get("full_name") or \
               line == extracted.get("company_name") or \
               line == extracted.get("designation"):
                continue
            
            # Skip lines with email, phone, website
            if any(pattern in line.lower() for pattern in ['@', 'www.', '.com']) or \
               re.search(r'\d{10}|\+91', line):
                continue
            
            # Remaining lines are likely address
            address_lines.append(line)
        
        return address_lines
    
    def _calculate_confidence_score(self, extracted_data: Dict[str, Any], raw_text: str) -> float:
        """Calculate confidence score based on extracted data quality"""
        
        score = 0.0
        max_score = 100.0
        
        # Check for presence of key fields
        if extracted_data.get("full_name"):
            score += 20.0
        if extracted_data.get("company_name"):
            score += 20.0
        if extracted_data.get("email"):
            score += 25.0
        if extracted_data.get("phone") or extracted_data.get("mobile"):
            score += 20.0
        if extracted_data.get("designation"):
            score += 10.0
        if extracted_data.get("website"):
            score += 5.0
        
        # Quality checks
        if len(raw_text.strip()) > 50:  # Sufficient text extracted
            score *= 1.0
        elif len(raw_text.strip()) > 20:
            score *= 0.8
        else:
            score *= 0.5
        
        return min(score / max_score, 1.0)  # Normalize to 0-1 range
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")


# Global service instance
ocr_service = BusinessCardOCRService()


class EmailAttachmentOCRService:
    """Extended OCR service for processing email attachments"""
    
    def __init__(self):
        self.business_card_service = ocr_service
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.pdf']
    
    async def process_email_attachment(self, attachment_id: int) -> Dict[str, Any]:
        """
        Process email attachment for OCR text extraction
        
        Args:
            attachment_id: Email attachment ID
            
        Returns:
            Dict containing extracted text and metadata
        """
        from app.models.email import EmailAttachment
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get attachment from database
            attachment = db.query(EmailAttachment).filter(
                EmailAttachment.id == attachment_id
            ).first()
            
            if not attachment:
                return {
                    "success": False,
                    "error": "Attachment not found"
                }
            
            # Check if file format is supported
            file_ext = os.path.splitext(attachment.original_filename.lower())[1]
            if file_ext not in self.supported_formats:
                return {
                    "success": False,
                    "error": f"Unsupported file format: {file_ext}"
                }
            
            # Create temporary file
            temp_dir = "/tmp/email_ocr"
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, f"attachment_{attachment_id}{file_ext}")
            
            try:
                # Write attachment data to temporary file
                with open(temp_file_path, 'wb') as f:
                    f.write(attachment.file_data)
                
                # Process based on file type
                if file_ext == '.pdf':
                    extracted_text = await self._extract_text_from_pdf(temp_file_path)
                else:
                    extracted_text = await self._extract_text_from_image(temp_file_path)
                
                # Update attachment record with extracted text
                if hasattr(attachment, 'extracted_text'):
                    attachment.extracted_text = extracted_text
                    attachment.ocr_processed = True
                    attachment.ocr_processed_at = datetime.now()
                    db.commit()
                
                return {
                    "success": True,
                    "extracted_text": extracted_text,
                    "attachment_id": attachment_id,
                    "filename": attachment.original_filename,
                    "text_length": len(extracted_text) if extracted_text else 0
                }
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error processing attachment {attachment_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using multiple methods"""
        try:
            import fitz  # PyMuPDF
            
            extracted_text = ""
            pdf_document = fitz.open(file_path)
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # First try to extract text directly
                page_text = page.get_text()
                if page_text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                else:
                    # If no text found, try OCR on page image
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    
                    # Save as temporary image for OCR
                    temp_img_path = f"{file_path}_page_{page_num}.png"
                    with open(temp_img_path, 'wb') as img_file:
                        img_file.write(img_data)
                    
                    try:
                        page_text = await self.business_card_service._extract_text_from_image(temp_img_path)
                        if page_text.strip():
                            extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n{page_text}"
                    finally:
                        if os.path.exists(temp_img_path):
                            os.unlink(temp_img_path)
            
            pdf_document.close()
            return extracted_text.strip()
            
        except ImportError:
            logger.warning("PyMuPDF not available, falling back to image conversion")
            # Fallback: convert PDF to image and use OCR
            return await self._extract_text_from_image(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    async def _extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image file using OCR"""
        return await self.business_card_service._extract_text_from_image(file_path)
    
    async def batch_process_attachments(self, attachment_ids: List[int]) -> Dict[str, Any]:
        """
        Process multiple email attachments for OCR in batch
        
        Args:
            attachment_ids: List of attachment IDs to process
            
        Returns:
            Dict containing batch processing results
        """
        results = {
            "success": True,
            "processed": [],
            "failed": [],
            "total_attachments": len(attachment_ids)
        }
        
        for attachment_id in attachment_ids:
            try:
                result = await self.process_email_attachment(attachment_id)
                if result["success"]:
                    results["processed"].append({
                        "attachment_id": attachment_id,
                        "text_length": result.get("text_length", 0)
                    })
                else:
                    results["failed"].append({
                        "attachment_id": attachment_id,
                        "error": result.get("error", "Unknown error")
                    })
            except Exception as e:
                results["failed"].append({
                    "attachment_id": attachment_id,
                    "error": str(e)
                })
        
        results["success"] = len(results["failed"]) == 0
        return results
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported for OCR"""
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in self.supported_formats

# Global email attachment OCR service instance
email_attachment_ocr_service = EmailAttachmentOCRService()