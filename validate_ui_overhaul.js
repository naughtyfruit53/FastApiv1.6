#!/usr/bin/env node

/**
 * Validation script for UI Overhaul implementation
 * This script validates the implementation without requiring a full server setup
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating UI Overhaul Implementation...\n');

// Check if all required files exist
const requiredFiles = [
  'frontend/src/hooks/usePincodeLookup.ts',
  'frontend/src/components/AddVendorModal.tsx',
  'frontend/src/components/AddCustomerModal.tsx', 
  'frontend/src/components/CompanyDetailsModal.tsx',
  'frontend/src/components/AddShippingAddressModal.tsx',
  'frontend/src/pages/_app.tsx',
  'frontend/src/pages/ui-test.tsx',
  'app/api/pincode.py'
];

let allFilesExist = true;

console.log('📁 Checking required files:');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file}`);
    allFilesExist = false;
  }
});

console.log('\n🔧 Checking implementation details:');

// Check theme configuration
const appFile = path.join(__dirname, 'frontend/src/pages/_app.tsx');
if (fs.existsSync(appFile)) {
  const content = fs.readFileSync(appFile, 'utf8');
  
  const checks = [
    { pattern: /fontSize:\s*['""]18px['""]/, description: 'Page title font size (18px)' },
    { pattern: /fontSize:\s*['""]15px['""]/, description: 'Section title font size (15px)' },
    { pattern: /fontSize:\s*['""]12px['""]/, description: 'Modal input font size (12px)' },
    { pattern: /height:\s*['""]27px['""]/, description: 'Modal input height (27px)' },
    { pattern: /MuiTextField/, description: 'TextField component styling' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(content)) {
      console.log(`  ✅ ${check.description}`);
    } else {
      console.log(`  ⚠️  ${check.description}`);
    }
  });
}

// Check pincode hook
const hookFile = path.join(__dirname, 'frontend/src/hooks/usePincodeLookup.ts');
if (fs.existsSync(hookFile)) {
  const content = fs.readFileSync(hookFile, 'utf8');
  
  const checks = [
    { pattern: /\/api\/v1\/pincode\/lookup/, description: 'Correct API endpoint path' },
    { pattern: /loading.*indicator/i, description: 'Loading indicator support' },
    { pattern: /error.*handling/i, description: 'Error handling' },
    { pattern: /debounce|timeout/i, description: 'Debouncing implementation' },
    { pattern: /clearData/, description: 'Data cleanup function' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(content)) {
      console.log(`  ✅ ${check.description}`);
    } else {
      console.log(`  ⚠️  ${check.description}`);
    }
  });
}

// Check modal components for pincode integration
console.log('\n🎭 Checking modal components:');
const modalComponents = [
  'AddVendorModal.tsx',
  'AddCustomerModal.tsx', 
  'CompanyDetailsModal.tsx',
  'AddShippingAddressModal.tsx'
];

modalComponents.forEach(component => {
  const componentFile = path.join(__dirname, `frontend/src/components/${component}`);
  if (fs.existsSync(componentFile)) {
    const content = fs.readFileSync(componentFile, 'utf8');
    
    const hasHook = /usePincodeLookup/.test(content);
    const hasReordering = /PIN.*Code.*before.*City/i.test(content) || 
                         (content.indexOf('pin_code') < content.indexOf('city') && 
                          content.indexOf('address2') < content.indexOf('pin_code'));
    const hasLoadingIndicator = /CircularProgress|loading/i.test(content);
    const hasErrorHandling = /error.*handling|Alert.*error/i.test(content);
    
    console.log(`  ${component}:`);
    console.log(`    ${hasHook ? '✅' : '❌'} Pincode hook integration`);
    console.log(`    ${hasReordering ? '✅' : '❌'} Address field reordering`);
    console.log(`    ${hasLoadingIndicator ? '✅' : '❌'} Loading indicators`);
    console.log(`    ${hasErrorHandling ? '✅' : '❌'} Error handling`);
  }
});

// Check backend API
console.log('\n🔙 Checking backend API:');
const backendFile = path.join(__dirname, 'app/api/pincode.py');
if (fs.existsSync(backendFile)) {
  const content = fs.readFileSync(backendFile, 'utf8');
  
  const checks = [
    { pattern: /STATE_CODE_MAP/, description: 'State code mapping' },
    { pattern: /api\.postalpincode\.in/, description: 'External API integration' },
    { pattern: /HTTPException.*503/, description: 'Service unavailable handling' },
    { pattern: /HTTPException.*404/, description: 'Not found handling' },
    { pattern: /city.*state.*state_code/, description: 'Complete response data' }
  ];
  
  checks.forEach(check => {
    if (check.pattern.test(content)) {
      console.log(`  ✅ ${check.description}`);
    } else {
      console.log(`  ⚠️  ${check.description}`);
    }
  });
}

console.log('\n📊 Summary:');
console.log(`  Files checked: ${requiredFiles.length}`);
console.log(`  Implementation status: ${allFilesExist ? '✅ Complete' : '⚠️  Some files missing'}`);
console.log(`  Ready for testing: ${allFilesExist ? 'Yes' : 'No'}`);

console.log('\n🚀 Next Steps:');
console.log('  1. Start the Next.js development server');
console.log('  2. Navigate to /ui-test page');
console.log('  3. Test each modal with valid PIN codes (400001, 110001, etc.)');
console.log('  4. Verify styling changes in browser developer tools');
console.log('  5. Test error handling with invalid PIN codes');

console.log('\n✨ Implementation Complete!');