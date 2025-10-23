import { renderHook, act } from '@testing-library/react';
import { usePWA } from '../../hooks/usePWA';

// Mock service worker
const mockServiceWorker = {
  register: jest.fn(),
  ready: Promise.resolve({
    update: jest.fn(),
    addEventListener: jest.fn(),
  }),
};

Object.defineProperty(navigator, 'serviceWorker', {
  value: mockServiceWorker,
  configurable: true,
});

describe('usePWA', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => usePWA());

    expect(result.current.isInstallable).toBe(false);
    expect(result.current.isInstalled).toBe(false);
    expect(result.current.isOnline).toBe(true);
    expect(result.current.updateAvailable).toBe(false);
  });

  it('should detect standalone mode', () => {
    Object.defineProperty(window, 'matchMedia', {
      value: jest.fn().mockImplementation((query) => ({
        matches: query === '(display-mode: standalone)',
        media: query,
        onchange: null,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      })),
    });

    const { result } = renderHook(() => usePWA());

    expect(result.current.isInstalled).toBe(true);
  });

  it('should handle online/offline events', () => {
    const { result } = renderHook(() => usePWA());

    act(() => {
      window.dispatchEvent(new Event('offline'));
    });

    expect(result.current.isOnline).toBe(false);

    act(() => {
      window.dispatchEvent(new Event('online'));
    });

    expect(result.current.isOnline).toBe(true);
  });

  it('should register service worker', () => {
    mockServiceWorker.register.mockResolvedValue({
      addEventListener: jest.fn(),
      update: jest.fn(),
    });

    renderHook(() => usePWA());

    expect(mockServiceWorker.register).toHaveBeenCalledWith('/service-worker.js');
  });
});
