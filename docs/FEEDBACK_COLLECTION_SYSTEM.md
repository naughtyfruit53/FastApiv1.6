# Feedback Collection & Issue Triage System

## Overview

This document outlines the comprehensive feedback collection and issue triage system designed to capture user feedback, bug reports, enhancement requests, and provide structured workflows for issue resolution and feature development.

## Feedback Collection Mechanisms

### 1. In-App Feedback System

#### Feedback Widget Integration
```typescript
// frontend/src/components/FeedbackWidget.tsx
import React, { useState } from 'react';
import {
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Rating,
  Chip,
  Box,
  Typography,
  Alert
} from '@mui/material';
import { Feedback, BugReport, Lightbulb } from '@mui/icons-material';

interface FeedbackData {
  type: 'bug' | 'feature' | 'improvement' | 'question' | 'complaint' | 'praise';
  category: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  urgency: 'low' | 'medium' | 'high' | 'critical';
  satisfaction_rating: number;
  affected_module: string;
  steps_to_reproduce?: string;
  expected_behavior?: string;
  actual_behavior?: string;
  browser_info: string;
  user_agent: string;
  screenshot?: File;
  attachments?: File[];
}

const FeedbackWidget: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [feedbackData, setFeedbackData] = useState<FeedbackData>({
    type: 'bug',
    category: 'migration',
    title: '',
    description: '',
    severity: 'medium',
    urgency: 'medium',
    satisfaction_rating: 5,
    affected_module: 'migration_wizard',
    browser_info: navigator.userAgent,
    user_agent: navigator.userAgent
  });
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const feedbackTypes = [
    { value: 'bug', label: 'Bug Report', icon: <BugReport />, color: '#f44336' },
    { value: 'feature', label: 'Feature Request', icon: <Lightbulb />, color: '#ff9800' },
    { value: 'improvement', label: 'Improvement', icon: <Lightbulb />, color: '#2196f3' },
    { value: 'question', label: 'Question', icon: <Feedback />, color: '#9c27b0' },
    { value: 'complaint', label: 'Complaint', icon: <Feedback />, color: '#f44336' },
    { value: 'praise', label: 'Praise', icon: <Feedback />, color: '#4caf50' }
  ];

  const categories = [
    'migration',
    'integration_dashboard',
    'tally_integration',
    'email_integration',
    'calendar_integration',
    'user_management',
    'permissions',
    'performance',
    'ui_ux',
    'documentation',
    'other'
  ];

  const modules = [
    'migration_wizard',
    'integration_dashboard',
    'job_management',
    'file_upload',
    'data_mapping',
    'validation',
    'progress_monitoring',
    'rollback',
    'permission_management',
    'health_monitoring',
    'settings',
    'reports',
    'other'
  ];

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const formData = new FormData();
      
      // Add feedback data
      Object.entries(feedbackData).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          formData.append(key, value.toString());
        }
      });

      // Add screenshot if present
      if (feedbackData.screenshot) {
        formData.append('screenshot', feedbackData.screenshot);
      }

      // Add attachments if present
      if (feedbackData.attachments) {
        feedbackData.attachments.forEach((file, index) => {
          formData.append(`attachment_${index}`, file);
        });
      }

      // Add context information
      formData.append('url', window.location.href);
      formData.append('timestamp', new Date().toISOString());
      formData.append('viewport_size', `${window.innerWidth}x${window.innerHeight}`);
      formData.append('local_storage_data', JSON.stringify({
        theme: localStorage.getItem('theme'),
        language: localStorage.getItem('language')
      }));

      const response = await fetch('/api/v1/feedback/submit', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        setSubmitted(true);
        setTimeout(() => {
          setOpen(false);
          setSubmitted(false);
          // Reset form
          setFeedbackData({
            type: 'bug',
            category: 'migration',
            title: '',
            description: '',
            severity: 'medium',
            urgency: 'medium',
            satisfaction_rating: 5,
            affected_module: 'migration_wizard',
            browser_info: navigator.userAgent,
            user_agent: navigator.userAgent
          });
        }, 2000);
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleScreenshot = async () => {
    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      // Use html2canvas or similar library for screenshot
      // This is a simplified version
      const screenshotBlob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((blob) => resolve(blob!), 'image/png');
      });
      
      const file = new File([screenshotBlob], 'screenshot.png', { type: 'image/png' });
      setFeedbackData(prev => ({ ...prev, screenshot: file }));
    } catch (error) {
      console.error('Error taking screenshot:', error);
    }
  };

  return (
    <>
      <Fab
        color="primary"
        aria-label="feedback"
        onClick={() => setOpen(true)}
        sx={{
          position: 'fixed',
          bottom: 20,
          right: 20,
          zIndex: 1000
        }}
      >
        <Feedback />
      </Fab>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {submitted ? 'Feedback Submitted!' : 'Share Your Feedback'}
        </DialogTitle>
        
        <DialogContent>
          {submitted ? (
            <Alert severity="success">
              Thank you for your feedback! We'll review it and get back to you if needed.
            </Alert>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* Feedback Type Selection */}
              <FormControl fullWidth>
                <InputLabel>Feedback Type</InputLabel>
                <Select
                  value={feedbackData.type}
                  label="Feedback Type"
                  onChange={(e) => setFeedbackData(prev => ({
                    ...prev,
                    type: e.target.value as FeedbackData['type']
                  }))}
                >
                  {feedbackTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {type.icon}
                        {type.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Category and Module */}
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={feedbackData.category}
                    label="Category"
                    onChange={(e) => setFeedbackData(prev => ({
                      ...prev,
                      category: e.target.value
                    }))}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category} value={category}>
                        {category.replace('_', ' ').toUpperCase()}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl fullWidth>
                  <InputLabel>Affected Module</InputLabel>
                  <Select
                    value={feedbackData.affected_module}
                    label="Affected Module"
                    onChange={(e) => setFeedbackData(prev => ({
                      ...prev,
                      affected_module: e.target.value
                    }))}
                  >
                    {modules.map((module) => (
                      <MenuItem key={module} value={module}>
                        {module.replace('_', ' ').toUpperCase()}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              {/* Title and Description */}
              <TextField
                fullWidth
                label="Title"
                value={feedbackData.title}
                onChange={(e) => setFeedbackData(prev => ({
                  ...prev,
                  title: e.target.value
                }))}
                required
              />

              <TextField
                fullWidth
                label="Description"
                multiline
                rows={4}
                value={feedbackData.description}
                onChange={(e) => setFeedbackData(prev => ({
                  ...prev,
                  description: e.target.value
                }))}
                required
              />

              {/* Bug-specific fields */}
              {feedbackData.type === 'bug' && (
                <>
                  <TextField
                    fullWidth
                    label="Steps to Reproduce"
                    multiline
                    rows={3}
                    value={feedbackData.steps_to_reproduce || ''}
                    onChange={(e) => setFeedbackData(prev => ({
                      ...prev,
                      steps_to_reproduce: e.target.value
                    }))}
                  />

                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                      fullWidth
                      label="Expected Behavior"
                      value={feedbackData.expected_behavior || ''}
                      onChange={(e) => setFeedbackData(prev => ({
                        ...prev,
                        expected_behavior: e.target.value
                      }))}
                    />

                    <TextField
                      fullWidth
                      label="Actual Behavior"
                      value={feedbackData.actual_behavior || ''}
                      onChange={(e) => setFeedbackData(prev => ({
                        ...prev,
                        actual_behavior: e.target.value
                      }))}
                    />
                  </Box>
                </>
              )}

              {/* Severity and Urgency for bugs and feature requests */}
              {(feedbackData.type === 'bug' || feedbackData.type === 'feature') && (
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <FormControl fullWidth>
                    <InputLabel>Severity</InputLabel>
                    <Select
                      value={feedbackData.severity}
                      label="Severity"
                      onChange={(e) => setFeedbackData(prev => ({
                        ...prev,
                        severity: e.target.value as FeedbackData['severity']
                      }))}
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="critical">Critical</MenuItem>
                    </Select>
                  </FormControl>

                  <FormControl fullWidth>
                    <InputLabel>Urgency</InputLabel>
                    <Select
                      value={feedbackData.urgency}
                      label="Urgency"
                      onChange={(e) => setFeedbackData(prev => ({
                        ...prev,
                        urgency: e.target.value as FeedbackData['urgency']
                      }))}
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="critical">Critical</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              )}

              {/* Satisfaction Rating */}
              <Box>
                <Typography component="legend">Overall Satisfaction</Typography>
                <Rating
                  value={feedbackData.satisfaction_rating}
                  onChange={(_, newValue) => setFeedbackData(prev => ({
                    ...prev,
                    satisfaction_rating: newValue || 5
                  }))}
                  size="large"
                />
              </Box>

              {/* Screenshot and Attachments */}
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleScreenshot}
                  startIcon={<BugReport />}
                >
                  Take Screenshot
                </Button>
                
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<Feedback />}
                >
                  Attach Files
                  <input
                    type="file"
                    hidden
                    multiple
                    onChange={(e) => {
                      const files = Array.from(e.target.files || []);
                      setFeedbackData(prev => ({
                        ...prev,
                        attachments: files
                      }));
                    }}
                  />
                </Button>
              </Box>

              {/* Show attached files */}
              {(feedbackData.screenshot || feedbackData.attachments?.length) && (
                <Box>
                  <Typography variant="subtitle2">Attachments:</Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                    {feedbackData.screenshot && (
                      <Chip label="Screenshot" onDelete={() => 
                        setFeedbackData(prev => ({ ...prev, screenshot: undefined }))
                      } />
                    )}
                    {feedbackData.attachments?.map((file, index) => (
                      <Chip
                        key={index}
                        label={file.name}
                        onDelete={() => {
                          const newAttachments = [...(feedbackData.attachments || [])];
                          newAttachments.splice(index, 1);
                          setFeedbackData(prev => ({ ...prev, attachments: newAttachments }));
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setOpen(false)}>
            {submitted ? 'Close' : 'Cancel'}
          </Button>
          {!submitted && (
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={!feedbackData.title || !feedbackData.description || submitting}
            >
              {submitting ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FeedbackWidget;
```

