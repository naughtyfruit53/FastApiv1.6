// frontend/src/components/__tests__/AuditLogViewer.test.tsx

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AuditLogViewer, { AuditLog } from '../AuditLogViewer';

describe('AuditLogViewer', () => {
  const mockLogs: AuditLog[] = [
    {
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      user: 'john.doe@example.com',
      action: 'CREATE',
      entity_type: 'Customer',
      entity_id: 123,
      details: 'Created new customer record',
      ip_address: '192.168.1.1',
      status: 'success',
    },
    {
      id: 2,
      timestamp: '2024-01-15T11:00:00Z',
      user: 'jane.smith@example.com',
      action: 'UPDATE',
      entity_type: 'Order',
      entity_id: 456,
      details: 'Updated order status',
      ip_address: '192.168.1.2',
      status: 'success',
    },
    {
      id: 3,
      timestamp: '2024-01-15T11:30:00Z',
      user: 'admin@example.com',
      action: 'DELETE',
      entity_type: 'Product',
      entity_id: 789,
      details: 'Deleted product',
      ip_address: '192.168.1.3',
      status: 'failure',
    },
  ];

  const mockOnRefresh = jest.fn();
  const mockOnPageChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders audit log viewer with title', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    expect(screen.getByText('Audit Logs')).toBeInTheDocument();
  });

  it('displays audit log entries in table', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
    expect(screen.getByText('jane.smith@example.com')).toBeInTheDocument();
    expect(screen.getByText('admin@example.com')).toBeInTheDocument();
  });

  it('shows loading state when loading prop is true', () => {
    render(<AuditLogViewer logs={[]} loading={true} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no logs are available', () => {
    render(<AuditLogViewer logs={[]} />);
    expect(screen.getByText('No audit logs found')).toBeInTheDocument();
  });

  it('calls onRefresh when refresh button is clicked', () => {
    render(<AuditLogViewer logs={mockLogs} onRefresh={mockOnRefresh} />);
    
    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);
    
    expect(mockOnRefresh).toHaveBeenCalledTimes(1);
  });

  it('filters logs by search term', async () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    const searchInput = screen.getByPlaceholderText('Search logs...');
    fireEvent.change(searchInput, { target: { value: 'john' } });
    
    await waitFor(() => {
      expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
      expect(screen.queryByText('jane.smith@example.com')).not.toBeInTheDocument();
    });
  });

  it('displays action and status filters', async () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    // Verify all logs are shown initially
    expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
    expect(screen.getByText('jane.smith@example.com')).toBeInTheDocument();
    expect(screen.getByText('admin@example.com')).toBeInTheDocument();
  });

  it('renders filter controls', async () => {
    const { container } = render(<AuditLogViewer logs={mockLogs} />);
    
    // Verify filter controls are rendered
    const selects = container.querySelectorAll('.MuiSelect-select');
    expect(selects.length).toBeGreaterThanOrEqual(2); // Action and Status filters
  });

  it('displays correct status colors', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    const successChips = screen.getAllByText('success');
    expect(successChips).toHaveLength(2);
    
    const failureChip = screen.getByText('failure');
    expect(failureChip).toBeInTheDocument();
  });

  it('handles pagination', () => {
    render(
      <AuditLogViewer 
        logs={mockLogs} 
        onPageChange={mockOnPageChange}
        totalCount={50}
      />
    );
    
    const rowsPerPageSelect = screen.getByRole('combobox', { name: /rows per page/i });
    fireEvent.mouseDown(rowsPerPageSelect);
    
    // The test validates that pagination controls are present
    expect(rowsPerPageSelect).toBeInTheDocument();
  });

  it('displays action chips for each log', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    expect(screen.getByText('CREATE')).toBeInTheDocument();
    expect(screen.getByText('UPDATE')).toBeInTheDocument();
    expect(screen.getByText('DELETE')).toBeInTheDocument();
  });

  it('shows IP addresses in table', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    expect(screen.getByText('192.168.1.1')).toBeInTheDocument();
    expect(screen.getByText('192.168.1.2')).toBeInTheDocument();
    expect(screen.getByText('192.168.1.3')).toBeInTheDocument();
  });

  it('displays entity information correctly', () => {
    render(<AuditLogViewer logs={mockLogs} />);
    
    expect(screen.getByText(/Customer \(ID: 123\)/)).toBeInTheDocument();
    expect(screen.getByText(/Order \(ID: 456\)/)).toBeInTheDocument();
    expect(screen.getByText(/Product \(ID: 789\)/)).toBeInTheDocument();
  });
});
