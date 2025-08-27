// src/components/EntitySelector.tsx
// Unified Entity selection component for Customer + Vendor + Employee + ExpenseAccount

import React, { useState } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Chip,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
  Tooltip,
  CircularProgress
} from '@mui/material';
import { Add, Person, Business, Badge, AccountBalance } from '@mui/icons-material';
import { Controller, Control } from 'react-hook-form';
import { useEntityOptions, useEntityForm } from '../hooks/useEntity';
import { EntityType, EntityOption, ENTITY_CONFIGS } from '../types/entity.types';
import AddVendorModal from './AddVendorModal';
import AddCustomerModal from './AddCustomerModal';

interface EntitySelectorProps {
  name: string;
  control: Control<any>;
  label?: string;
  required?: boolean;
  entityTypes?: EntityType[];
  allowTypeSelection?: boolean;
  onEntityCreated?: (entity: any) => void;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
}

const getEntityIcon = (entityType: EntityType) => {
  switch (entityType) {
    case 'Customer':
      return <Person fontSize="small" />;
    case 'Vendor':
      return <Business fontSize="small" />;
    case 'Employee':
      return <Badge fontSize="small" />;
    case 'ExpenseAccount':
      return <AccountBalance fontSize="small" />;
    default:
      return <Person fontSize="small" />;
  }
};

const EntitySelector: React.FC<EntitySelectorProps> = ({
  name,
  control,
  label = 'Select Entity',
  required = false,
  entityTypes = ['Customer', 'Vendor'],
  allowTypeSelection = true,
  onEntityCreated,
  disabled = false,
  error = false,
  helperText
}) => {
  const [selectedEntityType, setSelectedEntityType] = useState<EntityType>(entityTypes[0]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addModalType, setAddModalType] = useState<'Customer' | 'Vendor'>('Customer');

  const { options, isLoading } = useEntityOptions(
    allowTypeSelection ? [selectedEntityType] : entityTypes
  );

  const handleAddNew = () => {
    if (selectedEntityType === 'Customer' || selectedEntityType === 'Vendor') {
      setAddModalType(selectedEntityType);
      setShowAddModal(true);
    } else {
      // For Employee and ExpenseAccount, we can add these modals later
      alert(`Create ${selectedEntityType} functionality will be implemented soon`);
    }
  };

  const handleEntityCreated = async (newEntity: any) => {
    setShowAddModal(false);
    if (onEntityCreated) {
      onEntityCreated(newEntity);
    }
  };

  // Enhanced options with "Add New" option
  const enhancedOptions = [
    ...options,
    {
      id: -1,
      name: `Add New ${selectedEntityType}...`,
      type: selectedEntityType,
      label: `Add New ${selectedEntityType}...`,
      value: -1,
      originalData: null
    } as EntityOption
  ];

  return (
    <Box>
      <Box display="flex" gap={1} alignItems="flex-start">
        {/* Entity Type Selector */}
        {allowTypeSelection && entityTypes.length > 1 && (
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={selectedEntityType}
              onChange={(e) => setSelectedEntityType(e.target.value as EntityType)}
              label="Type"
              disabled={disabled}
            >
              {entityTypes.map((type) => (
                <MenuItem key={type} value={type}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {getEntityIcon(type)}
                    {ENTITY_CONFIGS[type].displayName}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {/* Entity Selector */}
        <Box flex={1}>
          <Controller
            name={name}
            control={control}
            rules={{ required: required ? `${label} is required` : false }}
            render={({ field }) => (
              <Autocomplete
                {...field}
                options={enhancedOptions}
                getOptionLabel={(option) => 
                  typeof option === 'string' ? option : (option?.label || '')
                }
                renderOption={(props, option) => (
                  <Box component="li" {...props}>
                    <Box display="flex" alignItems="center" gap={1} width="100%">
                      {option.id === -1 ? (
                        <>
                          <Add fontSize="small" color="primary" />
                          <Typography color="primary" fontWeight="bold">
                            {option.label}
                          </Typography>
                        </>
                      ) : (
                        <>
                          {getEntityIcon(option.type)}
                          <Box>
                            <Typography variant="body2">
                              {option.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {option.type}
                            </Typography>
                          </Box>
                        </>
                      )}
                    </Box>
                  </Box>
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      {...getTagProps({ index })}
                      key={option.id}
                      label={option.name}
                      size="small"
                      color={option.type === 'Customer' ? 'success' : 'primary'}
                    />
                  ))
                }
                onChange={(_, newValue) => {
                  if (newValue && newValue.id === -1) {
                    handleAddNew();
                    return;
                  }
                  field.onChange(newValue);
                }}
                loading={isLoading}
                disabled={disabled}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label={label}
                    required={required}
                    error={error}
                    helperText={helperText}
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: (
                        <InputAdornment position="start">
                          {getEntityIcon(selectedEntityType)}
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <>
                          {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                isOptionEqualToValue={(option, value) => option.id === value?.id}
              />
            )}
          />
        </Box>
      </Box>

      {/* Add Entity Modals */}
      {addModalType === 'Customer' && (
        <AddCustomerModal
          open={showAddModal}
          onClose={() => setShowAddModal(false)}
          onAdd={handleEntityCreated}
        />
      )}
      
      {addModalType === 'Vendor' && (
        <AddVendorModal
          open={showAddModal}
          onClose={() => setShowAddModal(false)}
          onAdd={handleEntityCreated}
        />
      )}
    </Box>
  );
};

export default EntitySelector;