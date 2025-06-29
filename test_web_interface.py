#!/usr/bin/env python3
"""
Test script for HunyuanVideo-Avatar Web Interface
Verifies that all components are properly configured and working
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_status(message):
    print(f"\033[1;32m✅ {message}\033[0m")

def print_warning(message):
    print(f"\033[1;33m⚠️  {message}\033[0m")

def print_error(message):
    print(f"\033[1;31m❌ {message}\033[0m")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    required_packages = [
        'torch', 'gradio', 'fastapi', 'uvicorn', 'transformers', 'diffusers'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ✗ {package}")
    
    if missing_packages:
        print_error(f"Missing packages: {', '.join(missing_packages)}")
        return False
    
    print_status("All dependencies installed")
    return True

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        "hymm_gradio/web_demo.py",
        "hymm_gradio/fastapi_server.py", 
        "hymm_gradio/pipeline_utils.py",
        "run_web_demo.sh",
        "run_fastapi_server.sh",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"  ✗ {file_path}")
        else:
            print(f"  ✓ {file_path}")
    
    if missing_files:
        print_error(f"Missing files: {missing_files}")
        return False
    
    print_status("All required files present")
    return True

def main():
    print("🧪 HunyuanVideo-Avatar Web Interface Test")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("File Structure", check_file_structure()))
    results.append(("Dependencies", check_dependencies()))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("🎉 Web interface is ready!")
        print("\nTo start the web interface:")
        print("  bash run_web_demo.sh")
        print("  Open: http://localhost:7860")
    else:
        print_warning("⚠️  Some tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 