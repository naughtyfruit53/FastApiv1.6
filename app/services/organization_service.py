# app/services/organization_service.py (new file or revised if exists)

from sqlalchemy.orm import Session
from app.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationInDB

class OrganizationService:
    @staticmethod
    def create_organization(db: Session, org_create: OrganizationCreate) -> Organization:
        db_org = Organization(**org_create.dict())
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org