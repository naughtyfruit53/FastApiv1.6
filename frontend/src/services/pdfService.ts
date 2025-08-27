// Professional PDF Service for Vouchers
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface CompanyBranding {
  name: string;
  address: string;
  contact_number: string;
  email: string;
  logo_path?: string;
  website?: string;
  gstin?: string;
}

interface VoucherData {
  voucher_number: string;
  date: string;
  reference?: string;
  notes?: string;
  total_amount: number;
  items?: any[];
  // Party information (vendor/customer)
  party?: {
    name: string;
    address?: string;
    contact_number?: string;
    email?: string;
    gstin?: string;
  };
  // Voucher specific fields
  payment_method?: string;
  receipt_method?: string;
  payment_terms?: string;
}

interface PdfOptions {
  voucherType: string;
  voucherTitle: string;
  filename: string;
  showItems?: boolean;
  showTaxDetails?: boolean;
}

class ProfessionalPdfService {
  private doc: jsPDF;
  private pageWidth: number;
  private pageHeight: number;
  private margins = {
    top: 20,
    left: 20,
    right: 20,
    bottom: 30
  };

  constructor() {
    this.doc = new jsPDF();
    this.pageWidth = this.doc.internal.pageSize.getWidth();
    this.pageHeight = this.doc.internal.pageSize.getHeight();
  }

