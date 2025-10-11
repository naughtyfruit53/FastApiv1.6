# app/services/production_planning_service.py
"""
Production Planning and Scheduling Service

This service handles advanced production planning, resource allocation,
scheduling, capacity management, and order prioritization.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.models.vouchers.manufacturing_planning import ManufacturingOrder, BillOfMaterials
from app.models.product_models import Product

logger = logging.getLogger(__name__)


class ProductionScheduleItem:
    """Data class for production schedule items"""
    def __init__(
        self,
        mo_id: int,
        voucher_number: str,
        bom_id: int,
        product_name: str,
        planned_quantity: float,
        priority: str,
        planned_start_date: Optional[datetime],
        planned_end_date: Optional[datetime],
        estimated_hours: float,
        assigned_resources: Dict,
        dependencies: List[int] = None
    ):
        self.mo_id = mo_id
        self.voucher_number = voucher_number
        self.bom_id = bom_id
        self.product_name = product_name
        self.planned_quantity = planned_quantity
        self.priority = priority
        self.planned_start_date = planned_start_date
        self.planned_end_date = planned_end_date
        self.estimated_hours = estimated_hours
        self.assigned_resources = assigned_resources
        self.dependencies = dependencies or []


class ProductionPlanningService:
    """Production Planning and Scheduling Service"""

    # Priority weights for scheduling algorithm
    PRIORITY_WEIGHTS = {
        'urgent': 100,
        'high': 75,
        'medium': 50,
        'low': 25
    }

    @staticmethod
    async def calculate_order_priority_score(
        mo: ManufacturingOrder,
        current_date: datetime
    ) -> float:
        """
        Calculate priority score for a manufacturing order based on multiple factors
        
        Factors:
        - Priority level
        - Due date urgency
        - Order size
        - Waiting time
        """
        score = 0.0
        
        # Base priority weight
        score += ProductionPlanningService.PRIORITY_WEIGHTS.get(mo.priority, 50)
        
        # Due date urgency (higher score for sooner due dates)
        if mo.planned_end_date:
            days_until_due = (mo.planned_end_date - current_date).days
            if days_until_due <= 0:
                score += 200  # Overdue - highest priority
            elif days_until_due <= 3:
                score += 150  # Due very soon
            elif days_until_due <= 7:
                score += 100  # Due within a week
            elif days_until_due <= 14:
                score += 50  # Due within two weeks
        
        # Waiting time (higher score for orders waiting longer)
        if mo.date:
            days_waiting = (current_date - mo.date).days
            score += min(days_waiting * 2, 100)  # Cap at 100
        
        # Order size factor (prioritize larger orders slightly)
        if mo.planned_quantity > 100:
            score += 20
        elif mo.planned_quantity > 50:
            score += 10
        
        return score

    @staticmethod
    async def get_production_schedule(
        db: AsyncSession,
        organization_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        department: Optional[str] = None,
        status_filter: Optional[List[str]] = None
    ) -> List[ProductionScheduleItem]:
        """
        Get production schedule with prioritized manufacturing orders
        
        Args:
            db: Database session
            organization_id: Organization ID
            start_date: Filter by planned start date
            end_date: Filter by planned end date
            department: Filter by department
            status_filter: List of statuses to include
            
        Returns:
            List of ProductionScheduleItem objects sorted by priority
        """
        # Build query
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.organization_id == organization_id
        )
        
        if status_filter:
            stmt = stmt.where(ManufacturingOrder.production_status.in_(status_filter))
        else:
            stmt = stmt.where(ManufacturingOrder.production_status.in_(['planned', 'in_progress']))
        
        if start_date:
            stmt = stmt.where(ManufacturingOrder.planned_start_date >= start_date)
        
        if end_date:
            stmt = stmt.where(ManufacturingOrder.planned_end_date <= end_date)
        
        if department:
            stmt = stmt.where(ManufacturingOrder.production_department == department)
        
        result = await db.execute(stmt)
        orders = result.scalars().all()
        
        # Calculate priority scores and create schedule items
        current_date = datetime.now()
        schedule_items = []
        
        for mo in orders:
            # Get BOM to get product details
            stmt = select(BillOfMaterials).where(BillOfMaterials.id == mo.bom_id)
            result = await db.execute(stmt)
            bom = result.scalar_one_or_none()
            
            if not bom:
                continue
            
            # Get product name
            stmt = select(Product).where(Product.id == bom.output_item_id)
            result = await db.execute(stmt)
            product = result.scalar_one_or_none()
            
            product_name = product.product_name if product else "Unknown"
            
            # Calculate priority score
            priority_score = await ProductionPlanningService.calculate_order_priority_score(
                mo, current_date
            )
            
            # Create schedule item
            item = ProductionScheduleItem(
                mo_id=mo.id,
                voucher_number=mo.voucher_number,
                bom_id=mo.bom_id,
                product_name=product_name,
                planned_quantity=mo.planned_quantity,
                priority=mo.priority,
                planned_start_date=mo.planned_start_date,
                planned_end_date=mo.planned_end_date,
                estimated_hours=mo.estimated_setup_time + mo.estimated_run_time,
                assigned_resources={
                    'operator': mo.assigned_operator,
                    'supervisor': mo.assigned_supervisor,
                    'machine': mo.machine_id,
                    'workstation': mo.workstation_id
                }
            )
            
            schedule_items.append((priority_score, item))
        
        # Sort by priority score (descending)
        schedule_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for score, item in schedule_items]

    @staticmethod
    async def check_resource_availability(
        db: AsyncSession,
        organization_id: int,
        resource_type: str,  # 'operator', 'machine', 'workstation'
        resource_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Tuple[bool, List[Dict]]:
        """
        Check if a resource is available in a given time period
        
        Returns:
            Tuple of (is_available: bool, conflicting_orders: List[Dict])
        """
        # Build query for conflicting orders
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.organization_id == organization_id,
            ManufacturingOrder.production_status.in_(['planned', 'in_progress']),
            ManufacturingOrder.planned_start_date.isnot(None),
            ManufacturingOrder.planned_end_date.isnot(None)
        )
        
        # Add resource-specific filter
        if resource_type == 'operator':
            stmt = stmt.where(ManufacturingOrder.assigned_operator == resource_id)
        elif resource_type == 'machine':
            stmt = stmt.where(ManufacturingOrder.machine_id == resource_id)
        elif resource_type == 'workstation':
            stmt = stmt.where(ManufacturingOrder.workstation_id == resource_id)
        
        result = await db.execute(stmt)
        orders = result.scalars().all()
        
        # Check for time conflicts
        conflicts = []
        for order in orders:
            # Check if time periods overlap
            if not (end_date <= order.planned_start_date or start_date >= order.planned_end_date):
                conflicts.append({
                    'mo_id': order.id,
                    'voucher_number': order.voucher_number,
                    'start_date': order.planned_start_date.isoformat() if order.planned_start_date else None,
                    'end_date': order.planned_end_date.isoformat() if order.planned_end_date else None
                })
        
        return (len(conflicts) == 0, conflicts)

    @staticmethod
    async def allocate_resources(
        db: AsyncSession,
        organization_id: int,
        mo_id: int,
        operator: Optional[str] = None,
        supervisor: Optional[str] = None,
        machine_id: Optional[str] = None,
        workstation_id: Optional[str] = None,
        check_availability: bool = True
    ) -> Dict:
        """
        Allocate resources to a manufacturing order
        
        Args:
            db: Database session
            organization_id: Organization ID
            mo_id: Manufacturing order ID
            operator: Operator name/ID
            supervisor: Supervisor name/ID
            machine_id: Machine ID
            workstation_id: Workstation ID
            check_availability: Whether to check resource availability
            
        Returns:
            Dictionary with allocation result and any conflicts
        """
        # Get manufacturing order
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.id == mo_id,
            ManufacturingOrder.organization_id == organization_id
        )
        result = await db.execute(stmt)
        mo = result.scalar_one_or_none()
        
        if not mo:
            return {
                'success': False,
                'error': 'Manufacturing order not found'
            }
        
        conflicts = {}
        
        # Check availability if requested
        if check_availability and mo.planned_start_date and mo.planned_end_date:
            if operator:
                is_available, operator_conflicts = await ProductionPlanningService.check_resource_availability(
                    db, organization_id, 'operator', operator, mo.planned_start_date, mo.planned_end_date
                )
                if not is_available:
                    conflicts['operator'] = operator_conflicts
            
            if machine_id:
                is_available, machine_conflicts = await ProductionPlanningService.check_resource_availability(
                    db, organization_id, 'machine', machine_id, mo.planned_start_date, mo.planned_end_date
                )
                if not is_available:
                    conflicts['machine'] = machine_conflicts
            
            if workstation_id:
                is_available, workstation_conflicts = await ProductionPlanningService.check_resource_availability(
                    db, organization_id, 'workstation', workstation_id, mo.planned_start_date, mo.planned_end_date
                )
                if not is_available:
                    conflicts['workstation'] = workstation_conflicts
        
        # Update resource allocation (even if there are conflicts, for override capability)
        if operator:
            mo.assigned_operator = operator
        if supervisor:
            mo.assigned_supervisor = supervisor
        if machine_id:
            mo.machine_id = machine_id
        if workstation_id:
            mo.workstation_id = workstation_id
        
        await db.commit()
        
        return {
            'success': True,
            'mo_id': mo_id,
            'voucher_number': mo.voucher_number,
            'allocated_resources': {
                'operator': mo.assigned_operator,
                'supervisor': mo.assigned_supervisor,
                'machine': mo.machine_id,
                'workstation': mo.workstation_id
            },
            'conflicts': conflicts if conflicts else None,
            'has_conflicts': len(conflicts) > 0
        }

    @staticmethod
    async def calculate_capacity_utilization(
        db: AsyncSession,
        organization_id: int,
        start_date: datetime,
        end_date: datetime,
        department: Optional[str] = None
    ) -> Dict:
        """
        Calculate capacity utilization for a time period
        
        Returns:
            Dictionary with capacity metrics
        """
        # Get all manufacturing orders in the period
        stmt = select(ManufacturingOrder).where(
            ManufacturingOrder.organization_id == organization_id,
            ManufacturingOrder.production_status.in_(['planned', 'in_progress', 'completed']),
            ManufacturingOrder.planned_start_date >= start_date,
            ManufacturingOrder.planned_end_date <= end_date
        )
        
        if department:
            stmt = stmt.where(ManufacturingOrder.production_department == department)
        
        result = await db.execute(stmt)
        orders = result.scalars().all()
        
        # Calculate metrics
        total_planned_hours = sum(
            (mo.estimated_setup_time or 0) + (mo.estimated_run_time or 0)
            for mo in orders
        )
        
        total_actual_hours = sum(
            (mo.actual_setup_time or 0) + (mo.actual_run_time or 0)
            for mo in orders
            if mo.production_status in ['in_progress', 'completed']
        )
        
        completed_orders = [mo for mo in orders if mo.production_status == 'completed']
        in_progress_orders = [mo for mo in orders if mo.production_status == 'in_progress']
        planned_orders = [mo for mo in orders if mo.production_status == 'planned']
        
        # Calculate available capacity (assuming 8 hours per day per resource)
        total_days = (end_date - start_date).days
        # This is simplified - in reality, you'd calculate based on actual resources
        estimated_available_capacity = total_days * 8
        
        utilization_rate = (total_planned_hours / estimated_available_capacity * 100) if estimated_available_capacity > 0 else 0
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': total_days
            },
            'orders': {
                'total': len(orders),
                'completed': len(completed_orders),
                'in_progress': len(in_progress_orders),
                'planned': len(planned_orders)
            },
            'capacity': {
                'estimated_available_hours': estimated_available_capacity,
                'planned_hours': total_planned_hours,
                'actual_hours_consumed': total_actual_hours,
                'utilization_rate': round(utilization_rate, 2)
            },
            'efficiency': {
                'planned_vs_actual': round(
                    (total_actual_hours / total_planned_hours * 100) if total_planned_hours > 0 else 0,
                    2
                )
            }
        }

    @staticmethod
    async def suggest_optimal_schedule(
        db: AsyncSession,
        organization_id: int,
        planning_horizon_days: int = 30
    ) -> List[Dict]:
        """
        Suggest an optimal production schedule based on priorities and constraints
        
        Args:
            db: Database session
            organization_id: Organization ID
            planning_horizon_days: Number of days to plan ahead
            
        Returns:
            List of scheduled orders with suggested start/end dates
        """
        # Get prioritized schedule
        end_date = datetime.now() + timedelta(days=planning_horizon_days)
        schedule_items = await ProductionPlanningService.get_production_schedule(
            db, organization_id, end_date=end_date
        )
        
        # Simple scheduling algorithm: assign orders sequentially based on priority
        # Starting from current time
        current_time = datetime.now()
        scheduled_orders = []
        
        for item in schedule_items:
            # Calculate duration
            duration_hours = item.estimated_hours if item.estimated_hours > 0 else 8  # Default 1 day
            duration_days = duration_hours / 8  # Assuming 8-hour workday
            
            suggested_start = current_time
            suggested_end = current_time + timedelta(days=duration_days)
            
            scheduled_orders.append({
                'mo_id': item.mo_id,
                'voucher_number': item.voucher_number,
                'product_name': item.product_name,
                'quantity': item.planned_quantity,
                'priority': item.priority,
                'original_start_date': item.planned_start_date.isoformat() if item.planned_start_date else None,
                'original_end_date': item.planned_end_date.isoformat() if item.planned_end_date else None,
                'suggested_start_date': suggested_start.isoformat(),
                'suggested_end_date': suggested_end.isoformat(),
                'estimated_hours': item.estimated_hours,
                'assigned_resources': item.assigned_resources
            })
            
            # Move current time forward
            current_time = suggested_end + timedelta(hours=1)  # 1 hour buffer between orders
        
        return scheduled_orders
