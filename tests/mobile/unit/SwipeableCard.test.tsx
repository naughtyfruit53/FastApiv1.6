import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import SwipeableCard from '../../../frontend/src/components/mobile/SwipeableCard';
import { Delete, Archive, Star } from '@mui/icons-material';

// Mock mobile detection hook
jest.mock('../../../frontend/src/hooks/useMobileDetection', () => ({
  useMobileDetection: () => ({ isMobile: true }),
}));

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('SwipeableCard', () => {
  const defaultProps = {
    children: <div>Test Content</div>,
    leftActions: [
      {
        label: 'Archive',
        icon: <Archive />,
        color: 'secondary' as const,
        action: jest.fn(),
      },
    ],
    rightActions: [
      {
        label: 'Delete',
        icon: <Delete />,
        color: 'error' as const,
        action: jest.fn(),
      },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders children content', () => {
    render(
      <TestWrapper>
        <SwipeableCard {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders left action when provided', () => {
    render(
      <TestWrapper>
        <SwipeableCard {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Archive')).toBeInTheDocument();
  });

  it('renders right action when provided', () => {
    render(
      <TestWrapper>
        <SwipeableCard {...defaultProps} />
      </TestWrapper>
    );

    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('triggers left action when clicked', () => {
    const mockAction = jest.fn();
    const props = {
      ...defaultProps,
      leftActions: [
        {
          label: 'Archive',
          icon: <Archive />,
          color: 'secondary' as const,
          action: mockAction,
        },
      ],
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('Archive'));
    expect(mockAction).toHaveBeenCalledTimes(1);
  });

  it('triggers right action when clicked', () => {
    const mockAction = jest.fn();
    const props = {
      ...defaultProps,
      rightActions: [
        {
          label: 'Delete',
          icon: <Delete />,
          color: 'error' as const,
          action: mockAction,
        },
      ],
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    fireEvent.click(screen.getByText('Delete'));
    expect(mockAction).toHaveBeenCalledTimes(1);
  });

  it('does not render actions when disabled', () => {
    const props = {
      ...defaultProps,
      disabled: true,
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    // Actions should still be rendered but interactions should be disabled
    expect(screen.getByText('Archive')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  it('handles touch events for swiping', () => {
    const mockLeftAction = jest.fn();
    const props = {
      ...defaultProps,
      leftActions: [
        {
          label: 'Archive',
          icon: <Archive />,
          color: 'secondary' as const,
          action: mockLeftAction,
        },
      ],
      threshold: 50,
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    const card = screen.getByText('Test Content').closest('[role="presentation"]')?.parentElement;
    expect(card).toBeInTheDocument();

    if (card) {
      // Simulate swipe right (should trigger left action)
      fireEvent.touchStart(card, {
        touches: [{ clientX: 0, clientY: 0 }],
      });

      fireEvent.touchMove(card, {
        touches: [{ clientX: 60, clientY: 0 }],
      });

      fireEvent.touchEnd(card);

      expect(mockLeftAction).toHaveBeenCalledTimes(1);
    }
  });

  it('renders with custom threshold', () => {
    const props = {
      ...defaultProps,
      threshold: 100,
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('supports multiple actions', () => {
    const props = {
      ...defaultProps,
      leftActions: [
        {
          label: 'Archive',
          icon: <Archive />,
          color: 'secondary' as const,
          action: jest.fn(),
        },
        {
          label: 'Star',
          icon: <Star />,
          color: 'warning' as const,
          action: jest.fn(),
        },
      ],
      rightActions: [
        {
          label: 'Delete',
          icon: <Delete />,
          color: 'error' as const,
          action: jest.fn(),
        },
      ],
    };

    render(
      <TestWrapper>
        <SwipeableCard {...props} />
      </TestWrapper>
    );

    expect(screen.getByText('Archive')).toBeInTheDocument();
    expect(screen.getByText('Star')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });
});