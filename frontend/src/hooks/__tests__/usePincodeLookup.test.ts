// Test for enhanced usePincodeLookup hook with retry logic and caching
import { renderHook, act } from '@testing-library/react';
import axios from 'axios';
import { usePincodeLookup } from '../../hooks/usePincodeLookup';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('usePincodeLookup', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear the cache before each test
    (global as any).pincodeCache?.clear();
  });

  it('should successfully lookup and cache pincode data', async () => {
    const mockResponse = {
      data: {
        city: 'Mumbai',
        state: 'Maharashtra',
        state_code: '27'
      }
    };

    mockedAxios.get.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('400001');
    });

    expect(result.current.pincodeData).toEqual(mockResponse.data);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/pincode/lookup/400001');
  });

  it('should return cached data on subsequent requests', async () => {
    const mockResponse = {
      data: {
        city: 'Mumbai',
        state: 'Maharashtra',
        state_code: '27'
      }
    };

    mockedAxios.get.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => usePincodeLookup());

    // First call - should make API request
    await act(async () => {
      await result.current.lookupPincode('400001');
    });

    expect(mockedAxios.get).toHaveBeenCalledTimes(1);

    // Second call - should use cache
    await act(async () => {
      await result.current.lookupPincode('400001');
    });

    expect(mockedAxios.get).toHaveBeenCalledTimes(1); // No additional API call
    expect(result.current.pincodeData).toEqual(mockResponse.data);
  });

  it('should handle validation errors for invalid pincode format', async () => {
    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('invalid');
    });

    expect(result.current.error).toBe('Please enter a valid 6-digit PIN code');
    expect(result.current.pincodeData).toBe(null);
    expect(mockedAxios.get).not.toHaveBeenCalled();
  });

  it('should handle 404 errors gracefully', async () => {
    mockedAxios.get.mockRejectedValueOnce({
      response: { status: 404 }
    });

    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('999999');
    });

    expect(result.current.error).toBe('PIN code not found. Please enter city and state manually.');
    expect(result.current.pincodeData).toBe(null);
    expect(result.current.loading).toBe(false);
  });

  it('should retry on server errors with exponential backoff', async () => {
    // Mock multiple failures followed by success
    mockedAxios.get
      .mockRejectedValueOnce({ response: { status: 503 } })
      .mockRejectedValueOnce({ response: { status: 503 } })
      .mockResolvedValueOnce({
        data: {
          city: 'Delhi',
          state: 'Delhi',
          state_code: '07'
        }
      });

    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('110001');
    });

    expect(mockedAxios.get).toHaveBeenCalledTimes(3); // Initial + 2 retries
    expect(result.current.pincodeData).toEqual({
      city: 'Delhi',
      state: 'Delhi',
      state_code: '07'
    });
    expect(result.current.error).toBe(null);
  });

  it('should not retry on client errors (4xx)', async () => {
    mockedAxios.get.mockRejectedValueOnce({
      response: { status: 400 }
    });

    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('400001');
    });

    expect(mockedAxios.get).toHaveBeenCalledTimes(1); // No retries for client errors
    expect(result.current.error).toBe('Failed to lookup PIN code. Please enter details manually.');
  });

  it('should clear data correctly', async () => {
    const mockResponse = {
      data: {
        city: 'Mumbai',
        state: 'Maharashtra',
        state_code: '27'
      }
    };

    mockedAxios.get.mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => usePincodeLookup());

    await act(async () => {
      await result.current.lookupPincode('400001');
    });

    expect(result.current.pincodeData).toEqual(mockResponse.data);

    act(() => {
      result.current.clearData();
    });

    expect(result.current.pincodeData).toBe(null);
    expect(result.current.error).toBe(null);
    expect(result.current.loading).toBe(false);
  });
});