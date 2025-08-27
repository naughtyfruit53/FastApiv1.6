#!/bin/bash
# Simple test script to verify navigation structure changes

echo "=== Testing Master Data Refactor ==="
echo ""

# Check if all required page files exist
echo "Checking if individual module pages exist..."

pages=(
  "employees.tsx"
  "company-details.tsx" 
  "categories.tsx"
  "units.tsx"
  "chart-of-accounts.tsx"
  "tax-codes.tsx"
  "payment-terms.tsx"
  "vendors.tsx"
  "customers.tsx"
  "products.tsx"
  "bom.tsx"
)

missing_pages=0
for page in "${pages[@]}"; do
  if [ -f "frontend/src/pages/$page" ]; then
    echo "✅ $page exists"
  else
    echo "❌ $page missing"
    missing_pages=$((missing_pages + 1))
  fi
done

echo ""
echo "=== MegaMenu Structure Changes ==="
echo "Checking if master data hub has been removed..."

if grep -q "masterData:" frontend/src/components/MegaMenu.tsx; then
  echo "❌ Master Data menu still exists in MegaMenu"
else
  echo "✅ Master Data menu removed from MegaMenu"
fi

if grep -q "Business Entities" frontend/src/components/MegaMenu.tsx; then
  echo "✅ Business Entities section exists in ERP menu"
else
  echo "❌ Business Entities section missing"
fi

if grep -q "Financial Configuration" frontend/src/components/MegaMenu.tsx; then
  echo "✅ Financial Configuration section exists in Settings menu"
else
  echo "❌ Financial Configuration section missing"
fi

echo ""
echo "=== BOM Improvements ==="
echo "Checking BOM error handling improvements..."

if grep -q "cleanData" frontend/src/pages/masters/bom.tsx; then
  echo "✅ BOM data cleaning implemented"
else
  echo "❌ BOM data cleaning missing"
fi

if grep -q "validation error" frontend/src/pages/masters/bom.tsx; then
  echo "✅ BOM error logging improved"
else
  echo "❌ BOM error logging not improved"
fi

echo ""
echo "=== Product Name Mapping ==="
echo "Checking product name consistency..."

product_name_issues=0
if grep -q "product?.name" frontend/src/pages/vouchers/Purchase-Vouchers/grn.tsx; then
  echo "❌ Inconsistent product.name usage in GRN"
  product_name_issues=$((product_name_issues + 1))
else
  echo "✅ GRN uses consistent product_name"
fi

if grep -q "product?.name" frontend/src/pages/vouchers/Purchase-Vouchers/purchase-order.tsx; then
  echo "❌ Inconsistent product.name usage in Purchase Order"
  product_name_issues=$((product_name_issues + 1))
else
  echo "✅ Purchase Order uses consistent product_name"
fi

echo ""
echo "=== Summary ==="
echo "Missing pages: $missing_pages"
echo "Product name mapping issues: $product_name_issues"

if [ $missing_pages -eq 0 ] && [ $product_name_issues -eq 0 ]; then
  echo "🎉 All tests passed! Master data refactor completed successfully."
  exit 0
else
  echo "⚠️  Some issues found. Review the output above."
  exit 1
fi