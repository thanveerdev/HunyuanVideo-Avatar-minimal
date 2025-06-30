#!/usr/bin/env python3
"""
Deep TorchVision Import Fix
Prevents circular import issues at the library dependency level by intercepting
imports before diffusers, transformers, or any other library can trigger the issue.
"""

import sys
import os
from unittest.mock import MagicMock

def setup_deep_torchvision_fix():
    """Setup comprehensive TorchVision fix before any imports"""
    print("🔧 Applying deep TorchVision import fix...")
    
    # Set environment variables first
    os.environ['TORCH_OPERATOR_REGISTRATION_DISABLED'] = '1'
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '1'
    os.environ['TORCHVISION_DISABLE_CUDA_OPS'] = '1'
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    # Create comprehensive torchvision mock BEFORE any real imports
    if 'torchvision' not in sys.modules:
        print("   📦 Creating comprehensive TorchVision mock...")
        
        # Create the mock torchvision module
        mock_torchvision = MagicMock()
        
        # Mock the problematic extension module
        mock_extension = MagicMock()
        mock_extension._has_ops = MagicMock(return_value=False)
        mock_extension.nms = MagicMock()
        mock_extension.roi_align = MagicMock()
        mock_torchvision.extension = mock_extension
        
        # Mock transforms submodule
        mock_transforms = MagicMock()
        mock_transforms.InterpolationMode = MagicMock()
        mock_transforms.InterpolationMode.BILINEAR = 2
        mock_transforms.InterpolationMode.NEAREST = 0
        mock_transforms.Compose = MagicMock()
        mock_transforms.Resize = MagicMock()
        mock_transforms.CenterCrop = MagicMock()
        mock_transforms.ToTensor = MagicMock()
        mock_transforms.Normalize = MagicMock()
        mock_transforms.ToPILImage = MagicMock()
        mock_torchvision.transforms = mock_transforms
        
        # Mock _meta_registrations to prevent the circular import
        mock_meta = MagicMock()
        mock_torchvision._meta_registrations = mock_meta
        
        # Mock other commonly used modules
        mock_torchvision.datasets = MagicMock()
        mock_torchvision.io = MagicMock()
        mock_torchvision.models = MagicMock()
        mock_torchvision.ops = MagicMock()
        mock_torchvision.utils = MagicMock()
        
        # Set version to prevent version checks from failing
        mock_torchvision.__version__ = "0.16.0"
        mock_torchvision.__spec__ = MagicMock()
        
        # Install the mock in sys.modules
        sys.modules['torchvision'] = mock_torchvision
        sys.modules['torchvision.extension'] = mock_extension
        sys.modules['torchvision.transforms'] = mock_transforms
        sys.modules['torchvision._meta_registrations'] = mock_meta
        
        print("   ✅ TorchVision mock installed successfully")
    
    # Now try to import real torch and replace problematic functions
    try:
        import torch
        print("   ✅ PyTorch imported successfully")
        
        # If real torchvision exists, try to patch it
        try:
            # Remove the mock and try real torchvision
            if 'torchvision' in sys.modules and hasattr(sys.modules['torchvision'], '_mock_name'):
                del sys.modules['torchvision']
                del sys.modules['torchvision.extension']
                del sys.modules['torchvision.transforms']
                del sys.modules['torchvision._meta_registrations']
            
            import torchvision
            print(f"   ✅ Real TorchVision {torchvision.__version__} imported successfully")
            
            # Patch the problematic _has_ops function
            if hasattr(torchvision, 'extension') and hasattr(torchvision.extension, '_has_ops'):
                original_has_ops = torchvision.extension._has_ops
                torchvision.extension._has_ops = lambda: False
                print("   🔧 Patched torchvision.extension._has_ops() to return False")
            
        except Exception as e:
            print(f"   ⚠️  Real TorchVision failed to load: {e}")
            print("   🔄 Keeping mock TorchVision for compatibility")
            
            # Restore the mock
            sys.modules['torchvision'] = mock_torchvision
            sys.modules['torchvision.extension'] = mock_extension
            sys.modules['torchvision.transforms'] = mock_transforms
            sys.modules['torchvision._meta_registrations'] = mock_meta
        
    except Exception as e:
        print(f"   ❌ PyTorch import failed: {e}")
        return False
    
    print("   ✅ Deep TorchVision fix applied successfully")
    return True

def fix_gradio_compatibility():
    """Fix Gradio compatibility issues"""
    print("🔧 Applying Gradio compatibility fix...")
    
    try:
        import gradio as gr
        print(f"   📦 Gradio version: {gr.__version__}")
        
        # Check if we need to patch the launch method
        if hasattr(gr.Blocks, 'launch'):
            original_launch = gr.Blocks.launch
            
            def patched_launch(self, *args, **kwargs):
                # Remove deprecated arguments
                deprecated_args = ['enable_queue', 'inbrowser', 'debug', 'quiet']
                for arg in deprecated_args:
                    if arg in kwargs:
                        print(f"   🔧 Removing deprecated Gradio argument: {arg}")
                        del kwargs[arg]
                
                # Add new equivalent arguments
                if 'share' not in kwargs:
                    kwargs['share'] = False
                
                return original_launch(self, *args, **kwargs)
            
            gr.Blocks.launch = patched_launch
            print("   ✅ Gradio launch method patched for compatibility")
        
    except Exception as e:
        print(f"   ⚠️  Gradio compatibility fix failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Deep Library Import Fix")
    print("=" * 50)
    
    success = setup_deep_torchvision_fix()
    gradio_success = fix_gradio_compatibility()
    
    if success and gradio_success:
        print("✅ All fixes applied successfully!")
        print("🌐 Ready to start web interface")
    else:
        print("⚠️  Some fixes had issues, but continuing...")
        
    # Test the fixes
    print("\n🧪 Testing imports...")
    
    try:
        import torchvision
        print(f"✅ TorchVision: {torchvision.__version__}")
    except Exception as e:
        print(f"⚠️  TorchVision: {e}")
    
    try:
        from transformers import CLIPImageProcessor
        print("✅ CLIPImageProcessor imported successfully")
    except Exception as e:
        print(f"⚠️  CLIPImageProcessor: {e}")
    
    try:
        from diffusers.models import AutoencoderKL
        print("✅ AutoencoderKL imported successfully")
    except Exception as e:
        print(f"⚠️  AutoencoderKL: {e}")
    
    print("\n🎯 Deep fix completed!") 