import React, { useState } from 'react';
import { Box, Grid, Typography, Chip } from '@mui/material';
import { Add, FilterList, TrendingUp, TrendingDown } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar 
} from '../../components/mobile';

// TODO: CRITICAL - Replace hardcoded data with real inventory API integration
// TODO: Integrate with inventory services (stock management, movements, valuation)
// TODO: Implement real-time stock monitoring with live updates and auto-refresh
// TODO: Add mobile barcode scanning for stock management and transactions
// TODO: Create quick stock adjustment forms optimized for mobile input
// TODO: Implement low stock alert system with push notifications
// TODO: Add mobile-optimized stock movement tracking with history
// TODO: Create location-based inventory management for multi-warehouse
// TODO: Implement mobile cycle count interface with barcode integration
// TODO: Add inventory analytics dashboard with mobile-friendly charts
// TODO: Create mobile bulk import functionality for stock data
// TODO: Implement GPS-based stock tracking for field inventory
// TODO: Add photo capture for stock verification and documentation
// TODO: Create mobile inventory reporting with export capabilities
// TODO: Implement offline inventory management with sync capabilities

// Sample inventory data - REPLACE WITH REAL API INTEGRATION
const inventoryData = [
  {
    id: 'PRD-001',
    name: 'Widget A',
    category: 'Electronics',
    stock: 45,
    minStock: 10,
    status: 'In Stock',
    price: '₹1,250',
  },
  {
    id: 'PRD-002',
    name: 'Component B',
    category: 'Parts',
    stock: 5,
    minStock: 15,
    status: 'Low Stock',
    price: '₹850',
  },
  {
    id: 'PRD-003',
    name: 'Device C',
    category: 'Electronics',
    stock: 0,
    minStock: 5,
    status: 'Out of Stock',
    price: '₹2,150',
  },
];

const inventoryColumns = [
  {
    key: 'name',
    label: 'Product',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {row.id} • {row.category}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'stock',
    label: 'Stock',
    render: (value: number, row: any) => (
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {value}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Min: {row.minStock}
        </Typography>
      </Box>
    ),
  },
  {
    key: 'status',
    label: 'Status',
    render: (value: string) => (
      <Chip
        label={value}
        size="small"
        color={
          value === 'In Stock' ? 'success' 
          : value === 'Low Stock' ? 'warning' 
          : 'error'
        }
        sx={{ fontSize: '0.75rem' }}
      />
    ),
  },
  {
    key: 'price',
    label: 'Price',
    render: (value: string) => (
      <Typography variant="body2" sx={{ fontWeight: 600 }}>
        {value}
      </Typography>
    ),
  },
];

const MobileInventory: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredData = inventoryData.filter(item =>
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const rightActions = (
    <MobileButton
      variant="contained"
      startIcon={<Add />}
      size="small"
    >
      Add Item
    </MobileButton>
  );

  return (
    <MobileDashboardLayout
      title="Inventory"
      subtitle="Stock Management"
      rightActions={rightActions}
      showBottomNav={true}
    >
      {/* Search and Filter */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Box sx={{ flex: 1 }}>
          <MobileSearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search products..."
          />
        </Box>
        <MobileButton
          variant="outlined"
          startIcon={<FilterList />}
          sx={{ minWidth: 'auto', px: 2 }}
        >
          Filter
        </MobileButton>
      </Box>

      {/* Inventory Summary */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                1,248
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total Items
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                1,195
              </Typography>
              <Typography variant="caption" color="text.secondary">
                In Stock
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                41
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Low Stock
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
        <Grid item xs={3}>
          <MobileCard>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                12
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Out of Stock
              </Typography>
            </Box>
          </MobileCard>
        </Grid>
      </Grid>

      {/* Stock Alerts */}
      <MobileCard title="Stock Alerts" subtitle="Items requiring attention">
        <MobileTable
          columns={inventoryColumns}
          data={filteredData}
          onRowClick={(row) => console.log('Product clicked:', row)}
          showChevron={true}
          emptyMessage="No inventory items found"
        />
      </MobileCard>

      {/* Quick Actions */}
      <MobileCard title="Quick Actions">
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<TrendingUp />}
            >
              Stock In
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton 
              variant="outlined" 
              fullWidth
              startIcon={<TrendingDown />}
            >
              Stock Out
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Stock Report
            </MobileButton>
          </Grid>
          <Grid item xs={6}>
            <MobileButton variant="outlined" fullWidth>
              Reorder List
            </MobileButton>
          </Grid>
        </Grid>
      </MobileCard>
    </MobileDashboardLayout>
  );
};

export default MobileInventory;