  private async loadCompanyBranding(): Promise<CompanyBranding> {
    try {
      // Fetch company branding from API
      const response = await fetch('/api/v1/company/branding', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to load company branding:', error);
    }
    
    // Fallback to default branding
    return {
      name: 'Your Company Name',
      address: 'Company Address',
      contact_number: 'Contact Number',
      email: 'company@email.com',
      website: 'www.yourcompany.com'
    };
  }

  private drawHeader(company: CompanyBranding, voucherTitle: string): number {
    let yPosition = this.margins.top;

    // Company Logo (if available)
    if (company.logo_path) {
      try {
        // Create a more realistic logo placeholder with company initial
        const companyInitial = company.name.charAt(0).toUpperCase();
        this.doc.setDrawColor(100);
        this.doc.setFillColor(245, 245, 245);
        this.doc.roundedRect(this.margins.left, yPosition, 40, 25, 3, 3, 'FD');
        
        // Company initial in the logo area
        this.doc.setFontSize(16);
        this.doc.setFont('helvetica', 'bold');
        this.doc.setTextColor(80);
        this.doc.text(companyInitial, this.margins.left + 20, yPosition + 16, { align: 'center' });
        
        // Logo text
        this.doc.setFontSize(6);
        this.doc.setTextColor(120);
        this.doc.text('LOGO', this.margins.left + 20, yPosition + 21, { align: 'center' });
        this.doc.setTextColor(0);
      } catch (error) {
        console.warn('Logo display error:', error);
      }
    }

    // Company Information (right aligned)
    this.doc.setFontSize(16);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(0, 50, 100); // Professional blue color
    this.doc.text(company.name, this.pageWidth - this.margins.right, yPosition + 8, { align: 'right' });
    
    this.doc.setFontSize(9);
    this.doc.setFont('helvetica', 'normal');
    this.doc.setTextColor(0);
    yPosition += 12;
    
    const companyInfo = [
      company.address,
      `Phone: ${company.contact_number}`,
      `Email: ${company.email}`,
      company.website || '',
      company.gstin ? `GSTIN: ${company.gstin}` : ''
    ].filter(info => info.trim());

    companyInfo.forEach(info => {
      this.doc.text(info, this.pageWidth - this.margins.right, yPosition, { align: 'right' });
      yPosition += 4;
    });

    // Voucher Title (centered with background)
    yPosition += 15;
    const titleWidth = 120;
    const titleX = (this.pageWidth - titleWidth) / 2;
    
    // Title background
    this.doc.setFillColor(0, 50, 100);
    this.doc.rect(titleX, yPosition - 5, titleWidth, 12, 'F');
    
    // Title text
    this.doc.setFontSize(14);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(255, 255, 255);
    this.doc.text(voucherTitle, this.pageWidth / 2, yPosition + 3, { align: 'center' });
    
    // Reset text color
    this.doc.setTextColor(0);
    
    // Decorative line
    yPosition += 15;
    this.doc.setDrawColor(200);
    this.doc.setLineWidth(0.5);
    this.doc.line(this.margins.left, yPosition, this.pageWidth - this.margins.right, yPosition);
    
    return yPosition + 10;
  }

  private drawVoucherDetails(voucher: VoucherData, yPosition: number): number {
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'normal');

    // Left column - Voucher details
    const leftX = this.margins.left;
    const rightX = this.pageWidth / 2 + 10;
    let leftY = yPosition;
    let rightY = yPosition;

    // Voucher Number and Date
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Voucher Number:', leftX, leftY);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(voucher.voucher_number, leftX + 35, leftY);
    leftY += 6;

    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Date:', leftX, leftY);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(new Date(voucher.date).toLocaleDateString(), leftX + 35, leftY);
    leftY += 6;

    if (voucher.reference) {
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('Reference:', leftX, leftY);
      this.doc.setFont('helvetica', 'normal');
      this.doc.text(voucher.reference, leftX + 35, leftY);
      leftY += 6;
    }

    // Right column - Party details
    if (voucher.party) {
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('Party Details:', rightX, rightY);
      rightY += 6;

      this.doc.setFont('helvetica', 'normal');
      this.doc.text(voucher.party.name, rightX, rightY);
      rightY += 5;

      if (voucher.party.address) {
        const addressLines = this.doc.splitTextToSize(voucher.party.address, 80);
        this.doc.text(addressLines, rightX, rightY);
        rightY += addressLines.length * 4;
      }

      if (voucher.party.contact_number) {
        this.doc.text(`Phone: ${voucher.party.contact_number}`, rightX, rightY);
        rightY += 5;
      }

      if (voucher.party.email) {
        this.doc.text(`Email: ${voucher.party.email}`, rightX, rightY);
        rightY += 5;
      }

      if (voucher.party.gstin) {
        this.doc.text(`GSTIN: ${voucher.party.gstin}`, rightX, rightY);
        rightY += 5;
      }
    }

    // Additional voucher-specific fields
    if (voucher.payment_method) {
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('Payment Method:', leftX, leftY);
      this.doc.setFont('helvetica', 'normal');
      this.doc.text(voucher.payment_method, leftX + 35, leftY);
      leftY += 6;
    }

    if (voucher.receipt_method) {
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('Receipt Method:', leftX, leftY);
      this.doc.setFont('helvetica', 'normal');
      this.doc.text(voucher.receipt_method, leftX + 35, leftY);
      leftY += 6;
    }

    if (voucher.payment_terms) {
      this.doc.setFont('helvetica', 'bold');
      this.doc.text('Payment Terms:', leftX, leftY);
      this.doc.setFont('helvetica', 'normal');
      const termsLines = this.doc.splitTextToSize(voucher.payment_terms, 70);
      this.doc.text(termsLines, leftX + 35, leftY);
      leftY += termsLines.length * 4;
    }

    return Math.max(leftY, rightY) + 10;
  }

  private drawItemsTable(items: any[], yPosition: number): number {
    if (!items || items.length === 0) {
      return yPosition;
    }

    const columns = [
      { header: 'S.No.', dataKey: 'sno' },
      { header: 'Description', dataKey: 'description' },
      { header: 'HSN/SAC', dataKey: 'hsn' },
      { header: 'Qty', dataKey: 'quantity' },
      { header: 'Unit', dataKey: 'unit' },
      { header: 'Rate', dataKey: 'rate' },
      { header: 'Amount', dataKey: 'amount' }
    ];

    const tableData = items.map((item, index) => ({
      sno: (index + 1).toString(),
      description: item.product?.name || item.description || `Product ${item.product_id}`,
      hsn: item.hsn_code || item.hsn_sac || '-',
      quantity: item.quantity?.toString() || '0',
      unit: item.unit || 'Nos',
      rate: item.unit_price?.toFixed(2) || '0.00',
      amount: item.total_amount?.toFixed(2) || (item.quantity * item.unit_price)?.toFixed(2) || '0.00'
    }));

    autoTable(this.doc, {
      startY: yPosition,
      head: [columns.map(col => col.header)],
      body: tableData.map(row => columns.map(col => row[col.dataKey as keyof typeof row])),
      styles: {
        fontSize: 9,
        cellPadding: 3,
      },
      headStyles: {
        fillColor: [240, 240, 240],
        textColor: [0, 0, 0],
        fontStyle: 'bold',
      },
      alternateRowStyles: {
        fillColor: [250, 250, 250],
      },
      margin: { left: this.margins.left, right: this.margins.right },
    });

    return (this.doc as any).lastAutoTable.finalY + 10;
  }

