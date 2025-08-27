/**
 * Test file for ExportPrintToolbar component
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExportPrintToolbar from '../ExportPrintToolbar';
import { saveAs } from 'file-saver';

// Mock file-saver
jest.mock('file-saver', () => ({
  saveAs: jest.fn()
}));

const mockSaveAs = saveAs as jest.MockedFunction<typeof saveAs>;

describe('ExportPrintToolbar', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock window.print
    Object.defineProperty(window, 'print', {
      value: jest.fn(),
      writable: true
    });
  });

  describe('Default Behavior', () => {
    it('should render export and print buttons by default', () => {
      const mockExportExcel = jest.fn();
      const mockExportCSV = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          onExportCSV={mockExportCSV}
        />
      );
      
      expect(screen.getByText('Export')).toBeInTheDocument();
      expect(screen.getByLabelText('Print report')).toBeInTheDocument();
    });

    it('should show export menu when export button is clicked', async () => {
      const mockExportExcel = jest.fn();
      const mockExportCSV = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          onExportCSV={mockExportCSV}
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(screen.getByText('Export to Excel')).toBeInTheDocument();
        expect(screen.getByText('Export to CSV')).toBeInTheDocument();
      });
    });
  });

  describe('Excel Export', () => {
    it('should call onExportExcel when Excel option is clicked', async () => {
      const mockExportExcel = jest.fn().mockResolvedValue(new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }));
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          filename="test_report"
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });
      
      expect(mockExportExcel).toHaveBeenCalled();
    });

    it('should save file with correct filename', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const mockExportExcel = jest.fn().mockResolvedValue(mockBlob);
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          filename="sales_report"
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });
      
      await waitFor(() => {
        expect(mockSaveAs).toHaveBeenCalledWith(mockBlob, 'sales_report.xlsx');
      });
    });

    it('should handle export errors gracefully', async () => {
      const mockExportExcel = jest.fn().mockRejectedValue(new Error('Export failed'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error exporting Excel:', expect.any(Error));
      });
      
      consoleSpy.mockRestore();
    });
  });

  describe('CSV Export', () => {
    it('should call onExportCSV when CSV option is clicked', async () => {
      const mockExportCSV = jest.fn().mockResolvedValue(new Blob(['test'], { type: 'text/csv' }));
      
      render(
        <ExportPrintToolbar
          onExportCSV={mockExportCSV}
          filename="test_report"
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const csvOption = screen.getByText('Export to CSV');
        fireEvent.click(csvOption);
      });
      
      expect(mockExportCSV).toHaveBeenCalled();
    });

    it('should save CSV file with correct filename', async () => {
      const mockBlob = new Blob(['test'], { type: 'text/csv' });
      const mockExportCSV = jest.fn().mockResolvedValue(mockBlob);
      
      render(
        <ExportPrintToolbar
          onExportCSV={mockExportCSV}
          filename="inventory_report"
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const csvOption = screen.getByText('Export to CSV');
        fireEvent.click(csvOption);
      });
      
      await waitFor(() => {
        expect(mockSaveAs).toHaveBeenCalledWith(mockBlob, 'inventory_report.csv');
      });
    });
  });

  describe('Print Functionality', () => {
    it('should call window.print by default when print button is clicked', () => {
      render(<ExportPrintToolbar />);
      
      const printButton = screen.getByLabelText('Print report');
      fireEvent.click(printButton);
      
      expect(window.print).toHaveBeenCalled();
    });

    it('should call custom onPrint function when provided', () => {
      const mockOnPrint = jest.fn();
      
      render(<ExportPrintToolbar onPrint={mockOnPrint} />);
      
      const printButton = screen.getByLabelText('Print report');
      fireEvent.click(printButton);
      
      expect(mockOnPrint).toHaveBeenCalled();
      expect(window.print).not.toHaveBeenCalled();
    });
  });

  describe('Conditional Rendering', () => {
    it('should not show export button when no export handlers provided', () => {
      render(<ExportPrintToolbar showExcel={false} showCSV={false} />);
      
      expect(screen.queryByText('Export')).not.toBeInTheDocument();
      expect(screen.getByLabelText('Print report')).toBeInTheDocument();
    });

    it('should not show print button when showPrint is false', () => {
      render(<ExportPrintToolbar showPrint={false} />);
      
      expect(screen.queryByLabelText('Print report')).not.toBeInTheDocument();
    });

    it('should only show Excel option when showCSV is false', async () => {
      const mockExportExcel = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          showCSV={false}
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(screen.getByText('Export to Excel')).toBeInTheDocument();
        expect(screen.queryByText('Export to CSV')).not.toBeInTheDocument();
      });
    });

    it('should only show CSV option when showExcel is false', async () => {
      const mockExportCSV = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportCSV={mockExportCSV}
          showExcel={false}
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        expect(screen.getByText('Export to CSV')).toBeInTheDocument();
        expect(screen.queryByText('Export to Excel')).not.toBeInTheDocument();
      });
    });
  });

  describe('Loading and Disabled States', () => {
    it('should disable buttons when disabled prop is true', () => {
      const mockExportExcel = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          disabled={true}
        />
      );
      
      expect(screen.getByText('Export')).toBeDisabled();
      expect(screen.getByLabelText('Print report')).toBeDisabled();
    });

    it('should show loading indicator when loading is true', () => {
      const mockExportExcel = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
          loading={true}
        />
      );
      
      expect(screen.getByText('Export')).toBeDisabled();
      expect(screen.getByLabelText('Print report')).toBeDisabled();
      // Check for loading indicator (CircularProgress)
      expect(document.querySelector('.MuiCircularProgress-root')).toBeInTheDocument();
    });

    it('should disable export options during export', async () => {
      const mockExportExcel = jest.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(new Blob(['test'])), 100))
      );
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
        />
      );
      
      const exportButton = screen.getByText('Export');
      fireEvent.click(exportButton);
      
      await waitFor(() => {
        const excelOption = screen.getByText('Export to Excel');
        fireEvent.click(excelOption);
      });
      
      // Menu should close and buttons should be disabled during export
      expect(screen.queryByText('Export to Excel')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      const mockExportExcel = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
        />
      );
      
      expect(screen.getByLabelText('Export options')).toBeInTheDocument();
      expect(screen.getByLabelText('Print report')).toBeInTheDocument();
    });

    it('should be keyboard accessible', () => {
      const mockExportExcel = jest.fn();
      
      render(
        <ExportPrintToolbar
          onExportExcel={mockExportExcel}
        />
      );
      
      const exportButton = screen.getByText('Export');
      
      // Should be focusable
      exportButton.focus();
      expect(exportButton).toHaveFocus();
      
      // Should work with Enter key
      fireEvent.keyDown(exportButton, { key: 'Enter', code: 'Enter' });
      // Menu should open (we can test this by checking if menu items are rendered)
    });
  });
});