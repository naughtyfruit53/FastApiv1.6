import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter } from 'next/navigation';
import CreateVoucherButton from '../CreateVoucherButton';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

const mockPush = jest.fn();

describe('CreateVoucherButton', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
  });

  it('renders with correct text for purchase voucher', () => {
    render(<CreateVoucherButton voucherType="purchase" />);
    
    expect(screen.getByText('Create Purchase Voucher')).toBeInTheDocument();
  });

  it('renders with correct text for sales voucher', () => {
    render(<CreateVoucherButton voucherType="sales" />);
    
    expect(screen.getByText('Create Sales Voucher')).toBeInTheDocument();
  });

  it('renders with correct text for financial voucher', () => {
    render(<CreateVoucherButton voucherType="financial" />);
    
    expect(screen.getByText('Create Financial Voucher')).toBeInTheDocument();
  });

  it('renders with correct text for internal voucher', () => {
    render(<CreateVoucherButton voucherType="internal" />);
    
    expect(screen.getByText('Create Internal Voucher')).toBeInTheDocument();
  });

  it('navigates to purchase voucher page when clicked', () => {
    render(<CreateVoucherButton voucherType="purchase" />);
    
    const button = screen.getByText('Create Purchase Voucher');
    fireEvent.click(button);
    
    expect(mockPush).toHaveBeenCalledWith('/vouchers/Purchase-Vouchers/purchase-voucher');
  });

  it('does not render when visible is false', () => {
    render(<CreateVoucherButton voucherType="purchase" visible={false} />);
    
    expect(screen.queryByText('Create Purchase Voucher')).not.toBeInTheDocument();
  });

  it('has correct styling for yellow button', () => {
    render(<CreateVoucherButton voucherType="purchase" />);
    
    const button = screen.getByText('Create Purchase Voucher');
    expect(button).toHaveStyle({
      'background-color': '#FFD700',
      color: '#000',
      'font-weight': 'bold',
    });
  });

  it('renders as outlined variant when specified', () => {
    render(<CreateVoucherButton voucherType="purchase" variant="outlined" />);
    
    const button = screen.getByText('Create Purchase Voucher');
    expect(button).toHaveStyle({
      'background-color': 'transparent',
      color: '#FFD700',
    });
  });

  it('renders with small size when specified', () => {
    render(<CreateVoucherButton voucherType="purchase" size="small" />);
    
    const button = screen.getByText('Create Purchase Voucher');
    expect(button).toBeInTheDocument();
  });

  it('logs warning for unknown voucher type', () => {
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
    
    render(<CreateVoucherButton voucherType="unknown" />);
    
    const button = screen.getByText('Create Voucher');
    fireEvent.click(button);
    
    expect(consoleSpy).toHaveBeenCalledWith('No route defined for voucher type: unknown');
    expect(mockPush).not.toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });
});