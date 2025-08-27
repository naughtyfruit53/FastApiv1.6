import React, { useState } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Grid,
  Button
} from '@mui/material';
import AddVendorModal from '../components/AddVendorModal';
import AddCustomerModal from '../components/AddCustomerModal';
import CompanyDetailsModal from '../components/CompanyDetailsModal';
import AddShippingAddressModal from '../components/AddShippingAddressModal';

const UITestPage: React.FC = () => {
  const [vendorModalOpen, setVendorModalOpen] = useState(false);
  const [customerModalOpen, setCustomerModalOpen] = useState(false);
  const [companyModalOpen, setCompanyModalOpen] = useState(false);
  const [shippingModalOpen, setShippingModalOpen] = useState(false);

  const handleAddVendor = async (data: any) => {
    console.log('Vendor data:', data);
    alert('Vendor would be added with data: ' + JSON.stringify(data));
  };

  const handleAddCustomer = async (data: any) => {
    console.log('Customer data:', data);
    alert('Customer would be added with data: ' + JSON.stringify(data));
  };

  const handleAddShipping = async (data: any) => {
    console.log('Shipping address data:', data);
    alert('Shipping address would be added with data: ' + JSON.stringify(data));
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Page Title - should be 18px */}
      <Typography variant="h4" component="h1" gutterBottom>
        UI Overhaul Test Page
      </Typography>
      
      {/* Section Title - should be 15px */}
      <Typography variant="h6" component="h2" gutterBottom sx={{ mt: 4 }}>
        Modal Components Testing
      </Typography>

      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="body1" sx={{ mb: 3 }}>
          Test the enhanced modals with pincode auto-loading functionality, new styling (27px height, 12px font size),
          and reordered address fields (pincode first after address lines).
        </Typography>

        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={() => setVendorModalOpen(true)}
            >
              Test Vendor Modal
            </Button>
          </Grid>
          
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={() => setCustomerModalOpen(true)}
            >
              Test Customer Modal
            </Button>
          </Grid>
          
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={() => setCompanyModalOpen(true)}
            >
              Test Company Modal
            </Button>
          </Grid>
          
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Button 
              variant="contained" 
              fullWidth 
              onClick={() => setShippingModalOpen(true)}
            >
              Test Shipping Modal
            </Button>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" component="h3" gutterBottom>
            Features Implemented:
          </Typography>
          <ul>
            <li>All input fields in modals have 27px height and 12px font size</li>
            <li>Input labels use 12px font size</li>
            <li>Page titles use 18px font size (h4 variant)</li>
            <li>Section titles use 15px font size (h6 variant)</li>
            <li>Pincode auto-loading for city, state, and state code</li>
            <li>Address field reordering: Address1, Address2, PIN Code, City, State, State Code</li>
            <li>Loading indicators during pincode lookup</li>
            <li>Error handling for pincode API failures</li>
            <li>Manual override capability with readonly/disabled states</li>
            <li>Consistent styling across all address-enabled modals</li>
          </ul>
        </Box>
      </Paper>

      {/* Modals */}
      <AddVendorModal
        open={vendorModalOpen}
        onClose={() => setVendorModalOpen(false)}
        onAdd={handleAddVendor}
      />

      <AddCustomerModal
        open={customerModalOpen}
        onClose={() => setCustomerModalOpen(false)}
        onAdd={handleAddCustomer}
      />

      <CompanyDetailsModal
        open={companyModalOpen}
        onClose={() => setCompanyModalOpen(false)}
      />

      <AddShippingAddressModal
        open={shippingModalOpen}
        onClose={() => setShippingModalOpen(false)}
        onAdd={handleAddShipping}
      />
    </Container>
  );
};

export default UITestPage;