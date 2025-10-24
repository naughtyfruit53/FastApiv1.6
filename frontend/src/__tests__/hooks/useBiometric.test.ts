import { renderHook, act } from '@testing-library/react';
import { useBiometric } from '../../hooks/useBiometric';

describe('useBiometric', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should detect if biometric is not supported', () => {
    Object.defineProperty(window, 'PublicKeyCredential', {
      value: undefined,
      configurable: true,
    });

    const { result } = renderHook(() => useBiometric());

    expect(result.current.isSupported).toBe(false);
    expect(result.current.isAvailable).toBe(false);
  });

  it('should detect if biometric is supported', () => {
    Object.defineProperty(window, 'PublicKeyCredential', {
      value: {
        isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true),
      },
      configurable: true,
    });

    const { result } = renderHook(() => useBiometric());

    expect(result.current.isSupported).toBe(true);
  });

  it('should handle authentication failure', async () => {
    Object.defineProperty(window, 'PublicKeyCredential', {
      value: {
        isUserVerifyingPlatformAuthenticatorAvailable: jest.fn().mockResolvedValue(true),
      },
      configurable: true,
    });

    Object.defineProperty(navigator, 'credentials', {
      value: {
        get: jest.fn().mockRejectedValue(new Error('Authentication failed')),
      },
      configurable: true,
    });

    const { result } = renderHook(() => useBiometric());

    let success = false;
    await act(async () => {
      success = await result.current.authenticate();
    });

    expect(success).toBe(false);
    expect(result.current.error).toBeTruthy();
  });
});
