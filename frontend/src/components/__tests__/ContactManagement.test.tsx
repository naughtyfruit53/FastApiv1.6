// Simple utility function test for sales CRM
describe("Sales CRM Utilities", () => {
  it("should format currency correctly", () => {
    const formatCurrency = (amount: number): string => {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount);
    };

    expect(formatCurrency(1000)).toBe("$1,000.00");
    expect(formatCurrency(150000)).toBe("$150,000.00");
  });

  it("should calculate commission correctly", () => {
    const calculateCommission = (dealAmount: number, rate: number): number => {
      return dealAmount * (rate / 100);
    };

    expect(calculateCommission(100000, 8)).toBe(8000);
    expect(calculateCommission(50000, 10)).toBe(5000);
  });

  it("should validate PAN number format", () => {
    const validatePAN = (pan: string): boolean => {
      const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
      return panRegex.test(pan);
    };

    expect(validatePAN("ABCDE1234F")).toBe(true);
    expect(validatePAN("INVALID")).toBe(false);
    expect(validatePAN("abcde1234f")).toBe(false);
  });

  it("should validate Aadhaar number format", () => {
    const validateAadhaar = (aadhaar: string): boolean => {
      const aadhaarRegex = /^[0-9]{12}$/;
      return aadhaarRegex.test(aadhaar);
    };

    expect(validateAadhaar("123456789012")).toBe(true);
    expect(validateAadhaar("12345678901")).toBe(false); // 11 digits
    expect(validateAadhaar("1234567890123")).toBe(false); // 13 digits
    expect(validateAadhaar("12345678901a")).toBe(false); // contains letter
  });
});
