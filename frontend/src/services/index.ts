// frontend/src/services/index.ts
// Centralized exports for all services

// Core Services
export { default as api } from "../lib/api";

// Business Module Services
export * from "./hrService";
export * from "./marketingService";
export * from "./crmService";
export * from "./serviceDeskService";

// Existing Services
export * as AuthService from "./authService";
export * as AnalyticsService from "./analyticsService";
export * as StockService from "./stockService";
export * as VouchersService from "./vouchersService";
export * as MasterService from "./masterService";
export * as NotificationService from "./notificationService";
export * as OrganizationService from "./organizationService";
export * as RbacService from "./rbacService";
export * as ResetService from "./resetService";
export * as EntityService from "./entityService";
export * as FeedbackService from "./feedbackService";
export * as DispatchService from "./dispatchService";
export * as SlaService from "./slaService";
export * as ServiceAnalyticsService from "./serviceAnalyticsService";
export * as AssetService from "./assetService";
export * as TransportService from "./transportService";
export * as AdminService from "./adminService";
export * as PdfService from "./pdfService";
export * as NotificationWorkflow from "./notificationWorkflow";

// New Email Service
export * as EmailService from "./emailService";