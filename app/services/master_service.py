# app/services/master_service.py

"""
Master Data Service for advanced operations including external API integrations
"""

import requests
from functools import lru_cache
from typing import List, Dict, Any
import logging
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1000)  # In-memory cache for HSN lookups (max 1000 entries)
async def search_hsn_codes(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search HSN codes via FastGST API
    Returns list of dicts with hsn_code, description, gst_rate
    """
    try:
        # Clean query: allow HSN code or description search
        # If query looks like HSN (numeric), use /hsn/{query}; else use search
        if query.isdigit():
            url = f"{settings.FASTGST_API_URL}/hsn/{query}"
            response = requests.get(url, timeout=5)
            logger.info(f"HSN single lookup: {url} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    hsn_data = data['data']
                    return [{
                        'hsn_code': hsn_data.get('hsn_code', query),
                        'description': hsn_data.get('description', 'No description available'),
                        'gst_rate': float(hsn_data.get('gst_rate', 0.0))  # Ensure float for GST rate
                    }]
            logger.warning(f"HSN single lookup failed: {response.text}")
            return []
        else:
            # For description search, use /search?query=... (assuming FastGST has a search endpoint; adjust if needed)
            url = f"{settings.FASTGST_API_URL}/search"
            params = {'query': query, 'limit': limit}
            response = requests.get(url, params=params, timeout=5)
            logger.info(f"HSN search: {url} params={params} - Status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"HSN search API error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="HSN search API error")
        
        data = response.json()
        if not data.get('success') or not data.get('data'):
            return []
        
        # Format results: extract hsn_code, description, gst_rate
        results = []
        for item in data['data'][:limit]:
            results.append({
                'hsn_code': item.get('hsn_code', ''),
                'description': item.get('description', 'No description'),
                'gst_rate': float(item.get('gst_rate', 0.0))
            })
        
        return results
    
    except requests.RequestException as e:
        logger.error(f"FastGST API request failed: {str(e)}")
        raise HTTPException(status_code=503, detail="HSN search service unavailable - please enter manually")
    except Exception as e:
        logger.error(f"Unexpected error in HSN search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error in HSN search")