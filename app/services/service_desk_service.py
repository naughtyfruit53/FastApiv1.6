from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from app.models.service_models import Ticket

def get_tickets(
    db: Session,
    org_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    ticket_type: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    search: Optional[str] = None
) -> List[Ticket]:
    query = db.query(Ticket).filter(Ticket.organization_id == org_id)
    
    if status:
        query = query.filter(Ticket.status == status)
    
    if priority:
        query = query.filter(Ticket.priority == priority)
    
    if ticket_type:
        query = query.filter(Ticket.ticket_type == ticket_type)
    
    if assigned_to_id:
        query = query.filter(Ticket.assigned_to_id == assigned_to_id)
    
    if customer_id:
        query = query.filter(Ticket.customer_id == customer_id)
    
    if search:
        query = query.filter(or_(
            Ticket.title.ilike(f"%{search}%"),
            Ticket.description.ilike(f"%{search}%")
        ))
    
    # Add default ordering by created_at descending
    query = query.order_by(Ticket.created_at.desc())
    
    return query.offset(skip).limit(limit).all()