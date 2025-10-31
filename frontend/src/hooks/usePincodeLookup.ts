import { useState, useRef } from "react";
import { apiClient } from "../services/api/client";

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

// Single-flight map to prevent duplicate concurrent requests
const inflightRequests = new Map<string, Promise<PincodeData | null>>();
export const usePincodeLookup = (): UsePincodeLookupReturn => {
  const [pincodeData, setPincodeData] = useState<PincodeData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const lookupPincode = async (pincode: string): Promise<PincodeData | null> => {
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

    // Check if there's already an inflight request for this pincode (single-flight pattern)
    const existingRequest = inflightRequests.get(pincode);
    if (existingRequest) {
      return existingRequest;
    }

    setLoading(true);
    setError(null);

    // Create the request promise
    const requestPromise = (async () => {
      try {
        // Use the centralized apiClient with auth support
        // Note: Backend endpoint is now public, so this will work without auth too
        const response = await apiClient.get<PincodeData>(`/pincode/lookup/${pincode}`);
        const data = response.data;
        
        setPincodeData(data);
        // Cache successful lookup for the session
        pincodeCache.set(pincode, data);
        
        // Limit cache size to prevent memory bloat (keep last 100 lookups)
        if (pincodeCache.size > 100) {
          const firstKey = pincodeCache.keys().next().value;
          pincodeCache.delete(firstKey);
        }
        
        return data;
      } catch (err: any) {
        let errorMessage = "Failed to lookup PIN code. Please enter details manually.";
        
        if (err.response?.status === 404) {
          errorMessage = "PIN code not found. Please enter city and state manually.";
        } else if (err.response?.status === 503) {
          errorMessage = "PIN code lookup service is currently unavailable. Please try again later or enter details manually.";
        } else if (err.response?.status === 401) {
          errorMessage = "Authentication required. Please try again after logging in.";
        }
        
        setError(errorMessage);
        setPincodeData(null);
        return null;
      } finally {
        setLoading(false);
        // Clean up inflight request tracking immediately after completion
        inflightRequests.delete(pincode);
      }
    })();

    // Track this request to prevent duplicates
    inflightRequests.set(pincode, requestPromise);
    
    return requestPromise;
  };

  const clearData = () => {
    setPincodeData(null);
    setError(null);
    setLoading(false);
    // Clear any pending debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
  };

  return {
    lookupPincode,
    pincodeData,
    loading,
    error,
    clearData,
  };
};
