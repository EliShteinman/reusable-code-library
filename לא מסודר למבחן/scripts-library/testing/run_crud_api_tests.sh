#!/bin/bash
# scripts-library/testing/run_crud_api_tests.sh

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
API_URL="${1:-}"
BASE_PATH="${2:-/items}"
if [ -z "$API_URL" ]; then
    echo "ERROR: API Base URL must be provided."
    echo "Usage: $0 <api-url> [base-path]"
    exit 1
fi

FULL_URL="${API_URL}${BASE_PATH}"
ITEM_1_ID=101
ITEM_2_ID=102
NON_EXISTENT_ID=999

# --- Helper Functions ---
function print_header() { echo -e "\n--- $1 ---"; }
function run_test() {
    local test_name="$1"; local expected_status="$2"; shift 2; local curl_cmd=("$@")
    echo -n "Test: $test_name... "
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${curl_cmd[@]}")
    if [ "$STATUS_CODE" = "$expected_status" ]; then
        echo "✅ PASSED (Got $STATUS_CODE)"; return 0
    else
        echo "❌ FAILED (Expected $expected_status, Got $STATUS_CODE)"; exit 1
    fi
}
# --- Test Execution ---
echo "### Starting API Test Suite for: $FULL_URL ###"

print_header "Phase 0: Cleanup"
curl -s -o /dev/null -X DELETE "${FULL_URL}/${ITEM_1_ID}" || true
curl -s -o /dev/null -X DELETE "${FULL_URL}/${ITEM_2_ID}" || true
echo "Cleanup complete."

print_header "Phase 1: CREATE operations"
run_test "Create Item 1" "201" -X POST "${FULL_URL}/" -H "Content-Type: application/json" -d "{\"ID\": ${ITEM_1_ID}, \"name\": \"Test Item 1\"}"
run_test "Create Item 2" "201" -X POST "${FULL_URL}/" -H "Content-Type: application/json" -d "{\"ID\": ${ITEM_2_ID}, \"name\": \"Test Item 2\"}"

print_header "Phase 2: READ operations"
run_test "Get All Items" "200" -X GET "${FULL_URL}/"
run_test "Get Item 1" "200" -X GET "${FULL_URL}/${ITEM_1_ID}"
run_test "Get Non-Existent Item" "404" -X GET "${FULL_URL}/${NON_EXISTENT_ID}"

print_header "Phase 3: Error Handling"
run_test "Create Duplicate Item" "409" -X POST "${FULL_URL}/" -H "Content-Type: application/json" -d "{\"ID\": ${ITEM_1_ID}, \"name\": \"Duplicate\"}"

print_header "Phase 4: UPDATE operation"
run_test "Update Item 2" "200" -X PUT "${FULL_URL}/${ITEM_2_ID}" -H "Content-Type: application/json" -d "{\"name\": \"Updated Item 2\"}"

print_header "Phase 5: DELETE operations"
run_test "Delete Item 1" "204" -X DELETE "${FULL_URL}/${ITEM_1_ID}"
run_test "Verify Deletion of Item 1" "404" -X GET "${FULL_URL}/${ITEM_1_ID}"
run_test "Delete Non-Existent Item" "404" -X DELETE "${FULL_URL}/${NON_EXISTENT_ID}"

print_header "Phase 6: Final Cleanup"
run_test "Cleanup Item 2" "204" -X DELETE "${FULL_URL}/${ITEM_2_ID}"
echo -e "\n🎉 All tests completed successfully! 🎉"