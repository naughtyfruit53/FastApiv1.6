// frontend/src/context/CompanyContext.tsx
import React, { createContext, useContext } from "react";
import { useQuery } from "@tanstack/react-query";
import { companyService } from "../services/authService";
import { useAuth } from "./AuthContext";
import { useRouter } from "next/router";
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
  const { user, loading } = useAuth();
  const enabled =
    !loading &&
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
    queryFn: companyService.getCurrentCompany,
    enabled: enabled, // Only fetch when authenticated and not on login
    retry: false, // Don't retry on failure
    onError: (err: any) => {
      if (
        err.message === "No authentication token available" ||
        err.status === 401
      ) {
        // Silent handling for no token
        console.log(
          "[CompanyContext] No auth token - skipping setup check silently",
        );
      } else if (err.status === 404 || err.isCompanySetupRequired) {
        console.log(
          "[CompanyContext] Company setup needed due to 404/missing company",
        );
      } else {
        console.error(
          "[CompanyContext] Unexpected error fetching company:",
          err,
        );
        // toast functionality would be imported from react-toastify
        toast.error(`Error fetching company details: ${err.message}`);
      }
    },
  });
  const isCompanySetupNeeded =
    enabled && !isLoading && company === null && !error;
  return (
    <CompanyContext.Provider
      value={{ isCompanySetupNeeded, company, isLoading, error, refetch }}
    >
      {children}
    </CompanyContext.Provider>
  );
};
export const useCompany = (): any => {
  const context = useContext(CompanyContext);
  if (undefined === context) {
    throw new Error("useCompany must be used within a CompanyProvider");
  }
  return context;
};
