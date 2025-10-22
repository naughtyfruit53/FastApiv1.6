// frontend/src/components/__tests__/RoleOnboarding.test.tsx

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import RoleOnboarding from '../RoleOnboarding';

describe('RoleOnboarding', () => {
  const mockOnComplete = jest.fn();
  const mockOnSkip = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders onboarding for super_admin role', () => {
    render(
      <RoleOnboarding
        role="super_admin"
        userName="John Doe"
        onComplete={mockOnComplete}
        onSkip={mockOnSkip}
      />
    );

    expect(screen.getByText('Super_admin Onboarding')).toBeInTheDocument();
    expect(screen.getByText(/Welcome, John Doe/)).toBeInTheDocument();
  });

  it('renders onboarding for admin role', () => {
    render(
      <RoleOnboarding
        role="admin"
        userName="Jane Smith"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Admin Onboarding')).toBeInTheDocument();
  });

  it('renders onboarding for manager role', () => {
    render(
      <RoleOnboarding
        role="manager"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Manager Onboarding')).toBeInTheDocument();
  });

  it('renders onboarding for user role', () => {
    render(
      <RoleOnboarding
        role="user"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('User Onboarding')).toBeInTheDocument();
  });

  it('displays welcome step initially', () => {
    render(
      <RoleOnboarding
        role="admin"
        userName="Test User"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText('Welcome')).toBeInTheDocument();
    expect(screen.getByText(/Welcome, Test User/)).toBeInTheDocument();
  });

  it('advances to next step when Continue is clicked', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
      />
    );

    const continueButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueButton);

    // Should advance to the next step
    expect(screen.getByText('Organization Setup')).toBeInTheDocument();
  });

  it('goes back to previous step when Back is clicked', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
      />
    );

    // Advance to second step
    const continueButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueButton);

    // Go back
    const backButton = screen.getByRole('button', { name: /back/i });
    fireEvent.click(backButton);

    expect(screen.getByText('Welcome')).toBeInTheDocument();
  });

  it('calls onSkip when Skip Onboarding is clicked', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
        onSkip={mockOnSkip}
      />
    );

    const skipButton = screen.getByRole('button', { name: /skip onboarding/i });
    fireEvent.click(skipButton);

    expect(mockOnSkip).toHaveBeenCalledTimes(1);
  });

  it('provides continue buttons for navigation', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
      />
    );

    // Should have continue button on first step
    const continueButton = screen.getByRole('button', { name: /continue/i });
    expect(continueButton).toBeInTheDocument();
    
    // Navigate through steps
    fireEvent.click(continueButton);
    
    // Should still have navigation buttons
    expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
  });

  it('displays step indicator with correct count', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText(/Step 1 of/)).toBeInTheDocument();
  });

  it('shows role-specific content for super_admin', () => {
    render(
      <RoleOnboarding
        role="super_admin"
        onComplete={mockOnComplete}
      />
    );

    // Navigate to next step
    const continueButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueButton);

    expect(screen.getByText('Platform Overview')).toBeInTheDocument();
    expect(screen.getByText(/Manage Organizations/)).toBeInTheDocument();
  });

  it('shows role-specific content for manager', () => {
    render(
      <RoleOnboarding
        role="manager"
        onComplete={mockOnComplete}
      />
    );

    // Navigate to next step
    const continueButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueButton);

    expect(screen.getByText('Dashboard Overview')).toBeInTheDocument();
    expect(screen.getByText(/Team Analytics/)).toBeInTheDocument();
  });

  it('displays completion message on final step', () => {
    render(
      <RoleOnboarding
        role="user"
        onComplete={mockOnComplete}
      />
    );

    // Navigate through steps - user role has fewer steps
    const continueButton = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueButton);
    
    // Should have progressed to next step
    expect(screen.getByText('Getting Started')).toBeInTheDocument();
  });

  it('renders without userName when not provided', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
      />
    );

    expect(screen.getByText(/Welcome, User/)).toBeInTheDocument();
  });

  it('shows Skip button on first step when onSkip is provided', () => {
    render(
      <RoleOnboarding
        role="admin"
        onComplete={mockOnComplete}
        onSkip={mockOnSkip}
      />
    );

    expect(screen.getByRole('button', { name: /skip onboarding/i })).toBeInTheDocument();
  });
});
