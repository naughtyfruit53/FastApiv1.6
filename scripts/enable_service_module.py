# scripts/enable_service_module.py

import sys
import os
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user_models import Organization
import json

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def enable_service_module(org_id: int = 1):
    """Enable Service module for a specific organization"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Get current enabled modules
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            print(f"No organization found with ID {org_id}")
            return
        
        enabled_modules = org.enabled_modules or {}
        
        # Enable Service module
        enabled_modules["Service"] = True
        
        # Update organization
        stmt = (
            update(Organization)
            .where(Organization.id == org_id)
            .values(enabled_modules=enabled_modules)
        )
        db.execute(stmt)
        db.commit()
        
        print(f"\n✅ Service module enabled successfully for organization {org.name} (ID: {org_id})")
        print("\nCurrent enabled modules:")
        print(json.dumps(enabled_modules, indent=2))
        
        print("\nPlease restart the application and refresh the frontend to see changes.")
        
    except Exception as e:
        db.rollback()
        print(f"Error enabling module: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            org_id = int(sys.argv[1])
            enable_service_module(org_id)
        except ValueError:
            print("Organization ID must be an integer")
    else:
        enable_service_module()  # Default to org_id=1