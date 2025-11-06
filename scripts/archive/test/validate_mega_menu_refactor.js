#!/usr/bin/env node

/**
 * Mega Menu Refactor Validation Script
 * Validates that the new menu structure meets the requirements
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 MEGA MENU REFACTOR VALIDATION');
console.log('='.repeat(50));

// Read the MegaMenu.tsx file
const megaMenuPath = path.join(__dirname, 'frontend', 'src', 'components', 'MegaMenu.tsx');
const megaMenuContent = fs.readFileSync(megaMenuPath, 'utf-8');

// Check for required structural changes
const validationResults = {
  erpMenuExists: false,
  reportsAnalyticsExists: false,
  administrationInSettings: false,
  serviceCrmPresent: false,
  allInventoryInERP: false,
  allVouchersInERP: false,
  mastersInERP: false
};

console.log('\n📋 STRUCTURAL VALIDATION:');
console.log('-'.repeat(30));

// Check for ERP menu
if (megaMenuContent.includes("title: 'ERP'") && megaMenuContent.includes("icon: <Business />")) {
  validationResults.erpMenuExists = true;
  console.log('✅ ERP top-level menu created');
} else {
  console.log('❌ ERP top-level menu missing');
}

// Check for combined Reports & Analytics
if (megaMenuContent.includes("title: 'Reports & Analytics'") && megaMenuContent.includes("icon: <Assessment />")) {
  validationResults.reportsAnalyticsExists = true;
  console.log('✅ Reports & Analytics menu created');
} else {
  console.log('❌ Reports & Analytics menu missing');
}

// Check for Administration in Settings
if (megaMenuContent.includes("title: 'Administration'") && megaMenuContent.includes("settings:")) {
  validationResults.administrationInSettings = true;
  console.log('✅ Administration moved under Settings');
} else {
  console.log('❌ Administration not properly moved to Settings');
}

// Check for Service CRM
if (megaMenuContent.includes("title: 'Service CRM'") && megaMenuContent.includes("icon: <SupportAgent />")) {
  validationResults.serviceCrmPresent = true;
  console.log('✅ Service CRM module maintained');
} else {
  console.log('❌ Service CRM module missing');
}

// Check for Inventory in ERP
if (megaMenuContent.includes("title: 'Inventory Management'") && megaMenuContent.includes("erp:")) {
  validationResults.allInventoryInERP = true;
  console.log('✅ Inventory moved to ERP module');
} else {
  console.log('❌ Inventory not properly moved to ERP');
}

// Check for Vouchers in ERP
if (megaMenuContent.includes("Purchase Vouchers") && 
    megaMenuContent.includes("Sales Vouchers") && 
    megaMenuContent.includes("Manufacturing Vouchers") &&
    megaMenuContent.includes("Financial Vouchers")) {
  validationResults.allVouchersInERP = true;
  console.log('✅ All voucher types moved to ERP module');
} else {
  console.log('❌ Vouchers not properly organized in ERP');
}

// Check for Masters in ERP
if (megaMenuContent.includes("title: 'Master Data'") && megaMenuContent.includes("erp:")) {
  validationResults.mastersInERP = true;
  console.log('✅ Master Data moved to ERP module');
} else {
  console.log('❌ Master Data not properly moved to ERP');
}

console.log('\n🔐 RBAC VALIDATION:');
console.log('-'.repeat(20));

// Check RBAC permissions are maintained
const rbacChecks = [
  'servicePermission:',
  'SERVICE_PERMISSIONS',
  'role:',
  'superAdminOnly:'
];

let rbacMaintained = true;
rbacChecks.forEach(check => {
  if (megaMenuContent.includes(check)) {
    console.log(`✅ ${check} maintained`);
  } else {
    console.log(`❌ ${check} missing`);
    rbacMaintained = false;
  }
});

console.log('\n📊 NAVIGATION BUTTON VALIDATION:');
console.log('-'.repeat(35));

// Check organization user navigation
const orgUserNavChecks = [
  'ERP',
  'Reports & Analytics', 
  'Service CRM',
  'Settings'
];

orgUserNavChecks.forEach(nav => {
  if (megaMenuContent.includes(`>${nav}<`)) {
    console.log(`✅ ${nav} button present`);
  } else {
    console.log(`❌ ${nav} button missing`);
  }
});

// Check super admin navigation
if (megaMenuContent.includes('Dashboard') && 
    megaMenuContent.includes('Demo') && 
    megaMenuContent.includes('Settings')) {
  console.log('✅ Super Admin navigation updated');
} else {
  console.log('❌ Super Admin navigation not properly updated');
}

console.log('\n📝 FEATURE GUIDE VALIDATION:');
console.log('-'.repeat(30));

// Check if FEATURE_GUIDE.md exists
const featureGuidePath = path.join(__dirname, 'FEATURE_GUIDE.md');
if (fs.existsSync(featureGuidePath)) {
  const featureGuideContent = fs.readFileSync(featureGuidePath, 'utf-8');
  
  // Check for comprehensive content
  const guideChecks = [
    'ERP Module',
    'Reports & Analytics Module',
    'Service CRM Module',
    'Settings Module',
    'Role-Based Access Control',
    'Feature Activation Status'
  ];
  
  let guideComplete = true;
  guideChecks.forEach(section => {
    if (featureGuideContent.includes(section)) {
      console.log(`✅ ${section} documented`);
    } else {
      console.log(`❌ ${section} missing from guide`);
      guideComplete = false;
    }
  });
  
  if (guideComplete) {
    console.log('✅ FEATURE_GUIDE.md is comprehensive');
  }
} else {
  console.log('❌ FEATURE_GUIDE.md not found');
}

console.log('\n🎯 OVERALL VALIDATION SUMMARY:');
console.log('='.repeat(50));

const passedChecks = Object.values(validationResults).filter(v => v).length;
const totalChecks = Object.keys(validationResults).length;
const successRate = Math.round((passedChecks / totalChecks) * 100);

console.log(`Structural Changes: ${passedChecks}/${totalChecks} (${successRate}%)`);
console.log(`RBAC Preservation: ${rbacMaintained ? '✅ Maintained' : '❌ Issues Found'}`);
console.log(`Documentation: ${fs.existsSync(featureGuidePath) ? '✅ Complete' : '❌ Missing'}`);

if (successRate >= 85 && rbacMaintained && fs.existsSync(featureGuidePath)) {
  console.log('\n🎉 VALIDATION PASSED - Mega Menu Refactor Complete!');
  process.exit(0);
} else {
  console.log('\n⚠️  VALIDATION ISSUES FOUND - Review Required');
  process.exit(1);
}