# scripts/fix_super_admin_role.py

"""
Script to fix and assign Service Admin role to Organization Super Admins.
This script:
- Initializes default service roles if not present
- Assigns 'admin' service role to users with 'org_admin' role
- Handles all organizations or specific ones
"""

import sys
import os
from dotenv import load_dotenv
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import Organization, User, ServiceRole, UserServiceRole
from app.services.rbac import RBACService

# Load .env file
load_dotenv()

# Use DATABASE_URL from .env
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_super_admin_roles(org_id: Optional[int] = None):
    db = SessionLocal()
    try:
        rbac_service = RBACService(db)
        
        # Get organizations to process
        if org_id:
            orgs = db.query(Organization).filter(Organization.id == org_id).all()
        else:
            orgs = db.query(Organization).all()
        
        for org in orgs:
            print(f"\nProcessing organization: {org.name} (ID: {org.id})")
            
            # Initialize default roles if not present
            existing_roles = rbac_service.get_roles(org.id)
            if not existing_roles:
                print("Initializing default service roles...")
                initialized = rbac_service.initialize_default_roles(org.id)
                print(f"Initialized {len(initialized)} roles")
            else:
                print(f"Default roles already initialized ({len(existing_roles)} roles found)")
            
            # Get service admin role
            admin_role = db.query(ServiceRole).filter(
                ServiceRole.organization_id == org.id,
                ServiceRole.name == 'admin'
            ).first()
            
            if not admin_role:
                print("Error: Service admin role not found after initialization")
                continue
            
            # Get org super admins (users with role='org_admin')
            org_admins = db.query(User).filter(
                User.organization_id == org.id,
                User.role == 'org_admin'
            ).all()
            
            if not org_admins:
                print("No org super admins found")
                continue
            
            for admin in org_admins:
                print(f"Processing user: {admin.email} (ID: {admin.id})")
                
                # Check if already assigned
                existing_assignment = db.query(UserServiceRole).filter(
                    UserServiceRole.user_id == admin.id,
                    UserServiceRole.role_id == admin_role.id
                ).first()
                
                if existing_assignment:
                    if not existing_assignment.is_active:
                        existing_assignment.is_active = True
                        db.commit()
                        print("Reactivated existing service admin role assignment")
                    else:
                        print("Service admin role already assigned")
                    continue
                
                # Assign service admin role
                assignment = rbac_service.assign_role_to_user(
                    user_id=admin.id,
                    role_id=admin_role.id,
                    assigned_by_id=None  # System assignment
                )
                print("Assigned service admin role successfully")
        
        print("\nFix complete!")
        
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fix service admin roles for org super admins")
    parser.add_argument("--org_id", type=int, help="Specific organization ID to fix (optional)")
    args = parser.parse_args()
    
    fix_super_admin_roles(args.org_id)