import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CompanyLogoUpload from '../components/CompanyLogoUpload';
import { companyService } from '../services/authService';

// Mock the companyService
jest.mock('../services/authService', () => ({
  companyService: {
    uploadLogo: jest.fn(),
    deleteLogo: jest.fn(),
    getLogoUrl: jest.fn(),
  },
}));

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe('CompanyLogoUpload', () => {
  const mockCompanyService = companyService as jest.Mocked<typeof companyService>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockCompanyService.getLogoUrl.mockReturnValue('/api/v1/companies/1/logo');
  });

  it('renders upload area when no logo exists', () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null} 
      />
    );

    expect(screen.getByText('Company Logo')).toBeInTheDocument();
    expect(screen.getByText('Drag & drop logo here or click to upload')).toBeInTheDocument();
    expect(screen.getByText('PNG, JPG, JPEG, GIF up to 5MB')).toBeInTheDocument();
  });

  it('renders logo preview when logo exists', () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath="/path/to/logo.png" 
      />
    );

    expect(screen.getByText('Change')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /remove logo/i })).toBeInTheDocument();
  });

  it('shows error for invalid file type', async () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null} 
      />
    );

    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByRole('button', { name: /drag & drop logo here or click to upload/i });
    
    fireEvent.click(input);
    
    // Simulate file selection (this is a simplified test)
    // In a real test, you'd need to handle the file input properly
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(fileInput);
    }

    await waitFor(() => {
      expect(screen.getByText(/please select an image file/i)).toBeInTheDocument();
    });
  });

  it('shows error for oversized file', async () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null} 
      />
    );

    // Create a mock file that's too large (6MB)
    const largefile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.png', { type: 'image/png' });
    
    const input = screen.getByRole('button', { name: /drag & drop logo here or click to upload/i });
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      Object.defineProperty(fileInput, 'files', {
        value: [largefile],
        writable: false,
      });
      fireEvent.change(fileInput);
    }

    await waitFor(() => {
      expect(screen.getByText(/logo file size must be less than 5mb/i)).toBeInTheDocument();
    });
  });

  it('calls uploadLogo service when valid file is selected', async () => {
    mockCompanyService.uploadLogo.mockResolvedValue({ 
      message: 'Logo uploaded successfully',
      logo_path: '/path/to/new/logo.png'
    });

    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null} 
      />
    );

    const file = new File(['image data'], 'logo.png', { type: 'image/png' });
    const input = screen.getByRole('button', { name: /drag & drop logo here or click to upload/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(fileInput);
    }

    await waitFor(() => {
      expect(mockCompanyService.uploadLogo).toHaveBeenCalledWith(1, file);
    });
  });

  it('calls deleteLogo service when delete button is clicked', async () => {
    mockCompanyService.deleteLogo.mockResolvedValue({ 
      message: 'Logo deleted successfully'
    });

    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath="/path/to/logo.png" 
      />
    );

    const deleteButton = screen.getByRole('button', { name: /remove logo/i });
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockCompanyService.deleteLogo).toHaveBeenCalledWith(1);
    });
  });

  it('is disabled when disabled prop is true', () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null}
        disabled={true}
      />
    );

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(fileInput).toBeDisabled();
  });

  it('calls onLogoChange callback when logo changes', async () => {
    const mockOnLogoChange = jest.fn();
    mockCompanyService.uploadLogo.mockResolvedValue({ 
      message: 'Logo uploaded successfully',
      logo_path: '/path/to/new/logo.png'
    });

    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null}
        onLogoChange={mockOnLogoChange}
      />
    );

    const file = new File(['image data'], 'logo.png', { type: 'image/png' });
    const input = screen.getByRole('button', { name: /drag & drop logo here or click to upload/i });
    
    fireEvent.click(input);
    
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(fileInput);
    }

    await waitFor(() => {
      expect(mockOnLogoChange).toHaveBeenCalledWith('/path/to/new/logo.png');
    });
  });

  it('handles drag and drop functionality', async () => {
    renderWithProviders(
      <CompanyLogoUpload 
        companyId={1} 
        currentLogoPath={null}
      />
    );

    const file = new File(['image data'], 'logo.png', { type: 'image/png' });
    const dropZone = screen.getByRole('button', { name: /drag & drop logo here or click to upload/i });

    // Test drag over
    fireEvent.dragOver(dropZone);
    
    // Test drag leave
    fireEvent.dragLeave(dropZone);
    
    // Test drop
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(mockCompanyService.uploadLogo).toHaveBeenCalledWith(1, file);
    });
  });
});