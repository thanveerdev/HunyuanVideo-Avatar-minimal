#!/bin/bash

# Test runner for error persistence from My Pods Logs (29).txt
# This script tests if the critical errors identified in the logs still persist

echo "🚨 TESTING ERROR PERSISTENCE FROM MY PODS LOGS (29).TXT"
echo "=============================================================="
echo "Testing if the critical errors that prevent application startup persist"
echo ""

# Set script to exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 ERRORS IDENTIFIED IN THE LOGS:${NC}"
echo "1. ❌ ModuleNotFoundError: No module named 'flash_attn'"
echo "2. ❌ TypeError: argument of type 'bool' is not iterable (Gradio)"
echo "3. ❌ TorchVision operator torchvision::nms does not exist"
echo "4. ❌ InterpolationMode object has no attribute 'BOX'"
echo "5. ❌ FastAPI server fails to start due to import errors"
echo ""

echo -e "${BLUE}🧪 RUNNING FOCUSED TESTS...${NC}"
echo "=============================================================="

# Test 1: Flash Attention - PRIMARY ERROR
echo ""
echo -e "${BLUE}TEST 1: Testing flash_attn availability (PRIMARY ERROR)${NC}"
echo "------------------------------------------------------"

if python3 test_flash_attn_error.py; then
    echo -e "${GREEN}✅ Flash Attention test PASSED${NC}"
    FLASH_ATTN_OK=1
else
    echo -e "${RED}❌ Flash Attention test FAILED${NC}"
    FLASH_ATTN_OK=0
fi

# Test 2: Quick Python import tests
echo ""
echo -e "${BLUE}TEST 2: Testing critical Python imports${NC}"
echo "------------------------------------------------------"

PYTHON_TEST_SCRIPT="
import sys
import traceback

def test_import(module_name, description):
    try:
        __import__(module_name)
        print(f'✅ {description}: {module_name}')
        return True
    except Exception as e:
        print(f'❌ {description}: {module_name} - {e}')
        return False

print('Testing critical imports...')
results = []

# Test core dependencies
results.append(test_import('torch', 'PyTorch'))
results.append(test_import('torchvision', 'TorchVision'))
results.append(test_import('transformers', 'Transformers'))
results.append(test_import('gradio', 'Gradio'))
results.append(test_import('fastapi', 'FastAPI'))

# Test problematic imports
results.append(test_import('flash_attn', 'Flash Attention'))

try:
    from torchvision.transforms import InterpolationMode
    if hasattr(InterpolationMode, 'BOX'):
        print('✅ TorchVision InterpolationMode.BOX available')
        results.append(True)
    else:
        print('❌ TorchVision InterpolationMode.BOX missing')
        results.append(False)
except Exception as e:
    print(f'❌ TorchVision InterpolationMode test failed: {e}')
    results.append(False)

try:
    import torch
    import torchvision
    boxes = torch.tensor([[0, 0, 1, 1]], dtype=torch.float32)
    scores = torch.tensor([0.9], dtype=torch.float32)
    result = torchvision.ops.nms(boxes, scores, 0.5)
    print('✅ TorchVision NMS operator available')
    results.append(True)
except Exception as e:
    print(f'❌ TorchVision NMS operator failed: {e}')
    results.append(False)

passed = sum(results)
total = len(results)
print(f'\\nImport test results: {passed}/{total} passed')

if passed == total:
    sys.exit(0)
else:
    sys.exit(1)
"

if python3 -c "$PYTHON_TEST_SCRIPT"; then
    echo -e "${GREEN}✅ Python import tests PASSED${NC}"
    PYTHON_IMPORTS_OK=1
else
    echo -e "${RED}❌ Python import tests FAILED${NC}"
    PYTHON_IMPORTS_OK=0
fi

# Test 3: Test application import chain
echo ""
echo -e "${BLUE}TEST 3: Testing application import chain${NC}"
echo "------------------------------------------------------"

APP_IMPORT_TEST="
import sys
import traceback

def test_app_imports():
    import_chain = [
        'hymm_sp',
        'hymm_sp.modules',
        'hymm_sp.diffusion',
        'hymm_gradio'
    ]
    
    failed_imports = []
    
    for module in import_chain:
        try:
            __import__(module)
            print(f'✅ {module}')
        except Exception as e:
            failed_imports.append((module, str(e)))
            print(f'❌ {module}: {e}')
    
    if failed_imports:
        print(f'\\n❌ {len(failed_imports)} imports failed')
        return False
    else:
        print(f'\\n✅ All application imports successful')
        return True

if test_app_imports():
    sys.exit(0)
else:
    sys.exit(1)
"

if python3 -c "$APP_IMPORT_TEST"; then
    echo -e "${GREEN}✅ Application import chain PASSED${NC}"
    APP_IMPORTS_OK=1
else
    echo -e "${RED}❌ Application import chain FAILED${NC}"
    APP_IMPORTS_OK=0
fi

# Summary
echo ""
echo "=============================================================="
echo -e "${BLUE}📊 FINAL TEST SUMMARY${NC}"
echo "=============================================================="

if [ $FLASH_ATTN_OK -eq 1 ]; then
    echo -e "${GREEN}✅ Flash Attention: RESOLVED${NC}"
else
    echo -e "${RED}❌ Flash Attention: ERROR PERSISTS${NC}"
fi

if [ $PYTHON_IMPORTS_OK -eq 1 ]; then
    echo -e "${GREEN}✅ Python Imports: RESOLVED${NC}" 
else
    echo -e "${RED}❌ Python Imports: ERRORS PERSIST${NC}"
fi

if [ $APP_IMPORTS_OK -eq 1 ]; then
    echo -e "${GREEN}✅ Application Imports: RESOLVED${NC}"
else
    echo -e "${RED}❌ Application Imports: ERRORS PERSIST${NC}"
fi

echo ""

# Final verdict
if [ $FLASH_ATTN_OK -eq 1 ] && [ $PYTHON_IMPORTS_OK -eq 1 ] && [ $APP_IMPORTS_OK -eq 1 ]; then
    echo -e "${GREEN}🎉 SUCCESS: All critical errors have been RESOLVED!${NC}"
    echo -e "${GREEN}✅ The application should now start properly${NC}"
    exit 0
else
    echo -e "${RED}⚠️  FAILURE: Critical errors still PERSIST${NC}"
    echo -e "${RED}❌ The application will likely fail to start${NC}"
    echo ""
    echo -e "${YELLOW}💡 NEXT STEPS:${NC}"
    if [ $FLASH_ATTN_OK -eq 0 ]; then
        echo "   1. Install flash-attn: pip install flash-attn"
    fi
    if [ $PYTHON_IMPORTS_OK -eq 0 ]; then
        echo "   2. Install missing Python dependencies"
    fi
    if [ $APP_IMPORTS_OK -eq 0 ]; then
        echo "   3. Fix application import chain issues"
    fi
    exit 1
fi 