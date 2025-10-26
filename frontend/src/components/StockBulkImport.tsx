import React, { useState, useEffect, useRef } from "react";
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
  const [progress, setProgress] = useState(0); // For simulated progress
  const controllerRef = useRef<AbortController | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const { user } = useAuth();
  const { isCompanySetupNeeded } = useCompany();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
      setError(null);
      setResponse(null);
      setProgress(0);
    }
  };

  const startProgressSimulation = () => {
    setProgress(0);
    timerRef.current = setInterval(() => {
      setProgress((oldProgress) => {
        if (oldProgress >= 99) {
          clearInterval(timerRef.current!);
          return 99;
        }
        return oldProgress + 1;
      });
    }, 900); // Simulate over ~90s
  };

  const stopProgressSimulation = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an Excel file to upload.");
      return;
    }
    if (!user) {
      setError("Please log in before importing inventory.");
      return;
    }
    if (isCompanySetupNeeded) {
      setError("Company setup required before importing inventory. Please complete company setup first.");
      return;
    }
    setIsUploading(true);
    setError(null);
    setResponse(null);
    controllerRef.current = new AbortController(); // Manual abort control
    startProgressSimulation();

    try {
      const res = await bulkImportStock(selectedFile, { signal: controllerRef.current.signal });
      setResponse(res);
      setError(null);
      setProgress(100); // Complete progress
      if (res.message) {
        alert(`Import Successful: ${res.message}`);
      }
    } catch (err: any) {
      console.error("Bulk import error:", err);
      if (err.name === 'AbortError') {
        setError("Import canceled by user.");
      } else if (err.message.includes("timeout")) {
        setError("Request timed out (90s). The import may have completed on the server; refresh and check your stock list, or retry with a smaller file.");
      } else {
        handleApiError(err, "Failed to import Excel file. Check the file format and try again.");
        if (err.status === 412) {
          setError("Company setup required before importing inventory.");
        } else if (err.status === 400) {
          setError(err.userMessage || "Invalid request. Please check your data and try again.");
        } else if (err.status === 404) {
          setError(err.userMessage || "Resource not found. Please contact support if this continues.");
        } else {
          setError(err.userMessage || "Failed to import Excel file. Check the file format and try again.");
        }
      }
    } finally {
      stopProgressSimulation();
      setIsUploading(false);
      controllerRef.current = null;
    }
  };

  const handleCancel = () => {
    if (controllerRef.current) {
      controllerRef.current.abort();
    }
    setIsUploading(false);
    stopProgressSimulation();
    setProgress(0);
    setError("Import canceled by user.");
  };

  const handleRetry = () => {
    setError(null);
    setResponse(null);
    setProgress(0);
    handleSubmit();
  };

  useEffect(() => {
    return () => {
      stopProgressSimulation(); // Cleanup on unmount
    };
  }, []);

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
          {(error.includes("timed out") || error.includes("canceled")) && (
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
          ? "Importing... may take up to 1.5 minutes"
          : isCompanySetupNeeded
            ? "Company Setup Required"
            : "Import"}
      </Button>
      {isUploading && (
        <Button variant="outlined" color="error" onClick={handleCancel} sx={{ ml: 2 }}>
          Cancel
        </Button>
      )}
      {isUploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} sx={{ mb: 1 }} />
          <Typography variant="body2" color="textSecondary">
            Importing... this may take up to 1.5 minutes for large files (120+ rows). Progress: {Math.round(progress)}%
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default StockBulkImport;