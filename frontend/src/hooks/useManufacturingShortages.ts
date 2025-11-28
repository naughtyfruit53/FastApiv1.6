// frontend/src/hooks/useManufacturingShortages.ts
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../lib/api";

interface ShortageItem {
  product_id: number;
  product_name: string;
  required: number;
  available: number;
  shortage: number;
  unit: string;
  severity?: "no_po" | "po_no_dispatch" | "po_dispatch_grn_pending";
  purchase_order_status?: {
    has_order: boolean;
    on_order_quantity: number;
    orders: Array<{
      po_number: string;
      po_id: number;
      quantity: number;
      status: string;
      delivery_date?: string;
      has_dispatch: boolean;
      grn_status: string;
    }>;
  };
}

interface Recommendation {
  type: "critical" | "warning" | "success" | "info";
  message: string;
  action: string;
}

interface ShortageCheckResponse {
  manufacturing_order_id: number;
  voucher_number: string;
  production_status: string;
  is_material_available: boolean;
  total_shortage_items: number;
  critical_items: number;
  warning_items: number;
  shortages: ShortageItem[];
  recommendations: Recommendation[];
}

export const useManufacturingShortages = (moId?: number | null) => {
  const [showShortageDialog, setShowShortageDialog] = useState(false);

  const {
    data: shortageData,
    isLoading,
    error,
    refetch,
  } = useQuery<ShortageCheckResponse>({
    queryKey: ["manufacturing-shortages", moId],
    queryFn: async () => {
      if (!moId) throw new Error("No manufacturing order ID provided");
      const response = await api.get(
        `/manufacturing/manufacturing-orders/${moId}/check-shortages`,
      );
      return response.data;
    },
    enabled: false, // Only fetch when explicitly called
  });

  const checkShortages = async () => {
    if (!moId) {
      throw new Error("No manufacturing order ID provided");
    }
    const result = await refetch();
    return result.data;
  };

  const hasShortages = shortageData
    ? !shortageData.is_material_available
    : false;
  const hasCriticalShortages = shortageData
    ? shortageData.critical_items > 0
    : false;

  return {
    shortageData,
    isLoading,
    error,
    checkShortages,
    hasShortages,
    hasCriticalShortages,
    showShortageDialog,
    setShowShortageDialog,
  };
};

export default useManufacturingShortages;
