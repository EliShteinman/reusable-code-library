#!/bin/bash
# scripts-library/openshift/run_comprehensive_api_tests.sh
# Advanced API testing script based on exam solution patterns

# ================================================================================
#  Comprehensive End-to-End API Test Script
#  Based on the advanced patterns from the MongoDB FastAPI exam solution
# ================================================================================

# --- Configuration ---
API_URL="${1:-}"
BASE_PATH="${2:-/soldiersdb}"
TEST_SUITE="${3:-full}"

if [ -z "$API_URL" ]; then
    echo "ERROR: API Base URL must be provided as the first argument"
    echo "Usage: $0 <api-url> [base-path] [test-suite]"
    echo "Example: $0 https://my-app.example.com /soldiersdb full"
    echo "Test suites: basic, full, performance, security"
    exit 1
fi

FULL_URL="${API_URL}${BASE_PATH}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="api_tests_${TIMESTAMP}.log"

# Test data
SOLDIER_1_ID=301
SOLDIER_2_ID=302
INVALID_ID=999999
NEGATIVE_ID=-5

JSON_SOLDIER_1='{"ID": 301, "first_name": "Yitzhak", "last_name": "Rabin", "phone_number": 5551922, "rank": "Chief of Staff"}'
JSON_SOLDIER_2='{"ID": 302, "first_name": "Ariel", "last_name": "Sharon", "phone_number": 5551928, "rank": "Major General"}'
JSON_UPDATE='{"rank": "Prime Minister", "phone_number": 5552001}'
JSON_INVALID='{"ID": 404, "first_name": "Missing", "last_name": "Fields"}'
JSON_MALFORMED='{"ID": 505, "first_name": "Bad", "last_name"'

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# --- Helper Functions ---
print_header() {
    echo ""
    echo "================================================================="
    echo "   $1"
    echo "================================================================="
}

print_subheader() {
    echo ""
    echo "--- $1 ---"
}

log_test() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

run_test() {
    local test_name="$1"
    local expected_status="$2"
    local curl_cmd="$3"
    local description="$4"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Test $TOTAL_TESTS: $test_name... "

    # Execute curl command and capture both status and response
    RESPONSE=$(eval "$curl_cmd" -w "\n%{http_code}" -s)
    STATUS_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    log_test "TEST: $test_name - Expected: $expected_status, Got: $STATUS_CODE"

    if [ "$STATUS_CODE" = "$expected_status" ]; then
        echo "✅ PASSED"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        log_test "RESULT: PASSED - $description"
        return 0
    else
        echo "❌ FAILED (Expected $expected_status, got $STATUS_CODE)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_test "RESULT: FAILED - Expected $expected_status, got $STATUS_CODE"
        log_test "RESPONSE: $BODY"
        return 1
    fi
}

cleanup_test_data() {
    echo "Cleaning up test data..."
    curl -s -o /dev/null -X DELETE "${FULL_URL}/${SOLDIER_1_ID}"
    curl -s -o /dev/null -X DELETE "${FULL_URL}/${SOLDIER_2_ID}"
    curl -s -o /dev/null -X DELETE "${FULL_URL}/999"
}

# --- Test Suites ---
run_basic_tests() {
    print_header "BASIC FUNCTIONALITY TESTS"

    print_subheader "Health Checks"
    run_test "Liveness Check" "200" \
        "curl '${API_URL}/'" \
        "Basic liveness probe"

    run_test "Readiness Check" "200" \
        "curl '${API_URL}/health'" \
        "Detailed readiness probe"

    print_subheader "CRUD Operations"
    run_test "Get Empty Collection" "200" \
        "curl '${FULL_URL}/'" \
        "Should return empty array initially"

    run_test "Create Soldier 1" "201" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_SOLDIER_1'" \
        "Create new soldier record"

    run_test "Get Soldier by ID" "200" \
        "curl '${FULL_URL}/${SOLDIER_1_ID}'" \
        "Retrieve specific soldier"

    run_test "Get All Soldiers" "200" \
        "curl '${FULL_URL}/'" \
        "Should return array with one soldier"

    run_test "Update Soldier" "200" \
        "curl -X PUT '${FULL_URL}/${SOLDIER_1_ID}' -H 'Content-Type: application/json' -d '$JSON_UPDATE'" \
        "Update soldier information"

    run_test "Delete Soldier" "204" \
        "curl -X DELETE '${FULL_URL}/${SOLDIER_1_ID}'" \
        "Delete soldier record"

    run_test "Verify Deletion" "404" \
        "curl '${FULL_URL}/${SOLDIER_1_ID}'" \
        "Confirm soldier was deleted"
}

run_error_handling_tests() {
    print_header "ERROR HANDLING TESTS"

    # Create test data first
    curl -s -o /dev/null -X POST "${FULL_URL}/" -H "Content-Type: application/json" -d "$JSON_SOLDIER_1"

    print_subheader "Validation Errors"
    run_test "Duplicate ID Error" "409" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_SOLDIER_1'" \
        "Should reject duplicate soldier ID"

    run_test "Invalid Data Error" "422" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_INVALID'" \
        "Should reject missing required fields"

    run_test "Malformed JSON Error" "422" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_MALFORMED'" \
        "Should reject malformed JSON"

    print_subheader "Not Found Errors"
    run_test "Get Nonexistent Soldier" "404" \
        "curl '${FULL_URL}/${INVALID_ID}'" \
        "Should return 404 for missing soldier"

    run_test "Update Nonexistent Soldier" "404" \
        "curl -X PUT '${FULL_URL}/${INVALID_ID}' -H 'Content-Type: application/json' -d '$JSON_UPDATE'" \
        "Should return 404 when updating missing soldier"

    run_test "Delete Nonexistent Soldier" "404" \
        "curl -X DELETE '${FULL_URL}/${INVALID_ID}'" \
        "Should return 404 when deleting missing soldier"

    print_subheader "Input Validation"
    run_test "Negative ID Error" "422" \
        "curl '${FULL_URL}/${NEGATIVE_ID}'" \
        "Should reject negative soldier ID"

    # Cleanup
    curl -s -o /dev/null -X DELETE "${FULL_URL}/${SOLDIER_1_ID}"
}

