# app/services/entitlement_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import logging

from app.models.entitlement_models import (
    Module, Submodule, OrgEntitlement, OrgSubentitlement, EntitlementEvent, ModuleStatusEnum
)
from app.models.user_models import Organization, User
from app.schemas.entitlement_schemas import (
    ModuleResponse, SubmoduleResponse, ModuleEntitlementResponse, SubmoduleEntitlementResponse,
    OrgEntitlementsResponse, UpdateEntitlementsRequest, UpdateEntitlementsResponse,
    AppEntitlementsResponse, AppModuleEntitlement, EntitlementChanges
)
from sqlalchemy import func  # Import for func.lower

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
            'SETTINGS': 'ERP',  # NEW: Auto-enable settings if ERP enabled
            'LEDGER': 'FINANCE',  # NEW: Auto-enable ledger if FINANCE enabled
            'INVENTORY': 'ERP'  # NEW: Auto-enable inventory if ERP enabled
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
                # NEW: Instead of denying, assume enabled if submodule not defined
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
                self.db.add(module)
                await self.db.flush()
                created_count += 1
                logger.info(f"Created module: {normalized_module}")
            
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
                if not sub_result.scalar_one_or_none():
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
                    self.db.add(submodule)
                    created_count += 1
                    logger.info(f"Created submodule: {normalized_sub} for module {normalized_module}")
        
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