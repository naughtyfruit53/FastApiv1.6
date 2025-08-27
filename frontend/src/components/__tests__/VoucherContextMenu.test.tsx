import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import VoucherContextMenu from '../VoucherContextMenu';

// Mock the handlers
const mockHandlers = {
  onView: jest.fn(),
  onEdit: jest.fn(),
  onDelete: jest.fn(),
  onPrint: jest.fn(),
  onEmail: jest.fn(),
};

const mockVoucher = {
  id: 1,
  voucher_number: 'PV001',
  vendor: {
    name: 'Test Vendor',
    email: 'vendor@test.com',
  },
};

const mockVoucherWithCustomer = {
  id: 2,
  voucher_number: 'SV001',
  customer: {
    name: 'Test Customer',
    email: 'customer@test.com',
  },
};

describe('VoucherContextMenu', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders kebab menu button', () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    expect(screen.getByLabelText('voucher actions')).toBeInTheDocument();
  });

  it('opens menu when kebab button is clicked', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      expect(screen.getByText('View')).toBeInTheDocument();
      expect(screen.getByText('Edit')).toBeInTheDocument();
      expect(screen.getByText('Save as PDF')).toBeInTheDocument();
      expect(screen.getByText('Delete')).toBeInTheDocument();
    });
  });

  it('shows correct email recipient for purchase voucher', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      expect(screen.getByText('Send to Test Vendor')).toBeInTheDocument();
    });
  });

  it('shows correct email recipient for sales voucher', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucherWithCustomer}
        voucherType="Sales"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      expect(screen.getByText('Send to Test Customer')).toBeInTheDocument();
    });
  });

  it('calls onView when View is clicked', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      const viewButton = screen.getByText('View');
      fireEvent.click(viewButton);
    });

    expect(mockHandlers.onView).toHaveBeenCalledWith(1);
  });

  it('calls onEdit when Edit is clicked', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      const editButton = screen.getByText('Edit');
      fireEvent.click(editButton);
    });

    expect(mockHandlers.onEdit).toHaveBeenCalledWith(1);
  });

  it('calls onEmail when email is clicked', async () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      const emailButton = screen.getByText('Send to Test Vendor');
      fireEvent.click(emailButton);
    });

    expect(mockHandlers.onEmail).toHaveBeenCalledWith(1);
  });

  it('disables email when no recipient is available', async () => {
    const voucherWithoutEmail = {
      id: 3,
      voucher_number: 'PV003',
      vendor: {
        name: 'Test Vendor',
        // no email
      },
    };

    render(
      <VoucherContextMenu
        voucher={voucherWithoutEmail}
        voucherType="Purchase"
        {...mockHandlers}
      />
    );

    const kebabButton = screen.getByLabelText('voucher actions');
    fireEvent.click(kebabButton);

    await waitFor(() => {
      const emailButton = screen.getByText('Send Email');
      expect(emailButton.closest('li')).toHaveAttribute('aria-disabled', 'true');
    });
  });

  it('hides kebab button when showKebab is false', () => {
    render(
      <VoucherContextMenu
        voucher={mockVoucher}
        voucherType="Purchase"
        showKebab={false}
        {...mockHandlers}
      />
    );

    expect(screen.queryByLabelText('voucher actions')).not.toBeInTheDocument();
  });
});