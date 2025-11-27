@echo off
REM ========================================
REM API Testing Script cho Instructor Dashboard (Windows)
REM ========================================

setlocal enabledelayedexpansion

set API_BASE=http://localhost:5000
set INSTRUCTOR_ID=1

echo ========== INSTRUCTOR DASHBOARD API TESTS ==========
echo.

REM Test 1: Login
echo [Test 1] Login Instructor
echo.
curl -X POST "%API_BASE%/api/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"instructor@example.com\", \"password\": \"password123\"}"
echo.
echo.

REM Test 2: Get Dashboard
echo [Test 2] Get Dashboard
echo.
curl "%API_BASE%/api/instructor/dashboard?instructor_id=%INSTRUCTOR_ID%"
echo.
echo.

REM Test 3: Get Statistics
echo [Test 3] Get Statistics
echo.
curl "%API_BASE%/api/instructor/statistics?instructor_id=%INSTRUCTOR_ID%"
echo.
echo.

REM Test 4: Get Courses
echo [Test 4] Get Courses
echo.
curl "%API_BASE%/api/courses?instructor_id=%INSTRUCTOR_ID%"
echo.
echo.

REM Test 5: Get Course Curriculum
echo [Test 5] Get Course Curriculum
echo.
curl "%API_BASE%/api/courses/1/curriculum"
echo.
echo.

REM Test 6: Invalid Instructor ID
echo [Test 6] Test Invalid Instructor ID (Expected: 404)
echo.
curl "%API_BASE%/api/instructor/dashboard?instructor_id=99999"
echo.
echo.

REM Test 7: Missing Parameter
echo [Test 7] Test Missing Parameter (Expected: 400)
echo.
curl "%API_BASE%/api/instructor/dashboard"
echo.
echo.

echo ========== ALL TESTS COMPLETED ==========
pause
