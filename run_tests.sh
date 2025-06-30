#!/bin/bash

# Test runner script for HunyuanVideo-Avatar-minimal
# Provides easy commands to run different test suites

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup environment
setup_env() {
    print_status "Setting up test environment..."
    
    # Export environment variables
    export MODEL_BASE=./weights
    export PYTHONPATH=.
    export CUDA_VISIBLE_DEVICES=0
    
    # Create necessary directories
    mkdir -p weights assets/image assets/audio outputs tests/fixtures
    
    # Create dummy weights README if it doesn't exist
    if [ ! -f "weights/README.md" ]; then
        echo "# Model weights go here" > weights/README.md
    fi
    
    print_success "Environment setup complete"
}

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    
    if ! command_exists pip; then
        print_error "pip not found. Please install Python and pip first."
        exit 1
    fi
    
    # Install project dependencies
    if [ -f "requirements-minimal.txt" ]; then
        pip install -r requirements-minimal.txt
    else
        print_warning "requirements-minimal.txt not found"
    fi
    
    # Install test dependencies
    if [ -f "test-requirements.txt" ]; then
        pip install -r test-requirements.txt
    else
        print_warning "test-requirements.txt not found"
    fi
    
    print_success "Dependencies installed"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    python3 -m pytest tests/unit/ -v --cov=hymm_sp --cov-report=html:htmlcov --cov-report=term-missing --tb=short
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    python3 -m pytest tests/integration/ -v --tb=short -m "not slow"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    python3 -m pytest tests/performance/ -v --tb=short -m "not gpu"
}

# Function to run system tests
run_system_tests() {
    print_status "Running system tests..."
    python3 -m pytest tests/system/ -v --tb=short -m "not docker and not gpu"
}

# Function to run all tests
run_all_tests() {
    print_status "Running complete test suite..."
    
    local failed=0
    
    # Run each test suite and track failures
    run_unit_tests || failed=1
    run_integration_tests || failed=1
    run_performance_tests || failed=1
    run_system_tests || failed=1
    
    if [ $failed -eq 0 ]; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed!"
        return 1
    fi
}

# Function to run quick tests (unit only)
run_quick_tests() {
    print_status "Running quick test suite (unit tests only)..."
    python3 -m pytest tests/unit/ -v --tb=short
}

# Function to run linting
run_linting() {
    print_status "Running code quality checks..."
    
    local failed=0
    
    # Run flake8 if available
    if command_exists flake8; then
        flake8 hymm_sp tests --max-line-length=88 --extend-ignore=E203,W503 || failed=1
    else
        print_warning "flake8 not installed, skipping"
    fi
    
    # Run black if available
    if command_exists black; then
        black --check --diff . || failed=1
    else
        print_warning "black not installed, skipping"
    fi
    
    # Run isort if available
    if command_exists isort; then
        isort --check-only --diff . || failed=1
    else
        print_warning "isort not installed, skipping"
    fi
    
    if [ $failed -eq 0 ]; then
        print_success "All linting checks passed!"
    else
        print_error "Some linting checks failed!"
    fi
    
    return $failed
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  setup         Setup test environment"
    echo "  install       Install dependencies"
    echo "  unit          Run unit tests"
    echo "  integration   Run integration tests"
    echo "  performance   Run performance tests"
    echo "  system        Run system tests"
    echo "  all           Run all tests (default)"
    echo "  quick         Run quick tests (unit only)"
    echo "  lint          Run code quality checks"
    echo "  help          Show this help message"
    echo ""
    echo "Options:"
    echo "  --install-deps  Install dependencies before running tests"
    echo ""
    echo "Examples:"
    echo "  $0 quick                   # Run quick tests"
    echo "  $0 unit --install-deps     # Install deps and run unit tests"
    echo "  $0 all                     # Run all tests"
    echo "  $0 lint                    # Run linting only"
}

# Main script logic
main() {
    local command="${1:-all}"
    local install_deps_flag=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                install_deps_flag=true
                shift
                ;;
            *)
                command="$1"
                shift
                ;;
        esac
    done
    
    # Always setup environment
    setup_env
    
    # Install dependencies if requested
    if [ "$install_deps_flag" = true ]; then
        install_deps
    fi
    
    # Run the requested command
    case $command in
        setup)
            print_success "Environment already set up"
            ;;
        install)
            install_deps
            ;;
        unit)
            run_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        performance)
            run_performance_tests
            ;;
        system)
            run_system_tests
            ;;
        all)
            run_all_tests
            ;;
        quick)
            run_quick_tests
            ;;
        lint)
            run_linting
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 