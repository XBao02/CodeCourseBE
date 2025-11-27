#!/bin/bash

# ============================================
# API Testing Script cho Instructor Dashboard
# ============================================

API_BASE="http://localhost:5000"

# Màu cho output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========== INSTRUCTOR DASHBOARD API TESTS ==========${NC}\n"

# Test 1: Login
echo -e "${YELLOW}[Test 1] Login Instructor${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "instructor@example.com",
    "password": "password123"
  }')

echo "$LOGIN_RESPONSE" | jq '.'

# Extract instructorId
INSTRUCTOR_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.instructorId')
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

echo -e "${GREEN}✓ Instructor ID: $INSTRUCTOR_ID${NC}\n"

# Test 2: Get Dashboard
echo -e "${YELLOW}[Test 2] Get Dashboard${NC}"
curl -s "$API_BASE/api/instructor/dashboard?instructor_id=$INSTRUCTOR_ID" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

# Test 3: Get Statistics
echo -e "${YELLOW}[Test 3] Get Statistics${NC}"
curl -s "$API_BASE/api/instructor/statistics?instructor_id=$INSTRUCTOR_ID" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

# Test 4: Get Courses
echo -e "${YELLOW}[Test 4] Get Courses${NC}"
curl -s "$API_BASE/api/courses?instructor_id=$INSTRUCTOR_ID" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

# Test 5: Get Curriculum
echo -e "${YELLOW}[Test 5] Get Course Curriculum${NC}"
COURSE_ID=1  # Thay đổi theo course thực tế
curl -s "$API_BASE/api/courses/$COURSE_ID/curriculum" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

# Test 6: Error Case - Invalid Instructor ID
echo -e "${YELLOW}[Test 6] Test Invalid Instructor ID (Expected: 404)${NC}"
curl -s "$API_BASE/api/instructor/dashboard?instructor_id=99999" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

# Test 7: Error Case - Missing Parameter
echo -e "${YELLOW}[Test 7] Test Missing Parameter (Expected: 400)${NC}"
curl -s "$API_BASE/api/instructor/dashboard" | jq '.'
echo -e "${GREEN}✓ Done${NC}\n"

echo -e "${BLUE}========== ALL TESTS COMPLETED ==========${NC}"
