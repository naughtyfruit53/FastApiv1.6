# app/services/inventory_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal
import logging

from app.models.product_models import Stock  # FIXED: Import Stock from product_models.py where it's defined

logger = logging.getLogger(__name__)

class InventoryService:
    @staticmethod
    async def update_stock(
        db: AsyncSession,
        organization_id: int,
        product_id: int,
        delta: float
    ) -> None:
        """
        Update stock quantity for a product
        
        Args:
            db: Database session
            organization_id: Organization ID
            product_id: Product ID
            delta: Quantity change (negative for debit)
        """
        try:
            delta_dec = Decimal(str(delta))
            
            stmt = select(Stock).where(
                Stock.organization_id == organization_id,
                Stock.product_id == product_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()
            
            if not stock:
                # Create new stock entry if not exists
                stock = Stock(
                    organization_id=organization_id,
                    product_id=product_id,
                    quantity=Decimal('0')
                )
                db.add(stock)
                await db.flush()
            
            stock.quantity += delta_dec
            
            if stock.quantity < 0:
                logger.warning(
                    f"Negative stock {stock.quantity} for product {product_id} in organization {organization_id}"
                )
                # Allow negative stock as per common practice, or raise error if policy differs
            
            # Note: Caller should commit the transaction
            logger.info(f"Updated stock for product {product_id}: delta {delta}, new quantity {stock.quantity}")
            
        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {str(e)}")
            raise

    # Other methods...