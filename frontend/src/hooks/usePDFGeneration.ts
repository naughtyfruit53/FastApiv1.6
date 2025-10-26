// frontend/src/hooks/usePDFGeneration.ts

import { useState, useCallback } from 'react';
import { api } from '../lib/api';

export interface PDFGenerationOptions {
  voucherType: 'purchase' | 'sales' | 'quotation' | 'sales_order' | 'proforma';
  voucherId: number;
  download?: boolean;
  filename?: string;
}

export interface PDFGenerationState {
  isGenerating: boolean;
  error: string | null;
  success: boolean;
}

export interface PDFGenerationResult {
  success: boolean;
  error?: string;
  blob?: Blob;
}

export const usePDFGeneration = () => {
  const [state, setState] = useState<PDFGenerationState>({
    isGenerating: false,
    error: null,
    success: false
  });

  const generatePDF = useCallback(async (options: PDFGenerationOptions): Promise<PDFGenerationResult> => {
    const { voucherType, voucherId, download = false, filename } = options;

    setState({
      isGenerating: true,
      error: null,
      success: false
    });

    try {
      const endpoint = download
        ? `/voucher/${voucherType}/${voucherId}/download`
        : `/voucher/${voucherType}/${voucherId}`;

      const response = await api.post(endpoint, {}, {
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf'
        }
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        
        setState({
          isGenerating: false,
          error: null,
          success: true
        });

        return {
          success: true,
          blob
        };
      } else {
        throw new Error('Failed to generate PDF');
      }
    } catch (err: any) {
      console.error('PDF generation error:', err);
      
      let errorMessage = 'Failed to generate PDF';

      if (err.response?.status === 403) {
        errorMessage = 'You do not have permission to generate PDFs for this voucher';
      } else if (err.response?.status === 404) {
        errorMessage = 'Voucher not found';
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setState({
        isGenerating: false,
        error: errorMessage,
        success: false
      });

      return {
        success: false,
        error: errorMessage
      };
    }
  }, []);

  const previewPDF = useCallback(async (voucherType: string, voucherId: number) => {
    const result = await generatePDF({ 
      voucherType: voucherType as any, 
      voucherId, 
      download: false 
    });

    if (result.success && result.blob) {
      const url = window.URL.createObjectURL(result.blob);
      window.open(url, '_blank');
      window.URL.revokeObjectURL(url);
    }

    return result;
  }, [generatePDF]);

  const downloadPDF = useCallback(async (
    voucherType: string, 
    voucherId: number, 
    filename?: string
  ) => {
    const result = await generatePDF({ 
      voucherType: voucherType as any, 
      voucherId, 
      download: true, 
      filename 
    });

    if (result.success && result.blob) {
      const url = window.URL.createObjectURL(result.blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `${voucherType}_${voucherId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }

    return result;
  }, [generatePDF]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const clearSuccess = useCallback(() => {
    setState(prev => ({ ...prev, success: false }));
  }, []);

  return {
    ...state,
    generatePDF,
    previewPDF,
    downloadPDF,
    clearError,
    clearSuccess
  };
};

export default usePDFGeneration;