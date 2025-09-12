# scripts/init_rbac_for_org.py

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.rbac import RBACService
from app.models.user_models import User, ServiceRole

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def initialize_rbac_for_org(org_id: int = 1):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        rbac_service = RBACService(db)
        permissions = rbac_service.initialize_default_permissions()
        print(f"\n✅ Initialized {len(permissions)} default permissions, including mail permissions.")
        
        roles = rbac_service.initialize_default_roles(org_id)
        print("\n✅ Default roles created with mail permissions assigned:")
        for role in roles:
            print(f"- {role.name} ({role.display_name})")
        
        # Assign admin role to org admin
        org_admin = db.query(User).filter(
            User.organization_id == org_id,
            User.role == 'org_admin'
        ).first()
        
        if org_admin:
            admin_role = db.query(ServiceRole).filter(
                ServiceRole.organization_id == org_id,
                ServiceRole.name == 'admin'
            ).first()
            
            if admin_role:
                assignment = rbac_service.assign_role_to_user(org_admin.id, admin_role.id)
                print(f"\n✅ Assigned admin role (with mail:dashboard:read) to user {org_admin.email} (ID: {org_admin.id})")
            else:
                print("\n⚠️ Admin role not found - check if roles were created correctly")
        else:
            print("\n⚠️ Org admin user not found - verify user with role 'org_admin' exists in organization {org_id}")
        
        print("\nScript completed. Restart the application, log out and log in again to refresh permissions.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during initialization: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        org_id = int(sys.argv[1])
    else:
        org_id = 1  # Default to organization ID 1 as per your logs
    initialize_rbac_for_org(org_id)