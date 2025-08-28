import { render, screen } from '@testing-library/react';

// Employee management utility functions test
describe('Employee Management Utilities', () => {
  it('should generate employee code correctly', () => {
    const generateEmployeeCode = (department: string, sequence: number): string => {
      const deptCode = department.substring(0, 3).toUpperCase();
      const seqCode = sequence.toString().padStart(3, '0');
      return `${deptCode}${seqCode}`;
    };

    expect(generateEmployeeCode('Engineering', 1)).toBe('ENG001');
    expect(generateEmployeeCode('Human Resources', 25)).toBe('HUM025');
    expect(generateEmployeeCode('IT', 123)).toBe('IT123');
  });

  it('should validate Indian KYC fields', () => {
    // PAN validation
    const validatePAN = (pan: string): boolean => {
      const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
      return panRegex.test(pan);
    };

    // Aadhaar validation
    const validateAadhaar = (aadhaar: string): boolean => {
      const aadhaarRegex = /^[0-9]{12}$/;
      return aadhaarRegex.test(aadhaar);
    };

    // IFSC validation
    const validateIFSC = (ifsc: string): boolean => {
      const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
      return ifscRegex.test(ifsc);
    };

    // Test PAN validation
    expect(validatePAN('ABCDE1234F')).toBe(true);
    expect(validatePAN('INVALID')).toBe(false);

    // Test Aadhaar validation
    expect(validateAadhaar('123456789012')).toBe(true);
    expect(validateAadhaar('12345678901')).toBe(false);

    // Test IFSC validation
    expect(validateIFSC('SBIN0001234')).toBe(true);
    expect(validateIFSC('INVALID')).toBe(false);
  });

  it('should calculate employee tenure correctly', () => {
    const calculateTenure = (hireDate: string): number => {
      const hire = new Date(hireDate);
      const now = new Date('2024-01-01'); // Fixed date for testing
      const diffTime = Math.abs(now.getTime() - hire.getTime());
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      return Math.floor(diffDays / 365); // Years
    };

    expect(calculateTenure('2022-01-01')).toBe(2);
    expect(calculateTenure('2023-01-01')).toBe(1);
    expect(calculateTenure('2024-01-01')).toBe(0);
  });

  it('should format employee status correctly', () => {
    const getStatusDisplayName = (status: string): string => {
      const statusMap: Record<string, string> = {
        'active': 'Active',
        'inactive': 'Inactive',
        'on_leave': 'On Leave',
        'terminated': 'Terminated'
      };
      return statusMap[status] || status;
    };

    expect(getStatusDisplayName('active')).toBe('Active');
    expect(getStatusDisplayName('on_leave')).toBe('On Leave');
    expect(getStatusDisplayName('unknown')).toBe('unknown');
  });
});