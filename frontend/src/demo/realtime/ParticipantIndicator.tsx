/**
 * Participant Indicator Component
 * 
 * Displays active participants in a demo collaboration session.
 */

import React from 'react';
import {
  Box,
  Avatar,
  Chip,
  Tooltip,
  AvatarGroup,
  Typography,
  Paper,
} from '@mui/material';
import { People as PeopleIcon } from '@mui/icons-material';
import { Participant } from './websocketClient';

interface ParticipantIndicatorProps {
  participants: Participant[];
  currentUserId?: string;
  maxDisplay?: number;
  variant?: 'compact' | 'detailed';
}

export const ParticipantIndicator: React.FC<ParticipantIndicatorProps> = ({
  participants,
  currentUserId,
  maxDisplay = 3,
  variant = 'compact',
}) => {
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (userId: string) => {
    // Generate consistent color based on user ID
    const colors = ['#1976d2', '#388e3c', '#d32f2f', '#f57c00', '#7b1fa2', '#0097a7'];
    const index = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  };

  if (variant === 'compact') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AvatarGroup max={maxDisplay} sx={{ '& .MuiAvatar-root': { width: 32, height: 32, fontSize: '0.875rem' } }}>
          {participants.map((participant) => (
            <Tooltip
              key={participant.user_id}
              title={`${participant.user_name}${participant.user_id === currentUserId ? ' (You)' : ''}`}
              arrow
            >
              <Avatar
                sx={{
                  bgcolor: getAvatarColor(participant.user_id),
                  border: participant.user_id === currentUserId ? '2px solid #4caf50' : 'none',
                }}
              >
                {getInitials(participant.user_name)}
              </Avatar>
            </Tooltip>
          ))}
        </AvatarGroup>
        <Chip
          icon={<PeopleIcon />}
          label={`${participants.length} viewing`}
          size="small"
          color="primary"
          variant="outlined"
        />
      </Box>
    );
  }

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        borderRadius: 2,
        bgcolor: 'background.paper',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <PeopleIcon sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          Active Participants ({participants.length})
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {participants.map((participant) => (
          <Box
            key={participant.user_id}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              p: 1,
              borderRadius: 1,
              bgcolor: participant.user_id === currentUserId ? 'action.selected' : 'transparent',
            }}
          >
            <Avatar
              sx={{
                bgcolor: getAvatarColor(participant.user_id),
                width: 40,
                height: 40,
              }}
            >
              {getInitials(participant.user_name)}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body1" fontWeight={participant.user_id === currentUserId ? 600 : 400}>
                {participant.user_name}
                {participant.user_id === currentUserId && ' (You)'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Joined {new Date(participant.connected_at).toLocaleTimeString()}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
    </Paper>
  );
};

export default ParticipantIndicator;
