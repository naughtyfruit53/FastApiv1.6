import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useOrganization } from '../context/OrganizationContext';
import inventoryService from '../services/inventoryService';

export const useInventory = (params: { search?: string; page?: number; limit?: number } = {}) => {
  const queryClient = useQueryClient();
  const { currentOrganization } = useOrganization();

  const { data: inventoryData, isLoading: loadingInventory, error: errorInventory } = useQuery({
    queryKey: ['inventory', currentOrganization?.id, params],
    queryFn: () => inventoryService.getInventoryItems(currentOrganization?.id || 0, params),
    enabled: !!currentOrganization?.id,
  });

  const { data: lowStockAlerts, isLoading: loadingAlerts } = useQuery({
    queryKey: ['lowStockAlerts', currentOrganization?.id],
    queryFn: () => inventoryService.getLowStockAlerts(currentOrganization?.id || 0),
    enabled: !!currentOrganization?.id,
  });

  const addItemMutation = useMutation({
    mutationFn: (item: Partial<InventoryItem>) => inventoryService.addStockItem(currentOrganization?.id || 0, item),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
      queryClient.invalidateQueries({ queryKey: ['lowStockAlerts'] });
    },
  });

  return {
    items: inventoryData?.items || [],
    total: inventoryData?.total || 0,
    lowStockAlerts: lowStockAlerts || [],
    loading: loadingInventory || loadingAlerts,
    error: errorInventory,
    addItem: addItemMutation.mutate,
    // Add more mutations as needed
  };
};