// frontend/src/components/ExcelUploadComponent.tsx
"use client";

import React, { useState } from "react";
import {
  Button,
  Typography,
  CircularProgress,
  Alert,
  Box,
} from "@mui/material";
import { Upload as UploadIcon } from "@mui/icons-material";
import { apiClient } from "../services/api/client";

interface ExcelUploadComponentProps {
  endpoint?: string;
  acceptedFileTypes?: string;
  maxFileSize?: number; // in MB
  onUploadSuccess?: () => void;
  onUploadError?: (error: string) => void;
}

const ExcelUploadComponent: React.FC<ExcelUploadComponentProps> = ({
  endpoint = "/api/v1/stock/import/excel",
  acceptedFileTypes = ".xlsx,.xls,.csv",
  maxFileSize = 5,
  onUploadSuccess,
  onUploadError,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<{
    message: string;
    total_processed?: number;
    errors?: any[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file size
      if (file.size > maxFileSize * 1024 * 1024) {
        setError(`File size exceeds ${maxFileSize}MB limit`);
        setSelectedFile(null);
        return;
      }
      // Validate file type
      const fileExtension = file.name.split(".").pop()?.toLowerCase();
      const acceptedExtensions = acceptedFileTypes.split(",").map((ext) => ext.replace(".", "").toLowerCase());
      if (fileExtension && !acceptedExtensions.includes(`.${fileExtension}`)) {
        setError(`Invalid file type. Allowed types: ${acceptedFileTypes}`);
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setResponse(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await apiClient.uploadFile(endpoint, selectedFile, (progress) => {
        console.log(`Upload progress: ${progress}%`);
      });
      setResponse({ message: res.data.message });
      setSelectedFile(null);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Upload failed";
      setError(errorMessage);
      if (onUploadError) {
        onUploadError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6">Upload File</Typography>
      <Box sx={{ display: "flex", gap: 2, alignItems: "center", mt: 1 }}>
        <input
          type="file"
          accept={acceptedFileTypes}
          onChange={handleFileChange}
          style={{ display: "none" }}
          id="file-upload"
        />
        <label htmlFor="file-upload">
          <Button
            variant="outlined"
            component="span"
            startIcon={<UploadIcon />}
            disabled={loading}
          >
            Select File
          </Button>
        </label>
        {selectedFile && <Typography variant="body2">{selectedFile.name}</Typography>}
      </Box>
      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={loading || !selectedFile}
        sx={{ mt: 2 }}
        startIcon={loading ? <CircularProgress size={24} /> : <UploadIcon />}
      >
        {loading ? "Uploading..." : "Upload"}
      </Button>
      {response && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {response.message}
          {response.total_processed !== undefined && (
            <>
              {" (Processed: "}
              {response.total_processed}
              {", Errors: "}
              {response.errors?.length || 0}
              {")"}
            </>
          )}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ExcelUploadComponent;