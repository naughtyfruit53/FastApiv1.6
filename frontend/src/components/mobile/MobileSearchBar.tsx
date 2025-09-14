import React from 'react';
import { TextField, InputAdornment, IconButton } from '@mui/material';
import { Search, Clear } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onClear?: () => void;
  fullWidth?: boolean;
  autoFocus?: boolean;
}

const MobileSearchBar: React.FC<MobileSearchBarProps> = ({
  value,
  onChange,
  placeholder = 'Search...',
  onClear,
  fullWidth = true,
  autoFocus = false,
}) => {
  const { isMobile } = useMobileDetection();

  const handleClear = () => {
    onChange('');
    if (onClear) {
      onClear();
    }
  };

  return (
    <TextField
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      fullWidth={fullWidth}
      autoFocus={autoFocus}
      size={isMobile ? 'medium' : 'small'}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: isMobile ? 3 : 2,
          minHeight: isMobile ? 48 : 40,
          backgroundColor: 'background.paper',
        },
        '& .MuiInputBase-input': {
          fontSize: isMobile ? '1rem' : '0.875rem',
          padding: isMobile ? '12px 14px' : '8px 14px',
        },
      }}
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <Search sx={{ fontSize: isMobile ? '1.5rem' : '1.25rem' }} />
          </InputAdornment>
        ),
        endAdornment: value && (
          <InputAdornment position="end">
            <IconButton
              onClick={handleClear}
              size="small"
              sx={{
                minWidth: isMobile ? 44 : 32,
                minHeight: isMobile ? 44 : 32,
              }}
            >
              <Clear sx={{ fontSize: isMobile ? '1.25rem' : '1rem' }} />
            </IconButton>
          </InputAdornment>
        ),
      }}
    />
  );
};

export default MobileSearchBar;