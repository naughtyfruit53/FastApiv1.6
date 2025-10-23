import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import OnboardingTour from '../../components/OnboardingTour';

const mockSteps = [
  {
    title: 'Welcome',
    description: 'Welcome to the tour',
  },
  {
    title: 'Dashboard',
    description: 'This is your dashboard',
    target: '[data-tour="dashboard"]',
  },
  {
    title: 'Complete',
    description: 'Tour complete',
  },
];

describe('OnboardingTour', () => {
  const mockOnClose = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render tour dialog when open', () => {
    render(
      <OnboardingTour
        open={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText('Welcome to the tour')).toBeInTheDocument();
  });

  it('should not render when closed', () => {
    render(
      <OnboardingTour
        open={false}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    expect(screen.queryByText('Welcome')).not.toBeInTheDocument();
  });

  it('should navigate to next step', () => {
    render(
      <OnboardingTour
        open={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    expect(screen.getByText('Step 1 of 3')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Next'));

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Step 2 of 3')).toBeInTheDocument();
  });

  it('should navigate to previous step', () => {
    render(
      <OnboardingTour
        open={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    fireEvent.click(screen.getByText('Next'));
    expect(screen.getByText('Dashboard')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Back'));
    expect(screen.getByText('Welcome')).toBeInTheDocument();
  });

  it('should complete tour on last step', () => {
    render(
      <OnboardingTour
        open={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    fireEvent.click(screen.getByText('Next'));
    fireEvent.click(screen.getByText('Next'));

    expect(screen.getByText('Complete')).toBeInTheDocument();
    expect(screen.getByText('Complete', { selector: 'button span' })).toBeInTheDocument();

    fireEvent.click(screen.getByText('Complete', { selector: 'button span' }));

    expect(mockOnComplete).toHaveBeenCalled();
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should show progress indicator', () => {
    render(
      <OnboardingTour
        open={true}
        onClose={mockOnClose}
        onComplete={mockOnComplete}
        steps={mockSteps}
      />
    );

    // Should show progress bar
    const progressBar = document.querySelector('[role="progressbar"]');
    expect(progressBar).toBeInTheDocument();
  });
});
