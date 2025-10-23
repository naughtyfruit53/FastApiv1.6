import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import PWAInstallPrompt from '../../components/PWAInstallPrompt';
import { usePWA } from '../../hooks/usePWA';

jest.mock('../../hooks/usePWA');

const mockUsePWA = usePWA as jest.MockedFunction<typeof usePWA>;

describe('PWAInstallPrompt', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  it('should not render when not installable', () => {
    mockUsePWA.mockReturnValue({
      isInstallable: false,
      isInstalled: false,
      isOnline: true,
      promptInstall: jest.fn(),
      updateAvailable: false,
      updateServiceWorker: jest.fn(),
    });

    const { container } = render(<PWAInstallPrompt />);
    expect(container.firstChild).toBeNull();
  });

  it('should not render when previously dismissed', () => {
    localStorage.setItem('pwa-install-dismissed', 'true');

    mockUsePWA.mockReturnValue({
      isInstallable: true,
      isInstalled: false,
      isOnline: true,
      promptInstall: jest.fn(),
      updateAvailable: false,
      updateServiceWorker: jest.fn(),
    });

    const { container } = render(<PWAInstallPrompt />);
    expect(container.firstChild).toBeNull();
  });

  it('should render install prompt after delay', async () => {
    jest.useFakeTimers();

    mockUsePWA.mockReturnValue({
      isInstallable: true,
      isInstalled: false,
      isOnline: true,
      promptInstall: jest.fn(),
      updateAvailable: false,
      updateServiceWorker: jest.fn(),
    });

    render(<PWAInstallPrompt />);

    await act(async () => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(screen.getByText('Install TritIQ App')).toBeInTheDocument();
    });

    jest.useRealTimers();
  });

  it('should call promptInstall when install button clicked', async () => {
    jest.useFakeTimers();

    const mockPromptInstall = jest.fn().mockResolvedValue(undefined);

    mockUsePWA.mockReturnValue({
      isInstallable: true,
      isInstalled: false,
      isOnline: true,
      promptInstall: mockPromptInstall,
      updateAvailable: false,
      updateServiceWorker: jest.fn(),
    });

    render(<PWAInstallPrompt />);

    await act(async () => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(screen.getByText('Install')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Install'));
    });

    expect(mockPromptInstall).toHaveBeenCalled();

    jest.useRealTimers();
  });

  it('should dismiss and save to localStorage', async () => {
    jest.useFakeTimers();

    mockUsePWA.mockReturnValue({
      isInstallable: true,
      isInstalled: false,
      isOnline: true,
      promptInstall: jest.fn(),
      updateAvailable: false,
      updateServiceWorker: jest.fn(),
    });

    render(<PWAInstallPrompt />);

    await act(async () => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(screen.getByText('Not Now')).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByText('Not Now'));
    });

    expect(localStorage.getItem('pwa-install-dismissed')).toBe('true');

    jest.useRealTimers();
  });
});
