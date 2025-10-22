# app/schemas/website_agent.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


# WebsiteProject Schemas

class WebsiteProjectBase(BaseModel):
    """Base schema for website project"""
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: str = Field(default="landing_page")
    customer_id: Optional[int] = None
    status: str = Field(default="draft")
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    theme: str = Field(default="modern")
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    pages_config: Optional[Dict[str, Any]] = None
    seo_config: Optional[Dict[str, Any]] = None
    analytics_config: Optional[Dict[str, Any]] = None
    deployment_url: Optional[str] = None
    deployment_provider: Optional[str] = None
    chatbot_enabled: bool = False
    chatbot_config: Optional[Dict[str, Any]] = None


class WebsiteProjectCreate(WebsiteProjectBase):
    """Schema for creating a website project"""
    pass


class WebsiteProjectUpdate(BaseModel):
    """Schema for updating a website project"""
    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    project_type: Optional[str] = None
    customer_id: Optional[int] = None
    status: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    theme: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    pages_config: Optional[Dict[str, Any]] = None
    seo_config: Optional[Dict[str, Any]] = None
    analytics_config: Optional[Dict[str, Any]] = None
    deployment_url: Optional[str] = None
    deployment_provider: Optional[str] = None
    chatbot_enabled: Optional[bool] = None
    chatbot_config: Optional[Dict[str, Any]] = None


class WebsiteProject(WebsiteProjectBase):
    """Schema for website project response"""
    id: int
    organization_id: int
    last_deployed_at: Optional[datetime] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# WebsitePage Schemas

class WebsitePageBase(BaseModel):
    """Base schema for website page"""
    page_name: str = Field(..., min_length=1, max_length=200)
    page_slug: str = Field(..., min_length=1, max_length=200)
    page_type: str = Field(default="standard")
    title: str = Field(..., min_length=1)
    meta_description: Optional[str] = None
    content: Optional[str] = None
    sections_config: Optional[Dict[str, Any]] = None
    is_published: bool = False
    order_index: int = 0
    seo_keywords: Optional[str] = None
    og_image: Optional[str] = None


class WebsitePageCreate(WebsitePageBase):
    """Schema for creating a website page"""
    project_id: int


class WebsitePageUpdate(BaseModel):
    """Schema for updating a website page"""
    page_name: Optional[str] = Field(None, min_length=1, max_length=200)
    page_slug: Optional[str] = Field(None, min_length=1, max_length=200)
    page_type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1)
    meta_description: Optional[str] = None
    content: Optional[str] = None
    sections_config: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    order_index: Optional[int] = None
    seo_keywords: Optional[str] = None
    og_image: Optional[str] = None


class WebsitePage(WebsitePageBase):
    """Schema for website page response"""
    id: int
    organization_id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# WebsiteDeployment Schemas

class WebsiteDeploymentBase(BaseModel):
    """Base schema for website deployment"""
    deployment_version: str = Field(..., min_length=1)
    deployment_provider: str = Field(..., min_length=1)
    deployment_config: Optional[Dict[str, Any]] = None


class WebsiteDeploymentCreate(WebsiteDeploymentBase):
    """Schema for creating a website deployment"""
    project_id: int


class WebsiteDeployment(WebsiteDeploymentBase):
    """Schema for website deployment response"""
    id: int
    organization_id: int
    project_id: int
    deployment_status: str
    deployment_url: Optional[str] = None
    deployment_log: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deployed_by_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# WebsiteMaintenanceLog Schemas

class WebsiteMaintenanceLogBase(BaseModel):
    """Base schema for website maintenance log"""
    maintenance_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str = Field(default="completed")
    changes_summary: Optional[str] = None
    files_affected: Optional[Dict[str, Any]] = None
    automated: bool = False
    scheduled_at: Optional[datetime] = None


class WebsiteMaintenanceLogCreate(WebsiteMaintenanceLogBase):
    """Schema for creating a website maintenance log"""
    project_id: int


class WebsiteMaintenanceLog(WebsiteMaintenanceLogBase):
    """Schema for website maintenance log response"""
    id: int
    organization_id: int
    project_id: int
    performed_by_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Wizard Schemas

class WebsiteWizardStep1(BaseModel):
    """Step 1: Basic Information"""
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: str = Field(default="landing_page")
    customer_id: Optional[int] = None


class WebsiteWizardStep2(BaseModel):
    """Step 2: Design Configuration"""
    theme: str = Field(default="modern")
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None


class WebsiteWizardStep3(BaseModel):
    """Step 3: Content Configuration"""
    site_title: str = Field(..., min_length=1)
    site_description: Optional[str] = None
    pages: List[Dict[str, Any]] = Field(default_factory=list)


class WebsiteWizardStep4(BaseModel):
    """Step 4: Integration & Features"""
    chatbot_enabled: bool = False
    chatbot_config: Optional[Dict[str, Any]] = None
    analytics_config: Optional[Dict[str, Any]] = None
    seo_config: Optional[Dict[str, Any]] = None


class WebsiteWizardComplete(BaseModel):
    """Complete wizard data"""
    step1: WebsiteWizardStep1
    step2: WebsiteWizardStep2
    step3: WebsiteWizardStep3
    step4: WebsiteWizardStep4
