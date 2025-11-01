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
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")

        # Get all modules
        modules_result = await self.db.execute(
            select(Module)
            .options(selectinload(Module.submodules))
            .where(Module.is_active == True)
            .order_by(Module.sort_order, Module.display_name)
        )
        modules = modules_result.scalars().all()

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
        """Update organization entitlements"""
        # Verify organization exists
        org_result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = org_result.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organization with id {org_id} not found")

        # Get all modules by key
        modules_result = await self.db.execute(
            select(Module).where(Module.is_active == True)
        )
        modules_by_key = {m.module_key: m for m in modules_result.scalars().all()}

        # Get all submodules by (module_id, submodule_key)
        submodules_result = await self.db.execute(
            select(Submodule).where(Submodule.is_active == True)
        )
        submodules_map = {}
        for sub in submodules_result.scalars().all():
            submodules_map[(sub.module_id, sub.submodule_key)] = sub

        diff_data = {"modules": [], "submodules": []}

        # Apply module changes
        for module_change in request.changes.modules:
            if module_change.module_key not in modules_by_key:
                raise ValueError(f"Invalid module_key: {module_change.module_key}")

            module = modules_by_key[module_change.module_key]

            # Get or create org_entitlement
            org_ent_result = await self.db.execute(
                select(OrgEntitlement).where(
                    and_(
                        OrgEntitlement.org_id == org_id,
                        OrgEntitlement.module_id == module.id
                    )
                )
            )
            org_ent = org_ent_result.scalar_one_or_none()

            old_status = org_ent.status if org_ent else None
            old_trial_expires = org_ent.trial_expires_at if org_ent else None

            if org_ent:
                org_ent.status = module_change.status
                org_ent.trial_expires_at = module_change.trial_expires_at
                org_ent.source = 'admin_update'
                org_ent.updated_at = datetime.utcnow()
            else:
                org_ent = OrgEntitlement(
                    org_id=org_id,
                    module_id=module.id,
                    status=module_change.status,
                    trial_expires_at=module_change.trial_expires_at,
                    source='admin_update'
                )
                self.db.add(org_ent)

            diff_data["modules"].append({
                "module_key": module_change.module_key,
                "old_status": old_status,
                "new_status": module_change.status,
                "old_trial_expires_at": old_trial_expires.isoformat() if old_trial_expires else None,
                "new_trial_expires_at": module_change.trial_expires_at.isoformat() if module_change.trial_expires_at else None
            })

        # Apply submodule changes
        for submodule_change in request.changes.submodules:
            if submodule_change.module_key not in modules_by_key:
                raise ValueError(f"Invalid module_key: {submodule_change.module_key}")

            module = modules_by_key[submodule_change.module_key]
            submodule_key = (module.id, submodule_change.submodule_key)

            if submodule_key not in submodules_map:
                raise ValueError(f"Invalid submodule_key: {submodule_change.submodule_key} for module {submodule_change.module_key}")

            submodule = submodules_map[submodule_key]

            # Get or create org_subentitlement
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

            old_enabled = org_subent.enabled if org_subent else None

            if org_subent:
                org_subent.enabled = submodule_change.enabled
                org_subent.source = 'admin_update'
                org_subent.updated_at = datetime.utcnow()
            else:
                org_subent = OrgSubentitlement(
                    org_id=org_id,
                    module_id=module.id,
                    submodule_id=submodule.id,
                    enabled=submodule_change.enabled,
                    source='admin_update'
                )
                self.db.add(org_subent)

            diff_data["submodules"].append({
                "module_key": submodule_change.module_key,
                "submodule_key": submodule_change.submodule_key,
                "old_enabled": old_enabled,
                "new_enabled": submodule_change.enabled
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

        # Get org subentitlements
        org_subent_result = await self.db.execute(
            select(OrgSubentitlement)
            .where(OrgSubentitlement.org_id == org_id)
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
            submodules = org_subentitlements.get(org_ent.module_id, {})

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
        # Get module
        module_result = await self.db.execute(
            select(Module).where(
                and_(
                    Module.module_key == module_key,
                    Module.is_active == True
                )
            )
        )
        module = module_result.scalar_one_or_none()
        if not module:
            return False, 'disabled', f"Module '{module_key}' not found"

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
            return False, 'disabled', f"Module '{module_key}' is disabled for this organization"

        if org_ent.status == 'trial':
            if org_ent.trial_expires_at and org_ent.trial_expires_at < datetime.utcnow():
                return False, 'trial_expired', f"Module '{module_key}' trial has expired"

        # If checking submodule
        if submodule_key:
            # Get submodule
            submodule_result = await self.db.execute(
                select(Submodule).where(
                    and_(
                        Submodule.module_id == module.id,
                        Submodule.submodule_key == submodule_key,
                        Submodule.is_active == True
                    )
                )
            )
            submodule = submodule_result.scalar_one_or_none()
            if not submodule:
                return False, 'disabled', f"Submodule '{submodule_key}' not found in module '{module_key}'"

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
                return False, 'disabled', f"Submodule '{submodule_key}' is disabled for this organization"

        return True, org_ent.status, None
