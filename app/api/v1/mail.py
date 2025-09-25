# app/api/v1/mail.py

"""
Mail and Email Management API endpoints - Retained minimal for system sending if needed, but all client routes removed
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user_models import User
from app.models.system_models import SnappyMailConfig  # Assuming model from models/system_models.py or similar

router = APIRouter()

@router.get("/config/{user_id}", response_model=Optional[dict])
def get_snappymail_config(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch SnappyMail configuration for a specific user.
    Only accessible by the user themselves or org_admin.
    """
    if current_user.id != user_id and current_user.role != "org_admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    config = db.query(SnappyMailConfig).filter(SnappyMailConfig.user_id == user_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="No SnappyMail config found for this user")
    
    # Return as dict, excluding sensitive fields like password
    return {
        "imap_host": config.imap_host,
        "imap_port": config.imap_port,
        "smtp_host": config.smtp_host,
        "smtp_port": config.smtp_port,
        "use_ssl": config.use_ssl,
        "email": config.email
    }

# All previous routes removed as per custom mail replacement
# If any send endpoints are used for user creation, they were in email_service.py which is kept