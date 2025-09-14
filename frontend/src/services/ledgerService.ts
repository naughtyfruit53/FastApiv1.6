// frontend/src/services/ledgerService.ts
import api from '../lib/api';

export const getEntityBalance = async (entityType: string, entityId: string): Promise<number> => {
  try {
    console.log(`Fetching entity balance for ${entityType}/${entityId}`);
    const response = await api.get(`/balances/${entityType.toLowerCase()}/${entityId}`);
    console.log('Entity balance response:', response.data);
    return response.data.balance || 0;
  } catch (error) {
    console.error('Error fetching entity balance:', error);
    return 0;
  }
};

export const getVoucherBalance = async (voucherReference: string): Promise<number> => {
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