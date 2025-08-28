// frontend/src/services/index.ts
// Centralized exports for all services

// Core Services
export { default as api } from '../lib/api';

// Business Module Services
export * from './hrService';
export * from './marketingService';
export * from './crmService';
export * from './serviceDeskService';

// Existing Services
export * from './authService';
export * from './analyticsService';
export * from './stockService';
export * from './vouchersService';
export * from './masterService';
export * from './notificationService';
export * from './organizationService';
export * from './rbacService';
export * from './resetService';
export * from './entityService';
export * from './feedbackService';
export * from './dispatchService';
export * from './slaService';
export * from './serviceAnalyticsService';
export * from './assetService';
export * from './transportService';
export * from './adminService';
export * from './pdfService';
export * from './notificationWorkflow';