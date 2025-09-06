// frontend/src/context/CompanyContext.tsx
import React, { createContext, useContext } from "react";
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

  const {
    data: company,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["currentCompany"],
    queryFn: async () => {
      const response = await companyService.getCurrentCompany();
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
    onError: (err: any) => {
      console.error("[CompanyContext] Error fetching company:", {
        error: err.message,
        status: err.status,
        timestamp: new Date().toISOString(),
      });
      if (
        err.message === "No authentication token available" ||
        err.status === 401
      ) {
        console.log(
          "[CompanyContext] No auth token - skipping setup check silently",
        );
      } else if (err.status === 404 || err.isCompanySetupRequired) {
        console.log(
          "[CompanyContext] Company setup needed due to 404/missing company",
        );
        toast.error("Company details not found. Please complete company setup.");
      } else {
        toast.error(`Error fetching company details: ${err.message}`);
      }
    },
  });

  const isCompanySetupNeeded =
    enabled && !isLoading && company === null && !error;

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