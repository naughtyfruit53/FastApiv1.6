# scripts/check_user_permissions.py

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_user_permissions(user_identifier: str):
    """Check user's assigned roles and permissions, accepting ID or email"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Determine if identifier is ID or email
        try:
            user_id = int(user_identifier)
            user_filter = "id = :user_id"
            params = {'user_id': user_id}
        except ValueError:
            user_filter = "email = :email"
            params = {'email': user_identifier}
        
        # Get user details
        user_result = db.execute(text(f"""
            SELECT id, email, role, organization_id
            FROM users
            WHERE {user_filter}
        """), params).first()
        
        if not user_result:
            print(f"No user found with identifier '{user_identifier}'")
            return
        
        user_id = user_result[0]
        
        print("\n=== User Details ===")
        print(f"ID: {user_id}")
        print(f"Email: {user_result[1]}")
        print(f"Role: {user_result[2]}")
        print(f"Org ID: {user_result[3]}")
        
        # Get assigned service roles
        roles_result = db.execute(text("""
            SELECT sr.name, sr.display_name
            FROM user_service_roles usr
            JOIN service_roles sr ON usr.role_id = sr.id
            WHERE usr.user_id = :user_id
            AND usr.is_active = true
            AND sr.is_active = true
        """), {'user_id': user_id}).all()
        
        print("\n=== Assigned Service Roles ===")
        if roles_result:
            for role in roles_result:
                print(f"- {role[0]} ({role[1]})")
        else:
            print("No service roles assigned")
        
        # Get permissions
        permissions_result = db.execute(text("""
            SELECT DISTINCT sp.name, sp.display_name
            FROM user_service_roles usr
            JOIN service_role_permissions srp ON usr.role_id = srp.role_id
            JOIN service_permissions sp ON srp.permission_id = sp.id
            WHERE usr.user_id = :user_id
            AND usr.is_active = true
            AND sp.is_active = true
            ORDER BY sp.name
        """), {'user_id': user_id}).all()
        
        print("\n=== Service Permissions ===")
        if permissions_result:
            for perm in permissions_result:
                print(f"- {perm[0]} ({perm[1]})")
        else:
            print("No permissions found")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_identifier = sys.argv[1]
    else:
        user_identifier = 'husainkm@gmail.com'  # Default
    check_user_permissions(user_identifier)