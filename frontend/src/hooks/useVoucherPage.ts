// frontend/src/hooks/useVoucherPage.ts
import { useState, useCallback, useEffect, useMemo } from "react";
import { useRouter } from "next/router";
import { useForm, useFieldArray, useWatch } from "react-hook-form";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { voucherService } from "../services/vouchersService";
import {
  getVendors,
  getProducts,
  getCustomers,
  getEmployees,
} from "../services/masterService";
import { useAuth } from "../context/AuthContext";
import { useCompany } from "../context/CompanyContext";
import {
  calculateVoucherTotals,
  getDefaultVoucherValues,
  voucherListUtils,
  enhancedRateUtils,
  VOUCHER_PAGINATION_DEFAULTS,
  getAmountInWords,
} from "../utils/voucherUtils";
import { showErrorToast, showSuccessToast, handleVoucherError } from "../utils/errorHandling";
import { SUCCESS_MESSAGES, getDynamicMessage } from "../constants/messages";
import {
  generateStandalonePDF,
} from "../utils/pdfUtils";
import { VoucherPageConfig } from "../types/voucher.types";
import api from "../lib/api";

export const useVoucherPage = (config: VoucherPageConfig) => {
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const { isOrgContextReady } = useAuth();
  const { company } = useCompany();
  const queryClient = useQueryClient();
  console.log(
    "[useVoucherPage] Enhanced hook initialized for:",
    config.voucherType,
  );
  console.log("[useVoucherPage] config.endpoint:", config.endpoint);
  console.log("[useVoucherPage] isOrgContextReady:", isOrgContextReady);
  const [mode, setMode] = useState<"create" | "edit" | "view" | "revise">(
    (queryMode as "create" | "edit" | "view" | "revise") || "create",
  );
  const [selectedId, setSelectedId] = useState<number | null>(
    id ? Number(id) : null,
  );
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [showShippingModal, setShowShippingModal] = useState(false);
  const [showFullModal, setShowFullModal] = useState(false);
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [addCustomerLoading, setAddCustomerLoading] = useState(false);
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [addShippingLoading, setAddShippingLoading] = useState(false);
  const [addingItemIndex, setAddingItemIndex] = useState(-1);
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    voucher: any;
  } | null>(null);
  const [useDifferentShipping, setUseDifferentShipping] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(VOUCHER_PAGINATION_DEFAULTS.pageSize);
  const [searchTerm, setSearchTerm] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [filteredVouchers, setFilteredVouchers] = useState<any[]>([]);
  const [selectedReferenceType, setSelectedReferenceType] = useState<
    string | null
  >(null);
  const [selectedReferenceId, setSelectedReferenceId] = useState<number | null>(
    null,
  );
  const [referenceDocument, setReferenceDocument] = useState<any>(null);
  const [lineDiscountEnabled, setLineDiscountEnabled] = useState(false);
  const [lineDiscountType, setLineDiscountType] = useState<
    "percentage" | "amount" | null
  >(null);
  const [totalDiscountEnabled, setTotalDiscountEnabled] = useState(false);
  const [totalDiscountType, setTotalDiscountType] = useState<
    "percentage" | "amount" | null
  >(null);
  const [discountDialogOpen, setDiscountDialogOpen] = useState(false);
  const [discountDialogFor, setDiscountDialogFor] = useState<
    "line" | "total" | null
  >(null);

  useEffect(() => {
    const savedLineType = localStorage.getItem("voucherLineDiscountType");
    if (savedLineType)
      setLineDiscountType(savedLineType as "percentage" | "amount");
    const savedTotalType = localStorage.getItem("voucherTotalDiscountType");
    if (savedTotalType)
      setTotalDiscountType(savedTotalType as "percentage" | "amount");
  }, []);

  useEffect(() => {
    if (lineDiscountType)
      localStorage.setItem("voucherLineDiscountType", lineDiscountType);
  }, [lineDiscountType]);

  useEffect(() => {
    if (totalDiscountType)
      localStorage.setItem("voucherTotalDiscountType", totalDiscountType);
  }, [totalDiscountType]);

  const handleToggleLineDiscount = (enabled: boolean) => {
    if (enabled) {
      if (!lineDiscountType) {
        setDiscountDialogFor("line");
        setDiscountDialogOpen(true);
        return;
      }
    } else {
      setLineDiscountType(null);
      localStorage.removeItem("voucherLineDiscountType");
    }
    setLineDiscountEnabled(enabled);
  };

  const handleToggleTotalDiscount = (enabled: boolean) => {
    if (enabled) {
      if (!totalDiscountType) {
        setDiscountDialogFor("total");
        setDiscountDialogOpen(true);
        return;
      }
    } else {
      setTotalDiscountType(null);
      localStorage.removeItem("voucherTotalDiscountType");
    }
    setTotalDiscountEnabled(enabled);
  };

  const handleDiscountTypeSelect = (type: "percentage" | "amount") => {
    if (discountDialogFor === "line") {
      setLineDiscountType(type);
      setLineDiscountEnabled(true);
    } else {
      setTotalDiscountType(type);
      setTotalDiscountEnabled(true);
    }
    setDiscountDialogOpen(false);
    setDiscountDialogFor(null);
  };

  const handleDiscountDialogClose = () => {
    setDiscountDialogOpen(false);
    setDiscountDialogFor(null);
    if (discountDialogFor === "line") {
      setLineDiscountEnabled(false);
    } else if (discountDialogFor === "total") {
      setTotalDiscountEnabled(false);
    }
  };

  const defaultValues = useMemo(() => {
    const baseValues = {
      voucher_number: "Loading...",
      date: new Date().toISOString().slice(0, 10),
      reference: "",
      notes: "",
      reference_type: "",
      reference_id: null as number | null,
      reference_number: "",
      round_off: 0,
      parent_id: null as number | null,
      revision_number: 0,
    };
    if (config.hasItems === false) {
      return {
        ...baseValues,
        total_amount: 0,
        from_account: "",
        to_account: "",
        payment_method: "",
        receipt_method: "",
        name_id: null as number | null,
        name_type: "" as "Vendor" | "Customer",
      };
    } else {
      const itemDefaults = getDefaultVoucherValues(
        config.entityType === "purchase" ? "purchase" : "sales",
      );
      return {
        ...baseValues,
        ...itemDefaults,
        total_discount: 0,
        items: [
          {
            ...itemDefaults.items[0],
            unit_price: 0.0,
            original_unit_price: 0.0,
            discount_percentage: 0,
            discount_amount: 0.0,
          },
        ],
      };
    }
  }, [config.entityType, config.hasItems]);

  const {
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<any>({
    defaultValues,
  });

  const { fields, append, remove, replace } = useFieldArray({
    control,
    name: "items",
  });

  const watchedFields = useWatch({ control, name: ["items", "total_discount"] });
  const itemsWatch = watchedFields[0] || [];
  const totalDiscountWatch = watchedFields[1] || 0;

  const { data: vendorList } = useQuery({
    queryKey: ["vendors"],
    queryFn: getVendors,
    enabled:
      isOrgContextReady &&
      (config.entityType === "purchase" || config.entityType === "financial"),
    staleTime: 300000,
  });

  const { data: customerList } = useQuery({
    queryKey: ["customers"],
    queryFn: getCustomers,
    enabled:
      isOrgContextReady &&
      (config.entityType === "sales" || config.entityType === "financial"),
    staleTime: 300000,
  });

  const { data: voucherData, isLoading: isFetching } = useQuery({
    queryKey: [config.voucherType, selectedId],
    queryFn: () =>
      voucherService.getVoucherById(
        config.apiEndpoint || config.voucherType,
        selectedId!,
      ),
    enabled:
      !!selectedId &&
      isOrgContextReady &&
      (mode === "view" || mode === "edit" || mode === "revise"),
    staleTime: mode === "view" ? Infinity : 300000,
  });

  const watchedCustomerId = watch("customer_id");
  const watchedVendorId = watch("vendor_id");

  const isIntrastate = useMemo(() => {
    let isIntra = true;
    try {
      const selectedEntityId = watchedCustomerId || watchedVendorId;
      let selectedEntity = null;
      if (config.entityType === "sales" && customerList && selectedEntityId) {
        selectedEntity = customerList.find(
          (c: any) => c.id === selectedEntityId,
        );
      } else if (
        config.entityType === "purchase" &&
        vendorList && selectedEntityId
      ) {
        selectedEntity = vendorList.find((v: any) => v.id === selectedEntityId);
      }
      if (selectedEntity) {
        const companyStateCode = company?.state_code;
        if (!companyStateCode) {
          console.error("Company state code is not available.");
          return true;
        }
        const entityStateCode =
          selectedEntity.state_code || selectedEntity.gst_number?.slice(0, 2);
        if (!entityStateCode) {
          console.error("Entity state code or GST number is not available.");
          return true;
        }
        isIntra = entityStateCode === companyStateCode;
        console.log(
          `[useVoucherPage] Transaction is ${
            isIntra ? "intrastate" : "interstate"
          }`,
          {
            companyStateCode,
            entityStateCode,
            entity: selectedEntity.name,
          },
        );
      }
    } catch (error) {
      console.error("Error determining transaction state:", error);
      return true;
    }
    return isIntra;
  }, [
    watchedCustomerId,
    watchedVendorId,
    config.entityType,
    customerList,
    vendorList,
    company?.state_code,
  ]);

  const { computedItems, totalAmount, totalSubtotal, totalGst, totalCgst, totalSgst, totalIgst, totalDiscount, totalTaxable, gstBreakdown, totalRoundOff } = useMemo(() => {
    if (config.hasItems === false || !itemsWatch) {
      return {
        computedItems: [],
        totalAmount: watch("total_amount") || 0,
        totalSubtotal: 0,
        totalGst: 0,
        totalCgst: 0,
        totalSgst: 0,
        totalIgst: 0,
        totalDiscount: 0,
        totalTaxable: 0,
        gstBreakdown: {},
        totalRoundOff: 0,
      };
    }
    const formattedItems = itemsWatch.map((item: any) => ({
      ...item,
      unit_price: enhancedRateUtils.parseRate(String(item.unit_price || 0)),
    }));
    return calculateVoucherTotals(
      formattedItems,
      isIntrastate,
      lineDiscountEnabled ? lineDiscountType : null,
      totalDiscountEnabled ? totalDiscountType : null,
      totalDiscountWatch,
    );
  }, [
    itemsWatch,
    config.hasItems,
    watch,
    isIntrastate,
    lineDiscountEnabled,
    lineDiscountType,
    totalDiscountEnabled,
    totalDiscountType,
    totalDiscountWatch,
  ]);

  const {
    data: voucherList,
    isLoading: isLoadingList,
    refetch: refetchVoucherList,
  } = useQuery({
    queryKey: [config.voucherType, currentPage, pageSize],
    queryFn: () =>
      voucherService.getVouchers(config.voucherType, {
        skip: (currentPage - 1) * pageSize,
        limit: 500,
        sort: "desc",
        sortBy: "created_at",
      }),
    enabled: isOrgContextReady,
    staleTime: 300000,
    select: (data) =>
      data.map((voucher: any) => ({
        ...voucher,
        total_amount: calculateVoucherTotals(
          voucher.items || [],
          isIntrastate,
          voucher.line_discount_type,
          voucher.total_discount_type,
          voucher.total_discount || 0,
        ).totalAmount,
      })),
  });

  const { data: employeeList } = useQuery({
    queryKey: ["employees"],
    queryFn: getEmployees,
    enabled: isOrgContextReady && config.entityType === "financial",
    staleTime: 300000,
  });

  const { data: productList } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
    enabled: isOrgContextReady && config.hasItems !== false,
    staleTime: 300000,
  });

  const {
    data: nextVoucherNumber,
    isLoading: isNextNumberLoading,
    refetch: refetchNextNumber,
  } = useQuery({
    queryKey: [`next${config.voucherType}Number`],
    queryFn: () =>
      voucherService.getNextVoucherNumber(config.nextNumberEndpoint),
    enabled: mode === "create" && isOrgContextReady,
    staleTime: 300000,
  });

  const createMutation = useMutation({
    mutationFn: (data: any) =>
      voucherService.createVoucher(
        config.apiEndpoint || config.voucherType,
        data,
      ),
    onSuccess: async (newVoucher) => {
      console.log("[useVoucherPage] Voucher created successfully:", newVoucher);
      if (newVoucher.reference_id && newVoucher.reference_type) {
        try {
          const referenceConfig = getVoucherConfig(newVoucher.reference_type as any);
          await api.patch(
            `${referenceConfig.endpoint}/${newVoucher.reference_id}`,
            { used: true },
          );
          queryClient.invalidateQueries({
            queryKey: [newVoucher.reference_type],
          });
        } catch (error) {
          console.error("Error marking reference as used:", error);
        }
      }
      queryClient.setQueryData(
        [config.voucherType, currentPage, pageSize],
        (oldData: any) => {
          if (!oldData) {
            return [newVoucher];
          }
          return [newVoucher, ...oldData];
        },
      );
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      await refetchVoucherList();
      router.push({ query: { mode: "create" } }, undefined, { shallow: true });
      setMode("create");
      const { data: newNextNumber } = await refetchNextNumber();
      reset({
        ...defaultValues,
        voucher_number: newNextNumber,
      });
    },
    onError: (error: any) => {
      console.error("[useVoucherPage] Error creating voucher:", error);
      handleVoucherError(error, "create");
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: any) =>
      voucherService.updateVoucher(
        config.apiEndpoint || config.voucherType,
        selectedId!,
        data,
      ),
    onSuccess: () => {
      console.log("[useVoucherPage] Voucher updated successfully");
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      queryClient.invalidateQueries({
        queryKey: [config.voucherType, selectedId],
      });
      refetchVoucherList();
    },
    onError: (error: any) => {
      console.error("[useVoucherPage] Error updating voucher:", error);
      handleVoucherError(error, "update");
    },
  });

  const handleCreate = () => {
    setReferenceDocument(null);
    router.push({ query: { mode: "create" } }, undefined, { shallow: true });
    setMode("create");
    setSelectedId(null);
    reset(defaultValues);
  };

  const handleEdit = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "edit" } }, undefined, {
      shallow: true,
    });
    setMode("edit");
    setSelectedId(voucherId);
  };

  const handleRevise = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "revise" } }, undefined, {
      shallow: true,
    });
    setMode("revise");
    setSelectedId(voucherId);
  };

  const handleView = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "view" } }, undefined, {
      shallow: true,
    });
    setMode("view");
    setSelectedId(voucherId);
  };

  const handleSubmitForm = (data: any) => {
    if (config.hasItems === false) {
      if (data.entity?.type === "Vendor") {
        data.vendor_id = data.entity.id;
      } else if (data.entity?.type === "Customer") {
        data.customer_id = data.entity.id;
      } else if (data.entity?.type === "Employee") {
        data.employee_id = data.entity.id;
      }
      delete data.entity;
    } else {
      data.items = computedItems;
      data.total_amount = totalAmount;
    }
    if (referenceDocument) {
      data.reference_type = selectedReferenceType;
      data.reference_id = selectedReferenceId;
      data.reference_number =
        referenceDocument.voucher_number || referenceDocument.number;
    }
    if (lineDiscountEnabled && lineDiscountType) {
      data.line_discount_type = lineDiscountType;
    }
    if (totalDiscountEnabled && totalDiscountType) {
      data.total_discount_type = totalDiscountType;
    }
    if (mode === "create" || mode === "revise") {
      createMutation.mutate(data);
    } else if (mode === "edit") {
      updateMutation.mutate(data);
    }
  };

  const handleContextMenu = (event: React.MouseEvent, voucher: any) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX + 2,
      mouseY: event.clientY - 6,
      voucher,
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleReferenceSelected = (referenceData: any) => {
    console.log('[useVoucherPage] handleReferenceSelected called with:', referenceData);
    setReferenceDocument(referenceData);
    setSelectedReferenceType(referenceData.type);
    setSelectedReferenceId(referenceData.id);
    if (referenceData.items && config.hasItems && config.voucherType === 'goods-receipt-notes') {
      console.log('[useVoucherPage] Populating GRN items:', referenceData.items);
      fields.forEach((_, index) => remove(index));
      referenceData.items.forEach((item: any) => {
        append({
          product_id: item.product_id || null,
          product_name: item.product?.name || item.product_name || 'Unknown Product',
          ordered_quantity: item.quantity || 0,
          received_quantity: 0,
          accepted_quantity: 0,
          rejected_quantity: 0,
          unit_price: item.unit_price || 0,
          unit: item.unit || item.product?.unit || '',
          po_item_id: item.id || null,
        });
      });
    } else if (referenceData.items && config.hasItems) {
      const referenceItems = referenceData.items.map((item: any) => ({
        ...item,
        quantity: item.quantity || 0,
        unit_price: enhancedRateUtils.parseRate(String(item.unit_price || 0)),
      }));
      fields.forEach((_, index) => remove(index));
      referenceItems.forEach((item: any) => append(item));
    }
    if (referenceData.customer_id && config.entityType === "sales") {
      setValue("customer_id", referenceData.customer_id);
    }
    if (referenceData.vendor_id && config.entityType === "purchase") {
      setValue("vendor_id", referenceData.vendor_id);
    }
  };

  const sortedVouchers = useMemo(() => {
    if (!voucherList) {
      return [];
    }
    if (!Array.isArray(voucherList)) {
      console.warn(
        "[useVoucherPage] voucherList is not an array:",
        voucherList,
      );
      return [];
    }
    return voucherListUtils.sortLatestFirst(voucherList);
  }, [voucherList]);

  const latestVouchers = useMemo(
    () => voucherListUtils.getLatestVouchers(sortedVouchers, 7),
    [sortedVouchers],
  );

  const paginationData = useMemo(() => {
    const totalVouchers = sortedVouchers.length;
    return voucherListUtils.paginate(sortedVouchers, currentPage, pageSize);
  }, [sortedVouchers, currentPage, pageSize]);

  const handleSearch = () => {
    if (fromDate && toDate && new Date(toDate) < new Date(fromDate)) {
      alert("To date cannot be earlier than from date");
      return;
    }
    const filtered = sortedVouchers.filter((v) => {
      const lowerSearch = searchTerm.toLowerCase();
      let matchesSearch = v.voucher_number.toLowerCase().includes(lowerSearch);
      if (config.entityType === "purchase" && v.vendor?.name) {
        matchesSearch =
          matchesSearch || v.vendor.name.toLowerCase().includes(lowerSearch);
      } else if (config.entityType === "sales" && v.customer?.name) {
        matchesSearch =
          matchesSearch || v.customer.name.toLowerCase().includes(lowerSearch);
      }
      let matchesDate = true;
      if (fromDate) {
        matchesDate = matchesDate && new Date(v.date) >= new Date(fromDate);
      }
      if (toDate) {
        matchesDate = matchesDate && new Date(v.date) <= new Date(toDate);
      }
      return (!searchTerm || matchesSearch) && matchesDate;
    });
    setFilteredVouchers(filtered);
    setCurrentPage(1);
  };

  const handleModalOpen = useCallback(() => {
    setShowFullModal(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setShowFullModal(false);
  }, []);

  const handleGeneratePDF = useCallback(
    async (voucher?: any) => {
      const voucherToUse = voucher || voucherData;
      if (!voucherToUse?.id) {
        console.error("No voucher ID available for PDF generation");
        return;
      }
      await generateStandalonePDF(voucherToUse.id, config.voucherType, voucherToUse.voucher_number);
    },
    [config.voucherType, voucherData],
  );

  const handleDelete = useCallback(
    async (voucher: any) => {
      if (
        window.confirm(
          getDynamicMessage.confirmDelete("voucher", voucher.voucher_number),
        )
      ) {
        try {
          await voucherService.deleteVoucher(
            config.apiEndpoint || config.voucherType,
            voucher.id,
          );
          queryClient.invalidateQueries({ queryKey: [config.voucherType] });
          refetchVoucherList();
          showSuccessToast(
            getDynamicMessage.voucherDeleted(voucher.voucher_number),
          );
        } catch (error: any) {
          console.error("Error deleting voucher:", error);
          handleVoucherError(error, "delete");
        }
      }
    },
    [config.voucherType, config.apiEndpoint, queryClient, refetchVoucherList],
  );

  const refreshMasterData = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["vendors"] });
    queryClient.invalidateQueries({ queryKey: ["customers"] });
    queryClient.invalidateQueries({ queryKey: ["products"] });
  }, [queryClient]);

  const masterDataService = {
    createCustomer: (data: any) => api.post("/customers", data),
    createVendor: (data: any) => api.post("/vendors", data),
    createProduct: (data: any) => api.post("/products", data),
  };

  const handleAddCustomer = useCallback(
    async (customerData: any) => {
      setAddCustomerLoading(true);
      try {
        const response = await masterDataService.createCustomer(customerData);
        const newCustomer = response.data;
        queryClient.setQueryData(["customers"], (old: any) =>
          old ? old.concat(newCustomer) : [newCustomer],
        );
        queryClient.invalidateQueries({ queryKey: ["customers"] });
        if (config.entityType === "sales") {
          setValue("customer_id", newCustomer.id);
        }
        setShowAddCustomerModal(false);
        showSuccessToast(SUCCESS_MESSAGES.CUSTOMER_ADDED);
      } catch (error: any) {
        console.error("Error adding customer:", error);
        showErrorToast(error, "Failed to add customer");
      } finally {
        setAddCustomerLoading(false);
      }
    },
    [
      queryClient,
      setValue,
      setAddCustomerLoading,
      setShowAddCustomerModal,
      config.entityType,
    ],
  );

  const handleAddVendor = useCallback(
    async (vendorData: any) => {
      setAddVendorLoading(true);
      try {
        const response = await masterDataService.createVendor(vendorData);
        const newVendor = response.data;
        queryClient.setQueryData(["vendors"], (old: any) =>
          old ? old.concat(newVendor) : [newVendor],
        );
        queryClient.invalidateQueries({ queryKey: ["vendors"] });
        if (config.entityType === "purchase") {
          setValue("vendor_id", newVendor.id);
        }
        setShowAddVendorModal(false);
        showSuccessToast(SUCCESS_MESSAGES.VENDOR_ADDED);
      } catch (error: any) {
        console.error("Error adding vendor:", error);
        showErrorToast(error, "Failed to add vendor");
      } finally {
        setAddVendorLoading(false);
      }
    },
    [
      queryClient,
      setValue,
      setAddVendorLoading,
      setShowAddVendorModal,
      config.entityType,
    ],
  );

  const handleAddProduct = useCallback(
    async (productData: any) => {
      setAddProductLoading(true);
      try {
        const response = await masterDataService.createProduct(productData);
        const newProduct = response.data;
        queryClient.setQueryData(["products"], (old: any) =>
          old ? old.concat(newProduct) : [newProduct],
        );
        queryClient.invalidateQueries({ queryKey: ["products"] });
        setShowAddProductModal(false);
        showSuccessToast(SUCCESS_MESSAGES.PRODUCT_ADDED);
      } catch (error: any) {
        console.error("Error adding product:", error);
        showErrorToast(error, "Failed to add product");
      } finally {
        setAddProductLoading(false);
      }
    },
    [queryClient, setAddProductLoading, setShowAddProductModal],
  );

  const handleAddShipping = useCallback(
    async () => {
      setAddShippingLoading(true);
      try {
        setShowShippingModal(false);
        alert("Shipping address added successfully!");
      } catch (error: any) {
        console.error("Error adding shipping address:", error);
        alert("Error adding shipping address");
      } finally {
        setAddShippingLoading(false);
      }
    },
    [setAddShippingLoading, setShowShippingModal],
  );

  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "refreshMasterData") {
        refreshMasterData();
        localStorage.removeItem("refreshMasterData");
      }
    };
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [refreshMasterData]);

  useEffect(() => {
    if (mode === "create" && isOrgContextReady) {
      refetchNextNumber();
    }
  }, [mode, isOrgContextReady, refetchNextNumber]);

  useEffect(() => {
    console.log("Next Voucher Number:", nextVoucherNumber);
    console.log("Is Next Number Loading:", isNextNumberLoading);
    console.log("Is Org Context Ready:", isOrgContextReady);
    console.log("Mode:", mode);
  }, [nextVoucherNumber, isNextNumberLoading, isOrgContextReady, mode]);

  const isLoading =
    isLoadingList ||
    isFetching ||
    !isOrgContextReady ||
    createMutation.isPending ||
    updateMutation.isPending;

  useEffect(() => {
    if (isOrgContextReady) {
      console.log(
        "[useVoucherPage] Org context ready - refetching voucher list",
      );
      refetchVoucherList();
    }
  }, [isOrgContextReady, refetchVoucherList]);

  useEffect(() => {
    if (createMutation.isSuccess || updateMutation.isSuccess) {
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      refetchVoucherList();
      setTimeout(() => {
        refetchVoucherList();
      }, 500);
    }
  }, [
    createMutation.isSuccess,
    updateMutation.isSuccess,
    queryClient,
    config.voucherType,
    refetchVoucherList,
  ]);

  useEffect(() => {
    const newMode = (router.query.mode as
      | "create"
      | "edit"
      | "view"
      | "revise") || "create";
    const newId = router.query.id ? Number(router.query.id) : null;
    setMode(newMode);
    setSelectedId(newId);
  }, [router.query.mode, router.query.id]);

  return {
    mode,
    setMode,
    selectedId,
    isLoading,
    showAddVendorModal,
    setShowAddVendorModal,
    showAddCustomerModal,
    setShowAddCustomerModal,
    showAddProductModal,
    setShowAddProductModal,
    showShippingModal,
    setShowShippingModal,
    showFullModal,
    addVendorLoading,
    setAddVendorLoading,
    addCustomerLoading,
    setAddCustomerLoading,
    addProductLoading,
    setAddProductLoading,
    addShippingLoading,
    setAddShippingLoading,
    addingItemIndex,
    setAddingItemIndex,
    contextMenu,
    selectedReferenceType,
    setSelectedReferenceType,
    selectedReferenceId,
    setSelectedReferenceId,
    useDifferentShipping,
    setUseDifferentShipping,
    searchTerm,
    setSearchTerm,
    fromDate,
    setFromDate,
    toDate,
    setToDate,
    filteredVouchers,
    currentPage,
    pageSize,
    paginationData,
    handlePageChange,
    referenceDocument,
    handleReferenceSelected,
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    errors,
    fields,
    append,
    remove,
    voucherList,
    vendorList,
    customerList,
    employeeList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
    totalCgst,
    totalSgst,
    totalIgst,
    totalDiscount,
    totalTaxable,
    gstBreakup: gstBreakdown,
    isIntrastate,
    totalRoundOff,
    createMutation,
    updateMutation,
    handleCreate,
    handleEdit,
    handleRevise,
    handleView,
    handleSubmitForm,
    handleContextMenu,
    handleCloseContextMenu,
    handleSearch,
    handleModalOpen,
    handleModalClose,
    handleGeneratePDF,
    handleDelete,
    handleAddCustomer,
    handleAddVendor,
    handleAddProduct,
    handleAddShipping,
    refreshMasterData,
    getAmountInWords,
    isViewMode: mode === "view",
    enhancedRateUtils,
    lineDiscountEnabled,
    lineDiscountType,
    totalDiscountEnabled,
    totalDiscountType,
    handleToggleLineDiscount,
    handleToggleTotalDiscount,
    discountDialogOpen,
    handleDiscountDialogClose,
    handleDiscountTypeSelect,
    discountDialogFor,
  };
};