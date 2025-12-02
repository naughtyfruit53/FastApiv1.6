import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  CircularProgress,
  Box,
} from "@mui/material";
import { Lead } from "@services/crmService";

interface AssignLeadModalProps {
  open: boolean;
  onClose: () => void;
  onAssign: (leadId: number, userId: number) => Promise<void>;
  lead: Lead | null;
  users: Array<{ id: number; name: string; email: string }>;
  loading?: boolean;
}

const AssignLeadModal: React.FC<AssignLeadModalProps> = ({
  open,
  onClose,
  onAssign,
  lead,
  users,
  loading = false,
}) => {
  const handleAssign = async (userId: number) => {
    if (lead?.id) {
      await onAssign(lead.id, userId);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Typography variant="h6" component="div">
          Assign Lead to Sales User
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box>
          <List>
            {users.map((user) => (
              <ListItem
                key={user.id}
                button
                onClick={() => handleAssign(user.id)}
                disabled={loading}
              >
                <ListItemAvatar>
                  <Avatar>
                    {user.name.charAt(0)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={user.name}
                  secondary={user.email}
                />
              </ListItem>
            ))}
            {users.length === 0 && (
              <Typography variant="body2" color="textSecondary" align="center">
                No sales users available
              </Typography>
            )}
          </List>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading} color="inherit">
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AssignLeadModal;