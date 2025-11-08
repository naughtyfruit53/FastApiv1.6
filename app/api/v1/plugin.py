"""
Plugin System API endpoints
Manages plugin installation, configuration, and lifecycle
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.enforcement import require_access
from app.models.user_models import User
from app.models.plugin import Plugin, PluginInstallation, PluginHook, PluginRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plugins", tags=["plugins"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class PluginCreate(BaseModel):
    """Schema for creating plugin"""
    name: str = Field(..., description="Plugin name")
    slug: str = Field(..., description="Unique plugin identifier")
    plugin_type: str = Field(..., description="Type of plugin")
    description: Optional[str] = None
    version: str = Field(default="1.0.0")
    author: Optional[str] = None
    entry_point: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    required_permissions: Optional[List[str]] = None


class PluginUpdate(BaseModel):
    """Schema for updating plugin"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None


class PluginResponse(BaseModel):
    """Schema for plugin response"""
    id: int
    organization_id: Optional[int]
    name: str
    slug: str
    version: str
    plugin_type: str
    scope: str
    description: Optional[str]
    author: Optional[str]
    status: str
    enabled: bool
    install_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PluginInstallRequest(BaseModel):
    """Schema for installing plugin"""
    plugin_id: int
    settings: Optional[Dict[str, Any]] = None


class PluginInstallationResponse(BaseModel):
    """Schema for plugin installation response"""
    id: int
    plugin_id: int
    organization_id: int
    installed_version: str
    active: bool
    settings: Optional[Dict[str, Any]]
    installed_at: datetime

    class Config:
        from_attributes = True


class PluginHookCreate(BaseModel):
    """Schema for creating plugin hook"""
    plugin_id: int
    hook_name: str
    event_type: str
    handler_function: str
    priority: int = 100
    description: Optional[str] = None


class PluginHookResponse(BaseModel):
    """Schema for plugin hook response"""
    id: int
    plugin_id: int
    hook_name: str
    event_type: str
    handler_function: str
    priority: int
    enabled: bool
    execution_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Plugin Endpoints
# ============================================================================

@router.post("/", response_model=PluginResponse, status_code=status.HTTP_201_CREATED)
async def create_plugin(
    plugin_data: PluginCreate,
    auth: tuple = Depends(require_access("plugin", "create")),
    db: Session = Depends(get_db)
):
    """
    Create a new plugin (for developers/admins).
    """
    try:
        # Check if slug already exists
        existing = db.query(Plugin).filter(Plugin.slug == plugin_data.slug).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin with this slug already exists"
            )
        
        plugin = Plugin(
            organization_id=org_id,
            name=plugin_data.name,
            slug=plugin_data.slug,
            plugin_type=plugin_data.plugin_type,
            description=plugin_data.description,
            version=plugin_data.version,
            author=plugin_data.author,
            entry_point=plugin_data.entry_point,
            config=plugin_data.config,
            dependencies=plugin_data.dependencies,
            required_permissions=plugin_data.required_permissions,
            status="inactive",
            scope="organization"
        )
        
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        
        logger.info(f"User {current_user.id} created plugin {plugin.id} ({plugin.name})")
        return plugin
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create plugin: {str(e)}"
        )


@router.get("/", response_model=List[PluginResponse])
async def list_plugins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    plugin_type: Optional[str] = None,
    scope: Optional[str] = None,
    auth: tuple = Depends(require_access("plugin", "read")),
    db: Session = Depends(get_db)
):
    """
    List available plugins.
    """
    try:
        query = db.query(Plugin).filter(
            or_(
                Plugin.scope == "global",
                Plugin.organization_id == org_id
            )
        )
        
        if plugin_type:
            query = query.filter(Plugin.plugin_type == plugin_type)
        
        if scope:
            query = query.filter(Plugin.scope == scope)
        
        plugins = query.order_by(desc(Plugin.created_at)).offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.id} listed {len(plugins)} plugins")
        return plugins
        
    except Exception as e:
        logger.error(f"Error listing plugins: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list plugins: {str(e)}"
        )


