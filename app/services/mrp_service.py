# app/services/mrp_service.py
"""
Material Requirements Planning (MRP) Service

This service handles automatic calculation of material requirements from BOMs,
demand forecasting, inventory levels, and generates shortage alerts and 
purchase requisitions as needed.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
import logging
import math

from app.models.vouchers.manufacturing_planning import (
    ManufacturingOrder, BillOfMaterials, BOMComponent
)
from app.models.product_models import Product, Stock  # FIXED: Import Stock from product_models.py where it's defined
from app.models.enhanced_inventory_models import InventoryAlert
from app.schemas.inventory import AlertType, AlertStatus, AlertPriority

logger = logging.getLogger(__name__)


class MaterialRequirement:
    """Data class for material requirements"""
    def __init__(
        self,
        product_id: int,
        product_name: str,
        required_quantity: float,
        available_quantity: float,
        unit: str,
        shortage_quantity: float = 0.0,
        manufacturing_orders: List[int] = None
    ):
        self.product_id = product_id
        self.product_name = product_name
        self.required_quantity = required_quantity
        self.available_quantity = available_quantity
        self.unit = unit
        self.shortage_quantity = shortage_quantity
        self.manufacturing_orders = manufacturing_orders or []


class MRPService:
    """Material Requirements Planning Service"""

    @staticmethod
    async def calculate_material_requirements(
        db: AsyncSession,
        organization_id: int,
        manufacturing_order_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MaterialRequirement]:
        """
        Calculate material requirements from manufacturing orders
        
        Args:
            db: Database session
            organization_id: Organization ID
            manufacturing_order_ids: Specific MO IDs to calculate (if None, calculates for all active MOs)
            start_date: Filter MOs by planned start date
            end_date: Filter MOs by planned end date
            
        Returns:
            List of MaterialRequirement objects with shortage information
        """
        # Build query for manufacturing orders
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.organization_id == organization_id,
            ManufacturingOrder.production_status.in_(['planned', 'in_progress'])
        )
        
        if manufacturing_order_ids:
            stmt = stmt.where(ManufacturingOrder.id.in_(manufacturing_order_ids))
        
        if start_date:
            stmt = stmt.where(ManufacturingOrder.planned_start_date >= start_date)
        
        if end_date:
            stmt = stmt.where(ManufacturingOrder.planned_end_date <= end_date)
        
        result = await db.execute(stmt)
        manufacturing_orders = result.scalars().all()
        
        # Aggregate material requirements from all MOs
        material_requirements = {}  # product_id -> MaterialRequirement
        
        for mo in manufacturing_orders:
            # Get BOM for this MO
            stmt = select(BillOfMaterials).where(
                BillOfMaterials.id == mo.bom_id,
                BillOfMaterials.organization_id == organization_id
            )
            result = await db.execute(stmt)
            bom = result.scalar_one_or_none()
            
            if not bom:
                logger.warning(f"BOM {mo.bom_id} not found for MO {mo.id}")
                continue
            
            # Get BOM components
            stmt = select(BOMComponent).where(
                BOMComponent.bom_id == bom.id,
                BOMComponent.organization_id == organization_id
            )
            result = await db.execute(stmt)
            components = result.scalars().all()
            
            # Calculate required quantity based on MO planned quantity
            multiplier = (mo.planned_quantity - mo.produced_quantity) / bom.output_quantity
            
            for component in components:
                # Account for wastage
                wastage_factor = 1 + (component.wastage_percentage / 100)
                required_qty = component.quantity_required * multiplier * wastage_factor
                
                # Get product details
                stmt = select(Product).where(Product.id == component.component_item_id)
                result = await db.execute(stmt)
                product = result.scalar_one_or_none()
                
                if not product:
                    continue
                
                # Aggregate requirements
                if component.component_item_id not in material_requirements:
                    material_requirements[component.component_item_id] = {
                        'product': product,
                        'required_quantity': 0.0,
                        'unit': component.unit,
                        'manufacturing_orders': []
                    }
                
                material_requirements[component.component_item_id]['required_quantity'] += required_qty
                material_requirements[component.component_item_id]['manufacturing_orders'].append(mo.id)
        
        # Check available stock for each material
        requirements_list = []
        
        for product_id, req_data in material_requirements.items():
            # Get current stock
            stmt = select(Stock).where(
                Stock.organization_id == organization_id,
                Stock.product_id == product_id
            )
            result = await db.execute(stmt)
            stock_records = result.scalars().all()
            
            available_quantity = sum(s.quantity for s in stock_records)
            
            # Calculate shortage
            shortage = max(0, req_data['required_quantity'] - available_quantity)
            
            material_req = MaterialRequirement(
                product_id=product_id,
                product_name=req_data['product'].product_name,
                required_quantity=req_data['required_quantity'],
                available_quantity=available_quantity,
                unit=req_data['unit'],
                shortage_quantity=shortage,
                manufacturing_orders=req_data['manufacturing_orders']
            )
            
            requirements_list.append(material_req)
        
        return requirements_list

    @staticmethod
    async def calculate_max_producible(
        db: AsyncSession,
        organization_id: int,
        bom_id: int
    ) -> int:
        """Calculate maximum producible units based on current stock"""
        try:
            stmt = select(BillOfMaterials).where(
                BillOfMaterials.id == bom_id,
                BillOfMaterials.organization_id == organization_id
            )
            result = await db.execute(stmt)
            bom = result.scalar_one_or_none()
            
            if not bom:
                raise HTTPException(status_code=404, detail="BOM not found")
            
            stmt = select(BOMComponent).where(BOMComponent.bom_id == bom_id)
            result = await db.execute(stmt)
            components = result.scalars().all()
            
            if not components:
                return 0
            
            max_p = float('inf')
            
            for component in components:
                if component.quantity_required <= 0:
                    continue
                
                wastage_factor = 1 + (component.wastage_percentage / 100)
                req_per_unit = component.quantity_required * wastage_factor
                
                stmt = select(func.sum(Stock.quantity)).where(
                    Stock.product_id == component.component_item_id,
                    Stock.organization_id == organization_id
                )
                result = await db.execute(stmt)
                available = result.scalar() or 0
                
                producible = math.floor(available / req_per_unit)
                max_p = min(max_p, producible)
            
            return int(max_p) if max_p != float('inf') else 0
            
        except Exception as e:
            logger.error(f"Error calculating max producible: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to calculate max producible")

    @staticmethod
    async def check_producible(
        db: AsyncSession,
        organization_id: int,
        bom_id: int,
        quantity: float
    ) -> Dict:
        """Check if quantity is producible and get shortages if not"""
        try:
            max_p = await MRPService.calculate_max_producible(db, organization_id, bom_id)
            is_possible = quantity <= max_p
            
            if is_possible:
                return {
                    "is_possible": True,
                    "max_producible": max_p,
                    "shortages": []
                }
            
            # Calculate shortages
            stmt = select(BillOfMaterials).where(
                BillOfMaterials.id == bom_id,
                BillOfMaterials.organization_id == organization_id
            )
            result = await db.execute(stmt)
            bom = result.scalar_one_or_none()
            
            if not bom:
                raise HTTPException(status_code=404, detail="BOM not found")
            
            stmt = select(BOMComponent).where(BOMComponent.bom_id == bom_id)
            result = await db.execute(stmt)
            components = result.scalars().all()
            
            multiplier = quantity / bom.output_quantity
            shortages = []
            product_ids = []
            
            for component in components:
                wastage_factor = 1 + (component.wastage_percentage / 100)
                req = component.quantity_required * multiplier * wastage_factor
                
                stmt = select(func.sum(Stock.quantity)).where(
                    Stock.product_id == component.component_item_id,
                    Stock.organization_id == organization_id
                )
                result = await db.execute(stmt)
                available = result.scalar() or 0
                
                shortage_qty = max(0, req - available)
                
                if shortage_qty > 0:
                    stmt = select(Product).where(Product.id == component.component_item_id)
                    result = await db.execute(stmt)
                    product = result.scalar_one_or_none()
                    
                    shortages.append({
                        'product_id': component.component_item_id,
                        'product_name': product.product_name if product else 'Unknown',
                        'required': req,
                        'available': available,
                        'shortage': shortage_qty,
                        'unit': component.unit
                    })
                    product_ids.append(component.component_item_id)
            
            # Get PO info if shortages
            if product_ids:
                po_info = await MRPService.check_purchase_orders_for_products(db, organization_id, product_ids)
                
                for shortage in shortages:
                    pid = shortage['product_id']
                    if pid in po_info:
                        shortage['purchase_order_status'] = po_info[pid]
                        
                        # Determine severity
                        pos = po_info[pid]['purchase_orders']
                        has_pending_with_dispatch = any(
                            p['has_dispatch'] and p['grn_status'] in ['pending', 'partial'] for p in pos
                        )
                        has_any_po = len(pos) > 0
                        
                        if has_pending_with_dispatch:
                            shortage['severity'] = 'po_dispatch_grn_pending'
                        elif has_any_po:
                            shortage['severity'] = 'po_no_dispatch'
                        else:
                            shortage['severity'] = 'no_po'
            
            return {
                "is_possible": False,
                "max_producible": max_p,
                "shortages": shortages
            }
            
        except Exception as e:
            logger.error(f"Error checking producible: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to check producible")

    @staticmethod
    async def create_shortage_alerts(
        db: AsyncSession,
        organization_id: int,
        material_requirements: List[MaterialRequirement]
    ) -> List[InventoryAlert]:
        """
        Create or update alerts for material shortages
        
        Args:
            db: Database session
            organization_id: Organization ID
            material_requirements: List of material requirements with shortage info
            
        Returns:
            List of created/updated alerts
        """
        alerts_created = []
        
        for req in material_requirements:
            if req.shortage_quantity <= 0:
                continue
            
            # Check if alert already exists
            stmt = select(InventoryAlert).where(
                InventoryAlert.organization_id == organization_id,
                InventoryAlert.product_id == req.product_id,
                InventoryAlert.alert_type == AlertType.SHORTAGE_FOR_MO,
                InventoryAlert.status == AlertStatus.ACTIVE
            )
            result = await db.execute(stmt)
            existing_alert = result.scalar_one_or_none()
            
            mo_list = ', '.join(f"MO-{mo_id}" for mo_id in req.manufacturing_orders[:5])
            if len(req.manufacturing_orders) > 5:
                mo_list += f" and {len(req.manufacturing_orders) - 5} more"
            
            message = (
                f"Material shortage detected for '{req.product_name}'. "
                f"Required: {req.required_quantity:.2f} {req.unit}, "
                f"Available: {req.available_quantity:.2f} {req.unit}, "
                f"Shortage: {req.shortage_quantity:.2f} {req.unit}. "
                f"Affected MOs: {mo_list}"
            )
            
            if existing_alert:
                # Update existing alert
                existing_alert.current_stock = req.available_quantity
                existing_alert.message = message
                existing_alert.suggested_order_quantity = req.shortage_quantity
                existing_alert.updated_at = datetime.utcnow()
                alerts_created.append(existing_alert)
            else:
                # Create new alert
                alert = InventoryAlert(
                    organization_id=organization_id,
                    product_id=req.product_id,
                    alert_type=AlertType.SHORTAGE_FOR_MO,
                    current_stock=req.available_quantity,
                    reorder_level=req.required_quantity,
                    priority=AlertPriority.CRITICAL if req.shortage_quantity > req.required_quantity * 0.5 else AlertPriority.HIGH,
                    message=message,
                    suggested_order_quantity=req.shortage_quantity,
                    status=AlertStatus.ACTIVE
                )
                db.add(alert)
                alerts_created.append(alert)
        
        await db.commit()
        return alerts_created

    @staticmethod
    async def generate_purchase_requisitions_data(
        db: AsyncSession,
        organization_id: int,
        material_requirements: List[MaterialRequirement],
        department: str = "Production",
        priority: str = "high"
    ) -> Dict:
        """
        Generate purchase requisition data from material shortages
        
        Args:
            db: Database session
            organization_id: Organization ID
            material_requirements: List of material requirements with shortage info
            department: Department requesting materials
            priority: Priority level
            
        Returns:
            Dictionary with purchase requisition data ready to be created
        """
        pr_items = []
        
        for req in material_requirements:
            if req.shortage_quantity <= 0:
                continue
            
            # Get product details for unit price
            stmt = select(Product).where(Product.id == req.product_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()
            
            if not product:
                continue
            
            pr_items.append({
                'product_id': req.product_id,
                'product_name': req.product_name,
                'quantity': req.shortage_quantity,
                'unit': req.unit,
                'estimated_unit_price': product.unit_price,
                'estimated_total_price': req.shortage_quantity * product.unit_price,
                'required_date': datetime.now() + timedelta(days=7),  # Default 7 days
                'justification': f"Required for Manufacturing Orders: {', '.join(map(str, req.manufacturing_orders[:5]))}"
            })
        
        if not pr_items:
            return None
        
        total_estimated_budget = sum(item['estimated_total_price'] for item in pr_items)
        
        pr_data = {
            'requisition_date': datetime.now().date(),
            'required_date': (datetime.now() + timedelta(days=7)).date(),
            'department': department,
            'purpose': 'Material procurement for manufacturing orders',
            'justification': f'Auto-generated from MRP analysis. {len(pr_items)} items required for production.',
            'estimated_budget': total_estimated_budget,
            'priority': priority,
            'items': pr_items
        }
        
        return pr_data

    @staticmethod
    async def check_purchase_orders_for_products(
        db: AsyncSession,
        organization_id: int,
        product_ids: List[int]
    ) -> Dict[int, Dict]:
        """
        Check if purchase orders exist for given products
        
        Args:
            db: Database session
            organization_id: Organization ID
            product_ids: List of product IDs to check
            
        Returns:
            Dictionary mapping product_id to purchase order info
        """
        from app.models.vouchers.purchase import PurchaseOrder, PurchaseOrderItem
        
        if not product_ids:
            return {}
        
        # Get pending purchase orders for these products
        stmt = select(PurchaseOrderItem, PurchaseOrder).join(
            PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id
        ).where(
            PurchaseOrder.organization_id == organization_id,
            PurchaseOrderItem.product_id.in_(product_ids),
            PurchaseOrder.status.in_(['draft', 'pending', 'approved', 'partially_received']),
            PurchaseOrderItem.pending_quantity > 0
        )
        
        result = await db.execute(stmt)
        po_items = result.all()
        
        # Aggregate by product
        po_info = {}
        for item, po in po_items:
            pid = item.product_id
            if pid not in po_info:
                po_info[pid] = {
                    'has_order': True,
                    'total_on_order': 0.0,
                    'purchase_orders': []
                }
            
            po_info[pid]['total_on_order'] += item.pending_quantity
            po_info[pid]['purchase_orders'].append({
                'po_number': po.voucher_number,
                'po_id': po.id,
                'quantity': item.pending_quantity,
                'status': po.status,
                'delivery_date': po.delivery_date.isoformat() if po.delivery_date else None,
                'has_dispatch': po.has_dispatch if hasattr(po, 'has_dispatch') else False,  # Assume field
                'grn_status': po.grn_status if hasattr(po, 'grn_status') else 'pending'  # Assume field
            })
        
        # Add entries for products without orders
        for product_id in product_ids:
            if product_id not in po_info:
                po_info[product_id] = {
                    'has_order': False,
                    'total_on_order': 0.0,
                    'purchase_orders': []
                }
        
        return po_info

    @staticmethod
    async def check_material_availability_for_mo(
        db: AsyncSession,
        organization_id: int,
        manufacturing_order_id: int,
        include_po_status: bool = True
    ) -> Tuple[bool, List[Dict]]:
        """
        Check if all materials are available for a specific manufacturing order
        
        Args:
            db: Database session
            organization_id: Organization ID
            manufacturing_order_id: Manufacturing order ID
            include_po_status: Whether to include purchase order status for shortage items
            
        Returns:
            Tuple of (is_available: bool, shortage_details: List[Dict])
        """
        requirements = await MRPService.calculate_material_requirements(
            db, organization_id, [manufacturing_order_id]
        )
        
        shortages = []
        has_shortage = False
        shortage_product_ids = []
        
        for req in requirements:
            if req.shortage_quantity > 0:
                has_shortage = True
                shortage_product_ids.append(req.product_id)
                shortages.append({
                    'product_id': req.product_id,
                    'product_name': req.product_name,
                    'required': req.required_quantity,
                    'available': req.available_quantity,
                    'shortage': req.shortage_quantity,
                    'unit': req.unit
                })
        
        # Check purchase order status for shortage items
        if include_po_status and shortage_product_ids:
            po_info = await MRPService.check_purchase_orders_for_products(
                db, organization_id, shortage_product_ids
            )
            
            for shortage in shortages:
                pid = shortage['product_id']
                if pid in po_info:
                    shortage['purchase_order_status'] = po_info[pid]
                    
                    # Determine severity
                    pos = po_info[pid]['purchase_orders']
                    has_pending_with_dispatch = any(
                        p['has_dispatch'] and p['grn_status'] in ['pending', 'partial'] for p in pos
                    )
                    has_any_po = len(pos) > 0
                    
                    if has_pending_with_dispatch:
                        shortage['severity'] = 'po_dispatch_grn_pending'
                    elif has_any_po:
                        shortage['severity'] = 'po_no_dispatch'
                    else:
                        shortage['severity'] = 'no_po'
        
        return (not has_shortage, shortages)

    @staticmethod
    async def run_mrp_analysis(
        db: AsyncSession,
        organization_id: int,
        create_alerts: bool = True,
        generate_pr_data: bool = False
    ) -> Dict:
        """
        Run complete MRP analysis for all active manufacturing orders
        
        Args:
            db: Database session
            organization_id: Organization ID
            create_alerts: Whether to create shortage alerts
            generate_pr_data: Whether to generate purchase requisition data
            
        Returns:
            Dictionary with MRP analysis results
        """
        # Calculate material requirements
        requirements = await MRPService.calculate_material_requirements(db, organization_id)
        
        # Separate items with and without shortages
        items_with_shortage = [r for r in requirements if r.shortage_quantity > 0]
        items_sufficient = [r for r in requirements if r.shortage_quantity == 0]
        
        result = {
            'analysis_date': datetime.now().isoformat(),
            'total_materials': len(requirements),
            'materials_with_shortage': len(items_with_shortage),
            'materials_sufficient': len(items_sufficient),
            'shortages': [
                {
                    'product_id': r.product_id,
                    'product_name': r.product_name,
                    'required': r.required_quantity,
                    'available': r.available_quantity,
                    'shortage': r.shortage_quantity,
                    'unit': r.unit,
                    'affected_mos': r.manufacturing_orders
                }
                for r in items_with_shortage
            ],
            'sufficient_materials': [
                {
                    'product_id': r.product_id,
                    'product_name': r.product_name,
                    'required': r.required_quantity,
                    'available': r.available_quantity,
                    'unit': r.unit
                }
                for r in items_sufficient
            ]
        }
        
        # Create alerts if requested
        if create_alerts and items_with_shortage:
            alerts = await MRPService.create_shortage_alerts(
                db, organization_id, items_with_shortage
            )
            result['alerts_created'] = len(alerts)
        
        # Generate purchase requisition data if requested
        if generate_pr_data and items_with_shortage:
            pr_data = await MRPService.generate_purchase_requisitions_data(
                db, organization_id, items_with_shortage
            )
            result['purchase_requisition_data'] = pr_data
        
        return result
    