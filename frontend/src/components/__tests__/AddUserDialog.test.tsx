import React from 'react';
import { render, screen } from '@testing-library/react';
import AddUserDialog from '../AddUserDialog';

test('renders AddUserDialog title', () => {
  render(<AddUserDialog open={true} onClose={jest.fn()} organizationId={1} organizationName="Test Org" />);
  expect(screen.getByText(/Add User to Test Org/i)).toBeInTheDocument();
});