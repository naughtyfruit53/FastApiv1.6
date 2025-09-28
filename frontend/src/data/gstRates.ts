import Papa from 'papaparse';
import { toast } from 'react-toastify';

export interface HsnResult {
  hsn_code: string;
  description: string;
  gst_rate: number;
}

// Cache for loaded data
let gstDataCache: HsnResult[] | null = null;

// Function to load and parse CSV (async for fetch)
export const loadGstData = async (): Promise<HsnResult[]> => {
  if (gstDataCache) {
    return gstDataCache;
  }
  
  try {
    // Fetch the CSV from public folder
    const response = await fetch('/gst_rates.csv');
    if (!response.ok) {
      throw new Error(`Failed to fetch CSV: ${response.statusText}`);
    }
    const csvText = await response.text();
    
    // Parse CSV using PapaParse
    const parsed = Papa.parse<HsnResult>(csvText, {
      header: true,
      skipEmptyLines: true,
      transform: (value, field) => {
        if (field === 'gst_rate') {
          return parseFloat(value) * 100;  // Convert 0.05 to 5 (%)
        }
        return value.trim();
      }
    });
    
    if (parsed.errors.length > 0) {
      console.error('CSV Parse Errors:', parsed.errors);
      throw new Error('Failed to parse GST rates CSV');
    }
    
    gstDataCache = parsed.data;
    return gstDataCache;
  } catch (error) {
    console.error('Error loading GST data:', error);
    toast.error('Failed to load GST rates data. Please check console for details.');
    throw error;
  }
};