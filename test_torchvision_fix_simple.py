#!/usr/bin/env python3
"""
Simple test to verify TorchVision compatibility fix is working
"""
import sys

def test_torchvision_import():
    """Test if torchvision can be imported without errors"""
    print("🧪 Testing TorchVision import...")
    try:
        import torchvision
        print(f"   ✅ TorchVision version: {torchvision.__version__}")
        return True
    except Exception as e:
        print(f"   ⚠️  TorchVision import failed: {e}")
        return False

def test_audio_dataset_import():
    """Test if the audio_dataset module can be imported"""
    print("🧪 Testing audio_dataset import...")
    try:
        from hymm_sp.data_kits.audio_dataset import get_audio_feature
        print("   ✅ audio_dataset import successful")
        return True
    except Exception as e:
        print(f"   ⚠️  audio_dataset import failed: {e}")
        return False

def test_fastapi_server_import():
    """Test if the FastAPI server can be imported"""
    print("🧪 Testing FastAPI server import...")
    try:
        from hymm_gradio.fastapi_server import app
        print("   ✅ FastAPI server import successful")
        return True
    except Exception as e:
        print(f"   ⚠️  FastAPI server import failed: {e}")
        return False

def main():
    print("🚀 Testing TorchVision Compatibility Fix")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Basic TorchVision import
    if not test_torchvision_import():
        print("   💡 This is expected - using fallback mode")
    
    # Test 2: Audio dataset import (the critical one)
    if not test_audio_dataset_import():
        all_passed = False
        
    # Test 3: FastAPI server import
    if not test_fastapi_server_import():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All critical imports working!")
        print("🌐 FastAPI server should start successfully")
        return True
    else:
        print("❌ Some imports failed")
        print("⚠️  FastAPI server may have issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 