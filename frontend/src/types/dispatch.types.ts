// frontend/src/types/dispatch.types.ts

export const DISPATCH_ORDER_STATUSES = {
  PENDING: 'pending',
  IN_TRANSIT: 'in_transit',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled'
} as const;

export const DISPATCH_ITEM_STATUSES = {
  PENDING: 'pending',
  PACKED: 'packed',
  DISPATCHED: 'dispatched',
  DELIVERED: 'delivered'
} as const;

export const INSTALLATION_JOB_STATUSES = {
  SCHEDULED: 'scheduled',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
  RESCHEDULED: 'rescheduled'
} as const;

export const INSTALLATION_JOB_PRIORITIES = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent'
} as const;

export type DispatchOrderStatus = typeof DISPATCH_ORDER_STATUSES[keyof typeof DISPATCH_ORDER_STATUSES];
export type DispatchItemStatus = typeof DISPATCH_ITEM_STATUSES[keyof typeof DISPATCH_ITEM_STATUSES];
export type InstallationJobStatus = typeof INSTALLATION_JOB_STATUSES[keyof typeof INSTALLATION_JOB_STATUSES];
export type InstallationJobPriority = typeof INSTALLATION_JOB_PRIORITIES[keyof typeof INSTALLATION_JOB_PRIORITIES];

// Status display configurations
export const DISPATCH_ORDER_STATUS_CONFIG = {
  [DISPATCH_ORDER_STATUSES.PENDING]: {
    label: 'Pending',
    color: 'warning',
    icon: 'pending'
  },
  [DISPATCH_ORDER_STATUSES.IN_TRANSIT]: {
    label: 'In Transit',
    color: 'info',
    icon: 'local_shipping'
  },
  [DISPATCH_ORDER_STATUSES.DELIVERED]: {
    label: 'Delivered',
    color: 'success',
    icon: 'check_circle'
  },
  [DISPATCH_ORDER_STATUSES.CANCELLED]: {
    label: 'Cancelled',
    color: 'error',
    icon: 'cancel'
  }
} as const;

export const INSTALLATION_JOB_STATUS_CONFIG = {
  [INSTALLATION_JOB_STATUSES.SCHEDULED]: {
    label: 'Scheduled',
    color: 'info',
    icon: 'schedule'
  },
  [INSTALLATION_JOB_STATUSES.IN_PROGRESS]: {
    label: 'In Progress',
    color: 'warning',
    icon: 'construction'
  },
  [INSTALLATION_JOB_STATUSES.COMPLETED]: {
    label: 'Completed',
    color: 'success',
    icon: 'check_circle'
  },
  [INSTALLATION_JOB_STATUSES.CANCELLED]: {
    label: 'Cancelled',
    color: 'error',
    icon: 'cancel'
  },
  [INSTALLATION_JOB_STATUSES.RESCHEDULED]: {
    label: 'Rescheduled',
    color: 'warning',
    icon: 'event_repeat'
  }
} as const;

export const INSTALLATION_JOB_PRIORITY_CONFIG = {
  [INSTALLATION_JOB_PRIORITIES.LOW]: {
    label: 'Low',
    color: 'success',
    icon: 'keyboard_arrow_down'
  },
  [INSTALLATION_JOB_PRIORITIES.MEDIUM]: {
    label: 'Medium',
    color: 'warning',
    icon: 'remove'
  },
  [INSTALLATION_JOB_PRIORITIES.HIGH]: {
    label: 'High',
    color: 'error',
    icon: 'keyboard_arrow_up'
  },
  [INSTALLATION_JOB_PRIORITIES.URGENT]: {
    label: 'Urgent',
    color: 'error',
    icon: 'priority_high'
  }
} as const;

// Permission checks for dispatch management
export const hasDispatchManagementPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager'];
  return allowedRoles.includes(userRole);
};

export const hasDispatchViewPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager', 'support', 'standard_user'];
  return allowedRoles.includes(userRole);
};

export const hasInstallationManagementPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager'];
  return allowedRoles.includes(userRole);
};

export const hasInstallationViewPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager', 'support', 'technician', 'standard_user'];
  return allowedRoles.includes(userRole);
};

// Additional permission checks for new functionality
export const hasTaskManagementPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager'];
  return allowedRoles.includes(userRole);
};

export const hasCompletionPermission = (userRole: string): boolean => {
  const allowedRoles = ['org_admin', 'admin', 'manager', 'technician'];
  return allowedRoles.includes(userRole);
};