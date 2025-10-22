# tests/test_website_agent.py

import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.website_agent import (
    WebsiteProject,
    WebsitePage,
    WebsiteDeployment,
    WebsiteMaintenanceLog,
)


def test_create_website_project(db: Session, test_organization, test_user):
    """Test creating a website project"""
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Test Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        site_title="Test Site",
        site_description="A test website project",
        chatbot_enabled=True,
        created_by_id=test_user.id,
        updated_by_id=test_user.id,
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    assert project.id is not None
    assert project.project_name == "Test Website"
    assert project.project_type == "landing_page"
    assert project.status == "draft"
    assert project.theme == "modern"
    assert project.chatbot_enabled is True
    assert project.organization_id == test_organization.id


def test_create_website_page(db: Session, test_organization, test_user):
    """Test creating a website page"""
    # First create a project
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Test Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Create a page
    page = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="Home",
        page_slug="home",
        page_type="home",
        title="Welcome Home",
        meta_description="Home page description",
        content="<h1>Welcome</h1>",
        is_published=True,
        order_index=0,
    )
    
    db.add(page)
    db.commit()
    db.refresh(page)
    
    assert page.id is not None
    assert page.page_name == "Home"
    assert page.page_slug == "home"
    assert page.page_type == "home"
    assert page.is_published is True
    assert page.project_id == project.id


def test_create_deployment(db: Session, test_organization, test_user):
    """Test creating a deployment record"""
    # Create a project
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Test Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Create a deployment
    deployment = WebsiteDeployment(
        organization_id=test_organization.id,
        project_id=project.id,
        deployment_version="v1.0.0",
        deployment_status="success",
        deployment_provider="vercel",
        deployment_url="https://test.vercel.app",
        deployed_by_id=test_user.id,
        started_at=datetime.now(),
        completed_at=datetime.now(),
    )
    
    db.add(deployment)
    db.commit()
    db.refresh(deployment)
    
    assert deployment.id is not None
    assert deployment.deployment_version == "v1.0.0"
    assert deployment.deployment_status == "success"
    assert deployment.deployment_provider == "vercel"
    assert deployment.project_id == project.id


def test_create_maintenance_log(db: Session, test_organization, test_user):
    """Test creating a maintenance log"""
    # Create a project
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Test Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Create a maintenance log
    log = WebsiteMaintenanceLog(
        organization_id=test_organization.id,
        project_id=project.id,
        maintenance_type="content_update",
        title="Updated homepage content",
        description="Updated the homepage hero section",
        status="completed",
        changes_summary="Modified hero text and images",
        automated=False,
        performed_by_id=test_user.id,
        completed_at=datetime.now(),
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    assert log.id is not None
    assert log.maintenance_type == "content_update"
    assert log.title == "Updated homepage content"
    assert log.status == "completed"
    assert log.automated is False
    assert log.project_id == project.id


def test_project_with_relationships(db: Session, test_organization, test_user):
    """Test project with all relationships"""
    # Create a project
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Full Test Website",
        project_type="corporate",
        status="in_progress",
        theme="modern",
        chatbot_enabled=True,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add pages
    page1 = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="Home",
        page_slug="home",
        page_type="home",
        title="Home Page",
        is_published=True,
        order_index=0,
    )
    page2 = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="About",
        page_slug="about",
        page_type="about",
        title="About Us",
        is_published=True,
        order_index=1,
    )
    db.add_all([page1, page2])
    db.commit()
    
    # Add deployment
    deployment = WebsiteDeployment(
        organization_id=test_organization.id,
        project_id=project.id,
        deployment_version="v1.0.0",
        deployment_status="success",
        deployment_provider="netlify",
        deployed_by_id=test_user.id,
    )
    db.add(deployment)
    db.commit()
    
    # Add maintenance log
    log = WebsiteMaintenanceLog(
        organization_id=test_organization.id,
        project_id=project.id,
        maintenance_type="security_patch",
        title="Security Update",
        status="completed",
        automated=True,
        performed_by_id=test_user.id,
    )
    db.add(log)
    db.commit()
    
    # Refresh and verify relationships
    db.refresh(project)
    assert len(project.pages) == 2
    assert len(project.deployments) == 1
    assert len(project.maintenance_logs) == 1
    assert project.pages[0].page_name in ["Home", "About"]
    assert project.deployments[0].deployment_version == "v1.0.0"
    assert project.maintenance_logs[0].maintenance_type == "security_patch"


def test_unique_project_name_per_organization(db: Session, test_organization, test_user):
    """Test that project names must be unique per organization"""
    # Create first project
    project1 = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Unique Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project1)
    db.commit()
    
    # Try to create second project with same name
    project2 = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Unique Website",
        project_type="corporate",
        status="draft",
        theme="classic",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project2)
    
    with pytest.raises(Exception):  # Should raise IntegrityError
        db.commit()


def test_unique_page_slug_per_project(db: Session, test_organization, test_user):
    """Test that page slugs must be unique per project"""
    # Create project
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Test Website",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Create first page
    page1 = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="Home",
        page_slug="home",
        page_type="home",
        title="Home Page",
        is_published=True,
        order_index=0,
    )
    db.add(page1)
    db.commit()
    
    # Try to create second page with same slug
    page2 = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="Home Alt",
        page_slug="home",
        page_type="standard",
        title="Home Page Alt",
        is_published=False,
        order_index=1,
    )
    db.add(page2)
    
    with pytest.raises(Exception):  # Should raise IntegrityError
        db.commit()


def test_cascade_delete_project(db: Session, test_organization, test_user):
    """Test that deleting a project cascades to pages, deployments, and logs"""
    # Create project with related records
    project = WebsiteProject(
        organization_id=test_organization.id,
        project_name="Delete Test",
        project_type="landing_page",
        status="draft",
        theme="modern",
        chatbot_enabled=False,
        created_by_id=test_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Add related records
    page = WebsitePage(
        organization_id=test_organization.id,
        project_id=project.id,
        page_name="Home",
        page_slug="home",
        page_type="home",
        title="Home",
        is_published=True,
        order_index=0,
    )
    deployment = WebsiteDeployment(
        organization_id=test_organization.id,
        project_id=project.id,
        deployment_version="v1.0.0",
        deployment_status="success",
        deployment_provider="vercel",
        deployed_by_id=test_user.id,
    )
    log = WebsiteMaintenanceLog(
        organization_id=test_organization.id,
        project_id=project.id,
        maintenance_type="backup",
        title="Backup",
        status="completed",
        automated=True,
        performed_by_id=test_user.id,
    )
    
    db.add_all([page, deployment, log])
    db.commit()
    
    project_id = project.id
    
    # Delete project
    db.delete(project)
    db.commit()
    
    # Verify related records are deleted
    assert db.query(WebsiteProject).filter_by(id=project_id).first() is None
    assert db.query(WebsitePage).filter_by(project_id=project_id).count() == 0
    assert db.query(WebsiteDeployment).filter_by(project_id=project_id).count() == 0
    assert db.query(WebsiteMaintenanceLog).filter_by(project_id=project_id).count() == 0
