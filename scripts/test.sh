#!/bin/bash

# Test script for Odyn
# Usage: ./scripts/test.sh [options]

set -e

echo "🧪 Running Odyn tests..."

# Default options
COVERAGE=true
LINT=true
TYPE_CHECK=true
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --no-lint)
            LINT=false
            shift
            ;;
        --no-type-check)
            TYPE_CHECK=false
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --no-coverage     Skip coverage report"
            echo "  --no-lint         Skip linting"
            echo "  --no-type-check   Skip type checking"
            echo "  --verbose, -v     Verbose output"
            echo "  --help, -h        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run linting
if [ "$LINT" = true ]; then
    echo "🔍 Running linting..."
    if [ "$VERBOSE" = true ]; then
        uv run ruff check src/ tests/ --verbose
        uv run ruff format --check src/ tests/ --verbose
    else
        uv run ruff check src/ tests/
        uv run ruff format --check src/ tests/
    fi
    echo "✅ Linting passed"
fi

# Run type checking
if [ "$TYPE_CHECK" = true ]; then
    echo "🔍 Running type checking..."
    if [ "$VERBOSE" = true ]; then
        uv run ty src/ --verbose
    else
        uv run ty src/
    fi
    echo "✅ Type checking passed"
fi

# Run tests
echo "🧪 Running tests..."
if [ "$COVERAGE" = true ]; then
    if [ "$VERBOSE" = true ]; then
        uv run pytest --cov=odyn --cov-report=term-missing --cov-report=html -v
    else
        uv run pytest --cov=odyn --cov-report=term-missing --cov-report=html
    fi
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    if [ "$VERBOSE" = true ]; then
        uv run pytest -v
    else
        uv run pytest
    fi
fi

echo "✅ All tests passed!"
