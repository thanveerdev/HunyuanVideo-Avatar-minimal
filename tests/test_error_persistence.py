#!/usr/bin/env python3
"""
Test suite to detect persistence of errors identified in My Pods Logs (29).txt

This test suite specifically targets the errors found in the log:
1. Missing flash_attn dependency
2. Gradio TypeError with schema checking
3. TorchVision compatibility issues
4. FastAPI server startup issues
"""

import sys
import os
import pytest
import importlib
import subprocess
import warnings
from unittest.mock import patch, MagicMock
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestErrorPersistence:
    """Test suite to check if the critical errors from the logs persist"""
    
    def test_flash_attn_import(self):
        """Test if flash_attn module is available - PRIMARY ERROR from logs"""
        try:
            import flash_attn
            from flash_attn.flash_attn_interface import flash_attn_varlen_func
            print("✅ flash_attn is available")
            return True
        except ImportError as e:
            pytest.fail(f"❌ CRITICAL ERROR PERSISTS: flash_attn not available - {e}")
            return False
    
    def test_hymm_sp_models_audio_import(self):
        """Test the specific import chain that fails due to flash_attn"""
        try:
            # This is the exact import chain that fails in the logs
            from hymm_sp.modules.models_audio import HYVideoDiffusionTransformer, HUNYUAN_VIDEO_CONFIG
            print("✅ hymm_sp.modules.models_audio imports successfully")
            return True
        except ModuleNotFoundError as e:
            if "flash_attn" in str(e):
                pytest.fail(f"❌ CRITICAL ERROR PERSISTS: flash_attn dependency missing in models_audio - {e}")
            else:
                pytest.fail(f"❌ Import error in models_audio: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Other error in models_audio import: {e}")
            return False
    
    def test_gradio_schema_type_error(self):
        """Test for the Gradio TypeError: argument of type 'bool' is not iterable"""
        try:
            # Mock the problematic gradio_client function that fails
            from gradio_client import utils as gradio_utils
            
            # Test with a schema that might trigger the error
            test_schemas = [
                True,  # This boolean value causes the error
                False,
                {"type": "object"},
                {"const": "value"},
                {"additionalProperties": True}
            ]
            
            for schema in test_schemas:
                try:
                    if hasattr(gradio_utils, 'get_type'):
                        # This is where the error occurs: if "const" in schema
                        result = gradio_utils.get_type(schema)
                        print(f"✅ Schema {schema} processed successfully")
                except TypeError as e:
                    if "argument of type 'bool' is not iterable" in str(e):
                        pytest.fail(f"❌ GRADIO ERROR PERSISTS: TypeError with schema {schema} - {e}")
                        return False
                except Exception as e:
                    print(f"⚠️  Other error with schema {schema}: {e}")
            
            return True
            
        except ImportError:
            print("⚠️  gradio_client not available for testing")
            return False
    
    def test_torchvision_interpolation_mode_error(self):
        """Test for TorchVision InterpolationMode.BOX attribute error"""
        try:
            import torchvision.transforms.functional as F
            from torchvision.transforms import InterpolationMode
            
            # Test if InterpolationMode.BOX exists
            if hasattr(InterpolationMode, 'BOX'):
                print("✅ InterpolationMode.BOX is available")
                return True
            else:
                pytest.fail("❌ TORCHVISION ERROR PERSISTS: InterpolationMode.BOX not available")
                return False
                
        except ImportError as e:
            pytest.fail(f"❌ TorchVision import error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Other TorchVision error: {e}")
            return False
    
    def test_torchvision_nms_operator(self):
        """Test for TorchVision NMS operator availability"""
        try:
            import torch
            import torchvision
            
            # Test if torchvision::nms operator exists
            boxes = torch.tensor([[0, 0, 1, 1], [0.5, 0.5, 1.5, 1.5]], dtype=torch.float32)
            scores = torch.tensor([0.9, 0.8], dtype=torch.float32)
            
            result = torchvision.ops.nms(boxes, scores, 0.5)
            print("✅ torchvision::nms operator is available")
            return True
            
        except RuntimeError as e:
            if "operator torchvision::nms does not exist" in str(e):
                pytest.fail(f"❌ TORCHVISION ERROR PERSISTS: NMS operator not available - {e}")
                return False
            else:
                print(f"⚠️  Other NMS error: {e}")
                return False
        except Exception as e:
            print(f"⚠️  TorchVision NMS test error: {e}")
            return False
    
    def test_fastapi_server_startup(self):
        """Test if FastAPI server can start without the critical errors"""
        try:
            # Test if we can import the FastAPI server module
            from hymm_gradio.fastapi_server import app
            print("✅ FastAPI server module imports successfully")
            return True
            
        except ModuleNotFoundError as e:
            if "flash_attn" in str(e):
                pytest.fail(f"❌ FASTAPI ERROR PERSISTS: flash_attn dependency blocks server startup - {e}")
            else:
                pytest.fail(f"❌ FastAPI server import error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Other FastAPI server error: {e}")
            return False
    
    def test_transformers_clip_processor_import(self):
        """Test for the CLIPImageProcessor import error mentioned in logs"""
        try:
            from transformers.models.clip.image_processing_clip import CLIPImageProcessor
            print("✅ CLIPImageProcessor imports successfully")
            return True
            
        except ImportError as e:
            if "InterpolationMode" in str(e) and "BOX" in str(e):
                pytest.fail(f"❌ CLIP PROCESSOR ERROR PERSISTS: InterpolationMode.BOX issue - {e}")
                return False
            else:
                print(f"⚠️  Other CLIPImageProcessor import error: {e}")
                return False
        except Exception as e:
            print(f"⚠️  CLIPImageProcessor test error: {e}")
            return False
    
    def test_gradio_web_interface_startup(self):
        """Test if Gradio web interface can start without TypeError"""
        try:
            import gradio as gr
            
            # Create a simple interface to test schema processing
            def dummy_function(text):
                return f"Echo: {text}"
            
            # This should trigger the schema processing that causes the error
            interface = gr.Interface(
                fn=dummy_function,
                inputs=gr.Textbox(label="Input"),
                outputs=gr.Textbox(label="Output")
            )
            
            # Try to get API info which triggers the error in logs
            try:
                api_info = interface.get_api_info()
                print("✅ Gradio API info generation successful")
                return True
            except TypeError as e:
                if "argument of type 'bool' is not iterable" in str(e):
                    pytest.fail(f"❌ GRADIO API ERROR PERSISTS: {e}")
                    return False
                else:
                    raise e
                    
        except Exception as e:
            print(f"⚠️  Gradio interface test error: {e}")
            return False
    
    def test_comprehensive_import_chain(self):
        """Test the complete import chain that fails in the logs"""
        import_chain = [
            "hymm_gradio.fastapi_server",
            "hymm_sp.audio_video_inference", 
            "hymm_sp.diffusion",
            "hymm_sp.diffusion.pipelines",
            "hymm_sp.diffusion.pipelines.pipeline_hunyuan_video_audio",
            "hymm_sp.vae.autoencoder_kl_causal_3d",
            "hymm_sp.helpers",
            "hymm_sp.modules.posemb_layers",
            "hymm_sp.modules.models_audio"
        ]
        
        failed_imports = []
        
        for module_name in import_chain:
            try:
                importlib.import_module(module_name)
                print(f"✅ {module_name} imported successfully")
            except Exception as e:
                failed_imports.append((module_name, str(e)))
                print(f"❌ {module_name} failed: {e}")
        
        if failed_imports:
            error_msg = "IMPORT CHAIN ERRORS PERSIST:\n"
            for module, error in failed_imports:
                error_msg += f"  - {module}: {error}\n"
            pytest.fail(error_msg)
            return False
        
        return True

    def test_environment_requirements(self):
        """Test if all required dependencies are properly installed"""
        critical_packages = [
            "flash_attn",
            "torch",
            "torchvision", 
            "transformers",
            "gradio",
            "fastapi",
            "uvicorn"
        ]
        
        missing_packages = []
        
        for package in critical_packages:
            try:
                importlib.import_module(package)
                print(f"✅ {package} is available")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} is missing")
        
        if missing_packages:
            pytest.fail(f"❌ CRITICAL DEPENDENCIES MISSING: {', '.join(missing_packages)}")
            return False
        
        return True


