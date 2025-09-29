# app/services/email_search_service.py

"""
Advanced Email Search Service with PostgreSQL full-text search
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_, and_

logger = logging.getLogger(__name__)

class EmailSearchService:
    """Advanced search service for emails using PostgreSQL full-text search"""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Lazy initialization of database session"""
        if self.db is None:
            from app.core.database import SessionLocal
            self.db = SessionLocal()
        return self.db
    
    def full_text_search(
        self, 
        query: str, 
        organization_id: int,
        account_ids: Optional[List[int]] = None,
        customer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        has_attachments: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Perform full-text search on emails using PostgreSQL tsvector
        
        Args:
            query: Search query string
            organization_id: Organization ID for multi-tenant filtering
            account_ids: Optional list of email account IDs to search within
            customer_id: Optional customer ID to filter by
            vendor_id: Optional vendor ID to filter by
            date_from: Optional start date filter (ISO format)
            date_to: Optional end date filter (ISO format)
            has_attachments: Optional filter for emails with/without attachments
            limit: Maximum number of results to return
            offset: Pagination offset
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            from app.models.email import Email
            
            db = self._get_db()
            # Build base query with full-text search
            search_vector = func.to_tsvector('english', 
                func.coalesce(Email.subject, '') + ' ' + 
                func.coalesce(Email.body_text, '') + ' ' +
                func.coalesce(Email.sender_name, '') + ' ' +
                func.coalesce(Email.sender_email, '')
            )
            
            search_query = func.plainto_tsquery('english', query)
            
            base_query = db.query(Email).filter(
                Email.organization_id == organization_id,
                search_vector.op('@@')(search_query)
            )
            
            # Apply additional filters
            if account_ids:
                base_query = base_query.filter(Email.account_id.in_(account_ids))
            
            if customer_id:
                base_query = base_query.filter(Email.customer_id == customer_id)
            
            if vendor_id:
                base_query = base_query.filter(Email.vendor_id == vendor_id)
            
            if date_from:
                base_query = base_query.filter(Email.sent_at >= date_from)
            
            if date_to:
                base_query = base_query.filter(Email.sent_at <= date_to)
            
            if has_attachments is not None:
                base_query = base_query.filter(Email.has_attachments == has_attachments)
            
            # Count total results
            total_count = base_query.count()
            
            # Get paginated results with ranking
            results = (base_query
                      .add_columns(
                          func.ts_rank(search_vector, search_query).label('rank')
                      )
                      .order_by(text('rank DESC'), Email.sent_at.desc())
                      .limit(limit)
                      .offset(offset)
                      .all())
            
            # Format results
            emails = []
            for email, rank in results:
                email_dict = {
                    'id': email.id,
                    'subject': email.subject,
                    'sender_name': email.sender_name,
                    'sender_email': email.sender_email,
                    'recipient_emails': email.recipient_emails,
                    'body_text': email.body_text[:300] + '...' if email.body_text and len(email.body_text) > 300 else email.body_text,
                    'sent_at': email.sent_at,
                    'received_at': email.received_at,
                    'has_attachments': email.has_attachments,
                    'status': email.status.value,
                    'customer_id': email.customer_id,
                    'vendor_id': email.vendor_id,
                    'account_id': email.account_id,
                    'search_rank': float(rank) if rank else 0
                }
                
                # Add snippet/highlighting info
                email_dict['snippet'] = self._generate_search_snippet(
                    email.body_text or '', query, 200
                )
                
                emails.append(email_dict)
            
            return {
                'success': True,
                'emails': emails,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error performing full-text search: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'emails': [],
                'total_count': 0
            }
    
    def search_attachments(
        self, 
        query: str, 
        organization_id: int,
        file_types: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search email attachments by filename and extracted content
        
        Args:
            query: Search query string
            organization_id: Organization ID for multi-tenant filtering
            file_types: Optional list of file extensions to filter by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Dict containing attachment search results
        """
        try:
            # Build attachment search query
            base_query = (self.db.query(EmailAttachment, Email)
                         .join(Email, EmailAttachment.email_id == Email.id)
                         .filter(Email.organization_id == organization_id))
            
            # Full-text search on filename and extracted content
            search_conditions = [
                EmailAttachment.original_filename.ilike(f'%{query}%'),
                EmailAttachment.filename.ilike(f'%{query}%')
            ]
            
            # If attachment has extracted text content, search that too
            if hasattr(EmailAttachment, 'extracted_text'):
                search_vector = func.to_tsvector('english', 
                    func.coalesce(EmailAttachment.extracted_text, ''))
                search_query = func.plainto_tsquery('english', query)
                search_conditions.append(search_vector.op('@@')(search_query))
            
            base_query = base_query.filter(or_(*search_conditions))
            
            # Apply file type filter
            if file_types:
                file_type_conditions = []
                for file_type in file_types:
                    file_type_conditions.append(
                        EmailAttachment.original_filename.ilike(f'%.{file_type}')
                    )
                base_query = base_query.filter(or_(*file_type_conditions))
            
            # Count total results
            total_count = base_query.count()
            
            # Get paginated results
            results = (base_query
                      .order_by(EmailAttachment.created_at.desc())
                      .limit(limit)
                      .offset(offset)
                      .all())
            
            # Format results
            attachments = []
            for attachment, email in results:
                attachment_dict = {
                    'id': attachment.id,
                    'filename': attachment.original_filename,
                    'content_type': attachment.content_type,
                    'size_bytes': attachment.size_bytes,
                    'created_at': attachment.created_at,
                    'is_safe': attachment.is_safe,
                    'download_count': attachment.download_count,
                    'email': {
                        'id': email.id,
                        'subject': email.subject,
                        'sender_name': email.sender_name,
                        'sender_email': email.sender_email,
                        'sent_at': email.sent_at
                    }
                }
                
                # Add extracted text snippet if available
                if hasattr(attachment, 'extracted_text') and attachment.extracted_text:
                    attachment_dict['text_snippet'] = self._generate_search_snippet(
                        attachment.extracted_text, query, 150
                    )
                
                attachments.append(attachment_dict)
            
            return {
                'success': True,
                'attachments': attachments,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error searching attachments: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'attachments': [],
                'total_count': 0
            }
    
    def search_by_customer_vendor(
        self, 
        organization_id: int,
        customer_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search emails linked to specific customers or vendors
        
        Args:
            organization_id: Organization ID for multi-tenant filtering
            customer_id: Optional customer ID to search by
            vendor_id: Optional vendor ID to search by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            Dict containing email results linked to customer/vendor
        """
        try:
            base_query = self.db.query(Email).filter(
                Email.organization_id == organization_id
            )
            
            if customer_id:
                base_query = base_query.filter(Email.customer_id == customer_id)
            
            if vendor_id:
                base_query = base_query.filter(Email.vendor_id == vendor_id)
            
            # Count total results
            total_count = base_query.count()
            
            # Get paginated results
            emails = (base_query
                     .order_by(Email.sent_at.desc())
                     .limit(limit)
                     .offset(offset)
                     .all())
            
            # Format results
            email_list = []
            for email in emails:
                email_dict = {
                    'id': email.id,
                    'subject': email.subject,
                    'sender_name': email.sender_name,
                    'sender_email': email.sender_email,
                    'recipient_emails': email.recipient_emails,
                    'body_text': email.body_text[:300] + '...' if email.body_text and len(email.body_text) > 300 else email.body_text,
                    'sent_at': email.sent_at,
                    'received_at': email.received_at,
                    'has_attachments': email.has_attachments,
                    'status': email.status.value,
                    'customer_id': email.customer_id,
                    'vendor_id': email.vendor_id,
                    'account_id': email.account_id
                }
                email_list.append(email_dict)
            
            return {
                'success': True,
                'emails': email_list,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error searching by customer/vendor: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'emails': [],
                'total_count': 0
            }
    
    def suggest_search_terms(self, partial_query: str, organization_id: int) -> List[str]:
        """
        Generate search term suggestions based on email content
        
        Args:
            partial_query: Partial search query
            organization_id: Organization ID for multi-tenant filtering
            
        Returns:
            List of suggested search terms
        """
        try:
            suggestions = []
            
            # Get suggestions from email subjects
            subject_query = (self.db.query(Email.subject)
                           .filter(
                               Email.organization_id == organization_id,
                               Email.subject.ilike(f'%{partial_query}%')
                           )
                           .distinct()
                           .limit(5)
                           .all())
            
            for result in subject_query:
                if result.subject:
                    suggestions.append(result.subject)
            
            # Get suggestions from sender names
            sender_query = (self.db.query(Email.sender_name)
                          .filter(
                              Email.organization_id == organization_id,
                              Email.sender_name.ilike(f'%{partial_query}%')
                          )
                          .distinct()
                          .limit(3)
                          .all())
            
            for result in sender_query:
                if result.sender_name:
                    suggestions.append(result.sender_name)
            
            return list(set(suggestions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error generating search suggestions: {str(e)}")
            return []
    
    def _generate_search_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """
        Generate a search snippet with highlighted query terms
        
        Args:
            text: Full text content
            query: Search query
            max_length: Maximum snippet length
            
        Returns:
            Text snippet with query context
        """
        if not text or not query:
            return text[:max_length] if text else ""
        
        # Find the first occurrence of any query term
        query_terms = query.lower().split()
        text_lower = text.lower()
        
        best_position = -1
        for term in query_terms:
            position = text_lower.find(term)
            if position != -1:
                if best_position == -1 or position < best_position:
                    best_position = position
        
        if best_position == -1:
            # No match found, return beginning of text
            return text[:max_length] + ('...' if len(text) > max_length else '')
        
        # Calculate snippet boundaries
        start = max(0, best_position - max_length // 2)
        end = min(len(text), start + max_length)
        
        snippet = text[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            snippet = '...' + snippet
        if end < len(text):
            snippet = snippet + '...'
        
        return snippet
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

# Global email search service instance
email_search_service = EmailSearchService()