run_performance_tests() {
    print_header "PERFORMANCE TESTS"

    print_subheader "Load Testing"

    # Bulk create test
    echo "Creating 10 soldiers for load testing..."
    for i in $(seq 1001 1010); do
        JSON_DATA="{\"ID\": $i, \"first_name\": \"Test$i\", \"last_name\": \"Soldier\", \"phone_number\": $((5550000 + i)), \"rank\": \"Private\"}"
        curl -s -o /dev/null -X POST "${FULL_URL}/" -H "Content-Type: application/json" -d "$JSON_DATA"
    done

    # Performance test - concurrent reads
    echo "Running concurrent read test..."
    start_time=$(date +%s.%N)
    for i in $(seq 1 20); do
        curl -s -o /dev/null "${FULL_URL}/" &
    done
    wait
    end_time=$(date +%s.%N)

    duration=$(echo "$end_time - $start_time" | bc)
    echo "✅ Concurrent reads completed in ${duration}s"

    # Cleanup bulk data
    echo "Cleaning up bulk test data..."
    for i in $(seq 1001 1010); do
        curl -s -o /dev/null -X DELETE "${FULL_URL}/$i"
    done
}

run_security_tests() {
    print_header "SECURITY TESTS"

    print_subheader "Input Security"

    # SQL Injection attempts (should be irrelevant for MongoDB but good to test)
    JSON_SQL_INJECT='{"ID": 777, "first_name": "Robert\"; DROP TABLE soldiers; --", "last_name": "Tables", "phone_number": 5559999, "rank": "Hacker"}'
    run_test "SQL Injection Protection" "201" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_SQL_INJECT'" \
        "Should handle SQL injection attempts safely"

    # NoSQL Injection attempts
    JSON_NOSQL_INJECT='{"ID": 778, "first_name": {"$ne": null}, "last_name": "NoSQL", "phone_number": 5559998, "rank": "Injector"}'
    run_test "NoSQL Injection Protection" "422" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_NOSQL_INJECT'" \
        "Should reject NoSQL injection attempts"

    # XSS attempts
    JSON_XSS='{"ID": 779, "first_name": "<script>alert(\"XSS\")</script>", "last_name": "Script", "phone_number": 5559997, "rank": "Tester"}'
    run_test "XSS Protection" "201" \
        "curl -X POST '${FULL_URL}/' -H 'Content-Type: application/json' -d '$JSON_XSS'" \
        "Should handle XSS attempts safely"

    # Cleanup security test data
    curl -s -o /dev/null -X DELETE "${FULL_URL}/777"
    curl -s -o /dev/null -X DELETE "${FULL_URL}/779"

    print_subheader "HTTPS and Headers"
    if [[ $API_URL == https://* ]]; then
        echo "✅ API uses HTTPS"
    else
        echo "⚠️  WARNING: API not using HTTPS in production"
    fi

    # Check security headers
    HEADERS=$(curl -s -I "${API_URL}/")
    if echo "$HEADERS" | grep -qi "x-frame-options\|x-content-type-options\|x-xss-protection"; then
        echo "✅ Security headers detected"
    else
        echo "⚠️  WARNING: Missing security headers"
    fi
}

generate_report() {
    print_header "TEST RESULTS SUMMARY"

    echo "Test Suite: $TEST_SUITE"
    echo "API URL: $API_URL"
    echo "Timestamp: $TIMESTAMP"
    echo "Log File: $LOG_FILE"
    echo ""
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    echo ""

    if [ $FAILED_TESTS -eq 0 ]; then
        echo "🎉 ALL TESTS PASSED! 🎉"
        echo "API is functioning correctly."
    else
        echo "⚠️  SOME TESTS FAILED"
        echo "Check the log file for details: $LOG_FILE"
    fi

    echo ""
    echo "================================================================="
}

# --- Main Execution ---
echo "### Starting Comprehensive API Test Suite ###"
echo "API Endpoint: $FULL_URL"
echo "Test Suite: $TEST_SUITE"
echo "Log File: $LOG_FILE"

# Initial cleanup
cleanup_test_data

# Run test suites based on selection
case "$TEST_SUITE" in
    "basic")
        run_basic_tests
        ;;
    "full")
        run_basic_tests
        run_error_handling_tests
        run_performance_tests
        ;;
    "performance")
        run_performance_tests
        ;;
    "security")
        run_security_tests
        ;;
    *)
        echo "Unknown test suite: $TEST_SUITE"
        echo "Available suites: basic, full, performance, security"
        exit 1
        ;;
esac

# Final cleanup
cleanup_test_data

# Generate report
generate_report

# Exit with appropriate code
exit $FAILED_TESTS