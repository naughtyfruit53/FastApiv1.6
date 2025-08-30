// Test page to demonstrate the enhanced Add Product modal with bidirectional HSN/Product search
import React, { useState } from 'react';
import { Box, Button, Typography, Container } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AddProductModal from '../src/components/AddProductModal';

const queryClient = new QueryClient();

const TestAddProductModal = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAddProduct = async (productData: any) => {
    setLoading(true);
    console.log('Product Data:', productData);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLoading(false);
    setModalOpen(false);
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Enhanced Add Product Modal Demo
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          This demo showcases the bidirectional HSN/Product search functionality:
        </Typography>
        <ul>
          <li>Type a product name to see suggested HSN codes</li>
          <li>Type or select an HSN code to see related products and auto-fill unit/GST rate</li>
          <li>Autocomplete functionality for HSN codes from existing products</li>
          <li>Intelligent auto-population between product name and HSN fields</li>
        </ul>
        
        <Button 
          variant="contained" 
          onClick={() => setModalOpen(true)}
          sx={{ mt: 2 }}
        >
          Open Add Product Modal
        </Button>

        <AddProductModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onAdd={handleAddProduct}
          loading={loading}
          initialName=""
        />
      </Container>
    </QueryClientProvider>
  );
};

export default TestAddProductModal;