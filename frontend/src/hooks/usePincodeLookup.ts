import { useState, useEffect } from 'react';
import axios from 'axios';

interface PincodeData {
  city: string;
  state: string;
  state_code: string;
}

interface UsePincodeLookupReturn {
  lookupPincode: (pincode: string) => Promise<void>;
  pincodeData: PincodeData | null;
  loading: boolean;
  error: string | null;
  clearData: () => void;
}

// Session-based cache for pincode lookups
const pincodeCache = new Map<string, PincodeData>();

// Retry utility with exponential backoff
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> => {
  let lastError: Error;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry for client errors (4xx) or if it's the last attempt
      if (error.response?.status >= 400 && error.response?.status < 500) {
        throw error;
      }
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff: 1s, 2s, 4s
      const delay = baseDelay * Math.pow(2, attempt);
      await sleep(delay);
    }
  }
  
  throw lastError!;
};

export const usePincodeLookup = (): UsePincodeLookupReturn => {
  const [pincodeData, setPincodeData] = useState<PincodeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lookupPincode = async (pincode: string): Promise<void> => {
    // Validate pincode format
    if (!pincode || !/^\d{6}$/.test(pincode)) {
      setError('Please enter a valid 6-digit PIN code');
      return;
    }

    // Check cache first
    const cachedData = pincodeCache.get(pincode);
    if (cachedData) {
      setPincodeData(cachedData);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use retry logic for better reliability
      const response = await retryWithBackoff(
        () => axios.get(`/api/v1/pincode/lookup/${pincode}`),
        3, // 3 retries
        1000 // 1 second base delay
      );
      
      const data = response.data;
      setPincodeData(data);
      
      // Cache successful lookup for the session
      pincodeCache.set(pincode, data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('PIN code not found. Please enter city and state manually.');
      } else if (err.response?.status === 503) {
        setError('PIN code lookup service is currently unavailable. Please try again later or enter details manually.');
      } else {
        setError('Failed to lookup PIN code. Please enter details manually.');
      }
      setPincodeData(null);
    } finally {
      setLoading(false);
    }
  };

  const clearData = () => {
    setPincodeData(null);
    setError(null);
    setLoading(false);
  };

  return {
    lookupPincode,
    pincodeData,
    loading,
    error,
    clearData
  };
};