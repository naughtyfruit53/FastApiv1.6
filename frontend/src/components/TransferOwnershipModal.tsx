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

interface TransferOwnershipModalProps {
  open: boolean;
  onClose: () => void;
  onTransfer: (leadId: number, ownerId: number) => Promise<void>;
  lead: Lead | null;
  users: Array<{ id: number; name: string; email: string }>;
  loading?: boolean;
}

const TransferOwnershipModal: React.FC<TransferOwnershipModalProps> = ({
  open,
  onClose,
  onTransfer,
  lead,
  users,
  loading = false,
}) => {
  const handleTransfer = async (ownerId: number) => {
    if (lead?.id) {
      await onTransfer(lead.id, ownerId);
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
          Transfer Lead Ownership
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Box>
          <List>
            {users.map((user) => (
              <ListItem
                key={user.id}
                button
                onClick={() => handleTransfer(user.id)}
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
                No users available for transfer
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

export default TransferOwnershipModal;