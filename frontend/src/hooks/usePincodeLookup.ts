// frontend/src/hooks/usePincodeLookup.ts

import { useState, useRef } from "react";

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

// State to GST state code mapping (from the modal component)
const stateToCodeMap: { [key: string]: string } = {
  "Andhra Pradesh": "37",
  "Arunachal Pradesh": "12",
  "Assam": "18",
  "Bihar": "10",
  "Chhattisgarh": "22",
  "Goa": "30",
  "Gujarat": "24",
  "Haryana": "06",
  "Himachal Pradesh": "02",
  "Jammu and Kashmir": "01",
  "Jharkhand": "20",
  "Karnataka": "29",
  "Kerala": "32",
  "Madhya Pradesh": "23",
  "Maharashtra": "27",
  "Manipur": "14",
  "Meghalaya": "17",
  "Mizoram": "15",
  "Nagaland": "13",
  "Odisha": "21",
  "Punjab": "03",
  "Rajasthan": "08",
  "Sikkim": "11",
  "Tamil Nadu": "33",
  "Telangana": "36",
  "Tripura": "16",
  "Uttar Pradesh": "09",
  "Uttarakhand": "05",
  "West Bengal": "19",
  "Andaman and Nicobar Islands": "35",
  "Chandigarh": "04",
  "Dadra and Nagar Haveli and Daman and Diu": "26",
  "Lakshadweep": "31",
  "Delhi": "07",
  "Puducherry": "34",
  "Ladakh": "38",
};

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
        // Use public API: https://api.postalpincode.in/pincode/{pincode}
        const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data: any[] = await response.json();
        
        if (!data || data.length === 0 || data[0].Status !== "Success" || !data[0].PostOffice || data[0].PostOffice.length === 0) {
          throw new Error("PIN code not found");
        }
        
        // Extract from first PostOffice
        const postOffice = data[0].PostOffice[0];
        const result: PincodeData = {
          city: postOffice.District || postOffice.Block || postOffice.Name,
          state: postOffice.State,
          state_code: stateToCodeMap[postOffice.State.trim()] || "",
        };
        
        // Validate state code
        if (!result.state_code) {
          console.warn(`No state code found for state: ${result.state}`);
        }
        
        setPincodeData(result);
        // Cache successful lookup for the session
        pincodeCache.set(pincode, result);
        
        // Limit cache size to prevent memory bloat (keep last 100 lookups)
        if (pincodeCache.size > 100) {
          const firstKey = pincodeCache.keys().next().value;
          pincodeCache.delete(firstKey);
        }
        
        return result;
      } catch (err: any) {
        let errorMessage = "Failed to lookup PIN code. Please enter details manually.";
        
        if (err.message.includes("not found")) {
          errorMessage = "PIN code not found. Please enter city and state manually.";
        } else if (err.message.includes("HTTP error")) {
          errorMessage = "PIN code lookup service is currently unavailable. Please try again later or enter details manually.";
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