### 2. Backend Feedback API

#### Feedback Submission API
```python
# app/api/v1/feedback.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import json

from app.core.database import get_db
from app.api.v1.auth import get_current_active_user
from app.core.org_restrictions import require_current_organization_id
from app.models import User
from app.models.feedback_models import (
    FeedbackSubmission, FeedbackType, FeedbackStatus, FeedbackPriority,
    FeedbackCategory, FeedbackAttachment
)
from app.schemas.feedback import (
    FeedbackSubmissionCreate, FeedbackSubmissionResponse,
    FeedbackSearchResponse, FeedbackStatistics
)
from app.services.feedback_service import FeedbackService
from app.services.notification_service import NotificationService

router = APIRouter()

@router.post("/submit", response_model=FeedbackSubmissionResponse)
async def submit_feedback(
    type: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    severity: Optional[str] = Form("medium"),
    urgency: Optional[str] = Form("medium"),
    satisfaction_rating: Optional[int] = Form(5),
    affected_module: Optional[str] = Form(None),
    steps_to_reproduce: Optional[str] = Form(None),
    expected_behavior: Optional[str] = Form(None),
    actual_behavior: Optional[str] = Form(None),
    browser_info: Optional[str] = Form(None),
    user_agent: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    viewport_size: Optional[str] = Form(None),
    local_storage_data: Optional[str] = Form(None),
    screenshot: Optional[UploadFile] = File(None),
    attachments: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Submit user feedback, bug reports, or feature requests"""
    
    feedback_service = FeedbackService(db)
    notification_service = NotificationService()
    
    # Create feedback submission
    feedback_data = {
        "type": type,
        "category": category,
        "title": title,
        "description": description,
        "severity": severity,
        "urgency": urgency,
        "satisfaction_rating": satisfaction_rating,
        "affected_module": affected_module,
        "steps_to_reproduce": steps_to_reproduce,
        "expected_behavior": expected_behavior,
        "actual_behavior": actual_behavior,
        "browser_info": browser_info,
        "user_agent": user_agent,
        "url": url,
        "viewport_size": viewport_size,
        "local_storage_data": json.loads(local_storage_data) if local_storage_data else None
    }
    
    feedback = await feedback_service.create_feedback(
        feedback_data, current_user.id, organization_id
    )
    
    # Handle file uploads
    if screenshot:
        await feedback_service.add_attachment(
            feedback.id, screenshot, "screenshot"
        )
    
    if attachments:
        for attachment in attachments:
            await feedback_service.add_attachment(
                feedback.id, attachment, "attachment"
            )
    
    # Auto-assign based on category and severity
    assigned_to = await feedback_service.auto_assign_feedback(feedback)
    
    # Send notifications
    if feedback.severity in ["high", "critical"] or feedback.type == "bug":
        await notification_service.notify_feedback_submission(feedback, assigned_to)
    
    return feedback

@router.get("/search", response_model=List[FeedbackSearchResponse])
async def search_feedback(
    q: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Search and filter feedback submissions"""
    
    # Only super admins or assigned users can search all feedback
    if not current_user.is_super_admin:
        created_by = current_user.id  # Regular users only see their own feedback
    
    feedback_service = FeedbackService(db)
    
    search_params = {
        "query": q,
        "type": type,
        "category": category,
        "status": status,
        "severity": severity,
        "assigned_to": assigned_to,
        "created_by": created_by,
        "organization_id": organization_id,
        "date_from": date_from,
        "date_to": date_to,
        "limit": limit,
        "offset": offset
    }
    
    return await feedback_service.search_feedback(search_params)

@router.get("/statistics", response_model=FeedbackStatistics)
async def get_feedback_statistics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Get feedback statistics and analytics"""
    
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feedback_service = FeedbackService(db)
    return await feedback_service.get_feedback_statistics(organization_id, days)

@router.put("/{feedback_id}/status")
async def update_feedback_status(
    feedback_id: int,
    status: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Update feedback status (admin only)"""
    
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feedback_service = FeedbackService(db)
    notification_service = NotificationService()
    
    feedback = await feedback_service.update_feedback_status(
        feedback_id, status, resolution_notes, current_user.id
    )
    
    # Notify user of status change
    if status in ["resolved", "closed", "wont_fix"]:
        await notification_service.notify_feedback_resolution(feedback)
    
    return {"message": "Feedback status updated successfully"}

@router.post("/{feedback_id}/assign")
async def assign_feedback(
    feedback_id: int,
    assigned_to: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_id: int = Depends(require_current_organization_id)
):
    """Assign feedback to a team member (admin only)"""
    
    if not current_user.is_super_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feedback_service = FeedbackService(db)
    notification_service = NotificationService()
    
    feedback = await feedback_service.assign_feedback(
        feedback_id, assigned_to, current_user.id
    )
    
    # Notify assigned user
    await notification_service.notify_feedback_assignment(feedback)
    
    return {"message": "Feedback assigned successfully"}
```

