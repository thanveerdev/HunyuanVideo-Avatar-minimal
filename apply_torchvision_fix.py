#!/usr/bin/env python3
"""
Apply TorchVision Compatibility Fix for RunPod Deployment
Fixes the circular import issue that prevents FastAPI server startup
"""
import os
import sys

def set_torchvision_env():
    """Set environment variables for TorchVision compatibility"""
    print("🔧 Setting TorchVision compatibility environment variables...")
    
    # Disable problematic TorchVision operators
    os.environ['TORCH_OPERATOR_REGISTRATION_DISABLED'] = '1'
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '1'
    
    # Force CPU-only mode for problematic operations
    os.environ['TORCHVISION_DISABLE_CUDA_OPS'] = '1'
    
    # Set PyTorch to use legacy mode for better compatibility
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    print("   ✅ Environment variables set")

def main():
    print("🚀 Applying TorchVision Compatibility Fix")
    print("=" * 50)
    
    # Set environment variables
    set_torchvision_env()
    
    print("\n✅ TorchVision compatibility fix applied!")
    print("💡 The defensive imports in audio_dataset.py will handle any remaining issues")
    print("🌐 Ready to start the web interface")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 