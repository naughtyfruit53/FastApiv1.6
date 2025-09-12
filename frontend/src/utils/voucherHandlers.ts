// src/utils/voucherHandlers.ts
// Utility functions for common voucher handlers (submit, duplicate, etc.).
import api from '../lib/api'; // Adjust path
import { toast } from 'react-toastify';

export const handleFinalSubmit = async (
  data: any,
  watch: any,
  computedItems: any[],
  isIntrastate: boolean,
  totalAmount: number,
  totalRoundOff: number,
  lineDiscountEnabled: boolean,
  lineDiscountType: string,
  totalDiscountEnabled: boolean,
  totalDiscountType: string,
  createMutation: any,
  updateMutation: any,
  mode: string,
  handleGeneratePDF: (response: any) => void,
  refreshMasterData: () => void,
  config: any
) => {
  if (!data.vendor_id) {
    toast.error("Please select a vendor");
    return;
  }

  const validItems = data.items.filter((item: any) => item.product_id && item.quantity > 0);
  if (validItems.length === 0) {
    toast.error("Please add at least one valid product with quantity");
    return;
  }

  data.items = validItems;

  if (config.hasItems !== false) {
    data.line_discount_type = lineDiscountEnabled ? lineDiscountType : null;
    data.total_discount_type = totalDiscountEnabled ? totalDiscountType : null;
    data.total_discount = watch('total_discount') || 0;
    data.items = computedItems.map((item: any) => ({
      ...item,
      cgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
      sgst_rate: isIntrastate ? item.gst_rate / 2 : 0,
      igst_rate: isIntrastate ? 0 : item.gst_rate,
    }));
    data.total_amount = totalAmount;
    data.is_intrastate = isIntrastate;
    data.round_off = totalRoundOff;
  }

  const itemsToUpdate = data.items.filter(
    (item: any) => item.unit_price !== item.original_unit_price && item.product_id
  );
  if (itemsToUpdate.length > 0) {
    if (confirm(`Some items have updated prices. Update master product prices for ${itemsToUpdate.length} items?`)) {
      await Promise.all(
        itemsToUpdate.map((item: any) =>
          api.put(`/products/${item.product_id}`, { unit_price: item.unit_price })
        )
      );
      refreshMasterData();
    }
  }

  data.items = data.items.map(({ original_unit_price, ...item }: any) => item);

  let response;
  if (mode === "create") {
    response = await createMutation.mutateAsync(data);
    if (confirm("Voucher created successfully. Generate PDF?")) {
      handleGeneratePDF(response);
    }
  } else if (mode === "edit") {
    response = await updateMutation.mutateAsync(data);
    if (confirm("Voucher updated successfully. Generate PDF?")) {
      handleGeneratePDF(response);
    }
  }
};

export const handleDuplicate = async (
  id: number,
  voucherList: any[],
  reset: (data: any) => void,
  setMode: (mode: string) => void,
  voucherType: string
) => {
  try {
    const voucher = voucherList?.find((v) => v.id === id);
    if (!voucher) return;
    reset({
      ...voucher,
      voucher_number: "",
      date: new Date().toISOString().split("T")[0],
      created_at: undefined,
      updated_at: undefined,
      id: undefined,
    });
    setMode("create");
    toast.success(`${voucherType} duplicated successfully`);
  } catch (err) {
    console.error(`Error duplicating ${voucherType.toLowerCase()}:`, err);
    toast.error(`Failed to duplicate ${voucherType.toLowerCase()}`);
  }
};

export const getStockColor = (stock: number, reorder: number) => {
  if (stock === 0) return "error.main";
  if (stock <= reorder) return "warning.main";
  return "success.main";
};