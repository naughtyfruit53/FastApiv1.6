// src/types/entity.types.ts
// Entity abstraction types for unified Customer + Vendor interface

export type EntityType = 'Customer' | 'Vendor' | 'Employee' | 'ExpenseAccount';

export interface BaseEntity {
  id: number;
  name: string;
  type: EntityType;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  gst_number?: string;
  pan_number?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

export interface Customer extends Omit<BaseEntity, 'type'> {
  type: 'Customer';
  customer_type?: string;
  credit_limit?: number;
  payment_terms?: string;
}

export interface Vendor extends Omit<BaseEntity, 'type'> {
  type: 'Vendor';
  vendor_type?: string;
  credit_limit?: number;
  payment_terms?: string;
}

export interface Employee extends Omit<BaseEntity, 'type'> {
  type: 'Employee';
  employee_id?: string;
  department?: string;
  designation?: string;
  salary?: number;
}

export interface ExpenseAccount extends Omit<BaseEntity, 'type'> {
  type: 'ExpenseAccount';
  account_code?: string;
  account_category?: string;
  is_debit?: boolean;
}

export type Entity = Customer | Vendor | Employee | ExpenseAccount;

export interface EntityOption {
  id: number;
  name: string;
  type: EntityType;
  label: string; // Formatted display label
  value: number; // For form compatibility
  originalData: Entity | null; // Full entity data, null for "Add New" options
}

export interface EntityConfig {
  type: EntityType;
  endpoint: string;
  displayName: string;
  color: string;
  icon?: string;
}

export const ENTITY_CONFIGS: Record<EntityType, EntityConfig> = {
  Customer: {
    type: 'Customer',
    endpoint: '/customers',
    displayName: 'Customer',
    color: '#2E7D32',
    icon: 'person'
  },
  Vendor: {
    type: 'Vendor', 
    endpoint: '/vendors',
    displayName: 'Vendor',
    color: '#1976D2',
    icon: 'business'
  },
  Employee: {
    type: 'Employee',
    endpoint: '/employees',
    displayName: 'Employee', 
    color: '#F57C00',
    icon: 'badge'
  },
  ExpenseAccount: {
    type: 'ExpenseAccount',
    endpoint: '/expense-accounts',
    displayName: 'Expense Account',
    color: '#7B1FA2',
    icon: 'account_balance'
  }
};