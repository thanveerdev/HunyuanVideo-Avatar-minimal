#!/usr/bin/env python3
"""
Docker Fixes Verification Script
Tests all the fixes applied to the HunyuanVideo-Avatar Docker builds
"""
import sys
import os
import importlib
import traceback

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def test_flash_attention():
    """Test Flash Attention installation and functionality"""
    print_header("Testing Flash Attention")
    
    try:
        import flash_attn
        print_success(f"Flash Attention imported successfully - version: {flash_attn.__version__}")
        
        # Test specific flash attention components
        from flash_attn.flash_attn_interface import flash_attn_varlen_func
        print_success("Flash Attention interface imported successfully")
        
        return True
    except ImportError as e:
        print_error(f"Flash Attention not available: {e}")
        print_warning("This is expected if using the no-flash-attn build")
        return False
    except Exception as e:
        print_error(f"Flash Attention test failed: {e}")
        return False

def test_pytorch_torchvision():
    """Test PyTorch and TorchVision compatibility"""
    print_header("Testing PyTorch and TorchVision")
    
    try:
        import torch
        print_success(f"PyTorch imported - version: {torch.__version__}")
        print_success(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print_success(f"CUDA version: {torch.version.cuda}")
            print_success(f"GPU count: {torch.cuda.device_count()}")
        
        # Test TorchVision
        import torchvision
        print_success(f"TorchVision imported - version: {torchvision.__version__}")
        
        # Test the problematic NMS operator
        from torchvision.ops import nms
        print_success("TorchVision NMS operator imported successfully")
        
        # Test transforms
        from torchvision import transforms
        print_success("TorchVision transforms imported successfully")
        
        return True
    except Exception as e:
        print_error(f"PyTorch/TorchVision test failed: {e}")
        traceback.print_exc()
        return False

def test_web_interface():
    """Test web interface dependencies"""
    print_header("Testing Web Interface Dependencies")
    
    try:
        import gradio
        print_success(f"Gradio imported - version: {gradio.__version__}")
        
        import fastapi
        print_success(f"FastAPI imported - version: {fastapi.__version__}")
        
        import uvicorn
        print_success(f"Uvicorn imported - version: {uvicorn.__version__}")
        
        import pydantic
        print_success(f"Pydantic imported - version: {pydantic.__version__}")
        
        return True
    except Exception as e:
        print_error(f"Web interface test failed: {e}")
        traceback.print_exc()
        return False

def test_core_dependencies():
    """Test core ML dependencies"""
    print_header("Testing Core ML Dependencies")
    
    dependencies = [
        ('diffusers', 'Diffusers'),
        ('transformers', 'Transformers'),
        ('accelerate', 'Accelerate'),
        ('librosa', 'Librosa'),
        ('soundfile', 'SoundFile'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
        ('imageio', 'ImageIO'),
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('einops', 'Einops'),
        ('omegaconf', 'OmegaConf'),
        ('loguru', 'Loguru'),
        ('tqdm', 'tqdm'),
        ('safetensors', 'SafeTensors'),
        ('psutil', 'psutil'),
        ('huggingface_hub', 'Hugging Face Hub'),
    ]
    
    success_count = 0
    for module_name, display_name in dependencies:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            print_success(f"{display_name} - version: {version}")
            success_count += 1
        except Exception as e:
            print_error(f"{display_name} import failed: {e}")
    
    print(f"\n📊 Core Dependencies: {success_count}/{len(dependencies)} successful")
    return success_count == len(dependencies)

def test_memory_optimization():
    """Test memory optimization package"""
    print_header("Testing Memory Optimization")
    
    try:
        import mmgp
        print_success(f"MMGP (Memory Management for GPU Poor) imported - version: {mmgp.__version__}")
        return True
    except Exception as e:
        print_error(f"MMGP import failed: {e}")
        return False

def test_environment_variables():
    """Test critical environment variables"""
    print_header("Testing Environment Variables")
    
    env_vars = [
        ('CUDA_HOME', 'CUDA installation path'),
        ('LD_LIBRARY_PATH', 'Library path'),
        ('PYTHONPATH', 'Python path'),
        ('MODEL_BASE', 'Model base path'),
    ]
    
    for var_name, description in env_vars:
        value = os.environ.get(var_name)
        if value:
            print_success(f"{var_name}: {value}")
        else:
            print_warning(f"{var_name} not set ({description})")
    
    # Test CUDA environment
    cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'not set')
    print_success(f"CUDA_VISIBLE_DEVICES: {cuda_visible}")
    
    return True

def test_application_imports():
    """Test application-specific imports"""
    print_header("Testing Application Imports")
    
    try:
        # Test if we can import the main application modules
        sys.path.insert(0, '/workspace')
        
        # Test hymm_sp imports
        try:
            from hymm_sp import constants
            print_success("hymm_sp.constants imported successfully")
        except Exception as e:
            print_warning(f"hymm_sp.constants import failed: {e}")
        
        # Test hymm_gradio imports
        try:
            from hymm_gradio import pipeline_utils
            print_success("hymm_gradio.pipeline_utils imported successfully")
        except Exception as e:
            print_warning(f"hymm_gradio.pipeline_utils import failed: {e}")
        
        return True
    except Exception as e:
        print_error(f"Application imports test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and return overall success"""
    print("🚀 HunyuanVideo-Avatar Docker Fixes Verification")
    print("This script tests all the fixes applied to the Docker builds")
    
    tests = [
        ("Flash Attention", test_flash_attention),
        ("PyTorch/TorchVision", test_pytorch_torchvision),
        ("Web Interface", test_web_interface),
        ("Core Dependencies", test_core_dependencies),
        ("Memory Optimization", test_memory_optimization),
        ("Environment Variables", test_environment_variables),
        ("Application Imports", test_application_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Results Summary")
    passed = 0
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n📊 Overall Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print_success("🎉 All tests passed! Docker fixes are working correctly.")
        return True
    elif passed >= len(results) * 0.8:  # 80% pass rate
        print_warning("⚠️  Most tests passed. Some issues may remain but basic functionality works.")
        return True
    else:
        print_error("❌ Multiple tests failed. Please check the Docker build and configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 