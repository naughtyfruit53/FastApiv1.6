// frontend/src/components/AdminUserForm.tsx
import React, { useState } from "react";
import {
  Box,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Button,
} from "@mui/material";
interface AdminUserFormProps {
  onSubmit: (_formData: any) => void;
}
const AdminUserForm: React.FC<AdminUserFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    email: "",
    full_name: "",
    role: "app_admin",
  });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };
  const handleChange =
    (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
      setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    };
  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField
        fullWidth
        label="Email"
        value={formData.email}
        onChange={handleChange("email")}
        required
        margin="normal"
      />
      <TextField
        fullWidth
        label="Full Name"
        value={formData.full_name}
        onChange={handleChange("full_name")}
        margin="normal"
      />
      <FormControl fullWidth margin="normal">
        <InputLabel>Role</InputLabel>
        <Select
          label="Role"
          value={formData.role}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, role: e.target.value }))
          }
        >
          <MenuItem value="super_admin">Super Admin</MenuItem>
          <MenuItem value="app_admin">App Admin</MenuItem>
        </Select>
      </FormControl>
      <Button type="submit" variant="contained" fullWidth sx={{ mt: 2 }}>
        Create User
      </Button>
    </Box>
  );
};
export default AdminUserForm;