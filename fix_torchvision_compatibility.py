#!/usr/bin/env python3
"""
TorchVision Compatibility Fix Script
Handles PyTorch/TorchVision version mismatches that cause the NMS operator error
Updated for PyTorch 2.4.0 + TorchVision 0.19.0 compatibility
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
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
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
    
    # Set CUDA environment for better compatibility
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
    
    # TorchVision specific fixes
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '0'  # Keep video API enabled
    os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
    
    # Ensure proper library loading
    if 'LD_LIBRARY_PATH' not in os.environ:
        os.environ['LD_LIBRARY_PATH'] = '/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu'
    
    print("   ✅ Environment variables set")

def test_torch_import():
    """Test if PyTorch can be imported correctly"""
    print("🧪 Testing PyTorch import...")
    try:
        import torch
        print(f"   PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU count: {torch.cuda.device_count()}")
        return True
    except Exception as e:
        print(f"   ❌ PyTorch import failed: {e}")
        return False

def test_torchvision_import():
    """Test if torchvision can be imported without the NMS error"""
    print("🧪 Testing TorchVision import...")
    try:
        # Clear any cached imports
        modules_to_clear = [mod for mod in sys.modules.keys() if mod.startswith('torchvision')]
        for mod in modules_to_clear:
            if mod in sys.modules:
                del sys.modules[mod]
        
        import torchvision
        print(f"   TorchVision version: {torchvision.__version__}")
        
        # Test the specific problematic operation
        from torchvision.ops import nms
        print("   ✅ TorchVision NMS operator import: SUCCESS")
        
        # Test transforms (common source of issues)
        from torchvision import transforms
        print("   ✅ TorchVision transforms import: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"   ❌ TorchVision import failed: {e}")
        return False

def test_opencv_compatibility():
    """Test OpenCV compatibility with TorchVision"""
    print("🧪 Testing OpenCV compatibility...")
    try:
        import cv2
        print(f"   OpenCV version: {cv2.__version__}")
        return True
    except Exception as e:
        print(f"   ❌ OpenCV import failed: {e}")
        return False

def reinstall_compatible_versions():
    """Reinstall PyTorch and TorchVision with compatible versions for CUDA 12.4"""
    print("🔧 Reinstalling compatible PyTorch/TorchVision versions for CUDA 12.4...")
    
    # Don't uninstall - just upgrade to ensure compatibility
    success = run_command(
        "pip install --upgrade torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124",
        "Install/upgrade compatible PyTorch versions"
    )
    
    if not success:
        print("   Trying CPU-only fallback...")
        run_command(
            "pip install --upgrade torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0",
            "Install CPU-only PyTorch versions"
        )

def apply_runtime_fixes():
    """Apply runtime fixes for TorchVision compatibility"""
    print("🔧 Applying runtime TorchVision fixes...")
    
    try:
        # Import and configure torch first
        import torch
        
        # Set optimal settings
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Configure memory management
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            # Set memory fraction to avoid OOM
            torch.cuda.set_per_process_memory_fraction(0.9)
        
        print("   ✅ Runtime fixes applied successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Runtime fixes failed: {e}")
        return False

def main():
    print("🚀 TorchVision Compatibility Fix (PyTorch 2.4.0)")
    print("=" * 60)
    
    # Step 1: Set environment variables
    set_compatibility_env()
    
    # Step 2: Test PyTorch first
    if not test_torch_import():
        print("\n❌ PyTorch is not working correctly")
        return False
    
    # Step 3: Test TorchVision
    if test_torchvision_import():
        print("\n✅ TorchVision is already working correctly!")
        # Still apply runtime fixes for optimization
        apply_runtime_fixes()
        return True
    
    print("\n⚠️  TorchVision has compatibility issues, attempting fix...")
    
    # Step 4: Test OpenCV compatibility
    test_opencv_compatibility()
    
    # Step 5: Try reinstalling with compatible versions
    reinstall_compatible_versions()
    
    # Step 6: Apply runtime fixes
    apply_runtime_fixes()
    
    # Step 7: Test again
    if test_torchvision_import():
        print("\n✅ TorchVision compatibility fix successful!")
        return True
    else:
        print("\n❌ TorchVision compatibility fix failed")
        print("   The application will attempt to use fallback mode")
        print("   Consider using the no-flash-attn Docker image for better compatibility")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 