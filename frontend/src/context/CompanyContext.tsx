// frontend/src/context/CompanyContext.tsx

import React, { createContext, useContext, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../services/authService";
import { useAuth } from "./AuthContext";
import { useRouter } from "next/router";
import { toast } from "react-toastify";

interface CompanyContextType {
  isCompanySetupNeeded: boolean;
  company: any; // Replace with proper type
  isLoading: boolean;
  error: any;
  refetch: () => void;
}

const CompanyContext = createContext<CompanyContextType | undefined>(undefined);

export const CompanyProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const enabled =
    !authLoading &&
    !!user &&
    router.pathname !== "/login";

  const [isCompanySetupNeeded, setIsCompanySetupNeeded] = useState(false);

  const {
    data: company,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["currentCompany"],
    queryFn: async () => {
      const response = await authService.getCurrentCompany();
      const companyData = {
        ...response,
        state_code: response.state_code || response.gst_number?.slice(0, 2) || null,
      };
      return companyData;
    },
    enabled,
    retry: 3, // Retry up to 3 times on failure
    retryDelay: 1000, // 1 second delay between retries
    refetchOnMount: 'always', // Always refetch on component mount
    refetchOnWindowFocus: 'always', // Refetch on window focus
    staleTime: 0, // Data is always stale
    cacheTime: 0, // No caching
    onSuccess: (data) => {
      if (!data || (!data.state_code && !data.gst_number)) {
        setIsCompanySetupNeeded(true);
        toast.error("Company setup required. Please complete company details.", {
          toastId: "company-setup-required",
        });
      } else {
        setIsCompanySetupNeeded(false);
      }
    },
    onError: (err: any) => {
      const status = err.response?.status;
      if (status === 401) {
        router.push("/login");
      } else if (status === 404) {
        setIsCompanySetupNeeded(true);
        toast.error("Company details not found. Please complete company setup.", {
          toastId: "company-setup-not-found",
        });
      } else if (status === 400 && err.message.includes("state code or GST number")) {
        setIsCompanySetupNeeded(true);
        toast.error("Company setup incomplete. Please update company details.", {
          toastId: "company-setup-incomplete",
        });
      } else if (status === 403) {
        toast.error("Access denied. Insufficient permissions for company details.");
      } else {
        toast.error(`Error fetching company details: ${err.message}`);
      }
    },
  });

  useEffect(() => {
    if (enabled && !isLoading && !error && (company === null || (!company?.state_code && !company?.gst_number))) {
      setIsCompanySetupNeeded(true);
    }
  }, [enabled, isLoading, error, company, router]);

  return (
    <CompanyContext.Provider
      value={{ isCompanySetupNeeded, company, isLoading, error, refetch }}
    >
      {children}
    </CompanyContext.Provider>
  );
};

export const useCompany = (): CompanyContextType => {
  const context = useContext(CompanyContext);
  if (undefined === context) {
    throw new Error("useCompany must be used within a CompanyProvider");
  }
  return context;
};