### 3. Issue Triage Workflow

#### Automated Triage System
```python
# app/services/feedback_triage.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta

class TriagePriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TriageCategory(Enum):
    BUG_CRITICAL = "bug_critical"
    BUG_NORMAL = "bug_normal"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    SECURITY = "security"

@dataclass
class TriageRule:
    name: str
    condition: callable
    priority: TriagePriority
    category: TriageCategory
    assigned_team: str
    escalation_time_hours: int
    auto_responses: List[str]

class FeedbackTriageService:
    def __init__(self):
        self.triage_rules = self._load_triage_rules()
        self.keyword_mappings = self._load_keyword_mappings()
        self.team_assignments = self._load_team_assignments()
    
    def _load_triage_rules(self) -> List[TriageRule]:
        """Load triage rules configuration"""
        return [
            TriageRule(
                name="Critical Security Issue",
                condition=lambda f: any(word in f.description.lower() for word in 
                    ['security', 'vulnerability', 'exploit', 'hack', 'breach', 'password leak']),
                priority=TriagePriority.CRITICAL,
                category=TriageCategory.SECURITY,
                assigned_team="security",
                escalation_time_hours=2,
                auto_responses=["Security team notified", "Investigating immediately"]
            ),
            TriageRule(
                name="Migration Data Loss",
                condition=lambda f: f.category == "migration" and any(word in f.description.lower() for word in 
                    ['data loss', 'lost data', 'missing records', 'deleted', 'corrupted']),
                priority=TriagePriority.CRITICAL,
                category=TriageCategory.BUG_CRITICAL,
                assigned_team="migration",
                escalation_time_hours=4,
                auto_responses=["Critical migration issue", "Data integrity team notified"]
            ),
            TriageRule(
                name="Integration Failure",
                condition=lambda f: f.category.startswith("integration") and f.severity == "critical",
                priority=TriagePriority.HIGH,
                category=TriageCategory.BUG_CRITICAL,
                assigned_team="integration",
                escalation_time_hours=8,
                auto_responses=["Integration team assigned", "Investigating connection issues"]
            ),
            TriageRule(
                name="Performance Issue",
                condition=lambda f: any(word in f.description.lower() for word in 
                    ['slow', 'timeout', 'performance', 'lag', 'freeze', 'crash']),
                priority=TriagePriority.MEDIUM,
                category=TriageCategory.PERFORMANCE,
                assigned_team="performance",
                escalation_time_hours=24,
                auto_responses=["Performance team reviewing", "Analyzing system metrics"]
            ),
            TriageRule(
                name="Feature Request",
                condition=lambda f: f.type == "feature",
                priority=TriagePriority.LOW,
                category=TriageCategory.FEATURE_REQUEST,
                assigned_team="product",
                escalation_time_hours=72,
                auto_responses=["Feature request logged", "Product team will review"]
            ),
            TriageRule(
                name="Documentation Issue",
                condition=lambda f: any(word in f.description.lower() for word in 
                    ['documentation', 'help', 'guide', 'tutorial', 'unclear', 'confusing']),
                priority=TriagePriority.LOW,
                category=TriageCategory.DOCUMENTATION,
                assigned_team="documentation",
                escalation_time_hours=48,
                auto_responses=["Documentation team notified", "Will update guides"]
            ),
            TriageRule(
                name="UI/UX Issue",
                condition=lambda f: any(word in f.description.lower() for word in 
                    ['ui', 'ux', 'interface', 'design', 'layout', 'button', 'form']),
                priority=TriagePriority.MEDIUM,
                category=TriageCategory.IMPROVEMENT,
                assigned_team="frontend",
                escalation_time_hours=48,
                auto_responses=["UI/UX team assigned", "Reviewing design feedback"]
            )
        ]
    
    def _load_keyword_mappings(self) -> Dict[str, List[str]]:
        """Load keyword mappings for automatic categorization"""
        return {
            "migration": [
                "import", "export", "migrate", "transfer", "data import", "tally import",
                "excel import", "csv import", "mapping", "validation", "rollback"
            ],
            "integration": [
                "sync", "connection", "api", "webhook", "tally", "zoho", "email",
                "calendar", "integration", "external"
            ],
            "performance": [
                "slow", "timeout", "lag", "freeze", "crash", "memory", "cpu",
                "loading", "response time", "performance"
            ],
            "security": [
                "security", "vulnerability", "exploit", "hack", "breach", "password",
                "authentication", "authorization", "permission", "access"
            ],
            "ui_ux": [
                "interface", "design", "layout", "button", "form", "navigation",
                "menu", "color", "font", "responsive", "mobile"
            ]
        }
    
    def _load_team_assignments(self) -> Dict[str, Dict]:
        """Load team assignment configuration"""
        return {
            "security": {
                "lead": "security-lead@company.com",
                "members": ["sec1@company.com", "sec2@company.com"],
                "escalation_manager": "cto@company.com",
                "slack_channel": "#security-alerts"
            },
            "migration": {
                "lead": "migration-lead@company.com", 
                "members": ["mig1@company.com", "mig2@company.com"],
                "escalation_manager": "dev-manager@company.com",
                "slack_channel": "#migration-support"
            },
            "integration": {
                "lead": "integration-lead@company.com",
                "members": ["int1@company.com", "int2@company.com"], 
                "escalation_manager": "dev-manager@company.com",
                "slack_channel": "#integration-support"
            },
            "performance": {
                "lead": "perf-lead@company.com",
                "members": ["perf1@company.com", "perf2@company.com"],
                "escalation_manager": "dev-manager@company.com",
                "slack_channel": "#performance"
            },
            "product": {
                "lead": "product-manager@company.com",
                "members": ["pm1@company.com", "pm2@company.com"],
                "escalation_manager": "cpo@company.com",
                "slack_channel": "#product-feedback"
            },
            "frontend": {
                "lead": "frontend-lead@company.com",
                "members": ["fe1@company.com", "fe2@company.com"],
                "escalation_manager": "dev-manager@company.com",
                "slack_channel": "#frontend-support"
            },
            "documentation": {
                "lead": "docs-lead@company.com",
                "members": ["docs1@company.com", "docs2@company.com"],
                "escalation_manager": "product-manager@company.com",
                "slack_channel": "#documentation"
            }
        }
    
    def triage_feedback(self, feedback) -> Dict:
        """Automatically triage feedback and assign priority/team"""
        
        triage_result = {
            "feedback_id": feedback.id,
            "original_priority": feedback.severity,
            "triaged_priority": None,
            "category": None,
            "assigned_team": None,
            "assigned_members": [],
            "escalation_time": None,
            "auto_responses": [],
            "confidence_score": 0.0,
            "matching_rules": [],
            "recommended_actions": []
        }
        
        # Apply triage rules
        matching_rules = []
        for rule in self.triage_rules:
            try:
                if rule.condition(feedback):
                    matching_rules.append(rule)
            except Exception as e:
                print(f"Error applying rule {rule.name}: {e}")
        
        if matching_rules:
            # Use the highest priority rule
            best_rule = max(matching_rules, key=lambda r: 
                ["low", "medium", "high", "critical"].index(r.priority.value))
            
            triage_result.update({
                "triaged_priority": best_rule.priority.value,
                "category": best_rule.category.value,
                "assigned_team": best_rule.assigned_team,
                "assigned_members": self.team_assignments[best_rule.assigned_team]["members"],
                "escalation_time": datetime.utcnow() + timedelta(hours=best_rule.escalation_time_hours),
                "auto_responses": best_rule.auto_responses,
                "confidence_score": 0.9,
                "matching_rules": [rule.name for rule in matching_rules]
            })
        else:
            # Default triage for unmatched feedback
            triage_result.update({
                "triaged_priority": feedback.severity,
                "category": "general",
                "assigned_team": "support",
                "confidence_score": 0.3,
                "recommended_actions": ["Manual review required"]
            })
        
        # Add keyword-based suggestions
        triage_result["keyword_analysis"] = self._analyze_keywords(feedback)
        
        return triage_result
    
    def _analyze_keywords(self, feedback) -> Dict:
        """Analyze keywords in feedback for additional context"""
        text = f"{feedback.title} {feedback.description}".lower()
        
        keyword_scores = {}
        for category, keywords in self.keyword_mappings.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                keyword_scores[category] = score
        
        return {
            "keyword_scores": keyword_scores,
            "primary_category": max(keyword_scores.items(), key=lambda x: x[1])[0] if keyword_scores else None,
            "confidence": max(keyword_scores.values()) / len(self.keyword_mappings) if keyword_scores else 0
        }
    
    def escalate_overdue_feedback(self):
        """Check for overdue feedback and escalate as needed"""
        # This would be run as a scheduled task
        overdue_feedback = self._get_overdue_feedback()
        
        for feedback in overdue_feedback:
            team_config = self.team_assignments.get(feedback.assigned_team)
            if team_config:
                self._send_escalation_notification(feedback, team_config)
    
    def _get_overdue_feedback(self):
        """Get feedback that is overdue for response"""
        # Implementation to query database for overdue feedback
        pass
    
    def _send_escalation_notification(self, feedback, team_config):
        """Send escalation notification to team manager"""
        # Implementation to send escalation notifications
        pass
```

