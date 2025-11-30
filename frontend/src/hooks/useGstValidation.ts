// src/hooks/useGstValidation.ts  
// Hook for GST validation and error handling.  
import { useEffect, useMemo, useState } from 'react';  
import { useCompany } from '../context/CompanyContext'; // Adjust path  
  
export const useGstValidation = (selectedVendorId: any, vendorList: any[]) => {  
  const { company, isLoading: companyLoading } = useCompany();  
  const [gstError, setGstError] = useState<string | null>(null);  
  
  const companyState = useMemo(() => {  
    if (company?.state_code) return company.state_code;  
    if (company?.gst_number) return company.gst_number.slice(0, 2);  
    return null;  
  }, [company]);  
  
  useEffect(() => {  
    if (companyLoading) return;  
    const selectedVendor = vendorList?.find((v) => v.id === selectedVendorId);  
    let vendorState = selectedVendor?.state_code;  
    if (!vendorState && selectedVendor?.gst_number) {  
      vendorState = selectedVendor.gst_number.slice(0, 2);  
    }  
    if (selectedVendorId && !vendorState) {  
      setGstError("Vendor state code or GST number is missing. Please update vendor details.");  
    } else {  
      setGstError(null);  
    }  
  }, [selectedVendorId, vendorList, companyLoading]);  
  
  return { gstError };  
};  
