import React, { useState } from 'react';
import { Button, Box, Typography, Input, Alert } from '@mui/material';
import { masterDataService } from '../services/authService'; // Import the service
import { handleApiError } from '../utils/errorHandling';
import { useAuth } from '../context/AuthContext';
import { useCompany } from '../context/CompanyContext';

const StockBulkImport = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const { user } = useAuth();
  const { isCompanySetupNeeded } = useCompany();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setError(null); // Clear previous errors
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select an Excel file to upload.');
      return;
    }

    // Check if user is authenticated
    if (!user) {
      setError('Please log in before importing inventory.');
      return;
    }

    // Check if company setup is needed
    if (isCompanySetupNeeded) {
      setError('Company setup required before importing inventory. Please complete company setup first.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const res = await masterDataService.bulkImportStock(selectedFile);
      setResponse(res);
      setError(null);
    } catch (err: any) {
      handleApiError(err, 'Failed to import Excel file. Check the file format and try again.');
      setResponse(null);
      
      // Also set local error for display
      if (err.status === 412) {
        setError('Company setup required before importing inventory.');
      } else if (err.status === 400) {
        setError(err.userMessage || 'Invalid request. Please check your data and try again.');
      } else if (err.status === 404) {
        setError(err.userMessage || 'Resource not found. Please contact support if this continues.');
      } else {
        setError(err.userMessage || 'Failed to import Excel file. Check the file format and try again.');
      }
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6">Bulk Import Stock from Excel</Typography>
      
      {isCompanySetupNeeded && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Please complete company setup before importing inventory.
        </Alert>
      )}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Input
        type="file"
        onChange={handleFileChange}
        inputProps={{ accept: '.xlsx, .xls' }}
        sx={{ mb: 2 }}
        disabled={isUploading || isCompanySetupNeeded}
      />
      
      <Button 
        variant="contained" 
        onClick={handleSubmit}
        disabled={!selectedFile || isUploading || isCompanySetupNeeded}
      >
        {isUploading ? 'Importing...' : isCompanySetupNeeded ? 'Company Setup Required' : 'Import'}
      </Button>
      
      {response && (
        <Alert severity="success" sx={{ mt: 2 }}>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </Alert>
      )}
    </Box>
  );
};

export default StockBulkImport;