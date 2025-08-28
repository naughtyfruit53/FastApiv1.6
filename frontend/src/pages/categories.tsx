import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Category,
  Inventory
} from '@mui/icons-material';

const CategoriesPage: React.FC = () => {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialog, setAddDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent_category_id: '',
    is_active: true
  });

  // Mock data for demonstration
  const categories = [
    {
      id: 1,
      name: 'Electronics',
      description: 'Electronic components and devices',
      parent_category: null,
      product_count: 25,
      is_active: true
    },
    {
      id: 2,
      name: 'Components',
      description: 'Electronic components',
      parent_category: 'Electronics',
      parent_category_id: 1,
      product_count: 15,
      is_active: true
    },
    {
      id: 3,
      name: 'Cables',
      description: 'Various types of cables',
      parent_category: 'Electronics',
      parent_category_id: 1,
      product_count: 8,
      is_active: true
    },
    {
      id: 4,
      name: 'Hardware',
      description: 'Hardware items and tools',
      parent_category: null,
      product_count: 12,
      is_active: true
    }
  ];

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      parent_category_id: '',
      is_active: true
    });
  };

  const handleAddClick = () => {
    resetForm();
    setAddDialog(true);
  };

  const handleEditClick = (category: any) => {
    setSelectedCategory(category);
    setFormData({
      name: category.name || '',
      description: category.description || '',
      parent_category_id: category.parent_category_id || '',
      is_active: category.is_active
    });
    setEditDialog(true);
  };

  const handleSubmit = () => {
    if (selectedCategory) {
      // TODO: Implement update functionality
      console.log('Update category:', selectedCategory.id, formData);
    } else {
      // TODO: Implement create functionality
      console.log('Create category:', formData);
    }
    setAddDialog(false);
    setEditDialog(false);
  };

  const handleDeleteClick = (category: any) => {
    // TODO: Implement delete functionality
    console.log('Delete category:', category.id);
  };

  const filteredCategories = categories.filter((category: any) =>
    category.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get parent categories for dropdown
  const parentCategories = categories.filter(cat => !cat.parent_category_id);

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Categories
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddClick}
          >
            Add Category
          </Button>
        </Box>

        {/* Info Alert */}
        <Alert severity="info" sx={{ mb: 3 }}>
          Categories help organize your products for better inventory management and reporting.
          You can create hierarchical categories with parent-child relationships.
        </Alert>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Categories
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {categories.length}
                    </Typography>
                  </Box>
                  <Category sx={{ fontSize: 40, color: 'primary.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Active Categories
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {categories.filter(cat => cat.is_active).length}
                    </Typography>
                  </Box>
                  <Category sx={{ fontSize: 40, color: 'success.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Parent Categories
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {parentCategories.length}
                    </Typography>
                  </Box>
                  <Category sx={{ fontSize: 40, color: 'warning.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Total Products
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {categories.reduce((sum, cat) => sum + cat.product_count, 0)}
                    </Typography>
                  </Box>
                  <Inventory sx={{ fontSize: 40, color: 'info.main' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search categories by name or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
            }}
          />
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Category Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Parent Category</TableCell>
                <TableCell>Product Count</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCategories.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Box sx={{ py: 3 }}>
                      <Category sx={{ fontSize: 48, color: 'action.disabled', mb: 2 }} />
                      <Typography variant="h6" color="textSecondary">
                        No categories found
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Add your first category to organize your products
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredCategories.map((category: any) => (
                  <TableRow key={category.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Category sx={{ mr: 2, color: 'primary.main' }} />
                        <Typography variant="body1" fontWeight="medium">
                          {category.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{category.description || 'N/A'}</TableCell>
                    <TableCell>
                      {category.parent_category ? (
                        <Chip
                          label={category.parent_category}
                          size="small"
                          variant="outlined"
                        />
                      ) : (
                        <Typography variant="body2" color="textSecondary">
                          Root Category
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={category.product_count}
                        size="small"
                        color="info"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={category.is_active ? 'Active' : 'Inactive'}
                        color={category.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" color="primary" onClick={() => handleEditClick(category)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDeleteClick(category)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Add/Edit Category Dialog */}
        <Dialog 
          open={addDialog || editDialog} 
          onClose={() => { setAddDialog(false); setEditDialog(false); }}
          maxWidth="sm" 
          fullWidth
        >
          <DialogTitle>
            {selectedCategory ? 'Edit Category' : 'Add New Category'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Category Name *"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Parent Category</InputLabel>
                  <Select
                    value={formData.parent_category_id}
                    label="Parent Category"
                    onChange={(e) => setFormData(prev => ({ ...prev, parent_category_id: e.target.value }))}
                  >
                    <MenuItem value="">
                      <em>None (Root Category)</em>
                    </MenuItem>
                    {parentCategories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => { setAddDialog(false); setEditDialog(false); }}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} variant="contained">
              {selectedCategory ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default CategoriesPage;