@router.get("/{plugin_id}", response_model=PluginResponse)
async def get_plugin(
    plugin_id: int,
    auth: tuple = Depends(require_access("plugin", "read")),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific plugin.
    """
    try:
        plugin = db.query(Plugin).filter(
            and_(
                Plugin.id == plugin_id,
                or_(
                    Plugin.scope == "global",
                    Plugin.organization_id == org_id
                )
            )
        ).first()
        
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        return plugin
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get plugin: {str(e)}"
        )


@router.put("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: int,
    plugin_data: PluginUpdate,
    auth: tuple = Depends(require_access("plugin", "update")),
    db: Session = Depends(get_db)
):
    """
    Update a plugin.
    """
    try:
        plugin = db.query(Plugin).filter(
            and_(
                Plugin.id == plugin_id,
                Plugin.organization_id == org_id
            )
        ).first()
        
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        # Update fields
        update_data = plugin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(plugin, field, value)
        
        db.commit()
        db.refresh(plugin)
        
        logger.info(f"User {current_user.id} updated plugin {plugin.id}")
        return plugin
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update plugin: {str(e)}"
        )


# ============================================================================
# Plugin Installation Endpoints
# ============================================================================

@router.post("/install", response_model=PluginInstallationResponse, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    install_request: PluginInstallRequest,
    auth: tuple = Depends(require_access("plugin", "create")),
    db: Session = Depends(get_db)
):
    """
    Install a plugin for the organization.
    """
    try:
        # Verify plugin exists
        plugin = db.query(Plugin).filter(Plugin.id == install_request.plugin_id).first()
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        # Check if already installed
        existing = db.query(PluginInstallation).filter(
            and_(
                PluginInstallation.plugin_id == install_request.plugin_id,
                PluginInstallation.organization_id == org_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin already installed"
            )
        
        installation = PluginInstallation(
            plugin_id=install_request.plugin_id,
            organization_id=org_id,
            installed_by=current_user.id,
            installed_version=plugin.version,
            active=True,
            settings=install_request.settings
        )
        
        db.add(installation)
        
        # Update plugin install count
        plugin.install_count += 1
        plugin.last_installed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(installation)
        
        logger.info(f"User {current_user.id} installed plugin {plugin.id}")
        return installation
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error installing plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to install plugin: {str(e)}"
        )


@router.get("/installations", response_model=List[PluginInstallationResponse])
async def list_installations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active: Optional[bool] = None,
    auth: tuple = Depends(require_access("plugin", "read")),
    db: Session = Depends(get_db)
):
    """
    List installed plugins for the organization.
    """
    try:
        query = db.query(PluginInstallation).filter(
            PluginInstallation.organization_id == org_id
        )
        
        if active is not None:
            query = query.filter(PluginInstallation.active == active)
        
        installations = query.order_by(desc(PluginInstallation.installed_at)).offset(skip).limit(limit).all()
        
        return installations
        
    except Exception as e:
        logger.error(f"Error listing installations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list installations: {str(e)}"
        )


@router.delete("/installations/{installation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_plugin(
    installation_id: int,
    auth: tuple = Depends(require_access("plugin", "delete")),
    db: Session = Depends(get_db)
):
    """
    Uninstall a plugin.
    """
    try:
        installation = db.query(PluginInstallation).filter(
            and_(
                PluginInstallation.id == installation_id,
                PluginInstallation.organization_id == org_id
            )
        ).first()
        
        if not installation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Installation not found"
            )
        
        db.delete(installation)
        db.commit()
        
        logger.info(f"User {current_user.id} uninstalled plugin installation {installation_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uninstalling plugin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to uninstall plugin: {str(e)}"
        )


# ============================================================================
# Plugin Hook Endpoints
# ============================================================================

@router.post("/hooks", response_model=PluginHookResponse, status_code=status.HTTP_201_CREATED)
async def create_hook(
    hook_data: PluginHookCreate,
    auth: tuple = Depends(require_access("plugin", "create")),
    db: Session = Depends(get_db)
):
    """
    Register a plugin hook.
    """
    try:
        hook = PluginHook(
            plugin_id=hook_data.plugin_id,
            hook_name=hook_data.hook_name,
            event_type=hook_data.event_type,
            handler_function=hook_data.handler_function,
            priority=hook_data.priority,
            description=hook_data.description
        )
        
        db.add(hook)
        db.commit()
        db.refresh(hook)
        
        logger.info(f"Created hook {hook.id} for plugin {hook_data.plugin_id}")
        return hook
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating hook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create hook: {str(e)}"
        )


@router.get("/hooks", response_model=List[PluginHookResponse])
async def list_hooks(
    plugin_id: Optional[int] = None,
    event_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    auth: tuple = Depends(require_access("plugin", "read")),
    db: Session = Depends(get_db)
):
    """
    List plugin hooks.
    """
    try:
        query = db.query(PluginHook)
        
        if plugin_id:
            query = query.filter(PluginHook.plugin_id == plugin_id)
        
        if event_type:
            query = query.filter(PluginHook.event_type == event_type)
        
        hooks = query.order_by(PluginHook.priority).offset(skip).limit(limit).all()
        
        return hooks
        
    except Exception as e:
        logger.error(f"Error listing hooks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list hooks: {str(e)}"
        )
