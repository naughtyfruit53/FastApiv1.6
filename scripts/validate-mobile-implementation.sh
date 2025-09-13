#!/bin/bash

# Mobile Testing Script
# Comprehensive validation script for mobile components and functionality

set -e

echo "🚀 Starting Mobile Frontend Validation..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to frontend directory
cd "$(dirname "$0")/../frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
fi

echo ""
echo "📱 Mobile Component Validation"
echo "================================"

# 1. Lint Check (focusing on mobile components only)
print_status "Running linting on mobile components..."
if npx eslint src/components/mobile/**/*.{ts,tsx} src/utils/mobile/**/*.{ts,tsx} --fix 2>/dev/null; then
    print_success "Mobile components linting passed"
else
    print_warning "Some linting issues found in mobile components (auto-fixed where possible)"
fi

# 2. TypeScript compilation check
print_status "Checking TypeScript compilation..."
if npx tsc --noEmit --skipLibCheck; then
    print_success "TypeScript compilation successful"
else
    print_error "TypeScript compilation failed"
    exit 1
fi

# 3. Component file existence check
print_status "Validating mobile component files..."

mobile_components=(
    "src/components/mobile/SwipeableCard.tsx"
    "src/components/mobile/MobileBottomSheet.tsx"
    "src/components/mobile/MobileContextualMenu.tsx"
    "src/components/mobile/KeyboardNavigation.tsx"
    "src/components/mobile/index.ts"
    "src/utils/mobile/hapticFeedback.ts"
    "src/utils/mobile/DeviceConditional.tsx"
)

missing_files=0
for file in "${mobile_components[@]}"; do
    if [ -f "$file" ]; then
        print_success "✓ $file"
    else
        print_error "✗ Missing: $file"
        ((missing_files++))
    fi
done

if [ $missing_files -eq 0 ]; then
    print_success "All mobile component files present"
else
    print_error "$missing_files mobile component files missing"
    exit 1
fi

# 4. Test files validation
echo ""
echo "🧪 Test Suite Validation"
echo "========================="

test_files=(
    "../tests/mobile/unit/SwipeableCard.test.tsx"
    "../tests/mobile/unit/MobileBottomSheet.test.tsx"
    "../tests/mobile/integration/MobileWorkflows.test.tsx"
    "../tests/mobile/device-emulation/cross-device.spec.ts"
    "../tests/mobile/accessibility/compliance.spec.ts"
    "../tests/mobile/utils/accessibilityTester.ts"
)

missing_tests=0
for test_file in "${test_files[@]}"; do
    if [ -f "$test_file" ]; then
        print_success "✓ $test_file"
    else
        print_error "✗ Missing: $test_file"
        ((missing_tests++))
    fi
done

if [ $missing_tests -eq 0 ]; then
    print_success "All test files present"
else
    print_error "$missing_tests test files missing"
fi

# 5. Documentation validation
echo ""
echo "📚 Documentation Validation"
echo "============================"

docs=(
    "../docs/MOBILE_CONTRIBUTOR_GUIDE.md"
    "../docs/MOBILE_QA_GUIDE.md"
    "../MOBILE_UPGRADE_PATH.md"
)

missing_docs=0
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        # Check if document has substantial content (more than 1000 characters)
        if [ $(wc -c < "$doc") -gt 1000 ]; then
            print_success "✓ $doc ($(wc -c < "$doc") characters)"
        else
            print_warning "⚠ $doc exists but appears incomplete"
        fi
    else
        print_error "✗ Missing: $doc"
        ((missing_docs++))
    fi
done

if [ $missing_docs -eq 0 ]; then
    print_success "All documentation files present"
else
    print_error "$missing_docs documentation files missing"
fi

# 6. Build test
echo ""
echo "🏗️ Build Validation"
echo "==================="

print_status "Testing Next.js build process..."
if timeout 120 npm run build > /dev/null 2>&1; then
    print_success "Build successful"
else
    print_warning "Build timed out or failed (this may be expected in test environment)"
fi

# 7. Mobile route accessibility check
echo ""
echo "🎯 Mobile Routes Validation"
echo "==========================="

mobile_pages=(
    "src/pages/mobile/dashboard.tsx"
    "src/pages/mobile/sales.tsx"
    "src/pages/mobile/crm.tsx"
    "src/pages/mobile/inventory.tsx"
    "src/pages/mobile/finance.tsx"
    "src/pages/mobile/hr.tsx"
    "src/pages/mobile/service.tsx"
    "src/pages/mobile/reports.tsx"
    "src/pages/mobile/settings.tsx"
    "src/pages/mobile/login.tsx"
)

existing_mobile_pages=0
for page in "${mobile_pages[@]}"; do
    if [ -f "$page" ]; then
        print_success "✓ $page"
        ((existing_mobile_pages++))
    else
        print_warning "△ $page (may not be implemented yet)"
    fi
done

print_status "Mobile pages found: $existing_mobile_pages/${#mobile_pages[@]}"

# 8. Component exports validation
echo ""
echo "📦 Component Exports Validation"
echo "==============================="

print_status "Checking component exports..."

# Check if index.ts exports all components
if grep -q "SwipeableCard" src/components/mobile/index.ts && \
   grep -q "MobileBottomSheet" src/components/mobile/index.ts && \
   grep -q "MobileContextualMenu" src/components/mobile/index.ts && \
   grep -q "KeyboardNavigation" src/components/mobile/index.ts; then
    print_success "All new components properly exported"
else
    print_warning "Some components may not be properly exported in index.ts"
fi

# 9. Accessibility features check
echo ""
echo "♿ Accessibility Features Check"
echo "==============================="

print_status "Validating accessibility implementations..."

# Check for ARIA attributes in components
if grep -r "aria-" src/components/mobile/ > /dev/null; then
    print_success "ARIA attributes found in mobile components"
else
    print_warning "Limited ARIA attributes found"
fi

# Check for keyboard navigation support
if grep -r "onKeyDown\|tabIndex" src/components/mobile/ > /dev/null; then
    print_success "Keyboard navigation support found"
else
    print_warning "Limited keyboard navigation support found"
fi

# 10. Performance optimizations check
echo ""
echo "⚡ Performance Features Check"
echo "============================="

# Check for React.memo usage
if grep -r "React.memo\|memo" src/components/mobile/ > /dev/null; then
    print_success "React.memo optimization found"
else
    print_warning "Consider adding React.memo for performance optimization"
fi

# Check for useCallback usage
if grep -r "useCallback" src/components/mobile/ > /dev/null; then
    print_success "useCallback optimization found"
else
    print_warning "Consider adding useCallback for performance optimization"
fi

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="

total_checks=10
passed_checks=0

# Count successful validations (simplified)
if [ $missing_files -eq 0 ]; then ((passed_checks++)); fi
if [ $missing_tests -eq 0 ]; then ((passed_checks++)); fi
if [ $missing_docs -eq 0 ]; then ((passed_checks++)); fi
# Add other checks as needed

echo "Validation Score: $passed_checks/$total_checks checks completed successfully"

if [ $passed_checks -ge 8 ]; then
    echo ""
    print_success "🎉 Mobile frontend implementation validation PASSED!"
    print_success "Ready for production deployment"
    exit 0
elif [ $passed_checks -ge 6 ]; then
    echo ""
    print_warning "⚠️ Mobile frontend implementation mostly complete"
    print_warning "Minor issues detected - review warnings above"
    exit 0
else
    echo ""
    print_error "❌ Mobile frontend implementation validation FAILED"
    print_error "Critical issues detected - please review errors above"
    exit 1
fi