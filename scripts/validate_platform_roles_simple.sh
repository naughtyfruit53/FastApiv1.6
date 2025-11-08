#!/bin/bash
# Simple validation script for platform role refactor

echo "================================================================"
echo "Platform Role Validation"
echo "================================================================"
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FAILED=0
PASSED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Checking for app_admin role in schema${NC}"
echo "================================================================"
if grep -q "APP_ADMIN = \"app_admin\"" app/schemas/user.py; then
    echo -e "${GREEN}✓${NC} Found APP_ADMIN = \"app_admin\" in UserRole enum"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} APP_ADMIN not found in UserRole enum"
    ((FAILED++))
fi

if grep -q "APP_ADMIN = \"app_admin\"" app/schemas/user.py && grep -q "class PlatformUserRole" app/schemas/user.py; then
    echo -e "${GREEN}✓${NC} Found APP_ADMIN in PlatformUserRole enum"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} APP_ADMIN not found in PlatformUserRole enum"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}2. Checking for removal of platform_admin references${NC}"
echo "================================================================"
if ! grep -q "PLATFORM_ADMIN = \"platform_admin\"" app/schemas/user.py; then
    echo -e "${GREEN}✓${NC} No PLATFORM_ADMIN found in schema (correctly removed)"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} PLATFORM_ADMIN still found in schema"
    ((FAILED++))
fi

if grep -q "'app_admin':" app/core/permissions.py; then
    echo -e "${GREEN}✓${NC} Found 'app_admin' key in permissions.py"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} 'app_admin' key not found in permissions.py"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}3. Checking for app_user role removal${NC}"
echo "================================================================"
if ! grep -q "app_user" app/schemas/user.py && ! grep -q "APP_USER" app/schemas/user.py; then
    echo -e "${GREEN}✓${NC} No app_user references in schema"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Found app_user references in schema"
    ((FAILED++))
fi

if ! grep -q "'app_user'" app/core/permissions.py; then
    echo -e "${GREEN}✓${NC} No app_user references in permissions"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Found app_user references in permissions"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}4. Checking API endpoint updates${NC}"
echo "================================================================"
if grep -q "UserRole.APP_ADMIN" app/api/v1/app_users.py; then
    echo -e "${GREEN}✓${NC} Found UserRole.APP_ADMIN in app_users.py"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} UserRole.APP_ADMIN not found in app_users.py"
    ((FAILED++))
fi

if grep -q "super_admin can create/manage" app/api/v1/app_users.py || grep -q "Only super admins can" app/api/v1/app_users.py; then
    echo -e "${GREEN}✓${NC} Found super_admin only enforcement in app_users.py"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Super admin enforcement not found in app_users.py"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}5. Checking frontend updates${NC}"
echo "================================================================"
if grep -q "app_admin" frontend/src/components/AdminUserForm.tsx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Found app_admin in AdminUserForm.tsx"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} app_admin not found in AdminUserForm.tsx"
    ((FAILED++))
fi

if ! grep -q "platform_admin" frontend/src/components/AdminUserForm.tsx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} No platform_admin references in AdminUserForm.tsx"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Found platform_admin in AdminUserForm.tsx"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}6. Checking documentation${NC}"
echo "================================================================"
if [ -f "PLATFORM_ADMIN_GUIDE.md" ]; then
    echo -e "${GREEN}✓${NC} Found PLATFORM_ADMIN_GUIDE.md"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} PLATFORM_ADMIN_GUIDE.md not found"
    ((FAILED++))
fi

if grep -q "app_admin" PLATFORM_ADMIN_GUIDE.md; then
    echo -e "${GREEN}✓${NC} PLATFORM_ADMIN_GUIDE.md mentions app_admin"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} PLATFORM_ADMIN_GUIDE.md doesn't mention app_admin"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}7. Checking test files${NC}"
echo "================================================================"
if [ -f "tests/test_platform_permissions.py" ]; then
    echo -e "${GREEN}✓${NC} Found test_platform_permissions.py"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} test_platform_permissions.py not found"
    ((FAILED++))
fi

if [ -f "tests/test_platform_roles_simple.py" ]; then
    echo -e "${GREEN}✓${NC} Found test_platform_roles_simple.py"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} test_platform_roles_simple.py not found"
    ((FAILED++))
fi

echo ""
echo "================================================================"
echo "Validation Summary"
echo "================================================================"
TOTAL=$((PASSED + FAILED))
echo "Passed: $PASSED / $TOTAL"
echo "Failed: $FAILED / $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL VALIDATIONS PASSED${NC}"
    echo ""
    echo "Platform role implementation is correct!"
    exit 0
else
    echo -e "${RED}✗ SOME VALIDATIONS FAILED${NC}"
    echo ""
    echo "Please review the failed checks above."
    exit 1
fi
