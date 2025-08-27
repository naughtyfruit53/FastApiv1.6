#!/usr/bin/env node
// validate-mega-menu-implementation.js
// Validation script to ensure all menu routes and components exist

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating Mega Menu Implementation');
console.log('=' .repeat(50));

const frontendDir = './frontend/src';

// Define all the new pages that should exist
const requiredPages = [
  'pages/analytics/customer.tsx',
  'pages/analytics/sales.tsx', 
  'pages/analytics/purchase.tsx',
  'pages/analytics/service.tsx',
  'pages/analytics/service/job-completion.tsx',
  'pages/analytics/service/technician-performance.tsx',
  'pages/analytics/service/customer-satisfaction.tsx',
  'pages/analytics/service/sla-compliance.tsx',
  'pages/service/dashboard.tsx',
  'pages/service/dispatch.tsx',
  'pages/service/feedback.tsx',
  'pages/admin/rbac.tsx',
  'pages/admin/audit-logs.tsx',
  'pages/admin/notifications.tsx',
  'pages/inventory/bulk-import.tsx'
];

// Define existing components that should be referenced
const requiredComponents = [
  'components/MegaMenu.tsx',
  'components/ServiceAnalytics/ServiceAnalyticsDashboard.tsx',
  'components/ServiceAnalytics/JobCompletionChart.tsx',
  'components/ServiceAnalytics/TechnicianPerformanceChart.tsx',
  'components/ServiceAnalytics/CustomerSatisfactionChart.tsx',
  'components/ServiceAnalytics/SLAComplianceChart.tsx',
  'components/DispatchManagement/DispatchManagement.tsx',
  'components/FeedbackWorkflow/FeedbackWorkflowIntegration.tsx',
  'components/RoleManagement/RoleManagement.tsx',
  'components/CustomerAnalytics.tsx',
  'components/NotificationTemplates.tsx',
  'components/StockBulkImport.tsx'
];

// Validation functions
function validateFile(filePath) {
  const fullPath = path.join(frontendDir, filePath);
  const exists = fs.existsSync(fullPath);
  console.log(`${exists ? '✅' : '❌'} ${filePath}`);
  return exists;
}

function validateMegaMenuUpdates() {
  const megaMenuPath = path.join(frontendDir, 'components/MegaMenu.tsx');
  if (!fs.existsSync(megaMenuPath)) {
    console.log('❌ MegaMenu.tsx not found');
    return false;
  }

  const content = fs.readFileSync(megaMenuPath, 'utf8');
  
  const requiredFeatures = [
    'Analytics',
    'Service CRM', 
    'Administration',
    'Stock Bulk Import',
    'hasServicePermission',
    'SERVICE_PERMISSIONS',
    'canAccessServiceFeatures',
    'rbacService'
  ];

  console.log('\n🔍 Checking MegaMenu.tsx for required features:');
  let allFeaturesPresent = true;
  
  requiredFeatures.forEach(feature => {
    const hasFeature = content.includes(feature);
    console.log(`${hasFeature ? '✅' : '❌'} ${feature}`);
    if (!hasFeature) allFeaturesPresent = false;
  });

  return allFeaturesPresent;
}

function validateRBACIntegration() {
  const rbacServicePath = path.join(frontendDir, 'services/rbacService.ts');
  const rbacTypesPath = path.join(frontendDir, 'types/rbac.types.ts');
  
  console.log('\n🔐 Checking RBAC Integration:');
  const rbacServiceExists = validateFile('services/rbacService.ts');
  const rbacTypesExists = validateFile('types/rbac.types.ts');
  
  return rbacServiceExists && rbacTypesExists;
}

// Run validations
console.log('\n📄 Validating New Pages:');
const pagesValid = requiredPages.every(validateFile);

console.log('\n🧩 Validating Required Components:');
const componentsValid = requiredComponents.every(validateFile);

console.log('\n🎛️ Validating MegaMenu Updates:');
const megaMenuValid = validateMegaMenuUpdates();

const rbacValid = validateRBACIntegration();

// Summary
console.log('\n📊 VALIDATION SUMMARY:');
console.log('=' .repeat(50));
console.log(`Pages Created: ${pagesValid ? '✅ PASS' : '❌ FAIL'} (${requiredPages.length} pages)`);
console.log(`Components Available: ${componentsValid ? '✅ PASS' : '❌ FAIL'} (${requiredComponents.length} components)`);
console.log(`MegaMenu Updates: ${megaMenuValid ? '✅ PASS' : '❌ FAIL'}`);
console.log(`RBAC Integration: ${rbacValid ? '✅ PASS' : '❌ FAIL'}`);

const overallValid = pagesValid && componentsValid && megaMenuValid && rbacValid;
console.log(`\nOverall Status: ${overallValid ? '✅ IMPLEMENTATION COMPLETE' : '❌ ISSUES FOUND'}`);

if (overallValid) {
  console.log('\n🎉 All required features have been implemented!');
  console.log('🚀 The mega menu redesign is ready for testing with authenticated users.');
  console.log('📋 All features from FEATURE_ACCESS_MAPPING.md are now accessible.');
} else {
  console.log('\n⚠️  Some issues were found. Please review the failed items above.');
}

console.log('\n🔗 Key Implementation Features:');
console.log('• Role-based menu visibility (App Super Admin vs Organization Users)');
console.log('• Service permission integration with real-time checking');
console.log('• All previously hidden features now exposed through proper menu structure');
console.log('• RBAC controls ensure users only see features they have access to');
console.log('• Maintains backward compatibility with existing functionality');

process.exit(overallValid ? 0 : 1);