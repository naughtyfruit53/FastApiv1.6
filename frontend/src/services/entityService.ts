// src/services/entityService.ts
// Unified Entity service for Customer + Vendor + Employee + ExpenseAccount management

import api from '../lib/api';
import { Entity, EntityType, EntityOption, ENTITY_CONFIGS, Customer, Vendor, Employee, ExpenseAccount } from '../types/entity.types';

interface QueryFunctionContext {
  queryKey: any[];
  signal?: AbortSignal;
}

/**
 * Get all entities of a specific type
 */
export const getEntitiesByType = async (entityType: EntityType, { signal }: { signal?: AbortSignal } = {}) => {
  const config = ENTITY_CONFIGS[entityType];
  const response = await api.get(config.endpoint, { signal });
  return response.data.map((entity: any) => ({
    ...entity,
    type: entityType
  }));
};

/**
 * Get all entities across all types (unified)
 */
export const getAllEntities = async ({ signal }: { signal?: AbortSignal } = {}): Promise<Entity[]> => {
  try {
    const [customers, vendors] = await Promise.all([
      getEntitiesByType('Customer', { signal }).catch(() => []),
      getEntitiesByType('Vendor', { signal }).catch(() => [])
      // Future: Add Employee and ExpenseAccount when endpoints are available
      // getEntitiesByType('Employee', { signal }).catch(() => []),
      // getEntitiesByType('ExpenseAccount', { signal }).catch(() => [])
    ]);

    return [...customers, ...vendors];
  } catch (error) {
    console.error('Error fetching entities:', error);
    return [];
  }
};

/**
 * Convert entities to form-compatible options
 */
export const entitiesToOptions = (entities: Entity[]): EntityOption[] => {
  return entities.map(entity => ({
    id: entity.id,
    name: entity.name,
    type: entity.type,
    label: `${entity.name} (${entity.type})`,
    value: entity.id,
    originalData: entity
  }));
};

/**
 * Search entities across all types
 */
export const searchEntities = async (
  searchTerm: string, 
  entityTypes: EntityType[] = ['Customer', 'Vendor'],
  { signal }: { signal?: AbortSignal } = {}
): Promise<EntityOption[]> => {
  try {
    const searchPromises = entityTypes.map(async (type) => {
      const config = ENTITY_CONFIGS[type];
      const response = await api.get(config.endpoint, {
        params: {
          search: searchTerm,
          limit: 10,
          active_only: true
        },
        signal
      });
      return response.data.map((entity: any) => ({
        ...entity,
        type
      }));
    });

    const results = await Promise.all(searchPromises);
    const allEntities = results.flat();
    return entitiesToOptions(allEntities);
  } catch (error) {
    console.error('Error searching entities:', error);
    return [];
  }
};

/**
 * Get entity by ID and type
 */
export const getEntityById = async (
  id: number, 
  entityType: EntityType,
  { signal }: { signal?: AbortSignal } = {}
): Promise<Entity | null> => {
  try {
    const config = ENTITY_CONFIGS[entityType];
    const response = await api.get(`${config.endpoint}/${id}`, { signal });
    return {
      ...response.data,
      type: entityType
    };
  } catch (error) {
    console.error(`Error fetching ${entityType} with ID ${id}:`, error);
    return null;
  }
};

/**
 * Create new entity
 */
export const createEntity = async (
  entityType: EntityType,
  data: Partial<Entity>
): Promise<Entity> => {
  const config = ENTITY_CONFIGS[entityType];
  const response = await api.post(config.endpoint, data);
  return {
    ...response.data,
    type: entityType
  };
};

/**
 * Update existing entity
 */
export const updateEntity = async (
  id: number,
  entityType: EntityType,
  data: Partial<Entity>
): Promise<Entity> => {
  const config = ENTITY_CONFIGS[entityType];
  const response = await api.put(`${config.endpoint}/${id}`, data);
  return {
    ...response.data,
    type: entityType
  };
};

/**
 * Delete entity
 */
export const deleteEntity = async (
  id: number,
  entityType: EntityType
): Promise<void> => {
  const config = ENTITY_CONFIGS[entityType];
  await api.delete(`${config.endpoint}/${id}`);
};

/**
 * Get entity balance/outstanding amount
 */
export const getEntityBalance = async (
  id: number,
  entityType: EntityType,
  { signal }: { signal?: AbortSignal } = {}
) => {
  try {
    const params = entityType === 'Customer' ? { customer_id: id } : { vendor_id: id };
    const response = await api.get('/reports/outstanding-ledger', {
      params,
      signal
    });
    
    const balances = response.data?.outstanding_balances || [];
    return balances.find((balance: any) => 
      (entityType === 'Customer' && balance.customer_id === id) ||
      (entityType === 'Vendor' && balance.vendor_id === id)
    );
  } catch (error) {
    console.error(`Error fetching balance for ${entityType} ${id}:`, error);
    return null;
  }
};

// Legacy compatibility functions (to maintain existing code)
export const getVendors = ({ signal }: QueryFunctionContext = { queryKey: [] }) => 
  getEntitiesByType('Vendor', { signal });

export const getCustomers = ({ signal }: QueryFunctionContext = { queryKey: [] }) => 
  getEntitiesByType('Customer', { signal });