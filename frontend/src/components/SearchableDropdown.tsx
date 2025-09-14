// frontend/src/components/SearchableDropdown.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  TextField,
  Autocomplete,
  CircularProgress,
  Box,
  Typography,
  Button,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import debounce from 'lodash/debounce';

interface Option {
  label: string;
  value: any;
  [key: string]: any;
}

interface SearchableDropdownProps {
  label: string;
  options: Option[];
  value: any;
  onChange: (value: any) => void;
  getOptionLabel?: (option: Option) => string;
  getOptionValue?: (option: Option) => any;
  placeholder?: string;
  noOptionsText?: string;
  loadingText?: string;
  disabled?: boolean;
  fullWidth?: boolean;
  required?: boolean;
  error?: boolean;
  helperText?: string;
  size?: 'small' | 'medium';
  fetchOptions?: (searchTerm: string) => Promise<Option[]>;
  onAddNew?: () => void;
  onRefresh?: () => void;
  debounceTime?: number;
  showAddButton?: boolean;
  showRefreshButton?: boolean;
  renderOption?: (props: any, option: Option) => React.ReactNode;
}

const SearchableDropdown: React.FC<SearchableDropdownProps> = ({
  label,
  options: initialOptions,
  value,
  onChange,
  getOptionLabel = (option) => option.label,
  getOptionValue = (option) => option.value,
  placeholder = 'Search...',
  noOptionsText = 'No options found',
  loadingText = 'Loading...',
  disabled = false,
  fullWidth = true,
  required = false,
  error = false,
  helperText = '',
  size = 'small',
  fetchOptions,
  onAddNew,
  onRefresh,
  debounceTime = 300,
  showAddButton = false,
  showRefreshButton = false,
  renderOption,
}) => {
  const [options, setOptions] = useState<Option[]>(initialOptions);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState<Option | null>(null);

  useEffect(() => {
    setOptions(initialOptions);
  }, [initialOptions]);

  useEffect(() => {
    const option = options.find((opt) => getOptionValue(opt) === value);
    setSelectedOption(option || null);
    if (option) {
      setInputValue(getOptionLabel(option));
    }
  }, [value, options, getOptionLabel, getOptionValue]);

  const debouncedFetch = useCallback(
    debounce(async (searchTerm: string) => {
      if (fetchOptions) {
        setLoading(true);
        try {
          const fetchedOptions = await fetchOptions(searchTerm);
          setOptions(fetchedOptions);
        } catch (error) {
          console.error('Error fetching options:', error);
        } finally {
          setLoading(false);
        }
      }
    }, debounceTime),
    [fetchOptions, debounceTime]
  );

  const handleInputChange = (event: React.ChangeEvent<{}>, newInputValue: string) => {
    setInputValue(newInputValue);
    if (fetchOptions) {
      debouncedFetch(newInputValue);
    }
  };

  const handleChange = (event: React.ChangeEvent<{}>, newValue: Option | null) => {
    setSelectedOption(newValue);
    onChange(newValue ? getOptionValue(newValue) : null);
    if (newValue) {
      setInputValue(getOptionLabel(newValue));
    } else {
      setInputValue('');
    }
  };

  const filterOptions = (options: Option[], { inputValue }: { inputValue: string }) => {
    if (!fetchOptions) {
      return options.filter((option) =>
        getOptionLabel(option).toLowerCase().includes(inputValue.toLowerCase())
      );
    }
    return options;
  };

  return (
    <Box sx={{ position: 'relative', width: fullWidth ? '100%' : 'auto' }}>
      <Autocomplete
        size={size}
        options={options}
        getOptionLabel={getOptionLabel}
        value={selectedOption}
        onChange={handleChange}
        onInputChange={handleInputChange}
        inputValue={inputValue}
        filterOptions={filterOptions}
        disabled={disabled}
        noOptionsText={
          <Typography variant="body2" color="textSecondary">
            {noOptionsText}
          </Typography>
        }
        loading={loading}
        loadingText={
          <Box display="flex" alignItems="center">
            <CircularProgress size={16} sx={{ mr: 1 }} />
            <Typography variant="body2">{loadingText}</Typography>
          </Box>
        }
        renderInput={(params) => (
          <TextField
            {...params}
            label={label}
            placeholder={placeholder}
            required={required}
            error={error}
            helperText={helperText}
            fullWidth={fullWidth}
            variant="outlined"
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {loading ? <CircularProgress color="inherit" size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={renderOption}
      />
      {(showAddButton || showRefreshButton) && (
        <Box
          sx={{
            position: 'absolute',
            right: 0,
            top: '50%',
            transform: 'translateY(-50%)',
            display: 'flex',
            alignItems: 'center',
            pr: 1,
          }}
        >
          {showAddButton && onAddNew && (
            <IconButton size="small" onClick={onAddNew} disabled={disabled}>
              <AddIcon fontSize="small" />
            </IconButton>
          )}
          {showRefreshButton && onRefresh && (
            <IconButton size="small" onClick={onRefresh} disabled={disabled}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          )}
        </Box>
      )}
    </Box>
  );
};

export default SearchableDropdown;