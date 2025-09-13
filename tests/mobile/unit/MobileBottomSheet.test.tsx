import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import MobileBottomSheet from '../../../frontend/src/components/mobile/MobileBottomSheet';

// Mock mobile detection hook
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ isMobile: true }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('MobileBottomSheet', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    children: <div>Bottom Sheet Content</div>,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children content when open', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Bottom Sheet Content')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} open={false} />
      </TestWrapper>
    );

    expect(screen.queryByText('Bottom Sheet Content')).not.toBeInTheDocument();
  });

  it('renders title when provided', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} title="Test Title" />
      </TestWrapper>
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders close button when showCloseButton is true', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} showCloseButton={true} />
      </TestWrapper>
    );

    const closeButton = screen.getByRole('button');
    expect(closeButton).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const mockOnClose = jest.fn();
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} onClose={mockOnClose} showCloseButton={true} />
      </TestWrapper>
    );

    const closeButton = screen.getByRole('button');
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked and dismissible is true', () => {
    const mockOnClose = jest.fn();
    render(
      <TestWrapper>
        <MobileBottomSheet 
          {...defaultProps} 
          onClose={mockOnClose} 
          dismissible={true}
          backdrop={true}
        />
      </TestWrapper>
    );

    // Find backdrop (should be the first div with fixed positioning)
    const backdrop = document.querySelector('[style*="position: fixed"]');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    }
  });

  it('does not call onClose when backdrop is clicked and dismissible is false', () => {
    const mockOnClose = jest.fn();
    render(
      <TestWrapper>
        <MobileBottomSheet 
          {...defaultProps} 
          onClose={mockOnClose} 
          dismissible={false}
          backdrop={true}
        />
      </TestWrapper>
    );

    const backdrop = document.querySelector('[style*="position: fixed"]');
    if (backdrop) {
      fireEvent.click(backdrop);
      expect(mockOnClose).not.toHaveBeenCalled();
    }
  });

  it('renders handle when showHandle is true', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} showHandle={true} />
      </TestWrapper>
    );

    // Handle should be rendered (look for the small divider element)
    const handle = document.querySelector('[style*="width: 36"]');
    expect(handle).toBeInTheDocument();
  });

  it('does not render handle when showHandle is false', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} showHandle={false} />
      </TestWrapper>
    );

    const handle = document.querySelector('[style*="width: 36"]');
    expect(handle).not.toBeInTheDocument();
  });

  it('renders with auto height', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} height="auto" />
      </TestWrapper>
    );

    expect(screen.getByText('Bottom Sheet Content')).toBeInTheDocument();
  });

  it('renders with half height', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} height="half" />
      </TestWrapper>
    );

    const sheet = screen.getByText('Bottom Sheet Content').closest('[style*="position: fixed"]');
    expect(sheet).toHaveStyle({ height: '50%' });
  });

  it('renders with full height', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} height="full" />
      </TestWrapper>
    );

    const sheet = screen.getByText('Bottom Sheet Content').closest('[style*="position: fixed"]');
    expect(sheet).toHaveStyle({ height: '100%' });
  });

  it('renders with custom numeric height', () => {
    render(
      <TestWrapper>
        <MobileBottomSheet {...defaultProps} height={300} />
      </TestWrapper>
    );

    const sheet = screen.getByText('Bottom Sheet Content').closest('[style*="position: fixed"]');
    expect(sheet).toHaveStyle({ height: '300px' });
  });

  it('renders snap points indicators when provided', () => {
    const mockOnSnapChange = jest.fn();
    render(
      <TestWrapper>
        <MobileBottomSheet 
          {...defaultProps} 
          snapPoints={[25, 50, 75]} 
          initialSnap={1}
          onSnapChange={mockOnSnapChange}
        />
      </TestWrapper>
    );

    // Should render 3 snap indicators
    const indicators = document.querySelectorAll('[style*="border-radius: 50%"]');
    expect(indicators).toHaveLength(3);
  });

  it('handles touch events for snap points', () => {
    const mockOnSnapChange = jest.fn();
    render(
      <TestWrapper>
        <MobileBottomSheet 
          {...defaultProps} 
          snapPoints={[25, 50, 75]} 
          initialSnap={0}
          onSnapChange={mockOnSnapChange}
          dismissible={true}
        />
      </TestWrapper>
    );

    const sheet = screen.getByText('Bottom Sheet Content').closest('[style*="position: fixed"]');
    
    if (sheet) {
      // Simulate touch drag down
      fireEvent.touchStart(sheet, {
        touches: [{ clientY: 100 }],
      });

      fireEvent.touchMove(sheet, {
        touches: [{ clientY: 200 }],
      });

      fireEvent.touchEnd(sheet);

      // Should trigger snap change or close based on threshold
      expect(mockOnSnapChange).toHaveBeenCalled();
    }
  });
});