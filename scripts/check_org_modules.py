# scripts/check_org_modules.py

"""
Script to check organization enabled modules and user assignments
Run with: python -m scripts.check_org_modules <organization_id> <user_id or email>
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import json
import logging

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

def check_org_modules(org_id: int, user_identifier: str):
    """Check organization modules and user data"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Check organization
        org_result = db.execute(text("""
            SELECT 
                name,
                enabled_modules,
                status
            FROM organizations 
            WHERE id = :org_id
        """), {'org_id': org_id}).first()
        
        if not org_result:
            print(f"No organization found with ID {org_id}")
            return
        
        print("\n=== Organization Details ===")
        print(f"Name: {org_result[0]}")
        print(f"Status: {org_result[2]}")
        print("\nEnabled Modules:")
        modules = org_result[1]
        if isinstance(modules, str):
            modules = json.loads(modules)
        elif not isinstance(modules, dict):
            modules = {}
        for module, enabled in modules.items():
            status = "✅ Enabled" if enabled else "❌ Disabled"
            print(f"- {module}: {status}")
        
        # Check if Service is enabled
        if modules.get('Service', False):
            print("\n✅ Service module is enabled for this organization")
        else:
            print("\n❌ Service module is NOT enabled - this could be why it's not visible")
        
        # Resolve user_id from identifier (ID or email)
        try:
            user_id = int(user_identifier)
            user_filter = "id = :user_id"
            params = {'user_id': user_id, 'org_id': org_id}
        except ValueError:
            user_filter = "email = :email"
            params = {'email': user_identifier, 'org_id': org_id}
        
        user_result = db.execute(text(f"""
            SELECT 
                id,
                email,
                role,
                is_super_admin,
                assigned_modules
            FROM users 
            WHERE {user_filter}
            AND organization_id = :org_id
        """), params).first()
        
        if not user_result:
            print(f"\nNo user found with identifier '{user_identifier}' in organization {org_id}")
            return
        
        user_id = user_result[0]  # Now we have the user_id
        
        print("\n=== User Details ===")
        print(f"ID: {user_id}")
        print(f"Email: {user_result[1]}")
        print(f"Role: {user_result[2]}")
        print(f"Super Admin: {'Yes' if user_result[3] else 'No'}")
        
        print("\nAssigned Modules:")
        user_modules = user_result[4]
        if isinstance(user_modules, str):
            user_modules = json.loads(user_modules)
        elif not isinstance(user_modules, dict):
            user_modules = {}
        for module, enabled in user_modules.items():
            status = "✅ Assigned" if enabled else "❌ Not Assigned"
            print(f"- {module}: {status}")
        
        # Check Service assignment
        if user_modules.get('Service', False):
            print("\n✅ User has Service module assigned")
        else:
            print("\n❌ User does NOT have Service module assigned - this could prevent visibility")
        
        # Check RBAC roles
        roles_result = db.execute(text("""
            SELECT 
                sr.name,
                sr.display_name
            FROM user_service_roles usr
            JOIN service_roles sr ON usr.role_id = sr.id
            WHERE usr.user_id = :user_id
            AND usr.is_active = true
            AND sr.is_active = true
        """), {'user_id': user_id}).all()
        
        print("\n=== Assigned Service Roles ===")
        if roles_result:
            for role in roles_result:
                print(f"- {role[1]} ({role[0]})")
        else:
            print("No service roles assigned to this user")
        
        # Check Service permissions
        permissions_result = db.execute(text("""
            SELECT DISTINCT sp.name
            FROM user_service_roles usr
            JOIN service_role_permissions srp ON usr.role_id = srp.role_id
            JOIN service_permissions sp ON srp.permission_id = sp.id
            WHERE usr.user_id = :user_id
            AND usr.is_active = true
            AND sp.is_active = true
            AND sp.module LIKE '%service%'
        """), {'user_id': user_id}).all()
        
        print("\n=== Service-Related Permissions ===")
        if permissions_result:
            for perm in permissions_result:
                print(f"- {perm[0]}")
        else:
            print("No service-related permissions found for this user")
        
    except Exception as e:
        print(f"Error checking organization: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.check_org_modules <organization_id> <user_id or email>")
        sys.exit(1)
    
    try:
        org_id = int(sys.argv[1])
        user_identifier = sys.argv[2]
        check_org_modules(org_id, user_identifier)
    except ValueError:
        print("Organization ID must be an integer")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)