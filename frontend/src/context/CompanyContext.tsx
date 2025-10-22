// frontend/src/context/CompanyContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react"; // Added useState
import { useQuery } from "@tanstack/react-query";
import { companyService } from "../services/authService";
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
    !!localStorage.getItem("token") &&
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
      const response = await companyService.getCurrentCompany(); // Change to /companies/current if needed
      const companyData = {
        ...response,
        state_code: response.state_code || response.gst_number?.slice(0, 2) || null,
      };
      console.log("[CompanyContext] Company data fetched:", {
        companyData,
        state_code: companyData.state_code,
        gst_number: companyData.gst_number,
        timestamp: new Date().toISOString(),
      });
      return companyData;
    },
    enabled,
    retry: false,
    onSuccess: (data) => {
      if (!data) {
        setIsCompanySetupNeeded(true);
      }
    },
    onError: (err: any) => {
      console.error("[CompanyContext] Error fetching company:", {
        error: err.message,
        status: err.response?.status,
        timestamp: new Date().toISOString(),
      });
      const status = err.response?.status;
      if (status === 401) {
        console.log("[CompanyContext] 401 Unauthorized - redirecting to login");
        router.push("/login");
      } else if (status === 404 || err.isCompanySetupRequired) {
        console.log(
          "[CompanyContext] Company setup needed due to 404/missing company",
        );
        setIsCompanySetupNeeded(true);
        toast.error("Company details not found. Please complete company setup.");
      } else if (status === 403) {
        toast.error("Access denied. Insufficient permissions for company details.");
      } else {
        toast.error(`Error fetching company details: ${err.message}`);
      }
    },
  });

  useEffect(() => {
    if (enabled && !isLoading && !error && company === null) {
      setIsCompanySetupNeeded(true);
    }
  }, [enabled, isLoading, error, company]);

  useEffect(() => {
    if (company) {
      console.log("[CompanyContext] Company state updated:", {
        company,
        state_code: company.state_code,
        gst_number: company.gst_number,
        timestamp: new Date().toISOString(),
      });
    }
  }, [company]);

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