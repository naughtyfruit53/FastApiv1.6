# app/utils/text_processing.py

"""
Text processing utilities for email content
"""

import re
import html
from typing import Optional
from bs4 import BeautifulSoup


def extract_plain_text(html_content: str) -> str:
    """
    Extract plain text from HTML content
    """
    if not html_content:
        return ""
    
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing spaces
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception:
        # Fallback: simple regex-based HTML stripping
        text = re.sub('<[^<]+?>', '', html_content)
        text = html.unescape(text)
        return ' '.join(text.split())


def sanitize_html(html_content: str, allowed_tags: Optional[list] = None, allowed_attributes: Optional[dict] = None) -> str:
    """
    Sanitize HTML content for safe display
    """
    if not html_content:
        return ""
    
    try:
        # Use BeautifulSoup for more robust HTML parsing
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Default allowed tags for email content
        if allowed_tags is None:
            allowed_tags = [
                'p', 'br', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'strong', 'b', 'em', 'i', 'u', 'ol', 'ul', 'li', 'blockquote',
                'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
            ]
        
        if allowed_attributes is None:
            allowed_attributes = {
                'a': ['href', 'title'],
                'img': ['src', 'alt', 'width', 'height'],
                'table': ['border', 'cellpadding', 'cellspacing']
            }
        
        # Remove disallowed tags
        for tag in soup.find_all():
            if tag.name not in allowed_tags:
                tag.unwrap()  # Remove tag but keep content
            else:
                # Remove disallowed attributes
                tag_allowed_attrs = allowed_attributes.get(tag.name, [])
                tag_allowed_attrs.extend(allowed_attributes.get('*', []))
                
                attrs_to_remove = []
                for attr in tag.attrs:
                    if attr not in tag_allowed_attrs:
                        attrs_to_remove.append(attr)
                
                for attr in attrs_to_remove:
                    del tag[attr]
        
        # Remove potentially dangerous content
        for tag in soup.find_all():
            # Remove javascript: links
            if tag.name == 'a' and tag.get('href', '').startswith('javascript:'):
                tag['href'] = '#'
            
            # Remove data: URIs from images (potential XSS)
            if tag.name == 'img' and tag.get('src', '').startswith('data:'):
                tag['src'] = ''
        
        return str(soup)
        
    except Exception:
        # Fallback: return plain text
        return extract_plain_text(html_content)


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to specified length with ellipsis
    """
    if not text or len(text) <= max_length:
        return text or ""
    
    truncated = text[:max_length - 3].rsplit(' ', 1)[0]
    return truncated + "..."


def clean_email_subject(subject: str) -> str:
    """
    Clean email subject by removing Re:, Fwd: prefixes
    """
    if not subject:
        return ""
    
    # Remove common prefixes
    cleaned = re.sub(r'^(Re:|Fwd?:|RE:|FWD?:)\s*', '', subject, flags=re.IGNORECASE).strip()
    
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned


def extract_email_addresses(text: str) -> list:
    """
    Extract email addresses from text using regex
    """
    if not text:
        return []
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def is_auto_reply(subject: str, body: str) -> bool:
    """
    Detect if email is an auto-reply/out-of-office message
    """
    if not subject and not body:
        return False
    
    text_to_check = f"{subject} {body}".lower()
    
    auto_reply_indicators = [
        'out of office', 'auto reply', 'automatic reply', 'away message',
        'vacation', 'holiday', 'unavailable', 'do not reply', 'noreply',
        'automated response', 'delivery status notification'
    ]
    
    return any(indicator in text_to_check for indicator in auto_reply_indicators)


def extract_quoted_text(body: str) -> tuple:
    """
    Extract quoted text from email body
    Returns tuple of (new_content, quoted_content)
    """
    if not body:
        return "", ""
    
    # Common patterns for quoted text
    quote_patterns = [
        r'^>.*$',  # Lines starting with >
        r'^On .* wrote:.*$',  # "On ... wrote:" pattern
        r'^From:.*$',  # Forward headers
        r'^\s*-{3,}\s*Original Message\s*-{3,}.*$',  # Original message separator
    ]
    
    lines = body.split('\n')
    new_lines = []
    quoted_lines = []
    in_quote = False
    
    for line in lines:
        # Check if this line starts a quote
        if not in_quote:
            for pattern in quote_patterns:
                if re.match(pattern, line, re.MULTILINE | re.IGNORECASE):
                    in_quote = True
                    break
        
        if in_quote:
            quoted_lines.append(line)
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines).strip(), '\n'.join(quoted_lines).strip()