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

    expect(screen.getByText('Welcome to the tour')).toBeInTheDocument();
    expect(screen.getByText('Step 1 of 3')).toBeInTheDocument();
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

    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    expect(screen.getByText('This is your dashboard')).toBeInTheDocument();
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

    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('This is your dashboard')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /back/i }));
    expect(screen.getByText('Welcome to the tour')).toBeInTheDocument();
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

    const nextButtons = screen.getAllByRole('button', { name: /next/i });
    fireEvent.click(nextButtons[0]);
    fireEvent.click(screen.getByRole('button', { name: /next/i }));

    expect(screen.getByText('Tour complete')).toBeInTheDocument();
    
    const completeButton = screen.getByRole('button', { name: /complete/i });
    fireEvent.click(completeButton);

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
