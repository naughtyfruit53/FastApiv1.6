// src/hooks/useEntity.ts
// React hooks for Entity abstraction system

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import {
  getAllEntities,
  getEntitiesByType,
  searchEntities,
  getEntityById,
  createEntity,
  updateEntity,
  deleteEntity,
  getEntityBalance,
  entitiesToOptions
} from '../services/entityService';
import { Entity, EntityType, EntityOption } from '../types/entity.types';

/**
 * Hook to get all entities with unified interface
 */
export const useEntities = (entityTypes: EntityType[] = ['Customer', 'Vendor']) => {
  return useQuery({
    queryKey: ['entities', entityTypes],
    queryFn: ({ signal }) => {
      if (entityTypes.length === 1) {
        return getEntitiesByType(entityTypes[0], { signal });
      }
      return getAllEntities({ signal });
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook to get entity options for form dropdowns
 */
export const useEntityOptions = (entityTypes: EntityType[] = ['Customer', 'Vendor']) => {
  const { data: entities, ...queryProps } = useEntities(entityTypes);
  
  const options: EntityOption[] = entities ? entitiesToOptions(entities) : [];
  
  return {
    options,
    entities,
    ...queryProps
  };
};

/**
 * Hook for entity search with debouncing
 */
export const useEntitySearch = (
  searchTerm: string,
  entityTypes: EntityType[] = ['Customer', 'Vendor'],
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ['entitySearch', searchTerm, entityTypes],
    queryFn: ({ signal }) => searchEntities(searchTerm, entityTypes, { signal }),
    enabled: enabled && searchTerm.length >= 2,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

/**
 * Hook to get specific entity by ID and type
 */
export const useEntity = (id: number | null, entityType: EntityType | null) => {
  return useQuery({
    queryKey: ['entity', id, entityType],
    queryFn: ({ signal }) => {
      if (!id || !entityType) return null;
      return getEntityById(id, entityType, { signal });
    },
    enabled: !!id && !!entityType,
  });
};

/**
 * Hook for entity balance/outstanding amount
 */
export const useEntityBalance = (id: number | null, entityType: EntityType | null) => {
  return useQuery({
    queryKey: ['entityBalance', id, entityType],
    queryFn: ({ signal }) => {
      if (!id || !entityType) return null;
      return getEntityBalance(id, entityType, { signal });
    },
    enabled: !!id && !!entityType && ['Customer', 'Vendor'].includes(entityType),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

/**
 * Hook for entity mutations (create, update, delete)
 */
export const useEntityMutations = () => {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: ({ entityType, data }: { entityType: EntityType; data: Partial<Entity> }) =>
      createEntity(entityType, data),
    onSuccess: (_, { entityType }) => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      queryClient.invalidateQueries({ queryKey: ['entities', [entityType]] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, entityType, data }: { id: number; entityType: EntityType; data: Partial<Entity> }) =>
      updateEntity(id, entityType, data),
    onSuccess: (_, { entityType }) => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      queryClient.invalidateQueries({ queryKey: ['entities', [entityType]] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: ({ id, entityType }: { id: number; entityType: EntityType }) =>
      deleteEntity(id, entityType),
    onSuccess: (_, { entityType }) => {
      queryClient.invalidateQueries({ queryKey: ['entities'] });
      queryClient.invalidateQueries({ queryKey: ['entities', [entityType]] });
    },
  });

  return {
    createEntity: createMutation,
    updateEntity: updateMutation,
    deleteEntity: deleteMutation,
  };
};

/**
 * Hook for entity form state management
 */
export const useEntityForm = (initialEntityType: EntityType = 'Customer') => {
  const [selectedEntityType, setSelectedEntityType] = useState<EntityType>(initialEntityType);
  const [selectedEntityId, setSelectedEntityId] = useState<number | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const { options, isLoading } = useEntityOptions([selectedEntityType]);
  const { data: searchResults, isLoading: searchLoading } = useEntitySearch(
    searchTerm,
    [selectedEntityType],
    searchTerm.length >= 2
  );

  const displayOptions = searchTerm.length >= 2 ? (searchResults || []) : options;

  const handleEntitySelect = (entityOption: EntityOption | null) => {
    if (entityOption) {
      setSelectedEntityId(entityOption.id);
      setSelectedEntityType(entityOption.type);
    } else {
      setSelectedEntityId(null);
    }
  };

  const handleEntityTypeChange = (newType: EntityType) => {
    setSelectedEntityType(newType);
    setSelectedEntityId(null); // Reset selection when type changes
    setSearchTerm(''); // Reset search
  };

  return {
    // State
    selectedEntityType,
    selectedEntityId,
    showCreateModal,
    searchTerm,

    // Options
    options: displayOptions,
    isLoading: isLoading || searchLoading,

    // Handlers
    setSelectedEntityType: handleEntityTypeChange,
    setSelectedEntityId,
    setShowCreateModal,
    setSearchTerm,
    handleEntitySelect,
  };
};

/**
 * Legacy compatibility hooks
 */
export const useVendors = () => useEntities(['Vendor']);
export const useCustomers = () => useEntities(['Customer']);