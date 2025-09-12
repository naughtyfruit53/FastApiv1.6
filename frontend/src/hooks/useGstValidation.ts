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
    if (selectedVendorId && !selectedVendor?.state_code && !selectedVendor?.gst_number) {
      setGstError("Vendor state code or GST number is missing. Please update vendor details.");
    } else if (!companyState) {
      setGstError("Company state code or GST number is missing. Please update company details in settings.");
    } else {
      setGstError(null);
    }
  }, [selectedVendorId, vendorList, companyState, companyLoading]);

  return { gstError };
};