  private drawTotals(voucher: VoucherData, yPosition: number): number {
    const rightX = this.pageWidth - this.margins.right;
    
    // Add some spacing before totals
    yPosition += 5;
    
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'bold');
    
    // Draw total amount with professional styling
    const boxWidth = 80;
    const boxHeight = 20;
    
    // Total amount box with border and background
    this.doc.setDrawColor(0, 50, 100);
    this.doc.setFillColor(245, 250, 255);
    this.doc.setLineWidth(1);
    this.doc.roundedRect(rightX - boxWidth, yPosition, boxWidth, boxHeight, 2, 2, 'FD');
    
    // Total label and amount
    this.doc.setFontSize(11);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(0, 50, 100);
    this.doc.text('TOTAL AMOUNT:', rightX - 75, yPosition + 7);
    
    this.doc.setFontSize(13);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(0);
    this.doc.text(`₹ ${voucher.total_amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`, rightX - 5, yPosition + 14, { align: 'right' });
    
    yPosition += 25;

    // Amount in words with professional styling
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(80);
    this.doc.text('Amount in Words:', this.margins.left, yPosition);
    
    this.doc.setFont('helvetica', 'normal');
    this.doc.setTextColor(0);
    const amountInWords = this.numberToWords(voucher.total_amount);
    const wordsLines = this.doc.splitTextToSize(amountInWords, this.pageWidth - this.margins.left - this.margins.right - 40);
    
    // Add a subtle border around amount in words
    const wordsHeight = wordsLines.length * 4 + 6;
    this.doc.setDrawColor(200);
    this.doc.setLineWidth(0.5);
    this.doc.rect(this.margins.left + 35, yPosition - 3, this.pageWidth - this.margins.left - this.margins.right - 40, wordsHeight);
    
    this.doc.text(wordsLines, this.margins.left + 38, yPosition + 2);
    
