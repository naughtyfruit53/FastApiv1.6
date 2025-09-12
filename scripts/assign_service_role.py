# scripts/assign_service_role.py

"""
Script to assign a service role to a user in an organization
Run with: python -m scripts.assign_service_role <organization_id> <user_id or email> [role_name]
Default role: admin
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.rbac import RBACService
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

def assign_service_role(org_id: int, user_identifier: str, role_name: str = 'admin'):
    """Assign service role to user"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        rbac_service = RBACService(db)
        
        # Resolve user_id
        try:
            user_id = int(user_identifier)
            user_filter = "id = :user_id"
            params = {'user_id': user_id, 'org_id': org_id}
        except ValueError:
            user_filter = "email = :email"
            params = {'email': user_identifier, 'org_id': org_id}
        
        user_result = db.execute(text(f"""
            SELECT id
            FROM users 
            WHERE {user_filter}
            AND organization_id = :org_id
        """), params).first()
        
        if not user_result:
            print(f"No user found with identifier '{user_identifier}' in organization {org_id}")
            return
        
        user_id = user_result[0]
        
        # Find role
        role_result = db.execute(text("""
            SELECT id
            FROM service_roles
            WHERE organization_id = :org_id
            AND name = :role_name
            AND is_active = true
        """), {'org_id': org_id, 'role_name': role_name}).first()
        
        if not role_result:
            print(f"No active role found with name '{role_name}' in organization {org_id}")
            print("Available roles:")
            available_roles = db.execute(text("""
                SELECT name
                FROM service_roles
                WHERE organization_id = :org_id
                AND is_active = true
            """), {'org_id': org_id}).all()
            for role in available_roles:
                print(f"- {role[0]}")
            return
        
        role_id = role_result[0]
        
        # Assign role
        assignment = rbac_service.assign_role_to_user(user_id, role_id)
        
        print(f"\nSuccessfully assigned role '{role_name}' to user {user_id}")
        print(f"Assignment ID: {assignment.id}")
        print(f"Active: {assignment.is_active}")
        
    except Exception as e:
        print(f"Error assigning role: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python -m scripts.assign_service_role <organization_id> <user_id or email> [role_name]")
        print("Default role: admin")
        sys.exit(1)
    
    try:
        org_id = int(sys.argv[1])
        user_identifier = sys.argv[2]
        role_name = sys.argv[3] if len(sys.argv) > 3 else 'admin'
        
        assign_service_role(org_id, user_identifier, role_name)
    except ValueError:
        print("Organization ID must be an integer")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)