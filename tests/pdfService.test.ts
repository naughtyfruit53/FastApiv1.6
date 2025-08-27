// tests/pdfService.test.ts

import pdfService from '../frontend/src/services/pdfService';

// Mock jsPDF and autoTable
jest.mock('jspdf', () => {
  const mockDoc = {
    setFontSize: jest.fn(),
    setFont: jest.fn(),
    text: jest.fn(),
    setDrawColor: jest.fn(),
    setFillColor: jest.fn(),
    setLineWidth: jest.fn(),
    setTextColor: jest.fn(),
    rect: jest.fn(),
    line: jest.fn(),
    splitTextToSize: jest.fn().mockReturnValue(['Test line']),
    save: jest.fn(),
    internal: {
      pageSize: {
        getWidth: jest.fn().mockReturnValue(210),
        getHeight: jest.fn().mockReturnValue(297)
      }
    }
  };
  
  return jest.fn().mockImplementation(() => mockDoc);
});

jest.mock('jspdf-autotable', () => jest.fn());

// Mock fetch
global.fetch = jest.fn();

describe('PdfService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn().mockReturnValue('mock-token'),
        setItem: jest.fn(),
        removeItem: jest.fn()
      },
      writable: true
    });
  });

  describe('generateVoucherPDF', () => {
    const mockVoucherData = {
      voucher_number: 'PV/2526/00000001',
      date: '2024-01-01',
      reference: 'Test Reference',
      notes: 'Test Notes',
      total_amount: 1000,
      payment_method: 'Cash',
      party: {
        name: 'Test Party',
        address: 'Test Address',
        contact_number: '1234567890',
        email: 'test@party.com',
        gstin: 'TEST123456789'
      }
    };

    const mockPdfOptions = {
      voucherType: 'payment-voucher',
      voucherTitle: 'PAYMENT VOUCHER',
      filename: 'PaymentVoucher_PV_2526_00000001.pdf',
      showItems: false,
      showTaxDetails: false
    };

    it('should generate PDF successfully with company branding', async () => {
      // Mock successful company branding API response
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue({
          name: 'Test Company',
          address: 'Company Address',
          contact_number: '0987654321',
          email: 'company@test.com',
          logo_path: null
        })
      });

      // Mock successful audit log API response
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue({ status: 'logged' })
      });

      await pdfService.generateVoucherPDF(mockVoucherData, mockPdfOptions);

      // Verify API calls were made
      expect(fetch).toHaveBeenCalledWith('/api/v1/company/branding', expect.any(Object));
      expect(fetch).toHaveBeenCalledWith('/api/v1/audit/pdf-generation', expect.any(Object));
    });

    it('should use fallback branding when API fails', async () => {
      // Mock failed company branding API response
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

      // Mock successful audit log API response
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue({ status: 'logged' })
      });

      await pdfService.generateVoucherPDF(mockVoucherData, mockPdfOptions);

      // Should still complete successfully with fallback branding
      expect(fetch).toHaveBeenCalledWith('/api/v1/company/branding', expect.any(Object));
    });

    it('should handle missing authentication token', async () => {
      // Mock no token in localStorage
      (window.localStorage.getItem as jest.Mock).mockReturnValue(null);

      await expect(pdfService.generateVoucherPDF(mockVoucherData, mockPdfOptions))
        .rejects
        .toThrow('Failed to generate PDF. Please try again.');
    });

    it('should handle voucher data with items', async () => {
      const voucherWithItems = {
        ...mockVoucherData,
        items: [
          {
            product: { name: 'Test Product' },
            quantity: 2,
            unit: 'Nos',
            unit_price: 500,
            total_amount: 1000,
            hsn_code: '1234'
          }
        ]
      };

      const optionsWithItems = {
        ...mockPdfOptions,
        showItems: true
      };

      // Mock successful API responses
      (fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue({
            name: 'Test Company',
            address: 'Company Address',
            contact_number: '0987654321',
            email: 'company@test.com'
          })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: jest.fn().mockResolvedValue({ status: 'logged' })
        });

      await pdfService.generateVoucherPDF(voucherWithItems, optionsWithItems);

      // Should complete successfully
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    it('should continue even if audit logging fails', async () => {
      // Mock successful company branding API response
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValue({
          name: 'Test Company',
          address: 'Company Address',
          contact_number: '0987654321',
          email: 'company@test.com'
        })
      });

      // Mock failed audit log API response
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Audit API Error'));

      // Should not throw error even if audit fails
      await expect(pdfService.generateVoucherPDF(mockVoucherData, mockPdfOptions))
        .resolves
        .not.toThrow();
    });
  });

  describe('numberToWords', () => {
    it('should convert numbers to words correctly', () => {
      // Access the private method through the service instance
      const service = (pdfService as any);
      
      // Test basic numbers
      expect(service.numberToWords(0)).toBe('Zero');
      expect(service.numberToWords(1)).toBe('One Rupees Only');
      expect(service.numberToWords(25)).toBe('Twenty Five Rupees Only');
      expect(service.numberToWords(100)).toBe('One Hundred Rupees Only');
      expect(service.numberToWords(1000)).toBe('One Thousand Rupees Only');
      expect(service.numberToWords(100000)).toBe('One Lakh Rupees Only');
      expect(service.numberToWords(10000000)).toBe('One Crore Rupees Only');
    });

    it('should handle decimal amounts', () => {
      const service = (pdfService as any);
      
      expect(service.numberToWords(1.50)).toBe('One Rupees and Fifty Paise Only');
      expect(service.numberToWords(123.45)).toBe('One Hundred Twenty Three Rupees and Forty Five Paise Only');
    });
  });
});

describe('PDF Service Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle network errors gracefully', async () => {
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn().mockReturnValue('mock-token'),
      },
      writable: true
    });

    // Mock network error
    (fetch as jest.Mock).mockRejectedValue(new Error('Network Error'));

    const mockVoucherData = {
      voucher_number: 'TEST001',
      date: '2024-01-01',
      total_amount: 1000
    };

    const mockPdfOptions = {
      voucherType: 'test-voucher',
      voucherTitle: 'TEST VOUCHER',
      filename: 'test.pdf',
      showItems: false,
      showTaxDetails: false
    };

    await expect(pdfService.generateVoucherPDF(mockVoucherData, mockPdfOptions))
      .rejects
      .toThrow('Failed to generate PDF. Please try again.');
  });
});