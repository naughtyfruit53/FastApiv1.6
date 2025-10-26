import React, { useState } from "react";
import { Button, Box, Typography, Input, Alert, LinearProgress } from "@mui/material";
import { bulkImportStock } from "../services/stockService"; // Import from stockService
import { handleApiError } from "../utils/errorHandling";
import { useAuth } from "../context/AuthContext";
import { useCompany } from "../context/CompanyContext";

const StockBulkImport = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const { user } = useAuth();
  const { isCompanySetupNeeded } = useCompany();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setError(null); // Clear previous errors
      setResponse(null); // Clear previous response
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an Excel file to upload.");
      return;
    }
    // Check if user is authenticated
    if (!user) {
      setError("Please log in before importing inventory.");
      return;
    }
    // Check if company setup is needed
    if (isCompanySetupNeeded) {
      setError(
        "Company setup required before importing inventory. Please complete company setup first.",
      );
      return;
    }
    setIsUploading(true);
    setShowProgress(true); // Show progress immediately
    setError(null);
    setResponse(null);
    const controller = new AbortController(); // Manual abort control
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60s timeout

    try {
      const res = await bulkImportStock(selectedFile, { signal: controller.signal });
      setResponse(res);
      setError(null);
      // Show success message
      if (res.message) {
        alert(`Import Successful: ${res.message}`); // Simple popup for success
      }
    } catch (err: any) {
      console.error("Bulk import error:", err);
      if (err.name === 'AbortError' || err.message.includes("timeout")) {
        setError("Request timed out (60s). The import may have completed; refresh and check your stock list, or retry with a smaller file.");
      } else {
        handleApiError(
          err,
          "Failed to import Excel file. Check the file format and try again.",
        );
        if (err.status === 412) {
          setError("Company setup required before importing inventory.");
        } else if (err.status === 400) {
          setError(
            err.userMessage ||
              "Invalid request. Please check your data and try again.",
          );
        } else if (err.status === 404) {
          setError(
            err.userMessage ||
              "Resource not found. Please contact support if this continues.",
          );
        } else {
          setError(
            err.userMessage ||
              "Failed to import Excel file. Check the file format and try again.",
          );
        }
      }
    } finally {
      clearTimeout(timeoutId);
      setIsUploading(false);
      setShowProgress(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setResponse(null);
    handleSubmit();
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
          {error.includes("timed out") && (
            <Button size="small" onClick={handleRetry} sx={{ ml: 1 }}>
              Retry
            </Button>
          )}
        </Alert>
      )}
      {response && (
        <Alert severity="success" sx={{ mt: 2 }}>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </Alert>
      )}
      <Input
        type="file"
        onChange={handleFileChange}
        inputProps={{ accept: ".xlsx, .xls" }}
        sx={{ mb: 2 }}
        disabled={isUploading || isCompanySetupNeeded}
      />
      <Button
        variant="contained"
        onClick={handleSubmit}
        disabled={!selectedFile || isUploading || isCompanySetupNeeded}
      >
        {isUploading
          ? "Importing... may take up to 1 minute"
          : isCompanySetupNeeded
            ? "Company Setup Required"
            : "Import"}
      </Button>
      {showProgress && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress sx={{ mb: 1 }} />
          <Typography variant="body2" color="textSecondary">
            Importing... this may take up to 1 minute for large files (120+ rows).
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default StockBulkImport;