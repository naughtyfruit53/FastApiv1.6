# app/services/aftership_service.py

"""
AfterShip Integration Service
Provides shipment tracking functionality using AfterShip API
"""

import os
import logging
import hmac
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import aiohttp
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class AfterShipService:
    """Service for integrating with AfterShip tracking API"""
    
    BASE_URL = "https://api.aftership.com/v4"
    
    def __init__(self):
        self.api_key = os.getenv("AFTERSHIP_API_KEY", "")
        self.webhook_secret = os.getenv("AFTERSHIP_WEBHOOK_SECRET", "")
        self.enabled = os.getenv("AFTERSHIP_ENABLED", "false").lower() == "true"
        
        if self.enabled and not self.api_key:
            logger.warning("AfterShip is enabled but API key is not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers for AfterShip API"""
        return {
            "aftership-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    async def create_tracking(
        self,
        tracking_number: str,
        slug: Optional[str] = None,
        title: Optional[str] = None,
        order_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        destination_country: str = "IN",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new tracking in AfterShip
        
        Args:
            tracking_number: The shipment tracking number
            slug: Carrier slug (e.g., 'blue-dart', 'fedex'). Auto-detected if not provided
            title: Custom title for the tracking
            order_id: Reference order ID (e.g., PO number)
            customer_name: Name of the customer
            destination_country: ISO 2-letter country code
            **kwargs: Additional tracking parameters
        
        Returns:
            Dict containing tracking information
        """
        if not self.enabled:
            logger.info("AfterShip is disabled, returning mock tracking data")
            return self._mock_tracking_response(tracking_number, slug)
        
        url = f"{self.BASE_URL}/trackings"
        
        payload = {
            "tracking": {
                "tracking_number": tracking_number,
                "destination_country_iso3": destination_country,
            }
        }
        
        # Add optional fields if provided
        if slug:
            payload["tracking"]["slug"] = slug
        if title:
            payload["tracking"]["title"] = title
        if order_id:
            payload["tracking"]["order_id"] = order_id
        if customer_name:
            payload["tracking"]["customer_name"] = customer_name
        
        # Add any additional parameters
        payload["tracking"].update(kwargs)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"Successfully created tracking for {tracking_number}")
                        return data.get("data", {}).get("tracking", {})
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("meta", {}).get("message", "Unknown error")
                        logger.error(f"Failed to create tracking: {error_msg}")
                        raise HTTPException(status_code=response.status, detail=error_msg)
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error creating tracking: {e}")
            raise HTTPException(status_code=500, detail="Failed to communicate with tracking service")
    
    async def get_tracking(
        self,
        slug: str,
        tracking_number: str
    ) -> Dict[str, Any]:
        """
        Get tracking information for a shipment
        
        Args:
            slug: Carrier slug (e.g., 'blue-dart')
            tracking_number: The tracking number
        
        Returns:
            Dict containing tracking details with checkpoints
        """
        if not self.enabled:
            return self._mock_tracking_response(tracking_number, slug, status="InTransit")
        
        url = f"{self.BASE_URL}/trackings/{slug}/{tracking_number}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("tracking", {})
                    elif response.status == 404:
                        raise HTTPException(status_code=404, detail="Tracking not found")
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("meta", {}).get("message", "Unknown error")
                        raise HTTPException(status_code=response.status, detail=error_msg)
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching tracking: {e}")
            raise HTTPException(status_code=500, detail="Failed to communicate with tracking service")
    
    async def update_tracking(
        self,
        slug: str,
        tracking_number: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update tracking information
        
        Args:
            slug: Carrier slug
            tracking_number: The tracking number
            **kwargs: Fields to update (title, customer_name, etc.)
        
        Returns:
            Dict containing updated tracking information
        """
        if not self.enabled:
            return self._mock_tracking_response(tracking_number, slug)
        
        url = f"{self.BASE_URL}/trackings/{slug}/{tracking_number}"
        
        payload = {"tracking": kwargs}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    json=payload,
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("tracking", {})
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("meta", {}).get("message", "Unknown error")
                        raise HTTPException(status_code=response.status, detail=error_msg)
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error updating tracking: {e}")
            raise HTTPException(status_code=500, detail="Failed to communicate with tracking service")
    
    async def delete_tracking(
        self,
        slug: str,
        tracking_number: str
    ) -> bool:
        """
        Delete a tracking
        
        Args:
            slug: Carrier slug
            tracking_number: The tracking number
        
        Returns:
            True if successful
        """
        if not self.enabled:
            return True
        
        url = f"{self.BASE_URL}/trackings/{slug}/{tracking_number}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        logger.info(f"Successfully deleted tracking {tracking_number}")
                        return True
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("meta", {}).get("message", "Unknown error")
                        logger.error(f"Failed to delete tracking: {error_msg}")
                        return False
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error deleting tracking: {e}")
            return False
    
    async def get_trackings(
        self,
        fields: Optional[List[str]] = None,
        tag: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get list of trackings with filters
        
        Args:
            fields: Specific fields to return
            tag: Filter by tag (Pending, InTransit, OutForDelivery, Delivered, etc.)
            keyword: Search keyword
            limit: Maximum number of results (1-200)
            **kwargs: Additional filter parameters
        
        Returns:
            Dict containing list of trackings and pagination info
        """
        if not self.enabled:
            return {"trackings": [], "count": 0}
        
        url = f"{self.BASE_URL}/trackings"
        
        params = {"limit": min(limit, 200)}
        if fields:
            params["fields"] = ",".join(fields)
        if tag:
            params["tag"] = tag
        if keyword:
            params["keyword"] = keyword
        
        params.update(kwargs)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {})
                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("meta", {}).get("message", "Unknown error")
                        raise HTTPException(status_code=response.status, detail=error_msg)
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching trackings: {e}")
            raise HTTPException(status_code=500, detail="Failed to communicate with tracking service")
    
    async def detect_courier(
        self,
        tracking_number: str
    ) -> List[Dict[str, str]]:
        """
        Auto-detect courier from tracking number
        
        Args:
            tracking_number: The tracking number
        
        Returns:
            List of possible couriers with slug and name
        """
        if not self.enabled:
            # Mock response for common Indian carriers
            if tracking_number.startswith("BD"):
                return [{"slug": "blue-dart", "name": "Blue Dart"}]
            elif tracking_number.startswith("FDX"):
                return [{"slug": "fedex", "name": "FedEx"}]
            else:
                return [{"slug": "india-post", "name": "India Post"}]
        
        url = f"{self.BASE_URL}/couriers/detect"
        
        payload = {"tracking": {"tracking_number": tracking_number}}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("couriers", [])
                    else:
                        logger.warning(f"Could not detect courier for {tracking_number}")
                        return []
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error detecting courier: {e}")
            return []
    
    async def get_couriers(self) -> List[Dict[str, Any]]:
        """
        Get list of all supported couriers
        
        Returns:
            List of courier information
        """
        if not self.enabled:
            # Return common Indian couriers
            return [
                {"slug": "blue-dart", "name": "Blue Dart", "country": "IN"},
                {"slug": "fedex", "name": "FedEx", "country": None},
                {"slug": "dhl", "name": "DHL Express", "country": None},
                {"slug": "india-post", "name": "India Post", "country": "IN"},
                {"slug": "dtdc", "name": "DTDC", "country": "IN"},
            ]
        
        url = f"{self.BASE_URL}/couriers/all"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", {}).get("couriers", [])
                    else:
                        return []
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching couriers: {e}")
            return []
    
    async def bulk_create_trackings(
        self,
        trackings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple trackings in bulk
        
        Args:
            trackings: List of tracking objects to create
        
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            "success": [],
            "failed": [],
            "total": len(trackings),
            "success_count": 0,
            "failed_count": 0
        }
        
        for tracking in trackings:
            try:
                tracking_number = tracking.get("tracking_number")
                slug = tracking.get("slug")
                
                result = await self.create_tracking(
                    tracking_number=tracking_number,
                    slug=slug,
                    **{k: v for k, v in tracking.items() if k not in ["tracking_number", "slug"]}
                )
                
                results["success"].append({
                    "tracking_number": tracking_number,
                    "id": result.get("id")
                })
                results["success_count"] += 1
                
            except Exception as e:
                results["failed"].append({
                    "tracking_number": tracking.get("tracking_number"),
                    "error": str(e)
                })
                results["failed_count"] += 1
        
        return results
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        Verify webhook signature from AfterShip
        
        Args:
            payload: Raw webhook payload (bytes)
            signature: Signature from webhook header
        
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured, cannot verify signature")
            return True  # Allow webhook if secret not configured
        
        computed_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    
    def _mock_tracking_response(
        self,
        tracking_number: str,
        slug: Optional[str] = None,
        status: str = "Pending"
    ) -> Dict[str, Any]:
        """Generate mock tracking response for testing"""
        return {
            "id": f"mock_{tracking_number}",
            "tracking_number": tracking_number,
            "slug": slug or "mock-carrier",
            "active": True,
            "tag": status,
            "subtag": f"{status}_001",
            "expected_delivery": None,
            "tracking_link": f"https://track.aftership.com/{slug or 'mock'}/{tracking_number}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "checkpoints": []
        }


# Singleton instance
aftership_service = AfterShipService()
