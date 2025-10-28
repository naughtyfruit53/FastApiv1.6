"use client";
import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  TextField,
  Button,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Box,
} from "@mui/material";
import { Add as AddIcon } from "@mui/icons-material";

interface Contact {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  jobTitle: string;
  company: string;
  department: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  source: string;
  status: "active" | "inactive" | "lead";
  tags: string[];
  lastContact: string;
  created_at: string;
  assignedTo: string;
  notes: string;
}

interface AddContactModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const AddContactModal: React.FC<AddContactModalProps> = ({ open, onClose, onSuccess }) => {
  const [formData, setFormData] = useState<Omit<Contact, "id" | "created_at">>({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    jobTitle: "",
    company: "",
    department: "",
    address: "",
    city: "",
    state: "",
    zipCode: "",
    country: "",
    source: "",
    status: "lead",
    tags: [],
    lastContact: new Date().toISOString().split("T")[0], // Default to today
    assignedTo: "",
    notes: "",
  });
  const [tagInput, setTagInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleStatusChange = (e: any) => {
    setFormData((prev) => ({ ...prev, status: e.target.value }));
  };

  const handleAddTag = () => {
    if (tagInput.trim()) {
      setFormData((prev) => ({ ...prev, tags: [...prev.tags, tagInput.trim()] }));
      setTagInput("");
    }
  };

  const handleRemoveTag = (index: number) => {
    setFormData((prev) => ({ ...prev, tags: prev.tags.filter((_, i) => i !== index) }));
  };

  const handleSubmit = async () => {
    if (!formData.firstName || !formData.lastName || !formData.email) {
      setError("First Name, Last Name, and Email are required.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/v1/contacts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      if (response.ok) {
        onSuccess();
        onClose();
      } else {
        setError("Failed to add contact. Please try again.");
      }
    } catch (err) {
      setError("An error occurred. Please check your connection.");
      console.error("Error adding contact:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Add New Contact</DialogTitle>
      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="First Name"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Last Name"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Job Title"
              name="jobTitle"
              value={formData.jobTitle}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Company"
              name="company"
              value={formData.company}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Department"
              name="department"
              value={formData.department}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select value={formData.status} label="Status" onChange={handleStatusChange}>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="lead">Lead</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address"
              name="address"
              value={formData.address}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="City"
              name="city"
              value={formData.city}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="State"
              name="state"
              value={formData.state}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Zip Code"
              name="zipCode"
              value={formData.zipCode}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Country"
              name="country"
              value={formData.country}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Source"
              name="source"
              value={formData.source}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Assigned To"
              name="assignedTo"
              value={formData.assignedTo}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Last Contact Date"
              name="lastContact"
              type="date"
              value={formData.lastContact}
              onChange={handleChange}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              name="notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={handleChange}
            />
          </Grid>
          <Grid item xs={12}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <TextField
                fullWidth
                label="Add Tag"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
              />
              <Button variant="outlined" onClick={handleAddTag} startIcon={<AddIcon />}>
                Add
              </Button>
            </Box>
            <Box sx={{ mt: 1, display: "flex", flexWrap: "wrap", gap: 1 }}>
              {formData.tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  onDelete={() => handleRemoveTag(index)}
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSubmit} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "Add Contact"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddContactModal;