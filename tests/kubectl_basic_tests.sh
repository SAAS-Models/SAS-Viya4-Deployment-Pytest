#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

NAMESPACE="sas-viya"
TEST_RESULTS=()
FAILED_TESTS=0

# Function to run test
run_test() {
    local test_name=$1
    local command=$2
    local expected=$3
    
    echo -e "${YELLOW}Running: ${test_name}${NC}"
    
    result=$(eval $command 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: ${test_name}"
        TEST_RESULTS+=("PASS: ${test_name}")
    else
        echo -e "${RED}✗ FAILED${NC}: ${test_name}"
        echo "  Error: ${result}"
        TEST_RESULTS+=("FAIL: ${test_name}")
        ((FAILED_TESTS++))
    fi
    echo ""
}

# Test 1: Cluster connectivity
run_test "Cluster Connectivity" \
    "kubectl cluster-info" \
    "0"

# Test 2: Namespace exists
run_test "SAS Viya Namespace Exists" \
    "kubectl get namespace ${NAMESPACE}" \
    "0"

# Test 3: Node availability
run_test "Minimum Nodes Available" \
    "test \$(kubectl get nodes --no-headers | grep -c Ready) -ge 3" \
    "0"

# Test 4: Node resources
echo -e "${YELLOW}Node Resources:${NC}"
kubectl top nodes

# Test 5: Storage classes
run_test "Storage Classes Available" \
    "kubectl get storageclass | grep -E 'gp2|gp3'" \
    "0"

# Generate summary
echo -e "\n${YELLOW}========== TEST SUMMARY ==========${NC}"
for result in "${TEST_RESULTS[@]}"; do
    if [[ $result == PASS* ]]; then
        echo -e "${GREEN}$result${NC}"
    else
        echo -e "${RED}$result${NC}"
    fi
done

echo -e "\nTotal Failed Tests: ${FAILED_TESTS}"
exit $FAILED_TESTS
