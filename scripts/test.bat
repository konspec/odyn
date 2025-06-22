@echo off
REM Test script for Odyn (Windows)
REM Usage: scripts\test.bat [options]

echo 🧪 Running Odyn tests...

REM Default options
set COVERAGE=true
set LINT=true
set TYPE_CHECK=true
set VERBOSE=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="--no-coverage" (
    set COVERAGE=false
    shift
    goto :parse_args
)
if "%~1"=="--no-lint" (
    set LINT=false
    shift
    goto :parse_args
)
if "%~1"=="--no-type-check" (
    set TYPE_CHECK=false
    shift
    goto :parse_args
)
if "%~1"=="--verbose" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="-v" (
    set VERBOSE=true
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    echo Usage: %0 [options]
    echo Options:
    echo   --no-coverage     Skip coverage report
    echo   --no-lint         Skip linting
    echo   --no-type-check   Skip type checking
    echo   --verbose, -v     Verbose output
    echo   --help            Show this help
    exit /b 0
)
if "%~1"=="-h" (
    echo Usage: %0 [options]
    echo Options:
    echo   --no-coverage     Skip coverage report
    echo   --no-lint         Skip linting
    echo   --no-type-check   Skip type checking
    echo   --verbose, -v     Verbose output
    echo   --help            Show this help
    exit /b 0
)
echo Unknown option: %~1
echo Use --help for usage information
exit /b 1

:end_parse

REM Run linting
if "%LINT%"=="true" (
    echo 🔍 Running linting...
    if "%VERBOSE%"=="true" (
        uv run ruff check src/ tests/ --verbose
        uv run ruff format --check src/ tests/ --verbose
    ) else (
        uv run ruff check src/ tests/
        uv run ruff format --check src/ tests/
    )
    echo ✅ Linting passed
)

REM Run type checking
if "%TYPE_CHECK%"=="true" (
    echo 🔍 Running type checking...
    if "%VERBOSE%"=="true" (
        uv run ty src/ --verbose
    ) else (
        uv run ty src/
    )
    echo ✅ Type checking passed
)

REM Run tests
echo 🧪 Running tests...
if "%COVERAGE%"=="true" (
    if "%VERBOSE%"=="true" (
        uv run pytest --cov=odyn --cov-report=term-missing --cov-report=html -v
    ) else (
        uv run pytest --cov=odyn --cov-report=term-missing --cov-report=html
    )
    echo 📊 Coverage report generated in htmlcov/index.html
) else (
    if "%VERBOSE%"=="true" (
        uv run pytest -v
    ) else (
        uv run pytest
    )
)

echo ✅ All tests passed!
