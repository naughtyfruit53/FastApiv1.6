import React, { useState } from 'react';
import { Box, Grid, Typography, Chip, IconButton } from '@mui/material';
import { Add, FilterList, TrendingUp, TrendingDown, Search as SearchIcon } from '@mui/icons-material';
import { 
  MobileDashboardLayout, 
  MobileCard, 
  MobileButton, 
  MobileTable,
  MobileSearchBar,
  MobilePullToRefresh 
} from '../../components/mobile';
import { useInventory } from '../../hooks/useInventory';
import { MobileNavProvider } from '../../context/MobileNavContext';

// Define columns for MobileTable
const inventoryColumns = [
  {
    key: 'name',
    label: 'Product',
    render: (value: string, row: any) => (
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
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
        <Typography variant="body2" sx={{ fontWeight: 600, color: value > row.minStock ? 'success.main' : 'warning.main' }}>
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
        variant="filled"
        sx={{ fontSize: '0.75rem', fontWeight: 500 }}
      />
    ),
  },
  {
    key: 'price',
    label: 'Price',
    render: (value: string) => (
      <Typography variant="body2" sx={{ fontWeight: 600, color: 'info.main' }}>
        {value}
      </Typography>
    ),
  },
];

const MobileInventory: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const { items, total, lowStockAlerts, loading, error, addItem } = useInventory({ search: searchQuery });

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh or call refetch from hook
    await new Promise(resolve => setTimeout(resolve, 1000));
    setRefreshing(false);
  };

  const rightActions = (
    <Box sx={{ display: 'flex', gap: 1 }}>
      <MobileButton
        variant="contained"
        startIcon={<Add />}
        size="small"
        onClick={() => addItem({ /* Sample new item data */ })}
      >
        Add Item
      </MobileButton>
      <IconButton size="small">
        <FilterList />
      </IconButton>
    </Box>
  );

  if (loading) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="Inventory"
          subtitle="Stock Management"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <Typography>Loading inventory...</Typography>
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  if (error) {
    return (
      <MobileNavProvider>
        <MobileDashboardLayout
          title="Inventory"
          subtitle="Stock Management"
          rightActions={rightActions}
          showBottomNav={true}
        >
          <Alert severity="error">Error loading inventory: {error.message}</Alert>
        </MobileDashboardLayout>
      </MobileNavProvider>
    );
  }

  return (
    <MobileNavProvider>
      <MobileDashboardLayout
        title="Inventory"
        subtitle="Stock Management"
        rightActions={rightActions}
        showBottomNav={true}
      >
        <MobilePullToRefresh
          onRefresh={handleRefresh}
          isRefreshing={refreshing}
          enabled={true}
        >
          {/* Enhanced Search with Icon */}
          <MobileSearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search products by name, ID, or category..."
            startAdornment={<SearchIcon sx={{ color: 'action.active' }} />}
            sx={{
              mb: 2,
              bgcolor: 'background.paper',
              borderRadius: 2,
              boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
            }}
          />

          {/* Inventory Summary - Modern Cards with Gradients */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={3}>
              <MobileCard 
                sx={{ 
                  bgcolor: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
                  boxShadow: '0 4px 12px rgba(33,150,243,0.1)',
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.dark' }}>
                    {total}
                  </Typography>
                  <Typography variant="caption" color="primary.main">
                    Total Items
                  </Typography>
                </Box>
              </MobileCard>
            </Grid>
            <Grid item xs={3}>
              <MobileCard 
                sx={{ 
                  bgcolor: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
                  boxShadow: '0 4px 12px rgba(76,175,80,0.1)',
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.dark' }}>
                    {items.filter(item => item.stock > item.minStock).length}
                  </Typography>
                  <Typography variant="caption" color="success.main">
                    In Stock
                  </Typography>
                </Box>
              </MobileCard>
            </Grid>
            <Grid item xs={3}>
              <MobileCard 
                sx={{ 
                  bgcolor: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
                  boxShadow: '0 4px 12px rgba(255,152,0,0.1)',
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.dark' }}>
                    {items.filter(item => item.stock <= item.minStock && item.stock > 0).length}
                  </Typography>
                  <Typography variant="caption" color="warning.main">
                    Low Stock
                  </Typography>
                </Box>
              </MobileCard>
            </Grid>
            <Grid item xs={3}>
              <MobileCard 
                sx={{ 
                  bgcolor: 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)',
                  boxShadow: '0 4px 12px rgba(244,67,54,0.1)',
                }}
              >
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.dark' }}>
                    {items.filter(item => item.stock === 0).length}
                  </Typography>
                  <Typography variant="caption" color="error.main">
                    Out of Stock
                  </Typography>
                </Box>
              </MobileCard>
            </Grid>
          </Grid>

          {/* Main Inventory Table */}
          <MobileCard 
            title="Inventory List" 
            subtitle={`${items.length} items found`}
            sx={{
              boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
              borderRadius: 3,
            }}
          >
            <MobileTable
              columns={inventoryColumns}
              data={items}
              onRowClick={(row) => console.log('Product details:', row)} // Navigate to details
              showChevron={true}
              emptyMessage="No inventory items found matching your search"
              sortableColumns={['name', 'stock', 'price']} // Enable sorting
              pagination={{ pageSize: 10 }} // Mobile-friendly pagination
            />
          </MobileCard>

          {/* Stock Alerts Section */}
          <MobileCard 
            title="Stock Alerts" 
            subtitle={`${lowStockAlerts.length} items requiring attention`}
            sx={{
              mt: 3,
              bgcolor: 'warning.light',
              borderRadius: 3,
            }}
          >
            <MobileTable
              columns={inventoryColumns}
              data={lowStockAlerts}
              onRowClick={(row) => console.log('Alert details:', row)}
              showChevron={true}
              emptyMessage="No low stock alerts"
            />
          </MobileCard>

          {/* Quick Actions - Floating Style */}
          <Box sx={{ 
            position: 'fixed', 
            bottom: 80, 
            right: 16, 
            zIndex: 1200 
          }}>
            <MobileButton
              variant="contained"
              color="primary"
              size="large"
              sx={{ borderRadius: '50%', width: 56, height: 56, minWidth: 'auto' }}
              onClick={() => console.log('Add new item')}
            >
              <Add />
            </MobileButton>
          </Box>

          {/* Bottom Quick Actions */}
          <MobileCard title="Quick Actions" sx={{ mt: 3, borderRadius: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <MobileButton 
                  variant="outlined" 
                  fullWidth
                  startIcon={<TrendingUp />}
                  sx={{ borderRadius: 2 }}
                >
                  Stock In
                </MobileButton>
              </Grid>
              <Grid item xs={6}>
                <MobileButton 
                  variant="outlined" 
                  fullWidth
                  startIcon={<TrendingDown />}
                  sx={{ borderRadius: 2 }}
                >
                  Stock Out
                </MobileButton>
              </Grid>
              <Grid item xs={6}>
                <MobileButton 
                  variant="outlined" 
                  fullWidth
                  sx={{ borderRadius: 2 }}
                >
                  Stock Report
                </MobileButton>
              </Grid>
              <Grid item xs={6}>
                <MobileButton 
                  variant="outlined" 
                  fullWidth
                  sx={{ borderRadius: 2 }}
                >
                  Reorder List
                </MobileButton>
              </Grid>
            </Grid>
          </MobileCard>
        </MobilePullToRefresh>
      </MobileDashboardLayout>
    </MobileNavProvider>
  );
};

export default MobileInventory;
