import apiClient from './api/client';

interface InventoryItem {
  id: string;
  name: string;
  category: string;
  stock: number;
  minStock: number;
  status: 'In Stock' | 'Low Stock' | 'Out of Stock';
  price: string;
  // Add more fields as needed from actual API
}

const inventoryService = {
  async getInventoryItems(organizationId: number, params: { search?: string; page?: number; limit?: number } = {}): Promise<{ items: InventoryItem[]; total: number }> {
    try {
      const response = await apiClient.get(`/organizations/${organizationId}/inventory`, {
        params,
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching inventory items:', error);
      throw error;
    }
  },

  async getLowStockAlerts(organizationId: number): Promise<InventoryItem[]> {
    try {
      const response = await apiClient.get(`/organizations/${organizationId}/inventory/low-stock`);
      return response.data;
    } catch (error) {
      console.error('Error fetching low stock alerts:', error);
      throw error;
    }
  },

  async addStockItem(organizationId: number, item: Partial<InventoryItem>): Promise<InventoryItem> {
    try {
      const response = await apiClient.post(`/organizations/${organizationId}/inventory`, item);
      return response.data;
    } catch (error) {
      console.error('Error adding stock item:', error);
      throw error;
    }
  },

  // Add more methods as needed (e.g., updateItem, deleteItem, adjustStock)
};

export default inventoryService;