import React, { ReactNode } from 'react';
import { Box, Typography, IconButton, Divider, useTheme } from '@mui/material';
import { ChevronRight, MoreVert } from '@mui/icons-material';
import { useMobileDetection } from '../../hooks/useMobileDetection';

interface MobileTableColumn {
  key: string;
  label: string;
  render?: (value: any, row: any) => ReactNode;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface MobileTableRow {
  id: string | number;
  [key: string]: any;
}

interface MobileTableProps {
  columns: MobileTableColumn[];
  data: MobileTableRow[];
  onRowClick?: (row: MobileTableRow) => void;
  onRowAction?: (row: MobileTableRow) => void;
  showRowActions?: boolean;
  showChevron?: boolean;
  emptyMessage?: string;
  loading?: boolean;
  className?: string;
}

const MobileTable: React.FC<MobileTableProps> = ({
  columns,
  data,
  onRowClick,
  onRowAction,
  showRowActions = false,
  showChevron = true,
  emptyMessage = 'No data available',
  loading = false,
  className = '',
}) => {
  const theme = useTheme();
  const { isMobile } = useMobileDetection();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 200,
          backgroundColor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <Typography color="text.secondary">Loading...</Typography>
      </Box>
    );
  }

  if (data.length === 0) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: 200,
          backgroundColor: 'background.paper',
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Typography color="text.secondary">{emptyMessage}</Typography>
      </Box>
    );
  }

  if (!isMobile) {
    // Desktop table fallback - use existing table component
    return (
      <Box className={className}>
        {/* Desktop table implementation can be added here */}
        <Typography>Desktop table not implemented in mobile component</Typography>
      </Box>
    );
  }

  return (
    <Box
      className={`mobile-table ${className}`}
      sx={{
        backgroundColor: 'background.paper',
        borderRadius: 2,
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {data.map((row, index) => (
        <Box key={row.id || index}>
          <Box
            className="mobile-table-row"
            onClick={() => onRowClick?.(row)}
            sx={{
              padding: 2,
              cursor: onRowClick ? 'pointer' : 'default',
              '&:active': onRowClick ? {
                backgroundColor: 'action.hover',
              } : {},
              transition: 'background-color 0.2s ease',
            }}
          >
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
              }}
            >
              {columns.map((column) => {
                const value = row[column.key];
                const displayValue = column.render ? column.render(value, row) : value;

                return (
                  <Box
                    key={column.key}
                    className="mobile-table-cell"
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      minHeight: 24,
                    }}
                  >
                    <Typography
                      className="mobile-table-label"
                      variant="body2"
                      sx={{
                        color: 'text.secondary',
                        fontWeight: 500,
                        minWidth: '30%',
                        fontSize: '0.875rem',
                      }}
                    >
                      {column.label}:
                    </Typography>
                    <Box
                      className="mobile-table-value"
                      sx={{
                        flex: 1,
                        textAlign: column.align || 'right',
                        marginLeft: 2,
                      }}
                    >
                      {typeof displayValue === 'string' || typeof displayValue === 'number' ? (
                        <Typography
                          variant="body2"
                          sx={{
                            color: 'text.primary',
                            fontSize: '1rem',
                            fontWeight: column.key === columns[0].key ? 600 : 400,
                          }}
                        >
                          {displayValue}
                        </Typography>
                      ) : (
                        displayValue
                      )}
                    </Box>
                  </Box>
                );
              })}
            </Box>

            {(showRowActions || showChevron) && (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  alignItems: 'center',
                  marginTop: 1,
                  gap: 1,
                }}
              >
                {showRowActions && onRowAction && (
                  <IconButton
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRowAction(row);
                    }}
                    sx={{
                      padding: 1,
                      minWidth: 36,
                      minHeight: 36,
                    }}
                  >
                    <MoreVert fontSize="small" />
                  </IconButton>
                )}
                {showChevron && onRowClick && (
                  <IconButton
                    size="small"
                    sx={{
                      padding: 1,
                      minWidth: 36,
                      minHeight: 36,
                    }}
                  >
                    <ChevronRight fontSize="small" />
                  </IconButton>
                )}
              </Box>
            )}
          </Box>
          {index < data.length - 1 && <Divider />}
        </Box>
      ))}
    </Box>
  );
};

export default MobileTable;