### 4. Feedback Analytics Dashboard

#### Analytics and Reporting
```python
# app/services/feedback_analytics.py
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any

class FeedbackAnalyticsService:
    def __init__(self, db):
        self.db = db
    
    def get_feedback_overview(self, organization_id: int, days: int = 30) -> Dict:
        """Get comprehensive feedback overview"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Basic counts
        total_feedback = self.db.query(FeedbackSubmission).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).count()
        
        # Feedback by type
        feedback_by_type = self.db.query(
            FeedbackSubmission.type,
            func.count(FeedbackSubmission.id).label('count')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(FeedbackSubmission.type).all()
        
        # Feedback by status
        feedback_by_status = self.db.query(
            FeedbackSubmission.status,
            func.count(FeedbackSubmission.id).label('count')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(FeedbackSubmission.status).all()
        
        # Average satisfaction rating
        avg_satisfaction = self.db.query(
            func.avg(FeedbackSubmission.satisfaction_rating)
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).scalar() or 0
        
        # Response time metrics
        resolved_feedback = self.db.query(FeedbackSubmission).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.status == 'resolved',
                FeedbackSubmission.resolved_at.isnot(None),
                FeedbackSubmission.created_at >= since
            )
        ).all()
        
        response_times = []
        for feedback in resolved_feedback:
            response_time = (feedback.resolved_at - feedback.created_at).total_seconds() / 3600
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "period_days": days,
            "total_feedback": total_feedback,
            "feedback_by_type": {item.type: item.count for item in feedback_by_type},
            "feedback_by_status": {item.status: item.count for item in feedback_by_status},
            "average_satisfaction": round(avg_satisfaction, 2),
            "average_response_time_hours": round(avg_response_time, 2),
            "resolution_rate": len([f for f in resolved_feedback]) / total_feedback * 100 if total_feedback > 0 else 0
        }
    
    def get_trend_analysis(self, organization_id: int, days: int = 90) -> Dict:
        """Get feedback trends over time"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Daily feedback counts
        daily_feedback = self.db.query(
            func.date(FeedbackSubmission.created_at).label('date'),
            func.count(FeedbackSubmission.id).label('count')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(func.date(FeedbackSubmission.created_at)).all()
        
        # Weekly satisfaction trend
        weekly_satisfaction = self.db.query(
            func.date_trunc('week', FeedbackSubmission.created_at).label('week'),
            func.avg(FeedbackSubmission.satisfaction_rating).label('avg_rating')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(func.date_trunc('week', FeedbackSubmission.created_at)).all()
        
        return {
            "daily_feedback": [
                {"date": item.date.isoformat(), "count": item.count} 
                for item in daily_feedback
            ],
            "weekly_satisfaction": [
                {"week": item.week.isoformat(), "rating": round(item.avg_rating, 2)}
                for item in weekly_satisfaction
            ]
        }
    
    def get_category_analysis(self, organization_id: int, days: int = 30) -> Dict:
        """Analyze feedback by category and module"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Feedback by category
        category_stats = self.db.query(
            FeedbackSubmission.category,
            func.count(FeedbackSubmission.id).label('count'),
            func.avg(FeedbackSubmission.satisfaction_rating).label('avg_rating')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(FeedbackSubmission.category).all()
        
        # Feedback by affected module
        module_stats = self.db.query(
            FeedbackSubmission.affected_module,
            func.count(FeedbackSubmission.id).label('count'),
            func.avg(FeedbackSubmission.satisfaction_rating).label('avg_rating')
        ).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since
            )
        ).group_by(FeedbackSubmission.affected_module).all()
        
        return {
            "category_stats": [
                {
                    "category": item.category,
                    "count": item.count,
                    "avg_rating": round(item.avg_rating, 2)
                }
                for item in category_stats
            ],
            "module_stats": [
                {
                    "module": item.affected_module,
                    "count": item.count,
                    "avg_rating": round(item.avg_rating, 2)
                }
                for item in module_stats
            ]
        }
    
    def get_top_issues(self, organization_id: int, days: int = 30, limit: int = 10) -> List[Dict]:
        """Get most frequently reported issues"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Group similar feedback by keywords and patterns
        feedback_items = self.db.query(FeedbackSubmission).filter(
            and_(
                FeedbackSubmission.organization_id == organization_id,
                FeedbackSubmission.created_at >= since,
                FeedbackSubmission.type == 'bug'
            )
        ).all()
        
        # Simple keyword extraction for grouping
        issue_groups = {}
        for feedback in feedback_items:
            # Extract key phrases (simplified implementation)
            text = f"{feedback.title} {feedback.description}".lower()
            key_phrases = self._extract_key_phrases(text)
            
            for phrase in key_phrases:
                if phrase not in issue_groups:
                    issue_groups[phrase] = {
                        "phrase": phrase,
                        "count": 0,
                        "feedback_ids": [],
                        "avg_severity": 0,
                        "latest_report": None
                    }
                
                issue_groups[phrase]["count"] += 1
                issue_groups[phrase]["feedback_ids"].append(feedback.id)
                issue_groups[phrase]["latest_report"] = max(
                    issue_groups[phrase]["latest_report"] or feedback.created_at,
                    feedback.created_at
                )
        
        # Sort by frequency and return top issues
        top_issues = sorted(
            issue_groups.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:limit]
        
        return top_issues
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from feedback text (simplified)"""
        # This is a simplified implementation
        # In production, use NLP libraries like spaCy or NLTK
        common_phrases = [
            "migration failed", "sync error", "connection timeout", "data loss",
            "slow performance", "ui bug", "form error", "login issue",
            "upload failed", "validation error", "permission denied"
        ]
        
        found_phrases = []
        for phrase in common_phrases:
            if phrase in text:
                found_phrases.append(phrase)
        
        return found_phrases

    def generate_feedback_report(self, organization_id: int, days: int = 30) -> Dict:
        """Generate comprehensive feedback report"""
        overview = self.get_feedback_overview(organization_id, days)
        trends = self.get_trend_analysis(organization_id, days)
        categories = self.get_category_analysis(organization_id, days)
        top_issues = self.get_top_issues(organization_id, days)
        
        return {
            "report_generated": datetime.utcnow().isoformat(),
            "organization_id": organization_id,
            "period_days": days,
            "overview": overview,
            "trends": trends,
            "categories": categories,
            "top_issues": top_issues,
            "recommendations": self._generate_recommendations(overview, categories, top_issues)
        }
    
    def _generate_recommendations(self, overview: Dict, categories: Dict, top_issues: List[Dict]) -> List[str]:
        """Generate actionable recommendations based on feedback analysis"""
        recommendations = []
        
        # Satisfaction-based recommendations
        if overview["average_satisfaction"] < 3.0:
            recommendations.append("Critical: Average satisfaction is very low. Immediate action required.")
        elif overview["average_satisfaction"] < 4.0:
            recommendations.append("Warning: Average satisfaction is below target. Review recent issues.")
        
        # Response time recommendations
        if overview["average_response_time_hours"] > 48:
            recommendations.append("Improve response time: Consider adding more support staff or automating responses.")
        
        # Category-specific recommendations
        problem_categories = [cat for cat in categories["category_stats"] if cat["avg_rating"] < 3.5]
        if problem_categories:
            for cat in problem_categories:
                recommendations.append(f"Focus on {cat['category']}: Low satisfaction ({cat['avg_rating']}) with {cat['count']} reports.")
        
        # Top issues recommendations
        if top_issues and top_issues[0]["count"] > 5:
            recommendations.append(f"Priority fix needed: '{top_issues[0]['phrase']}' reported {top_issues[0]['count']} times.")
        
        return recommendations
```

This comprehensive feedback collection and issue triage system provides:

1. **Multi-channel Feedback Collection**: In-app widget, email, surveys, and direct reporting
2. **Automated Triage**: Intelligent routing based on type, severity, and content analysis
3. **Team Assignment**: Automatic assignment to appropriate teams with escalation workflows
4. **Analytics Dashboard**: Comprehensive reporting and trend analysis
5. **Response Management**: Structured workflows for issue resolution and user communication
6. **Quality Metrics**: Satisfaction tracking and performance measurement

The system ensures that all user feedback is captured, properly triaged, and addressed in a timely manner while providing valuable insights for continuous improvement.