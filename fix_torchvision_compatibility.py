#!/usr/bin/env python3
"""
TorchVision Compatibility Fix Script
Handles PyTorch/TorchVision version mismatches that cause the NMS operator error
"""
import os
import sys
import subprocess
import importlib

def run_command(cmd, description="command"):
    """Run a system command and return success status"""
    print(f"🔧 Running: {description}")
    print(f"   Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ SUCCESS")
            return True
        else:
            print(f"   ❌ FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def set_compatibility_env():
    """Set environment variables for better PyTorch/TorchVision compatibility"""
    print("🔧 Setting TorchVision compatibility environment variables...")
    
    # Disable problematic TorchVision operators
    os.environ['TORCH_OPERATOR_REGISTRATION_DISABLED'] = '1'
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '1'
    
    # Force CPU-only mode for problematic operations
    os.environ['TORCHVISION_DISABLE_CUDA_OPS'] = '1'
    
    # Set PyTorch to use legacy mode for better compatibility
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    print("   ✅ Environment variables set")

def test_torchvision_import():
    """Test if torchvision can be imported without the NMS error"""
    print("🧪 Testing TorchVision import...")
    try:
        # Clear any cached imports
        if 'torchvision' in sys.modules:
            del sys.modules['torchvision']
        if 'torchvision.transforms' in sys.modules:
            del sys.modules['torchvision.transforms']
        
        import torch
        print(f"   PyTorch version: {torch.__version__}")
        
        import torchvision
        print(f"   TorchVision version: {torchvision.__version__}")
        
        # Test the specific problematic operation
        torchvision.ops.nms
        print("   ✅ TorchVision NMS operator test: SUCCESS")
        return True
        
    except Exception as e:
        print(f"   ❌ TorchVision import failed: {e}")
        return False

def reinstall_compatible_versions():
    """Reinstall PyTorch and TorchVision with compatible versions"""
    print("🔧 Reinstalling compatible PyTorch/TorchVision versions...")
    
    # Uninstall existing versions
    run_command("pip uninstall -y torch torchvision torchaudio", "Uninstall existing PyTorch")
    
    # Install specific compatible versions
    run_command("pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0", "Install compatible versions")

def main():
    print("🚀 TorchVision Compatibility Fix")
    print("=" * 50)
    
    # Step 1: Set environment variables
    set_compatibility_env()
    
    # Step 2: Test current installation
    if test_torchvision_import():
        print("\n✅ TorchVision is already working correctly!")
        return True
    
    print("\n⚠️  TorchVision has compatibility issues, attempting fix...")
    
    # Step 3: Try reinstalling with compatible versions
    reinstall_compatible_versions()
    
    # Step 4: Test again
    if test_torchvision_import():
        print("\n✅ TorchVision compatibility fix successful!")
        return True
    else:
        print("\n❌ TorchVision compatibility fix failed")
        print("   The application will use fallback mode")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 