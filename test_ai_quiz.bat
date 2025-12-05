@echo off
REM Test AI Quiz Generation - Lesson Title Verification
REM Quick test to verify lesson titles are used correctly

echo ========================================
echo   AI Quiz Generation Test
echo ========================================
echo.

cd /d "%~dp0backend"

echo Running quick test...
echo.
python test_ai_quiz_quick.py

echo.
echo ========================================
echo.
echo To run full test suite (requires API key):
echo   python backend\test_ai_quiz.py
echo.
echo ========================================
pause
