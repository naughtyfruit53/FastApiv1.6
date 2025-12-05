// frontend/src/components/SortableTable.tsx
// SortableTable component for requirement #3 - Table Sorting on Header Click
import React, { useState, useMemo, useRef, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  Box,
  Typography,
  Tooltip,
} from "@mui/material";
import { visuallyHidden } from "@mui/utils";
export type Order = "asc" | "desc";
export interface HeadCell<T> {
  id: keyof T;
  label: string;
  numeric: boolean;
  disablePadding?: boolean;
  sortable?: boolean;
  width?: string | number;
  align?: "left" | "right" | "center";
  render?: (_value: any, _row: T) => React.ReactNode;
}
interface SortableTableProps<T> {
  data: T[];
  headCells: HeadCell<T>[];
  title?: string;
  defaultOrderBy?: keyof T;
  defaultOrder?: Order;
  onRowClick?: (_row: T) => void;
  onRowContextMenu?: (event: React.MouseEvent, row: T) => void; // NEW: Prop for right-click context menu on row
  onRequestSort?: (_property: keyof T) => void;
  dense?: boolean;
  stickyHeader?: boolean;
  maxHeight?: string | number;
  emptyMessage?: string;
  loading?: boolean;
  actions?: (_row: T) => React.ReactNode;
  rowSx?: (_row: T) => object;
}
export function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  const aVal = a[orderBy];
  const bVal = b[orderBy];
  // Handle null/undefined values
  if (bVal === null && aVal === null) {
    return 0;
  }
  if (bVal == null) {
    return -1;
  }
  if (aVal == null) {
    return 1;
  }
  // Handle different types
  if (typeof aVal === "number" && typeof bVal === "number") {
    return bVal - aVal;
  }
  if (typeof aVal === "string" && typeof bVal === "string") {
    return bVal.localeCompare(aVal, undefined, {
      numeric: true,
      sensitivity: "base",
    });
  }
  // Handle dates
  if (aVal instanceof Date && bVal instanceof Date) {
    return bVal.getTime() - aVal.getTime();
  }
  // Handle date strings
  if (typeof aVal === "string" && typeof bVal === "string") {
    const aDate = new Date(aVal);
    const bDate = new Date(bVal);
    if (!isNaN(aDate.getTime()) && !isNaN(bDate.getTime())) {
      return bDate.getTime() - aDate.getTime();
    }
  }
  // Default string comparison
  return String(bVal).localeCompare(String(aVal), undefined, {
    numeric: true,
    sensitivity: "base",
  });
}
export function getComparator<T>(
  order: Order,
  orderBy: keyof T,
): (_a: T, _b: T) => number {
  return order === "desc"
    ? (_a, _b) => descendingComparator(_a, _b, orderBy)
    : (_a, _b) => -descendingComparator(_a, _b, orderBy);
}
export function stableSort<T>(
  array: readonly T[],
  comparator: (_a: T, _b: T) => number,
) {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}
interface SortableTableHeadProps<T> {
  headCells: HeadCell<T>[];
  order: Order;
  orderBy: keyof T;
  onRequestSort: (_property: keyof T) => void;
  hasActions: boolean;
  widths: string[];
  setWidths: React.Dispatch<React.SetStateAction<string[]>>;
}
function SortableTableHead<T>(props: SortableTableHeadProps<T>) {
  const { headCells, order, orderBy, onRequestSort, hasActions, widths, setWidths } = props;
  const createSortHandler = (property: keyof T) => () => {
    onRequestSort(property);
  };

  const handleMouseDown = (index: number) => (e: React.MouseEvent) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = parseInt(widths[index], 10) || 150;

    const handleMouseMove = (e: MouseEvent) => {
      const diffX = e.clientX - startX;
      const newWidth = Math.max(50, startWidth + diffX); // Minimum width 50px
      const newWidths = [...widths];
      newWidths[index] = `${newWidth}px`;
      setWidths(newWidths);
    };

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <TableHead>
      <TableRow>
        {headCells.map((headCell, index) => (
          <TableCell
            key={String(headCell.id)}
            align={headCell.align || "center"}
            padding={headCell.disablePadding ? "none" : "normal"}
            sortDirection={orderBy === headCell.id ? order : false}
            sx={{
              fontWeight: "bold",
              width: widths[index],
              backgroundColor: "grey.50",
              padding: '4px 8px',
              fontSize: '0.875rem',
              position: 'relative',
              '& .resizer': {
                position: 'absolute',
                right: 0,
                top: 0,
                height: '100%',
                width: '5px',
                background: 'rgba(0, 0, 0, 0.2)',
                cursor: 'col-resize',
                userSelect: 'none',
                touchAction: 'none',
              },
              '& .resizer:hover': {
                background: 'blue',
              },
            }}
          >
            {headCell.sortable !== false ? (
              <TableSortLabel
                active={orderBy === headCell.id}
                direction={orderBy === headCell.id ? order : "asc"}
                onClick={createSortHandler(headCell.id)}
              >
                {headCell.label}
                {orderBy === headCell.id ? (
                  <Box component="span" sx={visuallyHidden}>
                    {order === "desc"
                      ? "sorted descending"
                      : "sorted ascending"}
                  </Box>
                ) : null}
              </TableSortLabel>
            ) : (
              headCell.label
            )}
            <Box 
              className="resizer" 
              onMouseDown={handleMouseDown(index)}
            />
          </TableCell>
        ))}
        {hasActions && (
          <TableCell
            align="center"
            sx={{ 
              fontWeight: "bold", 
              backgroundColor: "grey.50",
              width: widths[headCells.length],
              padding: '4px 8px',
              fontSize: '0.875rem',
              position: 'relative',
              '& .resizer': {
                position: 'absolute',
                right: 0,
                top: 0,
                height: '100%',
                width: '5px',
                background: 'rgba(0, 0, 0, 0.2)',
                cursor: 'col-resize',
                userSelect: 'none',
                touchAction: 'none',
              },
              '& .resizer:hover': {
                background: 'blue',
              },
            }}
          >
            <Box 
              className="resizer" 
              onMouseDown={handleMouseDown(headCells.length)}
            />
          </TableCell>
        )}
      </TableRow>
    </TableHead>
  );
}
function SortableTable<T>({
  data,
  headCells,
  title,
  defaultOrderBy,
  defaultOrder = "asc",
  onRowClick,
  onRowContextMenu, // NEW: Added to props
  onRequestSort,
  dense = false,
  stickyHeader = false,
  maxHeight,
  emptyMessage = "No data available",
  loading = false,
  actions,
  rowSx,
}: SortableTableProps<T>) {
  const [order, setOrder] = useState<Order>(defaultOrder);
  const [orderBy, setOrderBy] = useState<keyof T>(
    defaultOrderBy || headCells[0]?.id,
  );
  const [widths, setWidths] = useState<string[]>(
    headCells.map(headCell => headCell.width?.toString() || 'auto')
      .concat(actions ? ['auto'] : [])
  );

  const handleRequestSortInternal = (property: keyof T) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
    if (onRequestSort) {
      onRequestSort(property);
    }
  };

  const sortedData = useMemo(() => {
    if (!data?.length) {
      return [];
    }
    return stableSort(data, getComparator(order, orderBy));
  }, [data, order, orderBy]);
  const hasActions = Boolean(actions);
  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: "center" }}>
        <Typography>Loading...</Typography>
      </Paper>
    );
  }
  return (
    <Paper sx={{ width: "100%", mb: 2 }}>
      {title && (
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
        </Box>
      )}
      <TableContainer sx={{ maxHeight, overflowX: 'hidden' }}>
        <Table
          stickyHeader={stickyHeader}
          size={dense ? "small" : "medium"}
          aria-label="sortable table"
          sx={{ tableLayout: 'fixed', width: '100%' }}
        >
          <SortableTableHead
            headCells={headCells}
            order={order}
            orderBy={orderBy}
            onRequestSort={handleRequestSortInternal}
            hasActions={hasActions}
            widths={widths}
            setWidths={setWidths}
          />
          <TableBody>
            {sortedData.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={headCells.length + (hasActions ? 1 : 0)}
                  align="center"
                  sx={{ py: 3 }}
                >
                  <Typography color="textSecondary">{emptyMessage}</Typography>
                </TableCell>
              </TableRow>
            ) : (
              sortedData.map((row, index) => (
                <TableRow
                  hover={Boolean(onRowClick)}
                  onClick={onRowClick ? () => onRowClick(row) : undefined}
                  onContextMenu={onRowContextMenu ? (e) => onRowContextMenu(e, row) : undefined} // NEW: Attached to TableRow for right-click
                  key={index}
                  sx={{
                    cursor: onRowClick ? "pointer" : "default",
                    ...(rowSx ? rowSx(row) : {}),
                    '&:hover': onRowClick
                      ? { backgroundColor: "action.hover" }
                      : {},
                  }}
                >
                  {headCells.map((headCell, colIndex) => {
                    const cellValue = headCell.render
                      ? headCell.render(row[headCell.id], row)
                      : String(row[headCell.id] ?? "");
                    return (
                      <Tooltip title={cellValue} key={String(headCell.id)}>
                        <TableCell
                          align={headCell.align || "center"}
                          padding={headCell.disablePadding ? "none" : "normal"}
                          sx={{
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            width: widths[colIndex],
                          }}
                        >
                          {cellValue}
                        </TableCell>
                      </Tooltip>
                    );
                  })}
                  {hasActions && (
                    <TableCell 
                      align="center"
                      sx={{
                        padding: '4px 8px',
                        fontSize: '0.75rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        width: widths[headCells.length],
                      }}
                    >
                      {actions!(row)}
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}
export default SortableTable;
