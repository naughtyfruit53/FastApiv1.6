import { renderHook, act } from '@testing-library/react';
import { usePWA } from '../../hooks/usePWA';

// Mock service worker
const mockRegistration = {
  update: jest.fn(),
  addEventListener: jest.fn(),
  installing: null,
  waiting: null,
  active: null,
};

const mockServiceWorker = {
  register: jest.fn().mockResolvedValue(mockRegistration),
  ready: Promise.resolve(mockRegistration),
};

Object.defineProperty(navigator, 'serviceWorker', {
  value: mockServiceWorker,
  configurable: true,
  writable: true,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

describe('usePWA', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should initialize with default values', async () => {
    const { result } = renderHook(() => usePWA());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.isInstallable).toBe(false);
    expect(result.current.isInstalled).toBe(false);
    expect(result.current.isOnline).toBe(true);
    expect(result.current.updateAvailable).toBe(false);
  });

  it('should detect standalone mode', async () => {
    // Create a new mock for this specific test
    const standaloneMockMedia = jest.fn().mockImplementation((query) => ({
      matches: query === '(display-mode: standalone)',
      media: query,
      onchange: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));

    (window.matchMedia as jest.Mock) = standaloneMockMedia;

    const { result } = renderHook(() => usePWA());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.isInstalled).toBe(true);
  });

  it('should handle online/offline events', async () => {
    const { result } = renderHook(() => usePWA());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    await act(async () => {
      window.dispatchEvent(new Event('offline'));
    });

    expect(result.current.isOnline).toBe(false);

    await act(async () => {
      window.dispatchEvent(new Event('online'));
    });

    expect(result.current.isOnline).toBe(true);
  });

  it('should register service worker', async () => {
    renderHook(() => usePWA());

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(mockServiceWorker.register).toHaveBeenCalledWith('/service-worker.js');
  });
});