if __name__ == "__main__":
    """Run tests directly to check error persistence"""
    print("🔍 Testing for error persistence from My Pods Logs (29).txt")
    print("=" * 60)
    
    test_instance = TestErrorPersistence()
    
    tests = [
        ("Flash Attention Import", test_instance.test_flash_attn_import),
        ("HYMM SP Models Audio Import", test_instance.test_hymm_sp_models_audio_import),
        ("Gradio Schema Type Error", test_instance.test_gradio_schema_type_error),
        ("TorchVision InterpolationMode", test_instance.test_torchvision_interpolation_mode_error),
        ("TorchVision NMS Operator", test_instance.test_torchvision_nms_operator),
        ("FastAPI Server Startup", test_instance.test_fastapi_server_startup),
        ("Transformers CLIP Processor", test_instance.test_transformers_clip_processor_import),
        ("Gradio Web Interface", test_instance.test_gradio_web_interface_startup),
        ("Comprehensive Import Chain", test_instance.test_comprehensive_import_chain),
        ("Environment Requirements", test_instance.test_environment_requirements)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            results.append((test_name, "FAIL"))
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, status in results:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
    
    failed_tests = [name for name, status in results if status == "FAIL"]
    
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} test(s) failed - errors persist!")
        print("Failed tests:", ", ".join(failed_tests))
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} tests passed - errors have been resolved!")
        sys.exit(0) 