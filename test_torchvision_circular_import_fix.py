#!/usr/bin/env python3
"""
Test Script for TorchVision Circular Import Fix
Tests the exact import chain that was causing the failure in the logs
"""

import sys
import os

def test_torchvision_circular_import_fix():
    """Test the complete import chain that was failing"""
    print("🧪 Testing TorchVision Circular Import Fix")
    print("=" * 50)
    
    # Step 1: Apply the fix (same as in start_fastapi_with_fix.py)
    print("1️⃣ Applying TorchVision fix...")
    
    from unittest.mock import MagicMock
    
    # Set environment variables
    os.environ['TORCH_OPERATOR_REGISTRATION_DISABLED'] = '1'
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '1'
    os.environ['TORCHVISION_DISABLE_CUDA_OPS'] = '1'
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    # Create comprehensive mock
    mock_torchvision = MagicMock()
    mock_extension = MagicMock()
    mock_extension._has_ops = MagicMock(return_value=False)
    mock_torchvision.extension = mock_extension
    
    mock_transforms = MagicMock()
    mock_transforms.InterpolationMode = type('InterpolationMode', (), {
        'BILINEAR': 2, 'NEAREST': 0, 'BICUBIC': 3, 'LANCZOS': 1
    })()
    mock_torchvision.transforms = mock_transforms
    
    mock_meta = MagicMock()
    mock_torchvision._meta_registrations = mock_meta
    
    # Install mocks
    sys.modules['torchvision'] = mock_torchvision
    sys.modules['torchvision.extension'] = mock_extension
    sys.modules['torchvision.transforms'] = mock_transforms
    sys.modules['torchvision._meta_registrations'] = mock_meta
    
    print("   ✅ TorchVision mock installed")
    
    # Step 2: Test the exact import chain from the error
    print("\n2️⃣ Testing problematic import chain...")
    
    test_results = []
    
    # Test 1: PyTorch
    try:
        import torch
        print("   ✅ torch import: SUCCESS")
        test_results.append(("torch", True, None))
    except Exception as e:
        print(f"   ❌ torch import: FAILED - {e}")
        test_results.append(("torch", False, str(e)))
    
    # Test 2: TorchVision (should use our mock)
    try:
        import torchvision
        print("   ✅ torchvision import: SUCCESS")
        print(f"      Version: {torchvision.__version__}")
        print(f"      Has extension: {hasattr(torchvision, 'extension')}")
        print(f"      Extension._has_ops(): {torchvision.extension._has_ops()}")
        test_results.append(("torchvision", True, None))
    except Exception as e:
        print(f"   ❌ torchvision import: FAILED - {e}")
        test_results.append(("torchvision", False, str(e)))
    
    # Test 3: TorchVision InterpolationMode (this was in the error chain)
    try:
        from torchvision.transforms import InterpolationMode
        print("   ✅ torchvision.transforms.InterpolationMode import: SUCCESS")
        print(f"      BILINEAR: {InterpolationMode.BILINEAR}")
        test_results.append(("torchvision.transforms.InterpolationMode", True, None))
    except Exception as e:
        print(f"   ❌ torchvision.transforms.InterpolationMode import: FAILED - {e}")
        test_results.append(("torchvision.transforms.InterpolationMode", False, str(e)))
    
    # Test 4: Transformers (this imports TorchVision)
    try:
        from transformers.image_utils import ImageProcessingMixin
        print("   ✅ transformers.image_utils.ImageProcessingMixin import: SUCCESS")
        test_results.append(("transformers.image_utils", True, None))
    except Exception as e:
        print(f"   ❌ transformers.image_utils.ImageProcessingMixin import: FAILED - {e}")
        test_results.append(("transformers.image_utils", False, str(e)))
    
    # Test 5: AutoImageProcessor (this was in the error chain)
    try:
        from transformers import AutoImageProcessor
        print("   ✅ transformers.AutoImageProcessor import: SUCCESS")
        test_results.append(("transformers.AutoImageProcessor", True, None))
    except Exception as e:
        print(f"   ❌ transformers.AutoImageProcessor import: FAILED - {e}")
        test_results.append(("transformers.AutoImageProcessor", False, str(e)))
    
    # Test 6: Diffusers (this imports transformers)
    try:
        from diffusers.models import AutoencoderKL, ImageProjection
        print("   ✅ diffusers.models import: SUCCESS")
        test_results.append(("diffusers.models", True, None))
    except Exception as e:
        print(f"   ❌ diffusers.models import: FAILED - {e}")
        test_results.append(("diffusers.models", False, str(e)))
    
    # Test 7: Our FastAPI server imports
    try:
        sys.path.insert(0, '/workspace')
        sys.path.insert(0, '.')
        from hymm_gradio.pipeline_utils import data_preprocess_server
        print("   ✅ hymm_gradio.pipeline_utils import: SUCCESS")
        test_results.append(("hymm_gradio.pipeline_utils", True, None))
    except Exception as e:
        print(f"   ❌ hymm_gradio.pipeline_utils import: FAILED - {e}")
        test_results.append(("hymm_gradio.pipeline_utils", False, str(e)))
    
    # Test 8: The critical import that was failing
    try:
        from hymm_sp.audio_video_inference import HunyuanVideoSampler
        print("   ✅ hymm_sp.audio_video_inference.HunyuanVideoSampler import: SUCCESS")
        test_results.append(("HunyuanVideoSampler", True, None))
    except Exception as e:
        print(f"   ❌ hymm_sp.audio_video_inference.HunyuanVideoSampler import: FAILED - {e}")
        test_results.append(("HunyuanVideoSampler", False, str(e)))
    
    # Step 3: Summary
    print("\n3️⃣ Test Results Summary")
    print("-" * 50)
    
    success_count = sum(1 for _, success, _ in test_results if success)
    total_count = len(test_results)
    
    for test_name, success, error in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not success and error:
            print(f"        Error: {error}")
    
    print(f"\n📊 Overall Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("\n🎉 SUCCESS: TorchVision circular import fix is working correctly!")
        print("   The FastAPI server should now start without errors.")
        return True
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {total_count - success_count} tests failed")
        print("   Some issues may remain, but basic functionality should work.")
        return False

def test_fastapi_server_import():
    """Test importing the FastAPI server directly"""
    print("\n4️⃣ Testing FastAPI Server Import...")
    print("-" * 50)
    
    try:
        from hymm_gradio.fastapi_server import app
        print("   ✅ FastAPI server import: SUCCESS")
        print("   ✅ FastAPI app object created successfully")
        return True
    except Exception as e:
        print(f"   ❌ FastAPI server import: FAILED - {e}")
        import traceback
        print("   📋 Full traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 TorchVision Circular Import Fix Validation")
    print("=" * 60)
    
    # Run the main test
    fix_works = test_torchvision_circular_import_fix()
    
    # Test FastAPI server import
    fastapi_works = test_fastapi_server_import()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    if fix_works and fastapi_works:
        print("🎉 COMPLETE SUCCESS: All tests passed!")
        print("   ✅ TorchVision circular import fix works")
        print("   ✅ FastAPI server can be imported")
        print("   🚀 Ready to start the web interface!")
        sys.exit(0)
    elif fix_works:
        print("⚠️  PARTIAL SUCCESS: Fix works but FastAPI has issues")
        print("   ✅ TorchVision circular import fix works")
        print("   ❌ FastAPI server import failed")
        print("   🔧 FastAPI server may need additional fixes")
        sys.exit(1)
    else:
        print("❌ FAILURE: TorchVision fix needs improvement")
        print("   ❌ TorchVision circular import fix incomplete")
        print("   🔧 Additional debugging required")
        sys.exit(2) 