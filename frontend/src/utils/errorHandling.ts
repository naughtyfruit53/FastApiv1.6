import { toast } from 'react-toastify';

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

export const handleApiError = (error: ApiError, defaultMessage?: string) => {
  let message = defaultMessage || 'An error occurred';

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
    const companySetupMessage = message.includes('company') || message.includes('Company') 
      ? message 
      : 'Company setup required before performing this operation.';
    toast.error(companySetupMessage, {
      autoClose: 8000,
      toastId: 'company-setup-required'
    });
    return;
  }

  if (error.status === 404) {
    const notFoundMessage = message.includes('company') || message.includes('Company')
      ? message
      : message || 'Resource not found';
    toast.error(notFoundMessage, {
      autoClose: 5000,
    });
    return;
  }

  if (error.status === 403) {
    toast.error(message || 'Access denied', {
      autoClose: 5000,
    });
    return;
  }

  if (error.status === 400) {
    const badRequestMessage = message.includes('organization') || message.includes('company')
      ? message
      : message || 'Invalid request';
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

export const showCompanySetupRequiredMessage = () => {
  toast.warning('Please complete your company setup before accessing this feature.', {
    autoClose: 8000,
    toastId: 'company-setup-required-action'
  });
};