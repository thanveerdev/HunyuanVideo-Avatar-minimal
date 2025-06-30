#!/usr/bin/env python3
"""
Pre-import script to prevent TorchVision circular import issues in transformers library
This script should be run before starting the FastAPI server or any transformers imports
"""

import sys
import os
from unittest.mock import MagicMock

def setup_torchvision_mock():
    """Setup a mock TorchVision module to prevent circular import issues"""
    print("🔧 Setting up TorchVision mock to prevent circular imports...")
    
    # Only setup mock if torchvision isn't already loaded
    if 'torchvision' not in sys.modules:
        print("   📦 Creating TorchVision mock module...")
        
        # Create comprehensive mock
        mock_torchvision = MagicMock()
        
        # Mock transforms submodule
        mock_transforms = MagicMock()
        mock_transforms.InterpolationMode = type('InterpolationMode', (), {
            'BILINEAR': 'bilinear',
            'NEAREST': 'nearest',
            'BICUBIC': 'bicubic'
        })()
        mock_transforms.ToPILImage = MagicMock()
        mock_transforms.Compose = MagicMock()
        mock_transforms.Resize = MagicMock()
        mock_transforms.CenterCrop = MagicMock()
        mock_transforms.ToTensor = MagicMock()
        mock_transforms.Normalize = MagicMock()
        
        # Mock extension submodule (critical for preventing circular import)
        mock_extension = MagicMock()
        mock_extension._has_ops = MagicMock(return_value=False)
        
        # Mock other commonly imported submodules
        mock_ops = MagicMock()
        mock_models = MagicMock()
        mock_utils = MagicMock()
        mock_datasets = MagicMock()
        mock_io = MagicMock()
        
        # Assemble the mock module
        mock_torchvision.transforms = mock_transforms
        mock_torchvision.extension = mock_extension
        mock_torchvision.ops = mock_ops
        mock_torchvision.models = mock_models
        mock_torchvision.utils = mock_utils
        mock_torchvision.datasets = mock_datasets
        mock_torchvision.io = mock_io
        mock_torchvision.__version__ = "0.19.0"
        
        # Install mocks in sys.modules
        sys.modules['torchvision'] = mock_torchvision
        sys.modules['torchvision.transforms'] = mock_transforms
        sys.modules['torchvision.extension'] = mock_extension
        sys.modules['torchvision.ops'] = mock_ops
        sys.modules['torchvision.models'] = mock_models
        sys.modules['torchvision.utils'] = mock_utils
        sys.modules['torchvision.datasets'] = mock_datasets
        sys.modules['torchvision.io'] = mock_io
        
        print("   ✅ TorchVision mock installed successfully")
        return True
    else:
        print("   ℹ️  TorchVision already loaded, skipping mock")
        return False

def test_transformers_import():
    """Test if transformers can import CLIPImageProcessor without errors"""
    print("🧪 Testing transformers import after TorchVision mock...")
    
    try:
        from transformers import CLIPImageProcessor
        print("   ✅ CLIPImageProcessor imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ CLIPImageProcessor import failed: {e}")
        return False

def cleanup_and_reload_real_torchvision():
    """Remove mocks and try to load real TorchVision (optional)"""
    print("🔄 Attempting to load real TorchVision after transformers...")
    
    try:
        # Remove mocks if they exist
        mock_modules = [
            'torchvision', 'torchvision.transforms', 'torchvision.extension',
            'torchvision.ops', 'torchvision.models', 'torchvision.utils',
            'torchvision.datasets', 'torchvision.io'
        ]
        
        for module in mock_modules:
            if module in sys.modules and hasattr(sys.modules[module], '_mock_name'):
                print(f"   🗑️  Removing mock: {module}")
                del sys.modules[module]
        
        # Try to import real torchvision
        import torchvision
        print(f"   ✅ Real TorchVision loaded: {torchvision.__version__}")
        return True
        
    except Exception as e:
        print(f"   ⚠️  Real TorchVision could not be loaded: {e}")
        print("   ℹ️  Continuing with mocks (this is fine)")
        return False

def main():
    """Main function to setup TorchVision compatibility"""
    print("🚀 TorchVision Compatibility Setup")
    print("=" * 50)
    
    # Step 1: Setup mock
    mock_installed = setup_torchvision_mock()
    
    # Step 2: Test transformers import
    transformers_ok = test_transformers_import()
    
    # Step 3: Try to load real torchvision (optional)
    if mock_installed:
        real_torchvision_ok = cleanup_and_reload_real_torchvision()
    else:
        real_torchvision_ok = True
    
    # Summary
    print("\n📊 Setup Summary:")
    print(f"   Mock Installed: {'✅' if mock_installed else '❌'}")
    print(f"   Transformers OK: {'✅' if transformers_ok else '❌'}")
    print(f"   Real TorchVision: {'✅' if real_torchvision_ok else '⚠️'}")
    
    if transformers_ok:
        print("\n✅ TorchVision compatibility setup complete!")
        print("💡 FastAPI server should now start without circular import errors")
        return True
    else:
        print("\n❌ TorchVision compatibility setup failed!")
        print("⚠️  FastAPI server may still encounter import errors")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 