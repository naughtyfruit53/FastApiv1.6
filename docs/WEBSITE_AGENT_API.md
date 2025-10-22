# Website Agent API Documentation

## Overview

The Website Agent API provides endpoints for managing website projects, pages, deployments, and maintenance activities. All endpoints require authentication and are scoped to the user's organization.

## Base URL

```
/api/v1/website-agent
```

## Authentication

All endpoints require a valid JWT token passed in the `Authorization` header:

```
Authorization: Bearer <token>
```

## Endpoints

### Website Projects

#### List Projects

```http
GET /api/v1/website-agent/projects
```

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Number of records to return (default: 100, max: 100)
- `status` (string, optional): Filter by status ('draft', 'in_progress', 'review', 'deployed', 'archived')
- `project_type` (string, optional): Filter by type ('landing_page', 'ecommerce', 'corporate', 'blog', 'portfolio')

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "project_name": "Company Website",
    "project_type": "corporate",
    "status": "deployed",
    "theme": "modern",
    "primary_color": "#3f51b5",
    "secondary_color": "#f50057",
    "site_title": "ACME Corporation",
    "site_description": "Leading provider of innovative solutions",
    "deployment_url": "https://acme.example.com",
    "chatbot_enabled": true,
    "created_at": "2025-10-22T10:30:00Z",
    "last_deployed_at": "2025-10-22T14:00:00Z"
  }
]
```

#### Get Project

```http
GET /api/v1/website-agent/projects/{project_id}
```

**Response:** Single project object (same structure as list)

#### Create Project

```http
POST /api/v1/website-agent/projects
```

**Request Body:**
```json
{
  "project_name": "New Website",
  "project_type": "landing_page",
  "customer_id": 123,
  "theme": "modern",
  "primary_color": "#3f51b5",
  "secondary_color": "#f50057",
  "site_title": "Welcome to Our Site",
  "site_description": "This is our new website",
  "chatbot_enabled": true,
  "chatbot_config": {
    "enabled": true,
    "position": "bottom-right"
  }
}
```

**Response:** Created project object (201 Created)

#### Update Project

```http
PUT /api/v1/website-agent/projects/{project_id}
```

**Request Body:** Partial project object (all fields optional)

**Response:** Updated project object

#### Delete Project

```http
DELETE /api/v1/website-agent/projects/{project_id}
```

**Response:** 204 No Content

### Website Pages

#### List Pages

```http
GET /api/v1/website-agent/projects/{project_id}/pages
```

**Response:**
```json
[
  {
    "id": 1,
    "organization_id": 1,
    "project_id": 1,
    "page_name": "Home",
    "page_slug": "home",
    "page_type": "home",
    "title": "Welcome Home",
    "meta_description": "Welcome to our homepage",
    "content": "<h1>Welcome</h1><p>Content here</p>",
    "is_published": true,
    "order_index": 0,
    "created_at": "2025-10-22T10:30:00Z"
  }
]
```

#### Create Page

```http
POST /api/v1/website-agent/projects/{project_id}/pages
```

**Request Body:**
```json
{
  "project_id": 1,
  "page_name": "About Us",
  "page_slug": "about",
  "page_type": "about",
  "title": "About Our Company",
  "meta_description": "Learn more about us",
  "content": "<h1>About Us</h1>",
  "is_published": true,
  "order_index": 1
}
```

**Response:** Created page object (201 Created)

#### Update Page

```http
PUT /api/v1/website-agent/pages/{page_id}
```

**Request Body:** Partial page object

**Response:** Updated page object

#### Delete Page

```http
DELETE /api/v1/website-agent/pages/{page_id}
```

**Response:** 204 No Content

### Deployments

#### Deploy Project

```http
POST /api/v1/website-agent/projects/{project_id}/deploy
```

**Request Body:**
```json
{
  "project_id": 1,
  "deployment_version": "v1.0.0",
  "deployment_provider": "vercel",
  "deployment_config": {
    "build_command": "npm run build",
    "output_directory": "dist"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "organization_id": 1,
  "project_id": 1,
  "deployment_version": "v1.0.0",
  "deployment_status": "success",
  "deployment_provider": "vercel",
  "deployment_url": "https://project.vercel.app",
  "started_at": "2025-10-22T14:00:00Z",
  "completed_at": "2025-10-22T14:05:00Z",
  "created_at": "2025-10-22T14:00:00Z"
}
```

#### List Deployments

```http
GET /api/v1/website-agent/projects/{project_id}/deployments
```

**Response:** Array of deployment objects

### Maintenance Logs

#### Create Maintenance Log

```http
POST /api/v1/website-agent/projects/{project_id}/maintenance
```

**Request Body:**
```json
{
  "project_id": 1,
  "maintenance_type": "content_update",
  "title": "Updated homepage",
  "description": "Refreshed hero section with new images",
  "status": "completed",
  "changes_summary": "Updated 3 images and hero text",
  "automated": false
}
```

**Response:** Created maintenance log object (201 Created)

#### List Maintenance Logs

```http
GET /api/v1/website-agent/projects/{project_id}/maintenance
```

**Response:** Array of maintenance log objects

## Data Models

### WebsiteProject

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_name | string | Yes | Unique project name |
| project_type | string | Yes | Type of website |
| customer_id | integer | No | Linked customer ID |
| status | string | Yes | Project status |
| theme | string | Yes | Visual theme |
| primary_color | string | No | Primary brand color (hex) |
| secondary_color | string | No | Secondary brand color (hex) |
| site_title | string | No | Website title |
| site_description | string | No | Website description |
| logo_url | string | No | Logo image URL |
| favicon_url | string | No | Favicon URL |
| chatbot_enabled | boolean | Yes | Enable chatbot integration |
| deployment_url | string | No | Current deployment URL |
| deployment_provider | string | No | Deployment provider |

### WebsitePage

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | integer | Yes | Parent project ID |
| page_name | string | Yes | Page display name |
| page_slug | string | Yes | URL slug (unique per project) |
| page_type | string | Yes | Page type |
| title | string | Yes | Page title (for SEO) |
| meta_description | string | No | Meta description |
| content | string | No | Page content (HTML/JSON) |
| is_published | boolean | Yes | Publication status |
| order_index | integer | Yes | Display order |

### WebsiteDeployment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | integer | Yes | Parent project ID |
| deployment_version | string | Yes | Version identifier |
| deployment_provider | string | Yes | Provider (vercel, netlify, aws) |
| deployment_config | object | No | Provider-specific configuration |

### WebsiteMaintenanceLog

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | integer | Yes | Parent project ID |
| maintenance_type | string | Yes | Type of maintenance |
| title | string | Yes | Log title |
| description | string | No | Detailed description |
| status | string | Yes | Status (pending, completed, failed) |
| automated | boolean | Yes | Whether automated |

## Error Responses

All endpoints return standard HTTP error codes:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource (e.g., project name)
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing the issue"
}
```

## Organization Scoping

All resources are automatically scoped to the user's organization. Users can only access and modify resources belonging to their organization.

## RBAC

Access to Website Agent endpoints is controlled by the organization's RBAC settings. Required permissions:
- `website_agent.view`: View website projects
- `website_agent.create`: Create projects
- `website_agent.update`: Modify projects
- `website_agent.delete`: Delete projects
- `website_agent.deploy`: Deploy projects

## Best Practices

1. **Project Names**: Use descriptive, unique names for easy identification
2. **Page Slugs**: Keep slugs short, lowercase, and URL-friendly
3. **Versioning**: Use semantic versioning for deployments (v1.0.0)
4. **Maintenance Logs**: Document all changes for audit trail
5. **Testing**: Test deployments before marking projects as "deployed"
6. **Chatbot**: Configure chatbot settings before enabling integration

## Limitations

- Maximum 100 projects per organization
- Maximum 50 pages per project
- Page content size limited to 1MB
- Deployment logs retained for 90 days
- Maintenance logs retained for 1 year

## Integration Examples

### Creating a Complete Website

```python
import requests

API_BASE = "https://api.example.com"
TOKEN = "your_jwt_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# 1. Create project
project = requests.post(
    f"{API_BASE}/api/v1/website-agent/projects",
    headers=headers,
    json={
        "project_name": "My Website",
        "project_type": "landing_page",
        "theme": "modern",
        "site_title": "Welcome",
        "chatbot_enabled": True
    }
).json()

project_id = project["id"]

# 2. Create pages
pages = [
    {"page_name": "Home", "page_slug": "home", "title": "Home", "order_index": 0},
    {"page_name": "About", "page_slug": "about", "title": "About Us", "order_index": 1},
]

for page in pages:
    page["project_id"] = project_id
    page["page_type"] = "standard"
    page["is_published"] = True
    requests.post(
        f"{API_BASE}/api/v1/website-agent/projects/{project_id}/pages",
        headers=headers,
        json=page
    )

# 3. Deploy
deployment = requests.post(
    f"{API_BASE}/api/v1/website-agent/projects/{project_id}/deploy",
    headers=headers,
    json={
        "project_id": project_id,
        "deployment_version": "v1.0.0",
        "deployment_provider": "vercel"
    }
).json()

print(f"Deployed to: {deployment['deployment_url']}")
```

## Support

For API support and questions:
- Email: api-support@example.com
- Documentation: https://docs.example.com
- Status Page: https://status.example.com
