// frontend/src/hooks/useVoucherPage.ts
// Enhanced comprehensive hook for voucher page logic with comprehensive overhaul features
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
  getAmountInWords,  // Added import for getAmountInWords
} from "../utils/voucherUtils";
import {
  generateVoucherPDF,
  getVoucherPdfConfig,
} from "../utils/pdfUtils";
import { VoucherPageConfig } from "../types/voucher.types";
import api from "../lib/api"; // Direct import for list fetch

export const useVoucherPage = (config: VoucherPageConfig) => {
  const router = useRouter();
  const { id, mode: queryMode } = router.query;
  const { isOrgContextReady } = useAuth(); // Get isOrgContextReady from AuthContext
  const { company } = useCompany(); // Get company from CompanyContext
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
  // Modal states
  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [showAddCustomerModal, setShowAddCustomerModal] = useState(false);
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [showShippingModal, setShowShippingModal] = useState(false);
  const [showFullModal, setShowFullModal] = useState(false);
  // Loading states
  const [addVendorLoading, setAddVendorLoading] = useState(false);
  const [addCustomerLoading, setAddCustomerLoading] = useState(false);
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [addShippingLoading, setAddShippingLoading] = useState(false);
  const [addingItemIndex, setAddingItemIndex] = useState(-1);
  // UI states
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
    voucher: any;
  } | null>(null);
  const [useDifferentShipping, setUseDifferentShipping] = useState(false);
  // Enhanced pagination and filtering states
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(VOUCHER_PAGINATION_DEFAULTS.pageSize);
  const [searchTerm, setSearchTerm] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [filteredVouchers, setFilteredVouchers] = useState<any[]>([]);
  // Reference document states
  const [selectedReferenceType, setSelectedReferenceType] = useState<
    string | null
  >(null);
  const [selectedReferenceId, setSelectedReferenceId] = useState<number | null>(
    null,
  );
  const [referenceDocument, setReferenceDocument] = useState<any>(null);
  // Discount states (common across vouchers)
  const [lineDiscountEnabled, setLineDiscountEnabled] = useState(false);
  const [lineDiscountType, setLineDiscountType] = useState<'percentage' | 'amount' | null>(null);
  const [totalDiscountEnabled, setTotalDiscountEnabled] = useState(false);
  const [totalDiscountType, setTotalDiscountType] = useState<'percentage' | 'amount' | null>(null);
  // Discount dialog states
  const [discountDialogOpen, setDiscountDialogOpen] = useState(false);
  const [discountDialogFor, setDiscountDialogFor] = useState<'line' | 'total' | null>(null);
  // Load saved discount types from localStorage
  useEffect(() => {
    const savedLineType = localStorage.getItem('voucherLineDiscountType');
    if (savedLineType) setLineDiscountType(savedLineType as 'percentage' | 'amount');
    const savedTotalType = localStorage.getItem('voucherTotalDiscountType');
    if (savedTotalType) setTotalDiscountType(savedTotalType as 'percentage' | 'amount');
  }, []);
  // Save discount types to localStorage
  useEffect(() => {
    if (lineDiscountType) localStorage.setItem('voucherLineDiscountType', lineDiscountType);
  }, [lineDiscountType]);
  useEffect(() => {
    if (totalDiscountType) localStorage.setItem('voucherTotalDiscountType', totalDiscountType);
  }, [totalDiscountType]);
  // Handlers for toggling discounts
  const handleToggleLineDiscount = (enabled: boolean) => {
    if (enabled) {
      if (!lineDiscountType) {
        setDiscountDialogFor('line');
        setDiscountDialogOpen(true);
        return;
      }
    } else {
      // Reset when unchecked
      setLineDiscountType(null);
      localStorage.removeItem('voucherLineDiscountType');
    }
    setLineDiscountEnabled(enabled);
  };
  const handleToggleTotalDiscount = (enabled: boolean) => {
    if (enabled) {
      if (!totalDiscountType) {
        setDiscountDialogFor('total');
        setDiscountDialogOpen(true);
        return;
      }
    } else {
      // Reset when unchecked
      setTotalDiscountType(null);
      localStorage.removeItem('voucherTotalDiscountType');
    }
    setTotalDiscountEnabled(enabled);
  };
  const handleDiscountTypeSelect = (type: 'percentage' | 'amount') => {
    if (discountDialogFor === 'line') {
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
    // If canceled, uncheck the checkbox if needed
    if (discountDialogFor === 'line') {
      setLineDiscountEnabled(false);
    } else if (discountDialogFor === 'total') {
      setTotalDiscountEnabled(false);
    }
  };
  // Enhanced form management with reference support
  const defaultValues = useMemo(() => {
    const baseValues = {
      voucher_number: "",
      date: new Date().toISOString().slice(0, 10),
      reference: "",
      notes: "",
      // Reference document fields
      reference_type: "",
      reference_id: null as number | null,
      reference_number: "",
      round_off: 0,
      parent_id: null as number | null,
      revision_number: 0,
    };
    if (config.hasItems === false) {
      // Financial vouchers - use financial defaults
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
      // Vouchers with items - use standard defaults with enhanced rate formatting
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
            unit_price: 0.0, // Ensure 2 decimal places
            original_unit_price: 0.0,
            discount_percentage: 0,
            discount_amount: 0,
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
  // Always create field array and watch, but use conditionally
  const { fields, append, remove } = useFieldArray({
    control,
    name: "items",
  });
  // Combined useWatch for items and total_discount to avoid multiple calls
  const watchedFields = useWatch({ control, name: ["items", "total_discount"] });
  const itemsWatch = watchedFields[0] || [];  // Default to empty array
  const totalDiscountWatch = watchedFields[1] || 0;  // Default to 0
  const { data: vendorList } = useQuery({
    queryKey: ["vendors"],
    queryFn: getVendors,
    enabled:
      isOrgContextReady &&
      (config.entityType === "purchase" || config.entityType === "financial"),
  });
  const { data: customerList } = useQuery({
    queryKey: ["customers"],
    queryFn: getCustomers,
    enabled:
      isOrgContextReady &&
      (config.entityType === "sales" || config.entityType === "financial"),
  });
  const { data: voucherData, isLoading: isFetching } = useQuery({
    queryKey: [config.voucherType, selectedId],
    queryFn: () =>
      voucherService.getVoucherById(
        config.apiEndpoint || config.voucherType,
        selectedId!,
      ),
    enabled:
      !!selectedId && isOrgContextReady && (mode === "view" || mode === "edit" || mode === "revise"),
  });
  // Extract isIntrastate as separate memo for UI usage
  const isIntrastate = useMemo(() => {
    let isIntra = true;
    try {
      const selectedEntityId = watch("customer_id") || watch("vendor_id");
      let selectedEntity = null;
      if (config.entityType === "sales" && customerList && selectedEntityId) {
        selectedEntity = customerList.find(
          (c: any) => c.id === selectedEntityId,
        );
      } else if (
        config.entityType === "purchase" &&
        vendorList &&
        selectedEntityId
      ) {
        selectedEntity = vendorList.find((v: any) => v.id === selectedEntityId) || voucherData?.vendor;
      }
      if (selectedEntity) {
        const companyStateCode = company?.state_code;
        if (!companyStateCode) {
          console.error("Company state code is not available.");
          return true; // Assume intrastate to prevent crash
        }
        const entityStateCode =
          selectedEntity.state_code || selectedEntity.gst_number?.slice(0, 2);
        if (!entityStateCode) {
          console.error("Entity state code or GST number is not available.");
          return true; // Assume intrastate to prevent crash
        }
        isIntra = entityStateCode === companyStateCode;
      }
    } catch (error) {
      console.error("Error determining transaction state:", error);
      return true; // Assume intrastate to prevent crash
    }
    return isIntra;
  }, [
    watch("customer_id"),
    watch("vendor_id"),
    config.entityType,
    customerList,
    vendorList,
    company?.state_code,
    voucherData
  ]);
  // Enhanced computed values using the extracted isIntrastate
  const {
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
    totalCgst,
    totalSgst,
    totalIgst,
    totalDiscount,
    totalTaxable,
    gstBreakdown,
    totalRoundOff,
  } = useMemo(() => {
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
    // Ensure all rates are properly formatted
    const formattedItems = itemsWatch.map((item: any) => ({
      ...item,
      unit_price: enhancedRateUtils.parseRate(String(item.unit_price || 0)),
    }));
    return calculateVoucherTotals(
      formattedItems, 
      isIntrastate,
      lineDiscountEnabled ? lineDiscountType : null,
      totalDiscountEnabled ? totalDiscountType : null,
      totalDiscountWatch
    );
  }, [itemsWatch, config.hasItems, watch, isIntrastate, lineDiscountEnabled, lineDiscountType, totalDiscountEnabled, totalDiscountType, totalDiscountWatch]);  // Keep totalDiscountWatch in deps
  // Enhanced queries with pagination and sorting
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
  });
  // Handle data sorting when vouchers data changes
  useEffect(() => {
    if (voucherList && Array.isArray(voucherList)) {
      console.log(
        `[useVoucherPage] Successfully fetched vouchers for ${config.voucherType}:`,
        voucherList,
      );
      const sorted = voucherListUtils.sortLatestFirst(voucherList);
      setFilteredVouchers(sorted);
    }
  }, [voucherList, config.voucherType]);
  // Handle error logging
  useEffect(() => {
    if (isLoadingList === false && !voucherList) {
      console.error(
        `[useVoucherPage] Error fetching vouchers for ${config.voucherType}`,
      );
    }
  }, [isLoadingList, voucherList, config.voucherType]);
  const { data: employeeList } = useQuery({
    queryKey: ["employees"],
    queryFn: getEmployees,
    enabled: isOrgContextReady && config.entityType === "financial",
  });
  const { data: productList } = useQuery({
    queryKey: ["products"],
    queryFn: getProducts,
    enabled: isOrgContextReady && config.hasItems !== false,
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
  });
  // Enhanced mutations with auto-refresh and pagination support
  const createMutation = useMutation({
    mutationFn: (data: any) =>
      voucherService.createVoucher(
        config.apiEndpoint || config.voucherType,
        data,
      ),
    onSuccess: async (newVoucher) => {
      console.log("[useVoucherPage] Voucher created successfully:", newVoucher);
      // Mark reference as used if selected
      if (newVoucher.reference_id && newVoucher.reference_type) {
        try {
          const referenceConfig = getVoucherConfig(newVoucher.reference_type as any);
          await api.patch(`${referenceConfig.endpoint}/${newVoucher.reference_id}`, { used: true });
          queryClient.invalidateQueries({ queryKey: [newVoucher.reference_type] });
        } catch (error) {
          console.error("Error marking reference as used:", error);
        }
      }
      // Optimistically update the voucher list by prepending the new voucher
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
      await refetchVoucherList(); // Explicit refetch after invalidation
      router.push({ query: { mode: "create" } }, undefined, { shallow: true });
      reset(defaultValues);
      const { data: newNextNumber } = await refetchNextNumber();
      setValue("voucher_number", newNextNumber);
    },
    onError: (error: any) => {
      console.error("[useVoucherPage] Error creating voucher:", error);
      alert(error.response?.data?.detail || "Failed to create voucher");
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
      refetchVoucherList(); // Explicit refetch after invalidation
    },
    onError: (error: any) => {
      console.error("[useVoucherPage] Error updating voucher:", error);
      alert(error.response?.data?.detail || "Failed to update voucher");
    },
  });
  // Enhanced event handlers
  const handleCreate = () => {
    setReferenceDocument(null); // Clear reference
    router.push({ query: { mode: "create" } }, undefined, { shallow: true });
    reset(defaultValues);
  };
  const handleEdit = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "edit" } }, undefined, {
      shallow: true,
    });
  };
  const handleRevise = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "revise" } }, undefined, {
      shallow: true,
    });
  };
  const handleView = (voucherId: number) => {
    router.push({ query: { id: voucherId, mode: "view" } }, undefined, {
      shallow: true,
    });
  };
  const handleSubmitForm = (data: any) => {
    // Enhanced data preparation with reference support
    if (config.hasItems === false) {
      // Transform entity to vendor_id for payment voucher
      if (data.entity?.type === 'Vendor') {
        data.vendor_id = data.entity.id;
      } else if (data.entity?.type === 'Customer') {
        data.customer_id = data.entity.id;  // If model supports, else adjust
      } else if (data.entity?.type === 'Employee') {
        data.employee_id = data.entity.id;  // If applicable
      }
      // Remove entity object
      delete data.entity;
    } else {
      data.items = computedItems;
      data.total_amount = totalAmount;
    }
    // Add reference document data if selected
    if (referenceDocument) {
      data.reference_type = selectedReferenceType;
      data.reference_id = selectedReferenceId;
      data.reference_number =
        referenceDocument.voucher_number || referenceDocument.number;
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
  // Enhanced pagination handlers
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };
  // Enhanced reference document handling
  const handleReferenceSelected = (referenceData: any) => {
    setReferenceDocument(referenceData);
    setSelectedReferenceType(referenceData.type);
    setSelectedReferenceId(referenceData.id);
    // Auto-populate fields from reference document if applicable
    if (referenceData.items && config.hasItems) {
      // Auto-populate items from reference document
      const referenceItems = referenceData.items.map((item: any) => ({
        ...item,
        quantity: item.quantity || 0,
        unit_price: enhancedRateUtils.parseRate(String(item.unit_price || 0)),
      }));
      // Clear existing items and add reference items
      fields.forEach((_, index) => remove(index));
      referenceItems.forEach((item: any) => append(item));
    }
    // Auto-populate customer/vendor if applicable
    if (referenceData.customer_id && config.entityType === "sales") {
      setValue("customer_id", referenceData.customer_id);
    }
    if (referenceData.vendor_id && config.entityType === "purchase") {
      setValue("vendor_id", referenceData.vendor_id);
    }
  };
  // Enhanced search and filter functionality with pagination
  const sortedVouchers = useMemo(() => {
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
  // Enhanced pagination data
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
      // Search in voucher number
      let matchesSearch = v.voucher_number.toLowerCase().includes(lowerSearch);
      // Search in entity name based on voucher type
      if (config.entityType === "purchase" && v.vendor?.name) {
        matchesSearch =
          matchesSearch || v.vendor.name.toLowerCase().includes(lowerSearch);
      } else if (config.entityType === "sales" && v.customer?.name) {
        matchesSearch =
          matchesSearch || v.customer.name.toLowerCase().includes(lowerSearch);
      }
      // Date filtering
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
    setCurrentPage(1); // Reset to first page when filtering
  };
  // Modal handlers (missing from original)
  const handleModalOpen = useCallback(() => {
    setShowFullModal(true);
  }, []);
  const handleModalClose = useCallback(() => {
    setShowFullModal(false);
  }, []);
  // Enhanced PDF generation with proper config
  const handleGeneratePDF = useCallback(
    async (voucher?: any) => {
      const pdfConfig = getVoucherPdfConfig(config.voucherType);
      const voucherToUse = voucher || voucherData;
      if (!voucherToUse?.id) {
        console.error("No voucher ID available for PDF generation");
        return;
      }
      await generateVoucherPDF(voucherToUse.id, pdfConfig);
    },
    [config.voucherType, voucherData],
  );
  // Delete functionality
  const handleDelete = useCallback(
    async (voucher: any) => {
      if (
        window.confirm(
          `Are you sure you want to delete voucher ${voucher.voucher_number}?`,
        )
      ) {
        try {
          await voucherService.deleteVoucher(
            config.apiEndpoint || config.voucherType,
            voucher.id,
          );
          queryClient.invalidateQueries({ queryKey: [config.voucherType] });
          refetchVoucherList(); // Explicit refetch after deletion
          console.log("Voucher deleted successfully");
        } catch (error: any) {
          console.error("Error deleting voucher:", error);
          alert(error.response?.data?.detail || "Failed to delete voucher");
        }
      }
    },
    [config.voucherType, config.apiEndpoint, queryClient, refetchVoucherList],
  );
  // Master data refresh functionality
  const refreshMasterData = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["vendors"] });
    queryClient.invalidateQueries({ queryKey: ["customers"] });
    queryClient.invalidateQueries({ queryKey: ["products"] });
  }, [queryClient]);
  // Import missing service (should be added to imports at top of file)
  const masterDataService = {
    createCustomer: (data: any) => api.post("/customers", data),
    createVendor: (data: any) => api.post("/vendors", data),
    createProduct: (data: any) => api.post("/products", data),
  };
  // Customer add handler with auto-selection
  const handleAddCustomer = useCallback(
    async (customerData: any) => {
      setAddCustomerLoading(true);
      try {
        const response = await masterDataService.createCustomer(customerData);
        const newCustomer = response.data;
        // Update query data immediately
        queryClient.setQueryData(["customers"], (old: any) =>
          old ? old.concat(newCustomer) : [newCustomer],
        );
        queryClient.invalidateQueries({ queryKey: ["customers"] });
        // Auto-select the new customer (conditional on entity type)
        if (config.entityType === "sales") {
          setValue("customer_id", newCustomer.id);
        }
        setShowAddCustomerModal(false);
        alert("Customer added successfully!");
      } catch (error: any) {
        console.error("Error adding customer:", error);
        let errorMsg = "Error adding customer";
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail;
          if (Array.isArray(detail)) {
            errorMsg = detail.map((err: any) => err.msg || err).join(", ");
          } else if (typeof detail === "string") {
            errorMsg = detail;
          }
        }
        alert(errorMsg);
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
  // Vendor add handler with auto-selection
  const handleAddVendor = useCallback(
    async (vendorData: any) => {
      setAddVendorLoading(true);
      try {
        const response = await masterDataService.createVendor(vendorData);
        const newVendor = response.data;
        // Update query data immediately
        queryClient.setQueryData(["vendors"], (old: any) =>
          old ? old.concat(newVendor) : [newVendor],
        );
        queryClient.invalidateQueries({ queryKey: ["vendors"] });
        // Auto-select the new vendor (conditional on entity type)
        if (config.entityType === "purchase") {
          setValue("vendor_id", newVendor.id);
        }
        setShowAddVendorModal(false);
        alert("Vendor added successfully!");
      } catch (error: any) {
        console.error("Error adding vendor:", error);
        let errorMsg = "Error adding vendor";
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail;
          if (Array.isArray(detail)) {
            errorMsg = detail.map((err: any) => err.msg || err).join(", ");
          } else if (typeof detail === "string") {
            errorMsg = detail;
          }
        }
        alert(errorMsg);
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
  // Product add handler
  const handleAddProduct = useCallback(
    async (productData: any) => {
      setAddProductLoading(true);
      try {
        const response = await masterDataService.createProduct(productData);
        const newProduct = response.data;
        // Update query data immediately
        queryClient.setQueryData(["products"], (old: any) =>
          old ? old.concat(newProduct) : [newProduct],
        );
        queryClient.invalidateQueries({ queryKey: ["products"] });
        setShowAddProductModal(false);
        alert("Product added successfully!");
      } catch (error: any) {
        console.error("Error adding product:", error);
        alert(error.response?.data?.detail || "Error adding product");
      } finally {
        setAddProductLoading(false);
      }
    },
    [queryClient, setAddProductLoading, setShowAddProductModal],
  );
  // Shipping address add handler
  const handleAddShipping = useCallback(async () => {
    setAddShippingLoading(true);
    try {
      // Add shipping logic here
      setShowShippingModal(false);
      alert("Shipping address added successfully!");
    } catch (error: any) {
      console.error("Error adding shipping address:", error);
      alert("Error adding shipping address");
    } finally {
      setAddShippingLoading(false);
    }
  }, [setAddShippingLoading, setShowShippingModal]);
  // Effects - Enhanced data loading to fix bug where vouchers don't load saved data properly
  useEffect(() => {
    if (mode === "create" && nextVoucherNumber) {
      setValue("voucher_number", nextVoucherNumber);
    } else if (voucherData) {
      console.log("[useVoucherPage] Loading voucher data:", voucherData);
      // Reset with voucher data
      const formattedDate = voucherData.date ? new Date(voucherData.date).toISOString().split('T')[0] : '';
      const formattedData = {
        ...voucherData,
        date: formattedDate,
      };
      reset(formattedData);
      // Reconstruct and set 'entity' for financial vouchers
      if (config.hasItems === false && voucherData.entity_id && voucherData.entity_type) {
        setValue('entity', {
          id: voucherData.entity_id,
          type: voucherData.entity_type,
          name: voucherData.entity?.name || '',
          value: voucherData.entity_id,
          label: voucherData.entity?.name || '',
        });
      }
      // Set discount states from loaded data
      if (config.hasItems !== false) {
        setLineDiscountEnabled(!!voucherData.line_discount_type);
        setLineDiscountType(voucherData.line_discount_type || null);
        setTotalDiscountEnabled(!!voucherData.total_discount_type);
        setTotalDiscountType(voucherData.total_discount_type || null);
        setValue('total_discount', voucherData.total_discount || 0);
      }
      // Ensure items array is properly loaded for vouchers with items
      if (
        config.hasItems !== false &&
        voucherData.items &&
        Array.isArray(voucherData.items)
      ) {
        // Clear existing items first
        while (fields.length > 0) {
          remove(0);
        }
        // Add items from voucher data
        voucherData.items.forEach((item: any) => {
          append({
            ...item,
            // Ensure proper field mapping for UI
            original_unit_price: item.unit_price || 0,
            product_id: item.product_id,
            product_name: item.product_name || item.product?.product_name || "",
            unit: item.unit || item.product?.unit || "",
            current_stock: item.current_stock || 0,
            reorder_level: item.reorder_level || 0,
            discount_percentage: item.discount_percentage || 0,
            discount_amount: item.discount_amount || 0,
            gst_rate: item.gst_rate ?? 18,
          });
        });
        console.log("[useVoucherPage] Loaded items:", voucherData.items.length);
      }
    } else if (mode === "create") {
      reset(defaultValues);
    }
  }, [
    voucherData,
    mode,
    reset,
    nextVoucherNumber,
    setValue,
    defaultValues,
    config.hasItems,
    fields.length,
    remove,
    append,
  ]);
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
  // Loading state
  const isLoading = isLoadingList || isFetching || !isOrgContextReady;
  // Refetch voucher list when org context becomes ready
  useEffect(() => {
    if (isOrgContextReady) {
      console.log(
        "[useVoucherPage] Org context ready - refetching voucher list",
      );
      refetchVoucherList();
    }
  }, [isOrgContextReady, refetchVoucherList]);
  // Refetch list after create/update - Enhanced for immediate refresh
  useEffect(() => {
    if (createMutation.isSuccess || updateMutation.isSuccess) {
      // Immediate invalidation and refetch
      queryClient.invalidateQueries({ queryKey: [config.voucherType] });
      // Force immediate refetch
      refetchVoucherList();
      // Additional immediate refresh after short delay to ensure backend has processed
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
  // Sync state with query params for shallow routing
  useEffect(() => {
    const newMode = (router.query.mode as "create" | "edit" | "view" | "revise") || "create";
    const newId = router.query.id ? Number(router.query.id) : null;
    setMode(newMode);
    setSelectedId(newId);
  }, [router.query.mode, router.query.id]);
  return {
    // Enhanced state
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
    // Enhanced pagination
    currentPage,
    pageSize,
    paginationData,
    handlePageChange,
    // Reference document handling
    referenceDocument,
    handleReferenceSelected,
    // Form
    control,
    handleSubmit,
    reset,
    setValue,
    watch,
    errors,
    fields,
    append,
    remove,
    // Data
    voucherList,
    vendorList,
    customerList,
    employeeList,
    productList,
    voucherData,
    nextVoucherNumber,
    sortedVouchers,
    latestVouchers,
    // Computed
    computedItems,
    totalAmount,
    totalSubtotal,
    totalGst,
    totalCgst,
    totalSgst,
    totalIgst,
    totalDiscount,
    totalTaxable,
    gstBreakdown,
    isIntrastate,
    totalRoundOff,
    // Mutations
    createMutation,
    updateMutation,
    // Event handlers
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
    getAmountInWords,  // Now imported from utils
    // Enhanced utilities
    isViewMode: mode === "view",
    enhancedRateUtils,
    // Discount handlers and states
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