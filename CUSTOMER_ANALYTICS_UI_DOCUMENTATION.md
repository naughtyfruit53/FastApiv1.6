# Customer Analytics UI Components

## Overview
The Customer Analytics module provides a comprehensive interface for viewing customer insights and metrics directly from the customer management page.

## UI Components

### 1. Customer Analytics Button
- **Location**: Customers page (`/masters/customers`)
- **Icon**: Analytics icon (📊)
- **Action**: Opens Customer Analytics Modal
- **Styling**: Material-UI info-colored IconButton

### 2. Customer Analytics Modal
- **Type**: Full-width dialog modal
- **Size**: Large (lg) with 90vh height
- **Features**:
  - Responsive design
  - Scrollable content
  - Close button in header
  - Action buttons in footer

### 3. Customer Analytics Component

#### Header Section
```
📊 Customer Analytics
   [Customer Name]
```

#### Control Panel
```
☐ Show Recent Interactions    [Recent Interactions Limit: 5]
```

#### Summary Cards (4 cards in a row)
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 📈 Total Inter. │ │ 📅 Last Inter.  │ │ 📁 Active Segm. │ │ 📊 Inter. Types │
│     25          │ │   Jan 15, 2024  │ │      2          │ │      4          │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └─────────────────┘
```

#### Interaction Breakdown (2 cards side by side)
```
┌─────────────────────────────┐ ┌─────────────────────────────┐
│ Interaction Types           │ │ Interaction Status          │
│                             │ │                             │
│ CALL        [blue]     8    │ │ COMPLETED   [green]    18   │
│ EMAIL       [purple]  12    │ │ PENDING     [orange]    4   │
│ MEETING     [green]    3    │ │ IN_PROGRESS [blue]      3   │
│ SUPPORT     [orange]   2    │ │                             │
└─────────────────────────────┘ └─────────────────────────────┘
```

#### Customer Segments Table
```
┌────────────────────────────────────────────────────────────────────────┐
│ Customer Segments                                                      │
├─────────────┬─────────────┬─────────────────┬─────────────────────────┤
│ Segment     │ Value       │ Assigned Date   │ Description             │
├─────────────┼─────────────┼─────────────────┼─────────────────────────┤
│ [PREMIUM]   │ 250.00      │ Jan 01, 2024    │ Premium tier customer   │
│ [HIGH_VAL]  │ 500.00      │ Jan 05, 2024    │ High-value customer     │
└─────────────┴─────────────┴─────────────────┴─────────────────────────┘
```

#### Recent Interactions Table (if enabled)
```
┌─────────────────────────────────────────────────────────────────────────┐
│ Recent Interactions                                                     │
├────────────┬──────────────────────┬─────────────┬─────────────────────┤
│ Type       │ Subject              │ Status      │ Date                │
├────────────┼──────────────────────┼─────────────┼─────────────────────┤
│ [CALL]     │ Product inquiry      │ [COMPLETED] │ Jan 15, 2024        │
│ [EMAIL]    │ Follow-up email      │ [COMPLETED] │ Jan 14, 2024        │
│ [MEETING]  │ Product demo         │ [PENDING]   │ Jan 13, 2024        │
└────────────┴──────────────────────┴─────────────┴─────────────────────┘
```

#### Footer
```
Analytics calculated at: Jan 16, 2024, 12:00 PM
```

## Color Coding

### Interaction Types
- **CALL**: Blue chip
- **EMAIL**: Purple chip  
- **MEETING**: Green chip
- **SUPPORT_TICKET**: Orange chip
- **COMPLAINT**: Red chip
- **FEEDBACK**: Info blue chip

### Interaction Status
- **PENDING**: Orange chip
- **IN_PROGRESS**: Info blue chip
- **COMPLETED**: Green chip
- **CANCELLED**: Red chip

### Segments
- All segments use primary blue chips

## Responsive Design
- **Desktop**: 4 summary cards per row
- **Tablet**: 2 summary cards per row  
- **Mobile**: 1 summary card per row
- Tables are horizontally scrollable on small screens
- Modal adjusts height based on viewport

## Interactive Features
- **Toggle Controls**: Show/hide recent interactions
- **Configurable Limits**: Adjust number of recent interactions (1-20)
- **Real-time Updates**: Data refreshes automatically via React Query
- **Loading States**: Circular progress indicator during data fetch
- **Error Handling**: User-friendly error messages
- **Empty States**: Informative messages when no data available

## Integration Points
- **Customer List**: Analytics button in actions column
- **API Integration**: Uses analyticsService for data fetching
- **State Management**: React Query for caching and synchronization
- **Theme Integration**: Uses Material-UI theme colors and typography

## Technical Implementation
- **React + TypeScript**: Type-safe component implementation
- **Material-UI**: Consistent design system
- **React Query**: Efficient data fetching and caching
- **Responsive Grid**: CSS Grid and Flexbox for layouts
- **Accessibility**: ARIA labels and keyboard navigation support

## Usage Flow
1. User navigates to Customers page
2. User clicks Analytics (📊) button next to a customer
3. Modal opens showing comprehensive analytics
4. User can configure display options
5. User views detailed metrics and insights
6. User closes modal to return to customer list

This UI provides a comprehensive yet intuitive interface for viewing customer analytics without leaving the customer management workflow.