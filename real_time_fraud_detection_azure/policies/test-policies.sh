#!/bin/bash

# Policy Testing Script
# This script validates OPA policies for the fraud detection system

set -e

echo "=========================================="
echo "  OPA Policy Testing Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if OPA is installed
if ! command -v opa &> /dev/null; then
    echo -e "${RED}ERROR: OPA is not installed${NC}"
    echo "Please install OPA from: https://www.openpolicyagent.org/docs/latest/#running-opa"
    exit 1
fi

echo -e "${GREEN}✓ OPA found: $(opa version)${NC}"
echo ""

# Check if Conftest is installed (optional)
if command -v conftest &> /dev/null; then
    echo -e "${GREEN}✓ Conftest found: $(conftest --version)${NC}"
    CONFTEST_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Conftest not found (optional)${NC}"
    CONFTEST_AVAILABLE=false
fi
echo ""

# Run OPA tests
echo "=========================================="
echo "Running OPA Policy Tests..."
echo "=========================================="
echo ""

if opa test policies/ -v; then
    echo ""
    echo -e "${GREEN}✓ All OPA policy tests passed!${NC}"
    TEST_STATUS=0
else
    echo ""
    echo -e "${RED}✗ Some OPA policy tests failed${NC}"
    TEST_STATUS=1
fi

echo ""
echo "=========================================="
echo "Verifying Policy Syntax..."
echo "=========================================="
echo ""

# Verify Terraform policies
echo "Checking Terraform policies..."
if conftest verify --policy policies/terraform 2>/dev/null; then
    echo -e "${GREEN}✓ Terraform policies syntax valid${NC}"
elif [ "$CONFTEST_AVAILABLE" = true ]; then
    echo -e "${YELLOW}⚠ Could not verify Terraform policies (may not have tests)${NC}"
fi

# Verify Kubernetes policies
echo "Checking Kubernetes policies..."
if conftest verify --policy policies/kubernetes 2>/dev/null; then
    echo -e "${GREEN}✓ Kubernetes policies syntax valid${NC}"
elif [ "$CONFTEST_AVAILABLE" = true ]; then
    echo -e "${YELLOW}⚠ Could not verify Kubernetes policies (may not have tests)${NC}"
fi

echo ""
echo "=========================================="
echo "Policy Coverage Report"
echo "=========================================="
echo ""

# Count policy files
TERRAFORM_POLICIES=$(find policies/terraform -name "*.rego" | wc -l)
KUBERNETES_POLICIES=$(find policies/kubernetes -name "*.rego" | wc -l)
GATEKEEPER_CONSTRAINTS=$(find policies/kubernetes/gatekeeper -name "*.yaml" | wc -l)
TEST_FILES=$(find policies/tests -name "*.rego" | wc -l)

echo "Terraform Policies: $TERRAFORM_POLICIES"
echo "Kubernetes Policies: $KUBERNETES_POLICIES"
echo "Gatekeeper Constraints: $GATEKEEPER_CONSTRAINTS"
echo "Test Files: $TEST_FILES"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""

if [ $TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Test policies against actual Terraform plans"
    echo "  2. Deploy Gatekeeper constraints to Kubernetes"
    echo "  3. Integrate into CI/CD pipeline"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi

