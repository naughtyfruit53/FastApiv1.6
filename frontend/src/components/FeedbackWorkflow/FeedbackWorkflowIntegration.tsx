'use client';

import React, { useState } from 'react';
import {
  Button,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Divider,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Feedback as FeedbackIcon,
  Assignment as AssignmentIcon,
  Star as StarIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';

import {
  CustomerFeedbackModal,
  ServiceClosureDialog
} from './FeedbackWorkflow';
import { feedbackService } from '../services/feedbackService';

interface FeedbackWorkflowIntegrationProps {
  installationJob: any;
  completionRecord?: any;
  onWorkflowUpdate?: () => void;
  userRole: string;
}

export const FeedbackWorkflowIntegration: React.FC<FeedbackWorkflowIntegrationProps> = ({
  installationJob,
  completionRecord,
  onWorkflowUpdate,
  userRole
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [closureDialogOpen, setClosureDialogOpen] = useState(false);
  const [existingFeedback, setExistingFeedback] = useState<any>(null);
  const [existingClosure, setExistingClosure] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const isCustomer = userRole === 'customer';
  const isManager = userRole === 'manager' || userRole === 'admin';
  const isCompleted = completionRecord?.completion_status === 'completed';

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const loadExistingData = async () => {
    setLoading(true);
    try {
      const [feedback, closure] = await Promise.all([
        feedbackService.getFeedbackByJobId(installationJob.id),
        feedbackService.getClosureByJobId(installationJob.id)
      ]);
      setExistingFeedback(feedback);
      setExistingClosure(closure);
    } catch (error) {
      console.error('Error loading existing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenFeedbackModal = async () => {
    handleMenuClose();
    await loadExistingData();
    setFeedbackModalOpen(true);
  };

  const handleOpenClosureDialog = async () => {
    handleMenuClose();
    await loadExistingData();
    setClosureDialogOpen(true);
  };

  const handleSubmitFeedback = async (feedbackData: any) => {
    try {
      await feedbackService.submitFeedback(feedbackData);
      onWorkflowUpdate?.();
      setFeedbackModalOpen(false);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  };

  const handleServiceClosureAction = async (actionData: any) => {
    try {
      if (actionData.action === 'approve') {
        await feedbackService.approveServiceClosure(
          existingClosure.id,
          actionData.approval_notes
        );
      } else if (actionData.action === 'close') {
        await feedbackService.closeServiceTicket(
          existingClosure.id,
          actionData.final_closure_notes
        );
      } else if (actionData.action === 'reopen') {
        await feedbackService.reopenServiceTicket(
          existingClosure.id,
          actionData.reopening_reason
        );
      } else {
        // Create new closure
        await feedbackService.createServiceClosure(actionData);
      }
      
      onWorkflowUpdate?.();
      setClosureDialogOpen(false);
    } catch (error) {
      console.error('Error processing service closure:', error);
      throw error;
    }
  };

  const getFeedbackStatus = () => {
    if (!existingFeedback) return null;
    
    const statusConfig = {
      submitted: { label: 'Feedback Submitted', color: 'info', icon: FeedbackIcon },
      reviewed: { label: 'Feedback Reviewed', color: 'warning', icon: StarIcon },
      responded: { label: 'Feedback Responded', color: 'success', icon: CheckCircleIcon },
      closed: { label: 'Feedback Closed', color: 'default', icon: CheckCircleIcon }
    };

    return statusConfig[existingFeedback.feedback_status as keyof typeof statusConfig];
  };

  const getClosureStatus = () => {
    if (!existingClosure) return null;
    
    const statusConfig = {
      pending: { label: 'Closure Pending', color: 'warning', icon: ScheduleIcon },
      approved: { label: 'Closure Approved', color: 'info', icon: CheckCircleIcon },
      closed: { label: 'Service Closed', color: 'success', icon: CheckCircleIcon },
      reopened: { label: 'Service Reopened', color: 'error', icon: AssignmentIcon }
    };

    return statusConfig[existingClosure.closure_status as keyof typeof statusConfig];
  };

  // Show status indicators if data exists
  const feedbackStatus = getFeedbackStatus();
  const closureStatus = getClosureStatus();

  if (feedbackStatus || closureStatus) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {feedbackStatus && (
          <Tooltip title={feedbackStatus.label}>
            <Button
              size="small"
              color={feedbackStatus.color as any}
              startIcon={React.createElement(feedbackStatus.icon, { fontSize: 'small' })}
              onClick={handleOpenFeedbackModal}
            >
              {existingFeedback.overall_rating}/5
            </Button>
          </Tooltip>
        )}
        
        {closureStatus && (
          <Tooltip title={closureStatus.label}>
            <Button
              size="small"
              color={closureStatus.color as any}
              startIcon={React.createElement(closureStatus.icon, { fontSize: 'small' })}
              onClick={handleOpenClosureDialog}
            >
              {closureStatus.label}
            </Button>
          </Tooltip>
        )}

        <IconButton
          size="small"
          onClick={handleMenuOpen}
          disabled={loading}
        >
          <MoreVertIcon fontSize="small" />
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          {isCustomer && isCompleted && !existingFeedback && (
            <MenuItem onClick={handleOpenFeedbackModal}>
              <ListItemIcon>
                <FeedbackIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Submit Feedback</ListItemText>
            </MenuItem>
          )}

          {existingFeedback && (
            <MenuItem onClick={handleOpenFeedbackModal}>
              <ListItemIcon>
                <StarIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>View Feedback</ListItemText>
            </MenuItem>
          )}

          {isManager && (
            <>
              <Divider />
              <MenuItem onClick={handleOpenClosureDialog}>
                <ListItemIcon>
                  <AssignmentIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>
                  {existingClosure ? 'Manage Closure' : 'Create Closure'}
                </ListItemText>
              </MenuItem>
            </>
          )}
        </Menu>

        <CustomerFeedbackModal
          open={feedbackModalOpen}
          onClose={() => setFeedbackModalOpen(false)}
          installationJobId={installationJob.id}
          customerId={installationJob.customer_id}
          completionRecordId={completionRecord?.id}
          onSubmit={handleSubmitFeedback}
        />

        <ServiceClosureDialog
          open={closureDialogOpen}
          onClose={() => setClosureDialogOpen(false)}
          installationJobId={installationJob.id}
          completionRecordId={completionRecord?.id}
          customerFeedbackId={existingFeedback?.id}
          currentClosure={existingClosure}
          userRole={userRole}
          onSubmit={handleServiceClosureAction}
        />
      </div>
    );
  }

  // Show action buttons for new workflow
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {isCustomer && isCompleted && (
        <Button
          size="small"
          variant="outlined"
          color="primary"
          startIcon={<FeedbackIcon />}
          onClick={handleOpenFeedbackModal}
          disabled={loading}
        >
          Submit Feedback
        </Button>
      )}

      {isManager && isCompleted && (
        <Button
          size="small"
          variant="outlined"
          color="secondary"
          startIcon={<AssignmentIcon />}
          onClick={handleOpenClosureDialog}
          disabled={loading}
        >
          Manage Closure
        </Button>
      )}

      <CustomerFeedbackModal
        open={feedbackModalOpen}
        onClose={() => setFeedbackModalOpen(false)}
        installationJobId={installationJob.id}
        customerId={installationJob.customer_id}
        completionRecordId={completionRecord?.id}
        onSubmit={handleSubmitFeedback}
      />

      <ServiceClosureDialog
        open={closureDialogOpen}
        onClose={() => setClosureDialogOpen(false)}
        installationJobId={installationJob.id}
        completionRecordId={completionRecord?.id}
        customerFeedbackId={existingFeedback?.id}
        currentClosure={existingClosure}
        userRole={userRole}
        onSubmit={handleServiceClosureAction}
      />
    </div>
  );
};

export default FeedbackWorkflowIntegration;