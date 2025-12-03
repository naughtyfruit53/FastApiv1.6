# app/services/entitlement_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime
import logging
import json  # Add for handling permissions list

from app.models.entitlement_models import (
    Module, Submodule, OrgEntitlement, OrgSubentitlement, EntitlementEvent, ModuleStatusEnum
)
from app.models.user_models import Organization, User
from app.models.rbac_models import UserModulePermission
from app.schemas.entitlement_schemas import (
    ModuleResponse, SubmoduleResponse, ModuleEntitlementResponse, SubmoduleEntitlementResponse,
    OrgEntitlementsResponse, UpdateEntitlementsRequest, UpdateEntitlementsResponse,
    AppEntitlementsResponse, AppModuleEntitlement, EntitlementChanges
)
from sqlalchemy import func  # Import for func.lower
from sqlalchemy.exc import IntegrityError  # NEW: Import for error handling

# Import modules_registry to get full list
from app.core.modules_registry import get_all_modules

# Import for RBAC-only check
from app.core.module_categories import is_rbac_only_module

logger = logging.getLogger(__name__)


class EntitlementService:
    """Service for managing organization entitlements"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_modules(self) -> List[ModuleResponse]:
        """Get all modules with submodules"""
        result = await self.db.execute(
            select(Module)
            .options(selectinload(Module.submodules))
            .where(Module.is_active == True)
            .order_by(Module.sort_order, Module.display_name)
        )
        modules = result.scalars().all()

        return [
            ModuleResponse(
                id=module.id,
                module_key=module.module_key,
                display_name=module.display_name,
                description=module.description,
                icon=module.icon,
                sort_order=module.sort_order,
                is_active=module.is_active,
                submodules=[
                    SubmoduleResponse(
                        id=sub.id,
                        submodule_key=sub.submodule_key,
                        display_name=sub.display_name,
                        description=sub.description,
                        menu_path=sub.menu_path,
                        permission_key=sub.permission_key,
                        sort_order=sub.sort_order,
                        is_active=sub.is_active
                    )
                    for sub in sorted(module.submodules, key=lambda s: (s.sort_order, s.display_name))
                ]
            )
            for module in modules
        ]

    async def get_org_entitlements(self, org_id: int) -> OrgEntitlementsResponse:
        """Get effective entitlements for an organization"""
        # Get organization
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")

        # Get all modules
        result = await self.db.execute(
            select(Module)
            .options(selectinload(Module.submodules))
            .where(Module.is_active == True)
            .order_by(Module.sort_order, Module.display_name)
        )
        modules = result.scalars().all()

        # Get org entitlements
        org_ent_result = await self.db.execute(
            select(OrgEntitlement).where(OrgEntitlement.org_id == org_id)
        )
        org_entitlements = {oe.module_id: oe for oe in org_ent_result.scalars().all()}

        # Get org subentitlements
        org_subent_result = await self.db.execute(
            select(OrgSubentitlement).where(OrgSubentitlement.org_id == org_id)
        )
        org_subentitlements = {}
        for ose in org_subent_result.scalars().all():
            key = (ose.module_id, ose.submodule_id)
            org_subentitlements[key] = ose

        # Build response
        entitlements = []
        for module in modules:
            org_ent = org_entitlements.get(module.id)
            module_status = org_ent.status if org_ent else 'disabled'
            trial_expires_at = org_ent.trial_expires_at if org_ent else None
            source = org_ent.source if org_ent else 'default'

            # Calculate effective status for submodules
            submodules = []
            for submodule in sorted(module.submodules, key=lambda s: (s.sort_order, s.display_name)):
                org_subent = org_subentitlements.get((module.id, submodule.id))
                submodule_enabled = org_subent.enabled if org_subent else True
                
                # Effective status depends on both module and submodule
                if module_status == 'enabled' and submodule_enabled:
                    effective_status = 'enabled'
                elif module_status == 'trial' and submodule_enabled:
                    if trial_expires_at is None or trial_expires_at > datetime.utcnow():
                        effective_status = 'trial'
                    else:
                        effective_status = 'disabled'
                else:
                    effective_status = 'disabled'

                submodules.append(
                    SubmoduleEntitlementResponse(
                        submodule_id=submodule.id,
                        submodule_key=submodule.submodule_key,
                        submodule_display_name=submodule.display_name,
                        enabled=submodule_enabled,
                        effective_status=effective_status,
                        source=org_subent.source if org_subent else None
                    )
                )

            entitlements.append(
                ModuleEntitlementResponse(
                    module_id=module.id,
                    module_key=module.module_key,
                    module_display_name=module.display_name,
                    status=module_status,
                    trial_expires_at=trial_expires_at,
                    source=source,
                    submodules=submodules
                )
            )

        return OrgEntitlementsResponse(
            org_id=org_id,
            org_name=org.name,
            entitlements=entitlements
        )

    async def update_org_entitlements(
        self,
        org_id: int,
        request: UpdateEntitlementsRequest,
        actor_user_id: int
    ) -> UpdateEntitlementsResponse:
        """Update organization entitlements (diff-only changes)"""
        # Verify organization exists
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")

        # Get all modules by key
        result = await self.db.execute(
            select(Module).where(Module.is_active == True)
        )
        modules_by_key = {m.module_key.lower(): m for m in result.scalars().all()}  # Normalize to lower

        # Get all submodules by (module_id, submodule_key)
        result = await self.db.execute(
            select(Submodule).where(Submodule.is_active == True)
        )
        submodules_map = {}
        for sub in result.scalars().all():
            submodules_map[(sub.module_id, sub.submodule_key.lower())] = sub  # Normalize to lower

        diff_data = {"modules": [], "submodules": []}

        # Apply module changes
        for module_change in request.changes.modules or []:
            normalized_key = module_change.module_key.lower()
            module = modules_by_key.get(normalized_key)
            if not module:
                raise ValueError(f"Module with key '{module_change.module_key}' not found")

            stmt = select(OrgEntitlement).where(
                and_(
                    OrgEntitlement.org_id == org_id,
                    OrgEntitlement.module_id == module.id
                )
            )
            result = await self.db.execute(stmt)
            ent = result.scalar_one_or_none()

            new_status = module_change.status
            new_trial_expires_at = module_change.trial_expires_at
            new_source = module_change.source or 'manual'

            old_status = ent.status if ent else 'disabled'
            old_trial_expires_at = ent.trial_expires_at if ent else None

            if ent:
                ent.status = new_status
                ent.trial_expires_at = new_trial_expires_at
                ent.source = new_source
                ent.updated_at = datetime.utcnow()
            else:
                ent = OrgEntitlement(
                    org_id=org_id,
                    module_id=module.id,
                    status=new_status,
                    trial_expires_at=new_trial_expires_at,
                    source=new_source
                )
                self.db.add(ent)

            diff_data["modules"].append({
                "module_key": module.module_key,
                "old_status": old_status,
                "new_status": new_status,
                "old_trial_expires_at": old_trial_expires_at,
                "new_trial_expires_at": new_trial_expires_at
            })

        # Apply submodule changes
        for sub_change in request.changes.submodules or []:
            normalized_module_key = sub_change.module_key.lower()
            normalized_sub_key = sub_change.submodule_key.lower()
            
            module = modules_by_key.get(normalized_module_key)
            if not module:
                raise ValueError(f"Module with key '{sub_change.module_key}' not found")
            
            key = (module.id, normalized_sub_key)
            submodule = submodules_map.get(key)
            if not submodule:
                raise ValueError(f"Submodule '{sub_change.submodule_key}' not found in module '{sub_change.module_key}'")

            stmt = select(OrgSubentitlement).where(
                and_(
                    OrgSubentitlement.org_id == org_id,
                    OrgSubentitlement.module_id == module.id,
                    OrgSubentitlement.submodule_id == submodule.id  # Fixed: changed = to ==
                )
            )
            result = await self.db.execute(stmt)
            subent = result.scalar_one_or_none()

            new_enabled = sub_change.enabled
            new_source = sub_change.source or 'manual'

            old_enabled = subent.enabled if subent else True

            if subent:
                subent.enabled = new_enabled
                subent.source = new_source
                subent.updated_at = datetime.utcnow()
            else:
                subent = OrgSubentitlement(
                    org_id=org_id,
                    module_id=module.id,
                    submodule_id=submodule.id,
                    enabled=new_enabled,
                    source=new_source
                )
                self.db.add(subent)

            diff_data["submodules"].append({
                "module_key": module.module_key,
                "submodule_key": submodule.submodule_key,
                "old_enabled": old_enabled,
                "new_enabled": new_enabled
            })

        # Create entitlement event
        event = EntitlementEvent(
            org_id=org_id,
            event_type='entitlement_update',
            actor_user_id=actor_user_id,
            reason=request.reason,
            payload=diff_data
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(event)
        
        # Sync permissions with entitlement changes
        try:
            logger.info(f"Syncing permissions with entitlement changes for org {org_id}")
            sync_result = await self.sync_permissions_with_entitlements(
                org_id=org_id,
                module_changes=diff_data["modules"]
            )
            logger.info(f"Permission sync result: {sync_result}")
        except Exception as sync_error:
            logger.error(f"Error syncing permissions: {sync_error}", exc_info=True)
            # Don't fail the entire update if permission sync fails

        # NEW: Sync enabled_modules in organization
        logger.info(f"Syncing enabled_modules for org {org_id} after entitlement update")
        # Fetch all current org_entitlements
        org_ent_result = await self.db.execute(
            select(OrgEntitlement)
            .where(OrgEntitlement.org_id == org_id)
            .options(joinedload(OrgEntitlement.module))
        )
        current_entitlements = org_ent_result.scalars().all()

        enabled_modules = {}
        now = datetime.utcnow()
        for ent in current_entitlements:
            upper_key = ent.module.module_key.upper()
            if ent.status == 'enabled':
                enabled_modules[upper_key] = True
            elif ent.status == 'trial':
                if ent.trial_expires_at is None or ent.trial_expires_at > now:
                    enabled_modules[upper_key] = True
                else:
                    enabled_modules[upper_key] = False
            else:
                enabled_modules[upper_key] = False

        # Update organization
        org.enabled_modules = enabled_modules
        await self.db.commit()
        await self.db.refresh(org)
        logger.debug(f"Synced enabled_modules: {enabled_modules}")

        # Invalidate cache for real-time update
        from app.api.v1.entitlements import invalidate_entitlements_cache
        await invalidate_entitlements_cache(org_id)

        # Get updated entitlements
        updated_entitlements = await self.get_org_entitlements(org_id)

        return UpdateEntitlementsResponse(
            success=True,
            message="Entitlements updated successfully",
            event_id=event.id,
            updated_entitlements=updated_entitlements
        )

    async def get_app_entitlements(self, org_id: int) -> AppEntitlementsResponse:
        """Get entitlements for app use (optimized, cacheable format)"""
        if org_id is None:
            return AppEntitlementsResponse(
                org_id=0,
                entitlements={}
            )
        # Get org entitlements
        org_ent_result = await self.db.execute(
            select(OrgEntitlement)
            .where(OrgEntitlement.org_id == org_id)
            .options(joinedload(OrgEntitlement.module))
        )
        org_entitlements = org_ent_result.scalars().all()

        # Get organization for enabled_modules
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organization {org_id} not found")

        # NEW: Always ensure entitlements for all modules
        # Get all active modules
        modules_result = await self.db.execute(
            select(Module).where(Module.is_active == True)
        )
        all_modules = modules_result.scalars().all()
        modules_by_key = {m.module_key.upper(): m for m in all_modules}

        # Existing entitlements map
        ent_map = {e.module.module_key.upper(): e for e in org_entitlements}

        # Parent mappings for additional modules
        parent_mappings = {
            'CUSTOMER': 'ERP',
            'PRODUCT': 'ERP',
            'VENDOR': 'ERP',
            'VOUCHER': 'ERP',
            'STOCK': 'ERP',
            'BOM': 'MANUFACTURING',
            'FINANCE': 'ERP',
            'LEDGER': 'FINANCE',
        }

        migrated = False
        for upper_key, module in modules_by_key.items():
            if upper_key not in ent_map:
                enabled = org.enabled_modules.get(upper_key, False)
                
                # For additional modules, enable if parent is enabled
                if upper_key in parent_mappings:
                    parent_key = parent_mappings[upper_key]
                    parent_enabled = org.enabled_modules.get(parent_key, False)
                    if parent_enabled:
                        enabled = True
                        logger.info(f"Auto-enabling {upper_key} because parent {parent_key} is enabled")
                
                status = 'enabled' if enabled else 'disabled'
                ent = OrgEntitlement(
                    org_id=org_id,
                    module_id=module.id,
                    status=status,
                    source='auto_migration'
                )
                self.db.add(ent)
                migrated = True

        if migrated:
            await self.db.commit()
            
            # Refetch org_entitlements after adding missing
            org_ent_result = await self.db.execute(
                select(OrgEntitlement)
                .where(OrgEntitlement.org_id == org_id)
                .options(joinedload(OrgEntitlement.module))
            )
            org_entitlements = org_ent_result.scalars().all()
            
            logger.info(f"Auto-migrated missing entitlements for org {org_id}")

        # Get org subentitlements
        org_subent_result = await self.db.execute(
            select(OrgSubentitlement).where(OrgSubentitlement.org_id == org_id)
            .options(joinedload(OrgSubentitlement.submodule))
        )
        org_subentitlements = {}
        for ose in org_subent_result.scalars().all():
            if ose.module_id not in org_subentitlements:
                org_subentitlements[ose.module_id] = {}
            org_subentitlements[ose.module_id][ose.submodule.submodule_key] = ose.enabled

        # Build response
        entitlements = {}
        for org_ent in org_entitlements:
            module_key = org_ent.module.module_key
            submodules = org_subentitlements.get(org_ent.module.id, {})

            entitlements[module_key] = AppModuleEntitlement(
                module_key=module_key,
                status=org_ent.status,
                trial_expires_at=org_ent.trial_expires_at,
                submodules=submodules
            )

        return AppEntitlementsResponse(
            org_id=org_id,
            entitlements=entitlements
        )

    async def check_entitlement(
        self,
        org_id: int,
        module_key: str,
        submodule_key: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if organization has entitlement for a module/submodule.
        Returns: (is_entitled, status, reason)
        """
        # Normalize keys to lower for case-insensitive check
        normalized_module_key = module_key.lower()
        normalized_submodule_key = submodule_key.lower() if submodule_key else None
        
        logger.debug(f"Checking entitlement for org {org_id}, module: {normalized_module_key}, submodule: {normalized_submodule_key}")
        
        # NEW: Bypass for RBAC-only modules
        if is_rbac_only_module(normalized_module_key):
            logger.debug(f"Bypassing entitlement check for RBAC-only module: {normalized_module_key}")
            return True, 'enabled', None
        
        # Get module (case-insensitive query using func.lower)
        module_result = await self.db.execute(
            select(Module).where(
                and_(
                    func.lower(Module.module_key) == normalized_module_key,
                    Module.is_active == True
                )
            )
        )
        module = module_result.scalar_one_or_none()
        if not module:
            logger.warning(f"Module not found in database for key: {normalized_module_key}")
            # NEW: Auto-create missing module if not found
            module = Module(
                module_key=normalized_module_key,
                display_name=module_key.capitalize(),
                description=f"Auto-created module: {module_key}",
                icon="default",
                sort_order=999,  # High sort_order for auto-created
                is_active=True
            )
            self.db.add(module)
            await self.db.flush()
            await self.db.refresh(module)
            logger.info(f"Auto-created missing module: {normalized_module_key} with ID {module.id}")
            
            # Auto-create entitlement as enabled for this org
            ent = OrgEntitlement(
                org_id=org_id,
                module_id=module.id,
                status='enabled',
                source='auto_creation'
            )
            self.db.add(ent)
            await self.db.commit()
            logger.info(f"Auto-enabled module {normalized_module_key} for org {org_id}")
            
            return True, 'enabled', 'Auto-created and enabled'

        logger.debug(f"Found module ID {module.id} for key {normalized_module_key}")
        
        # Get org entitlement
        org_ent_result = await self.db.execute(
            select(OrgEntitlement).where(
                and_(
                    OrgEntitlement.org_id == org_id,
                    OrgEntitlement.module_id == module.id
                )
            )
        )
        org_ent = org_ent_result.scalar_one_or_none()

        if not org_ent or org_ent.status == 'disabled':
            logger.info(f"Module {normalized_module_key} disabled for org {org_id}")
            return False, 'disabled', f"Module '{module_key}' is disabled for this organization"

        if org_ent.status == 'trial':
            if org_ent.trial_expires_at and org_ent.trial_expires_at < datetime.utcnow():
                logger.info(f"Trial expired for module {normalized_module_key} in org {org_id}")
                return False, 'trial_expired', f"Module '{module_key}' trial has expired"

        # If checking submodule
        if normalized_submodule_key:
            # Get submodule (case-insensitive)
            submodule_result = await self.db.execute(
                select(Submodule).where(
                    and_(
                        Submodule.module_id == module.id,
                        func.lower(Submodule.submodule_key) == normalized_submodule_key,
                        Submodule.is_active == True
                    )
                )
            )
            submodule = submodule_result.scalar_one_or_none()
            if not submodule:
                logger.warning(f"Submodule not found: {normalized_submodule_key} in module {normalized_module_key}")
                # NEW: Assume enabled if submodule not defined
                logger.warning(f"Assuming submodule {normalized_submodule_key} enabled since not found in DB")
                return True, org_ent.status, None

            logger.debug(f"Found submodule ID {submodule.id} for key {normalized_submodule_key}")
            
            # Get org subentitlement
            org_subent_result = await self.db.execute(
                select(OrgSubentitlement).where(
                    and_(
                        OrgSubentitlement.org_id == org_id,
                        OrgSubentitlement.module_id == module.id,
                        OrgSubentitlement.submodule_id == submodule.id
                    )
                )
            )
            org_subent = org_subent_result.scalar_one_or_none()

            # If subentitlement exists and is disabled
            if org_subent and not org_subent.enabled:
                logger.info(f"Submodule {normalized_submodule_key} disabled for org {org_id}")
                return False, 'disabled', f"Submodule '{submodule_key}' is disabled for this organization"

        logger.info(f"Entitlement granted for module {normalized_module_key} in org {org_id}")
        return True, org_ent.status, None

    @staticmethod
    def get_available_modules() -> List[str]:
        """Get available modules for selection (7 as specified)"""
        return get_all_modules()  # Changed to return all from registry for completeness

    async def seed_all_modules(self):
        """Seed all modules and submodules from registry if not exist"""
        from app.core.modules_registry import MODULE_SUBMODULES
        
        created_count = 0
        
        for module_name, submodules in MODULE_SUBMODULES.items():
            normalized_module = module_name.lower()
            
            # Check if module already exists (case-insensitive)
            module_result = await self.db.execute(
                select(Module).where(func.lower(Module.module_key) == normalized_module)
            )
            module = module_result.scalar_one_or_none()
            
            if not module:
                module = Module(
                    module_key=normalized_module,
                    display_name=module_name,
                    description=f"{module_name} module",
                    icon="default",
                    sort_order=0,
                    is_active=True
                )
                try:
                    self.db.add(module)
                    await self.db.flush()
                    await self.db.refresh(module)
                    created_count += 1
                    logger.info(f"Created module: {normalized_module}")
                except IntegrityError as e:
                    logger.warning(f"Skipping duplicate module {normalized_module}: {e}")
                    await self.db.rollback()
                    # Re-query to get the existing one
                    module_result = await self.db.execute(
                        select(Module).where(func.lower(Module.module_key) == normalized_module)
                    )
                    module = module_result.scalar_one_or_none()
                    if not module:
                        raise  # If still not found, raise
            
            # Seed submodules
            for sub_name in submodules:
                normalized_sub = sub_name.lower()
                sub_result = await self.db.execute(
                    select(Submodule).where(
                        and_(
                            Submodule.module_id == module.id,
                            func.lower(Submodule.submodule_key) == normalized_sub
                        )
                    )
                )
                if sub_result.scalar_one_or_none():
                    continue  # Skip if exists
                
                submodule = Submodule(
                    module_id=module.id,
                    submodule_key=normalized_sub,
                    display_name=sub_name,
                    description=f"{sub_name} submodule",
                    menu_path=f"/{normalized_module}/{normalized_sub}",
                    permission_key=f"{normalized_module}_{normalized_sub}",
                    sort_order=0,
                    is_active=True
                )
                try:
                    self.db.add(submodule)
                    await self.db.flush()
                    created_count += 1
                    logger.info(f"Created submodule: {normalized_sub} for module {normalized_module}")
                except IntegrityError as e:
                    logger.warning(f"Skipping duplicate submodule {normalized_sub} for module {normalized_module}: {e}")
                    await self.db.rollback()
        
        await self.db.commit()
        logger.info(f"Seeded {created_count} modules/submodules")
        return created_count

    async def sync_enabled_modules(self, org_id: int):
        """Sync organization's enabled_modules with actual modules in registry"""
        from app.core.modules_registry import get_all_modules
        
        # Get current enabled_modules
        org_result = await self.db.execute(
            select(Organization.enabled_modules).where(Organization.id == org_id)
        )
        current_enabled = org_result.scalar() or {}
        
        # Get all available modules (lower)
        available = {m.lower(): True for m in get_all_modules()}
        
        # Sync: only keep enabled if in available, default False for new
        synced = {}
        for key in available:
            upper_key = key.upper()
            synced[upper_key] = current_enabled.get(upper_key, False)
        
        # Update organization
        await self.db.execute(
            Organization.__table__.update()
            .where(Organization.id == org_id)
            .values(enabled_modules=synced)
        )
        await self.db.commit()
        
        logger.info(f"Synced enabled_modules for org {org_id}: {synced}")
        return synced

    async def activate_category(
        self,
        org_id: int,
        category: str,
        actor_user_id: int,
        reason: str = "Category-based activation"
    ) -> UpdateEntitlementsResponse:
        """
        Activate all modules in a product category for an organization.
        This provides instant access to all features in the selected category.
        
        Args:
            org_id: Organization ID
            category: Product category key (e.g., 'crm_suite', 'erp_suite')
            actor_user_id: User performing the activation
            reason: Reason for activation (for audit trail)
        
        Returns:
            UpdateEntitlementsResponse with details of activation
        """
        from app.core.module_categories import get_modules_for_category, get_category_info
        
        # Get modules for this category
        module_keys = get_modules_for_category(category)
        if not module_keys:
            raise ValueError(f"Category '{category}' not found or has no modules")
        
        category_info = get_category_info(category)
        logger.info(f"Activating category '{category_info['display_name']}' with {len(module_keys)} modules for org {org_id}")
        
        # Build changes for all modules in the category
        from app.schemas.entitlement_schemas import UpdateEntitlementsRequest, EntitlementChanges, ModuleEntitlementChange
        
        module_changes = []
        for module_key in module_keys:
            module_changes.append(
                ModuleEntitlementChange(
                    module_key=module_key,
                    status='enabled',
                    source=f'category:{category}'
                )
            )
        
        changes = EntitlementChanges(modules=module_changes)
        request = UpdateEntitlementsRequest(
            reason=f"{reason} - Category: {category_info['display_name']}",
            changes=changes
        )
        
        # Use existing update method to apply changes
        return await self.update_org_entitlements(org_id, request, actor_user_id)

    async def deactivate_category(
        self,
        org_id: int,
        category: str,
        actor_user_id: int,
        reason: str = "Category-based deactivation"
    ) -> UpdateEntitlementsResponse:
        """
        Deactivate all modules in a product category for an organization.
        
        Args:
            org_id: Organization ID
            category: Product category key
            actor_user_id: User performing the deactivation
            reason: Reason for deactivation (for audit trail)
        
        Returns:
            UpdateEntitlementsResponse with details of deactivation
        """
        from app.core.module_categories import get_modules_for_category, get_category_info
        
        # Get modules for this category
        module_keys = get_modules_for_category(category)
        if not module_keys:
            raise ValueError(f"Category '{category}' not found or has no modules")
        
        category_info = get_category_info(category)
        logger.info(f"Deactivating category '{category_info['display_name']}' with {len(module_keys)} modules for org {org_id}")
        
        # Build changes for all modules in the category
        from app.schemas.entitlement_schemas import UpdateEntitlementsRequest, EntitlementChanges, ModuleEntitlementChange
        
        module_changes = []
        for module_key in module_keys:
            module_changes.append(
                ModuleEntitlementChange(
                    module_key=module_key,
                    status='disabled',
                    source=f'category:{category}'
                )
            )
        
        changes = EntitlementChanges(modules=module_changes)
        request = UpdateEntitlementsRequest(
            reason=f"{reason} - Category: {category_info['display_name']}",
            changes=changes
        )
        
        # Use existing update method to apply changes
        return await self.update_org_entitlements(org_id, request, actor_user_id)

    async def get_activated_categories(self, org_id: int) -> List[str]:
        """
        Get list of categories that are fully or partially activated for an organization.
        
        Args:
            org_id: Organization ID
        
        Returns:
            List of activated category keys
        """
        from app.core.module_categories import CATEGORY_MODULE_MAP, get_category_for_module
        
        # Get all enabled modules for the organization
        org_ent_result = await self.db.execute(
            select(OrgEntitlement)
            .where(OrgEntitlement.org_id == org_id)
            .options(joinedload(OrgEntitlement.module))
        )
        org_entitlements = org_ent_result.scalars().all()
        
        enabled_modules = set()
        now = datetime.utcnow()
        for ent in org_entitlements:
            if ent.status == 'enabled':
                enabled_modules.add(ent.module.module_key)
            elif ent.status == 'trial' and (ent.trial_expires_at is None or ent.trial_expires_at > now):
                enabled_modules.add(ent.module.module_key)
        
        # Check which categories are activated
        activated_categories = []
        for category, modules in CATEGORY_MODULE_MAP.items():
            # Category is considered activated if at least one of its modules is enabled
            if any(module in enabled_modules for module in modules):
                activated_categories.append(category)
        
        return activated_categories

    async def sync_permissions_with_entitlements(
        self,
        org_id: int,
        module_changes: List[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Synchronize user permissions with entitlement changes.
        
        When a module is disabled:
        - Revoke all user permissions for that module
        - Log the revocation for audit trail
        
        When a module is enabled:
        - Restore default permissions based on user role
        - Log the restoration
        
        Args:
            org_id: Organization ID
            module_changes: List of module changes with old_status and new_status
        
        Returns:
            Dictionary with counts of permissions revoked and restored
        """
        revoked_count = 0
        restored_count = 0
        
        if not module_changes:
            return {"revoked": 0, "restored": 0}
        
        # Get all modules by key for lookup
        result = await self.db.execute(
            select(Module).where(Module.is_active == True)
        )
        modules_by_key = {m.module_key.lower(): m for m in result.scalars().all()}
        
        for change in module_changes:
            module_key = change.get("module_key", "").lower()
            old_status = change.get("old_status", "")
            new_status = change.get("new_status", "")
            
            module = modules_by_key.get(module_key)
            if not module:
                continue
            
            # Module was disabled
            if old_status in ["enabled", "trial"] and new_status == "disabled":
                logger.info(f"Module {module_key} disabled - revoking permissions for org {org_id}")
                
                # Get all users in organization with permissions for this module
                result = await self.db.execute(
                    select(UserModulePermission)
                    .join(User, UserModulePermission.user_id == User.id)
                    .where(
                        and_(
                            User.organization_id == org_id,
                            UserModulePermission.module_id == module.id
                        )
                    )
                )
                permissions = result.scalars().all()
                
                # Delete permissions
                for perm in permissions:
                    await self.db.delete(perm)
                    revoked_count += 1
                
                logger.info(f"Revoked {len(permissions)} permissions for module {module_key}")
                
                # Log event
                event = EntitlementEvent(
                    org_id=org_id,
                    event_type='permissions_revoked',
                    actor_user_id=None,
                    reason=f"Module {module_key} disabled",
                    payload={
                        "module_key": module_key,
                        "permissions_revoked": len(permissions)
                    }
                )
                self.db.add(event)
            
            # Module was enabled
            elif old_status == "disabled" and new_status in ["enabled", "trial"]:
                logger.info(f"Module {module_key} enabled - restoring default permissions for org {org_id}")
                
                # Get all users in organization
                result = await self.db.execute(
                    select(User).where(
                        and_(
                            User.organization_id == org_id,
                            User.is_active == True
                        )
                    )
                )
                users = result.scalars().all()
                
                # Track restoration count for this module
                module_restored = 0
                
                # For each user, restore permissions based on their role
                for user in users:
                    # Admin roles get full access
                    if user.role in ["org_admin", "management"]:
                        # Check if permission already exists
                        result = await self.db.execute(
                            select(UserModulePermission).where(
                                and_(
                                    UserModulePermission.user_id == user.id,
                                    UserModulePermission.module_id == module.id
                                )
                            )
                        )
                        existing = result.scalar_one_or_none()
                        
                        if not existing:
                            perm = UserModulePermission(
                                user_id=user.id,
                                module_id=module.id,
                                has_access=True
                            )
                            self.db.add(perm)
                            module_restored += 1
                            restored_count += 1
                
                logger.info(f"Restored {module_restored} permissions for module {module_key}")
                
                # Log event
                event = EntitlementEvent(
                    org_id=org_id,
                    event_type='permissions_restored',
                    actor_user_id=None,
                    reason=f"Module {module_key} enabled",
                    payload={
                        "module_key": module_key,
                        "permissions_restored": module_restored
                    }
                )
                self.db.add(event)
        
        await self.db.commit()
        
        logger.info(f"Permission sync complete - Revoked: {revoked_count}, Restored: {restored_count}")
        return {"revoked": revoked_count, "restored": restored_count}

    async def initialize_org_entitlements(
        self,
        org_id: int,
        enabled_modules: Optional[Dict[str, bool]] = None,
        license_tier: str = "basic"
    ) -> Dict[str, str]:
        """
        Initialize entitlements for a newly created organization.
        
        This method should be called during organization creation to set up
        initial entitlement records based on:
        1. The organization's enabled_modules configuration
        2. The organization's license tier
        3. Always-on modules (email, dashboard)
        
        Args:
            org_id: Organization ID
            enabled_modules: Dictionary of module keys and their enabled status
            license_tier: License tier (basic, professional, enterprise, etc.)
        
        Returns:
            Dictionary mapping module keys to their initial status
        """
        from app.core.constants import ALWAYS_ON_MODULES
        
        # Get all modules
        result = await self.db.execute(
            select(Module).where(Module.is_active == True)
        )
        modules = result.scalars().all()
        
        if not modules:
            logger.warning("No modules found in database. Run seed_entitlements.py first.")
            return {}
        
        # Normalize enabled_modules keys (case-insensitive)
        enabled_map = {}
        if enabled_modules:
            for key, value in enabled_modules.items():
                enabled_map[key.lower()] = value
        
        # Track created entitlements
        created_entitlements = {}
        
        for module in modules:
            module_key_lower = module.module_key.lower()
            
            # Check if entitlement already exists
            result = await self.db.execute(
                select(OrgEntitlement).where(
                    and_(
                        OrgEntitlement.org_id == org_id,
                        OrgEntitlement.module_id == module.id
                    )
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.debug(f"Entitlement for {module.module_key} already exists for org {org_id}")
                created_entitlements[module.module_key] = existing.status
                continue
            
            # Determine initial status
            if module_key_lower in ALWAYS_ON_MODULES:
                # Always-on modules are always enabled
                status = ModuleStatusEnum.ENABLED
                logger.info(f"  ✓ {module.module_key}: Enabled (always-on)")
            elif enabled_map.get(module_key_lower, False):
                # Module is enabled in organization settings
                status = ModuleStatusEnum.ENABLED
                logger.info(f"  ✓ {module.module_key}: Enabled (org config)")
            elif license_tier in ['professional', 'enterprise']:
                # Professional/Enterprise tiers get trial for disabled modules
                status = ModuleStatusEnum.TRIAL
                logger.info(f"  ⌛ {module.module_key}: Trial (license tier: {license_tier})")
            else:
                # Basic tier and module not explicitly enabled
                status = ModuleStatusEnum.DISABLED
                logger.info(f"  ✗ {module.module_key}: Disabled (not in plan)")
            
            # Create entitlement record
            entitlement = OrgEntitlement(
                org_id=org_id,
                module_id=module.id,
                status=status.value,
                source='org_creation',
                trial_expires_at=None  # Can be set later for trial modules
            )
            self.db.add(entitlement)
            created_entitlements[module.module_key] = status.value
        
        # Commit all entitlements
        await self.db.commit()
        
        logger.info(f"✅ Initialized {len(created_entitlements)} entitlements for org {org_id}")
        return created_entitlements

    async def grant_rbac_permissions(self, org_id: int):
        """Grant RBAC permissions for enabled modules to org_admin"""
        # Get org_admin user (assuming ID 2 from logs)
        result = await self.db.execute(
            select(User).where(User.id == 2)  # Adjust for your user ID
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User not found for RBAC grant in org {org_id}")
            return

        # Get enabled modules
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            return

        enabled_modules = [key.lower() for key, value in org.enabled_modules.items() if value]

        # Current permissions
        current_permissions = user.permissions or []

        # Add module.* for each enabled module if not present
        updated = False
        for module_key in enabled_modules:
            wildcard_perm = f"{module_key}.*"
            if wildcard_perm not in current_permissions:
                current_permissions.append(wildcard_perm)
                updated = True
                logger.info(f"Granted {wildcard_perm} to org_admin in org {org_id}")

        if updated:
            user.permissions = current_permissions
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Updated permissions for org_admin in org {org_id}")
            