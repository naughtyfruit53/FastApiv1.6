import { toast } from "react-toastify";
interface ApiError {
  status?: number;
  userMessage?: string;
  response?: {
    data?: {
      detail?: string;
      message?: string;
    };
  };
}
export const handleApiError = (
  error: ApiError,
  defaultMessage?: string,
): any => {
  let message = defaultMessage || "An error occurred";
  // Check for user-friendly message first
  if (error.userMessage) {
    message = error.userMessage;
  } else if (error.response?.data?.detail) {
    message = error.response.data.detail;
  } else if (error.response?.data?.message) {
    message = error.response.data.message;
  }
  // Handle specific status codes with enhanced messaging
  if (error.status === 412) {
    // Precondition failed - usually company setup required
    const companySetupMessage =
      message.includes("company") || message.includes("Company")
        ? message
        : "Company setup required before performing this operation.";
    toast.error(companySetupMessage, {
      autoClose: 8000,
      toastId: "company-setup-required",
    });
    return;
  }
  if (error.status === 404) {
    const notFoundMessage =
      message.includes("company") || message.includes("Company")
        ? message
        : message || "Resource not found";
    toast.error(notFoundMessage, {
      autoClose: 5000,
    });
    return;
  }
  if (error.status === 403) {
    toast.error(message || "Access denied", {
      autoClose: 5000,
    });
    return;
  }
  if (error.status === 400) {
    const badRequestMessage =
      message.includes("organization") || message.includes("company")
        ? message
        : message || "Invalid request";
    toast.error(badRequestMessage, {
      autoClose: 6000,
    });
    return;
  }
  // Generic error
  toast.error(message, {
    autoClose: 5000,
  });
};
export const showCompanySetupRequiredMessage = (): any => {
  toast.warning(
    "Please complete your company setup before accessing this feature.",
    {
      autoClose: 8000,
      toastId: "company-setup-required-action",
    },
  );
};

/**
 * Extract error message from various error formats
 * Handles FastAPI validation errors, string messages, and nested objects
 */
export const extractErrorMessage = (error: any): string => {
  if (!error) {
    return "An unknown error occurred";
  }

  // Check for response data detail (FastAPI format)
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    // Handle array of error objects (validation errors)
    if (Array.isArray(detail)) {
      return detail.map((err: any) => err.msg || err.message || String(err)).join(", ");
    }
    
    // Handle string detail
    if (typeof detail === "string") {
      return detail;
    }
    
    // Handle object detail
    if (typeof detail === "object" && detail.message) {
      return detail.message;
    }
  }

  // Check for response data message
  if (error.response?.data?.message) {
    return error.response.data.message;
  }

  // Check for error message property
  if (error.message) {
    return error.message;
  }

  // Check for response status text
  if (error.response?.statusText) {
    return error.response.statusText;
  }

  // Fallback
  return "An error occurred while processing your request";
};

/**
 * Show error toast with extracted message
 */
export const showErrorToast = (error: any, defaultMessage?: string): void => {
  const message = defaultMessage || extractErrorMessage(error);
  toast.error(message);
};

/**
 * Show success toast
 */
export const showSuccessToast = (message: string): void => {
  toast.success(message);
};

/**
 * Show info toast
 */
export const showInfoToast = (message: string): void => {
  toast.info(message);
};

/**
 * Show warning toast
 */
export const showWarningToast = (message: string): void => {
  toast.warning(message);
};

/**
 * Handle async operation with error handling
 * Wraps an async function with try-catch and shows error toast on failure
 */
export const handleAsyncOperation = async <T>(
  operation: () => Promise<T>,
  errorMessage?: string
): Promise<T | null> => {
  try {
    return await operation();
  } catch (error) {
    showErrorToast(error, errorMessage);
    return null;
  }
};

/**
 * Standard error handler for master data operations
 */
export const handleMasterDataError = (error: any, entityName: string): void => {
  console.error(`Error with ${entityName}:`, error);
  showErrorToast(error, `Failed to save ${entityName}`);
};

/**
 * Standard error handler for voucher operations
 */
export const handleVoucherError = (error: any, operation: string): void => {
  console.error(`Voucher ${operation} error:`, error);
  showErrorToast(error, `Failed to ${operation} voucher`);
};
