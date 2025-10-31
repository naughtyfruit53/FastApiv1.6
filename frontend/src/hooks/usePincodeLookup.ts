import { useState, useRef, useCallback, useEffect } from "react";
import api from "../lib/api";

interface PincodeData {
  city: string;
  state: string;
  state_code: string;
}

interface UsePincodeLookupReturn {
  lookupPincode: (pincode: string) => Promise<PincodeData | null>;
  pincodeData: PincodeData | null;
  loading: boolean;
  error: string | null;
  clearData: () => void;
}

// Session-based cache for pincode lookups
const pincodeCache = new Map<string, PincodeData>();

// In-flight request tracker to prevent duplicate requests
const inflightRequests = new Map<string, Promise<PincodeData | null>>();

// Retry utility with exponential backoff
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000,
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
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const lookupPincode = useCallback(async (pincode: string): Promise<PincodeData | null> => {
    // Validate pincode format
    if (!pincode || !/^\d{6}$/.test(pincode)) {
      setError("Please enter a valid 6-digit PIN code");
      return null;
    }

    // Check cache first
    const cachedData = pincodeCache.get(pincode);
    if (cachedData) {
      setPincodeData(cachedData);
      setError(null);
      return cachedData;
    }

    // Check if there's already a request in flight for this pincode (single-flight pattern)
    const existingRequest = inflightRequests.get(pincode);
    if (existingRequest) {
      console.log(`[PincodeLookup] Reusing in-flight request for ${pincode}`);
      return existingRequest;
    }

    setLoading(true);
    setError(null);

    // Create a new request promise
    const requestPromise = (async () => {
      try {
        // Use retry logic for better reliability with authenticated client
        const response = await retryWithBackoff(
          () => api.get(`/pincode/lookup/${pincode}`),
          3, // 3 retries
          1000, // 1 second base delay
        );
        const data = response.data;
        setPincodeData(data);
        // Cache successful lookup for the session
        pincodeCache.set(pincode, data);
        return data;
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError("PIN code not found. Please enter city and state manually.");
        } else if (err.response?.status === 503) {
          setError(
            "PIN code lookup service is currently unavailable. Please try again later or enter details manually.",
          );
        } else if (err.response?.status === 401) {
          setError("Authentication required. Please log in and try again.");
        } else {
          setError("Failed to lookup PIN code. Please enter details manually.");
        }
        setPincodeData(null);
        return null;
      } finally {
        setLoading(false);
        // Remove from in-flight tracker
        inflightRequests.delete(pincode);
      }
    })();

    // Track this request
    inflightRequests.set(pincode, requestPromise);

    return requestPromise;
  }, []);

  // Debounced version of lookupPincode with proper cleanup
  const debouncedLookupPincode = useCallback((pincode: string): Promise<PincodeData | null> => {
    // Clear any existing debounce timer to prevent memory leaks
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }

    // Return a promise that resolves when the debounced call completes
    return new Promise((resolve, reject) => {
      debounceTimerRef.current = setTimeout(() => {
        lookupPincode(pincode).then(resolve).catch(reject);
        debounceTimerRef.current = null;
      }, 500); // 500ms debounce
    });
  }, [lookupPincode]);

  // Cleanup on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
        debounceTimerRef.current = null;
      }
    };
  }, []);

  const clearData = () => {
    setPincodeData(null);
    setError(null);
    setLoading(false);
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
  };

  return {
    lookupPincode: debouncedLookupPincode,
    pincodeData,
    loading,
    error,
    clearData,
  };
};
