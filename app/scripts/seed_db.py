# backend/seed_db.py
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import AsyncSessionLocal, Base, async_engine
from app.models.user_models import Organization, User  # Direct import from user_models.py
from app.models.entitlement_models import OrgEntitlement, OrgSubentitlement, EntitlementEvent  # Direct import from entitlement_models.py
from app.models.rbac_models import ServicePermission, ServiceRole, ServiceRolePermission, UserServiceRole
from app.core.config import settings
from app.core.security import get_password_hash

async def seed_rbac_data(session: AsyncSession):
    """Seed RBAC modules, permissions, roles, and assignments"""
    # Define permissions (add more as needed from your menuConfig or requirements)
    permissions_data = [
        # Inventory permissions
        {'name': 'inventory_read', 'display_name': 'Read Inventory', 'description': 'View inventory data and reports', 'module': 'inventory', 'action': 'read'},
        {'name': 'inventory_create', 'display_name': 'Create Inventory', 'description': 'Create inventory items', 'module': 'inventory', 'action': 'create'},
        {'name': 'inventory_update', 'display_name': 'Update Inventory', 'description': 'Update inventory items', 'module': 'inventory', 'action': 'update'},
        {'name': 'inventory_delete', 'display_name': 'Delete Inventory', 'description': 'Delete inventory items', 'module': 'inventory', 'action': 'delete'},
        {'name': 'inventory_view', 'display_name': 'View Inventory', 'description': 'View inventory overview', 'module': 'inventory', 'action': 'view'},

        # Reports permissions (to fix reports_view false in frontend checks)
        {'name': 'reports_view', 'display_name': 'View Reports', 'description': 'View all reports', 'module': 'reports', 'action': 'view'},

        # Add other permissions based on your app (e.g., from menuConfig.tsx)
        {'name': 'master_data_view', 'display_name': 'View Master Data', 'description': 'View master data', 'module': 'master_data', 'action': 'view'},
        {'name': 'manufacturing_view', 'display_name': 'View Manufacturing', 'description': 'View manufacturing', 'module': 'manufacturing', 'action': 'view'},
        {'name': 'vouchers_view', 'display_name': 'View Vouchers', 'description': 'View vouchers', 'module': 'vouchers', 'action': 'view'},
        {'name': 'finance_view', 'display_name': 'View Finance', 'description': 'View finance', 'module': 'finance', 'action': 'view'},
        {'name': 'accounting_view', 'display_name': 'View Accounting', 'description': 'View accounting', 'module': 'accounting', 'action': 'view'},
        {'name': 'ai_analytics_view', 'display_name': 'View AI Analytics', 'description': 'View AI analytics', 'module': 'ai_analytics', 'action': 'view'},
        {'name': 'sales_view', 'display_name': 'View Sales', 'description': 'View sales', 'module': 'sales', 'action': 'view'},
        {'name': 'marketing_view', 'display_name': 'View Marketing', 'description': 'View marketing', 'module': 'marketing', 'action': 'view'},
        {'name': 'service_view', 'display_name': 'View Service', 'description': 'View service', 'module': 'service', 'action': 'view'},
        {'name': 'admin_view', 'display_name': 'View Admin', 'description': 'View admin', 'module': 'admin', 'action': 'view'},
        {'name': 'hr_view', 'display_name': 'View HR', 'description': 'View HR', 'module': 'hr', 'action': 'view'},
        {'name': 'projects_view', 'display_name': 'View Projects', 'description': 'View projects', 'module': 'projects', 'action': 'view'},
        {'name': 'tasks_calendar_view', 'display_name': 'View Tasks/Calendar', 'description': 'View tasks and calendar', 'module': 'tasks_calendar', 'action': 'view'},
    ]

    async with session.begin():
        # Insert permissions if not exist - check by module and action to avoid duplicates
        for perm in permissions_data:
            stmt = select(ServicePermission).where(
                and_(
                    ServicePermission.module == perm['module'],
                    ServicePermission.action == perm['action']
                )
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_perm = ServicePermission(**perm)
                session.add(new_perm)
                print(f"Inserted new permission: {perm['name']}")
            else:
                print(f"Permission for {perm['module']}_{perm['action']} already exists, skipping")

    print("Seeded permissions")

    async with session.begin():
        # Define roles (assuming org_id=1 for default org; adjust as needed)
        roles_data = [
            {'organization_id': 1, 'name': 'org_admin', 'display_name': 'Organization Admin', 'description': 'Full access for org admins'},
            # Add other roles like 'finance_manager', etc., if needed
        ]

        roles = {}
        for role in roles_data:
            stmt = select(ServiceRole).where(
                and_(ServiceRole.organization_id == role['organization_id'], ServiceRole.name == role['name'])
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_role = ServiceRole(**role)
                session.add(new_role)
                await session.refresh(new_role)
                roles[role['name']] = new_role
            else:
                roles[role['name']] = existing

    print("Seeded roles")

    async with session.begin():
        # Assign all permissions to org_admin (full access)
        org_admin_role = roles.get('org_admin')
        if org_admin_role:
            for perm_data in permissions_data:
                stmt_perm = select(ServicePermission).where(
                    and_(
                        ServicePermission.module == perm_data['module'],
                        ServicePermission.action == perm_data['action']
                    )
                )
                result_perm = await session.execute(stmt_perm)
                perm = result_perm.scalar_one_or_none()
                if perm:
                    stmt_mapping = select(ServiceRolePermission).where(
                        and_(ServiceRolePermission.role_id == org_admin_role.id, ServiceRolePermission.permission_id == perm.id)
                    )
                    result_mapping = await session.execute(stmt_mapping)
                    existing_mapping = result_mapping.scalar_one_or_none()
                    if not existing_mapping:
                        mapping = ServiceRolePermission(role_id=org_admin_role.id, permission_id=perm.id)
                        session.add(mapping)
                        print(f"Assigned {perm.name} to org_admin")

    print("Assigned permissions to org_admin role")

    async with session.begin():
        # Assign role to default user (assume user_id=2 for potymatic@gmail.com from logs; adjust based on your DB)
        user_id = 2  # From logs: userId: 2
        role_assignment_data = [
            {'user_id': user_id, 'role_id': org_admin_role.id, 'assigned_by_id': None}
        ]
        for assignment in role_assignment_data:
            stmt = select(UserServiceRole).where(
                and_(UserServiceRole.user_id == assignment['user_id'], UserServiceRole.role_id == assignment['role_id'])
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_assignment = UserServiceRole(**assignment)
                session.add(new_assignment)

    print("Assigned org_admin role to user")

async def seed_default_data(session: AsyncSession):
    """Seed default organization and admin user if not exist"""
    async with session.begin():
        # Default organization
        stmt_org = select(Organization).where(Organization.id == 1)
        result_org = await session.execute(stmt_org)
        org = result_org.scalar_one_or_none()
        if not org:
            default_org = Organization(
                id=1,
                name="Default Organization",
                subdomain="default",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(default_org)
            print("Seeded default organization")

    async with session.begin():
        # Default admin user
        stmt_user = select(User).where(User.email == 'potymatic@gmail.com')
        result_user = await session.execute(stmt_user)
        user = result_user.scalar_one_or_none()
        if not user:
            hashed_password = get_password_hash("default_password")  # Change this!
            default_user = User(
                id=2,
                email='potymatic@gmail.com',
                hashed_password=hashed_password,
                role='org_admin',
                is_super_admin=False,
                organization_id=1,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(default_user)
            print("Seeded default admin user")

async def main():
    async with AsyncSessionLocal() as session:  # Use AsyncSessionLocal() to get session
        await seed_default_data(session)
        await seed_rbac_data(session)
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())