// frontend/src/services/ledgerService.ts
import api from '../utils/api';

export const getEntityBalance = async (entityType: string, entityId: string): Promise<number> => {
  if (!entityType || !entityId) {
    console.error('entityType and entityId are required');
    return 0;
  }
  try {
    console.log(`Fetching entity balance for ${entityType}/${entityId}`);
    const response = await api.get('/ledger/outstanding', {
      params: {
        account_type: entityType.toLowerCase(),
        account_id: entityId,
      },
    });
    console.log('Entity balance response:', response.data);
    const balance = response.data.outstanding_balances.find(
      (b: any) => b.account_type === entityType.toLowerCase() && b.account_id === parseInt(entityId)
    );
    if (!balance) {
      console.warn(`No balance found for ${entityType}/${entityId}`);
      return 0;
    }
    return balance.outstanding_amount;
  } catch (error: any) {
    console.error(`Error fetching entity balance for ${entityType}/${entityId}:`, {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });
    return 0;
  }
};

export const getVoucherBalance = async (voucherReference: string): Promise<number> => {
  if (!voucherReference) {
    console.error('voucherReference is required');
    return 0;
  }
  try {
    console.log(`Fetching voucher balance for ${voucherReference}`);
    const response = await api.get(`/vouchers/balance/${voucherReference}`);
    console.log('Voucher balance response:', response.data);
    return response.data.outstanding || 0;
  } catch (error) {
    console.error('Error fetching voucher balance:', error);
    return 0;
  }
};