#!/usr/bin/env python3
"""
Test script to validate TorchVision compatibility fixes
"""
import sys
import os

print("🧪 Testing TorchVision Compatibility Fix...")
print("=" * 50)

# Test 1: Basic torch import
try:
    import torch
    print("✅ PyTorch import: SUCCESS")
    print(f"   PyTorch version: {torch.__version__}")
except Exception as e:
    print(f"❌ PyTorch import: FAILED - {e}")
    sys.exit(1)

# Test 2: TorchVision import (the problematic one)
try:
    import torchvision
    print("✅ TorchVision import: SUCCESS")
    print(f"   TorchVision version: {torchvision.__version__}")
    TORCHVISION_AVAILABLE = True
except Exception as e:
    print(f"⚠️  TorchVision import: FAILED - {e}")
    print("   Will use fallback implementation")
    TORCHVISION_AVAILABLE = False

# Test 3: Test our pipeline_utils import
try:
    sys.path.insert(0, '/workspace')
    from hymm_gradio.pipeline_utils import data_preprocess_server, save_videos_grid
    print("✅ pipeline_utils import: SUCCESS")
except Exception as e:
    print(f"❌ pipeline_utils import: FAILED - {e}")
    print(f"   Error details: {str(e)}")

# Test 4: Test FastAPI server import
try:
    from hymm_gradio.fastapi_server import app
    print("✅ FastAPI server import: SUCCESS")
except Exception as e:
    print(f"❌ FastAPI server import: FAILED - {e}")
    print(f"   Error details: {str(e)}")

print("\n" + "=" * 50)
print("🏁 TorchVision Compatibility Test Complete")

if TORCHVISION_AVAILABLE:
    print("✅ Status: TorchVision fully functional")
else:
    print("⚠️  Status: Using fallback mode (should still work)") 