    return yPosition + wordsHeight + 10;
  }

  private drawNotes(notes: string, yPosition: number): number {
    if (!notes) return yPosition;

    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Notes:', this.margins.left, yPosition);
    
    this.doc.setFont('helvetica', 'normal');
    const notesLines = this.doc.splitTextToSize(notes, this.pageWidth - this.margins.left - this.margins.right - 15);
    this.doc.text(notesLines, this.margins.left + 15, yPosition);
    
    return yPosition + (notesLines.length * 4) + 10;
  }

  private drawFooter(yPosition: number): void {
    const footerY = this.pageHeight - this.margins.bottom;
    
    // Terms and conditions section (if space allows)
    if (yPosition < footerY - 40) {
      this.doc.setFontSize(8);
      this.doc.setFont('helvetica', 'bold');
      this.doc.setTextColor(80);
      this.doc.text('Terms & Conditions:', this.margins.left, yPosition + 5);
      
      this.doc.setFont('helvetica', 'normal');
      this.doc.setTextColor(100);
      const terms = [
        '• Payment is due within 30 days of invoice date',
        '• Late payments may incur additional charges',
        '• All disputes must be raised within 7 days'
      ];
      
      terms.forEach((term, index) => {
        this.doc.text(term, this.margins.left, yPosition + 12 + (index * 4));
      });
    }
    
    // Authorized signature with enhanced styling
    this.doc.setFontSize(10);
    this.doc.setFont('helvetica', 'bold');
    this.doc.setTextColor(0);
    this.doc.text('For ' + (this.doc as any).companyName || 'Organization', this.pageWidth - this.margins.right - 60, footerY - 25);
    
    this.doc.setFont('helvetica', 'normal');
    this.doc.text('Authorized Signatory', this.pageWidth - this.margins.right - 60, footerY - 10);
    
    // Signature line
    this.doc.setDrawColor(0);
    this.doc.setLineWidth(0.5);
    this.doc.line(this.pageWidth - this.margins.right - 80, footerY - 5, this.pageWidth - this.margins.right - 10, footerY - 5);
    
    // Footer separator line
    this.doc.setDrawColor(200);
    this.doc.setLineWidth(0.5);
    this.doc.line(this.margins.left, footerY + 5, this.pageWidth - this.margins.right, footerY + 5);
    
    // Footer disclaimer
    this.doc.setFontSize(8);
    this.doc.setFont('helvetica', 'italic');
    this.doc.setTextColor(120);
    this.doc.text('This is a computer-generated document and does not require a physical signature.', 
                  this.pageWidth / 2, footerY + 10, { align: 'center' });
    
    // Page number and generation info
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(`Page 1`, this.margins.left, footerY + 10);
    this.doc.text(`Generated on: ${new Date().toLocaleDateString()}`, this.pageWidth - this.margins.right, footerY + 10, { align: 'right' });
    
    this.doc.setTextColor(0);
  }

  private numberToWords(num: number): string {
    // Simple implementation - in production, use a proper library
    if (num === 0) return 'Zero';
    
    const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                  'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
    const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
    
    const convert = (n: number): string => {
      if (n < 20) return ones[n];
      if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 ? ' ' + ones[n % 10] : '');
      if (n < 1000) return ones[Math.floor(n / 100)] + ' Hundred' + (n % 100 ? ' ' + convert(n % 100) : '');
      if (n < 100000) return convert(Math.floor(n / 1000)) + ' Thousand' + (n % 1000 ? ' ' + convert(n % 1000) : '');
      if (n < 10000000) return convert(Math.floor(n / 100000)) + ' Lakh' + (n % 100000 ? ' ' + convert(n % 100000) : '');
      return convert(Math.floor(n / 10000000)) + ' Crore' + (n % 10000000 ? ' ' + convert(n % 10000000) : '');
    };
    
    const rupees = Math.floor(num);
    const paise = Math.round((num - rupees) * 100);
    
    let result = convert(rupees) + ' Rupees';
    if (paise > 0) {
      result += ' and ' + convert(paise) + ' Paise';
    }
    result += ' Only';
    
    return result;
  }

  async generateVoucherPDF(voucher: VoucherData, options: PdfOptions): Promise<void> {
    this.doc = new jsPDF(); // Reset document
    
    try {
      // Load company branding
      const company = await this.loadCompanyBranding();
      
      // Draw header
      let yPosition = this.drawHeader(company, options.voucherTitle);
      
      // Draw voucher details
      yPosition = this.drawVoucherDetails(voucher, yPosition);
      
      // Draw items table if applicable
      if (options.showItems && voucher.items && voucher.items.length > 0) {
        yPosition = this.drawItemsTable(voucher.items, yPosition);
      }
      
      // Draw totals
      yPosition = this.drawTotals(voucher, yPosition);
      
      // Draw notes
      if (voucher.notes) {
        yPosition = this.drawNotes(voucher.notes, yPosition);
      }
      
      // Draw footer
      this.drawFooter(yPosition);
      
      // Save the PDF
      this.doc.save(options.filename);
      
      // Log the PDF generation for audit
      this.logPdfGeneration(options.voucherType, voucher.voucher_number);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      throw new Error('Failed to generate PDF. Please try again.');
    }
  }

  private async logPdfGeneration(voucherType: string, voucherNumber: string): Promise<void> {
    try {
      await fetch('/api/v1/audit/pdf-generation', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'pdf_generated',
          voucher_type: voucherType,
          voucher_number: voucherNumber,
          timestamp: new Date().toISOString()
        })
      });
    } catch (error) {
      console.warn('Failed to log PDF generation:', error);
    }
  }
}

export const pdfService = new ProfessionalPdfService();
export default pdfService;