#!/usr/bin/env python3
"""
Focused test for the flash_attn dependency error from My Pods Logs (29).txt

This is the PRIMARY error that prevents the application from starting:
ModuleNotFoundError: No module named 'flash_attn'
"""

import sys
import os
import traceback

def test_flash_attn_availability():
    """Test if flash_attn module is available"""
    print("🔍 Testing flash_attn availability...")
    print("=" * 50)
    
    try:
        print("Attempting to import flash_attn...")
        import flash_attn
        print("✅ flash_attn module imported successfully")
        
        print("Attempting to import flash_attn_varlen_func...")
        from flash_attn.flash_attn_interface import flash_attn_varlen_func
        print("✅ flash_attn_varlen_func imported successfully")
        
        print("\n✅ SUCCESS: flash_attn is properly installed and available")
        return True
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("\n❌ CRITICAL ERROR PERSISTS: flash_attn is not available")
        print("\nThis is the PRIMARY error preventing the application from starting.")
        print("The error chain is:")
        print("  hymm_gradio/fastapi_server.py")
        print("  -> hymm_sp/audio_video_inference.py") 
        print("  -> hymm_sp/modules/models_audio.py")
        print("  -> from flash_attn.flash_attn_interface import flash_attn_varlen_func")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False

def test_hymm_sp_import_chain():
    """Test the specific import chain that fails due to flash_attn"""
    print("\n🔍 Testing HYMM SP import chain...")
    print("=" * 50)
    
    import_steps = [
        ("hymm_sp.modules", "Base modules package"),
        ("hymm_sp.modules.models_audio", "Models audio module (where flash_attn is required)"),
    ]
    
    for module_name, description in import_steps:
        try:
            print(f"Importing {module_name} ({description})...")
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
        except ImportError as e:
            print(f"❌ {module_name} FAILED: {e}")
            if "flash_attn" in str(e):
                print("❌ CONFIRMED: This is the flash_attn dependency error")
                return False
            else:
                print(f"❌ Different import error: {e}")
                return False
        except Exception as e:
            print(f"❌ {module_name} UNEXPECTED ERROR: {e}")
            return False
    
    print("✅ SUCCESS: All imports in chain completed successfully")
    return True

def test_install_flash_attn():
    """Provide instructions for installing flash_attn"""
    print("\n💡 FLASH ATTENTION INSTALLATION GUIDE")
    print("=" * 50)
    print("If flash_attn is missing, here are installation options:")
    print()
    print("1. Standard installation:")
    print("   pip install flash-attn")
    print()
    print("2. From source (if you have CUDA dev tools):")
    print("   pip install flash-attn --no-build-isolation")
    print()
    print("3. For specific CUDA versions, check:")
    print("   https://github.com/Dao-AILab/flash-attention")
    print()
    print("4. Alternative: Install pre-built wheels from:")
    print("   https://github.com/Dao-AILab/flash-attention/releases")
    print()
    print("Note: flash-attn requires:")
    print("  - CUDA-compatible GPU")
    print("  - PyTorch with CUDA support")
    print("  - Compatible CUDA toolkit")

if __name__ == "__main__":
    print("🚨 TESTING ERROR PERSISTENCE FROM MY PODS LOGS (29).TXT")
    print("Testing the PRIMARY error that prevents application startup")
    print("=" * 70)
    
    # Test flash_attn availability
    flash_attn_ok = test_flash_attn_availability()
    
    # Test import chain
    import_chain_ok = test_hymm_sp_import_chain()
    
    # Show installation guide if needed
    if not flash_attn_ok:
        test_install_flash_attn()
    
    print("\n" + "=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)
    
    if flash_attn_ok and import_chain_ok:
        print("✅ SUCCESS: The flash_attn error has been RESOLVED!")
        print("✅ The application should now be able to start properly.")
        sys.exit(0)
    else:
        print("❌ FAILURE: The flash_attn error PERSISTS!")
        print("❌ This error will prevent the application from starting.")
        print("❌ Install flash_attn to resolve this critical issue.")
        sys.exit(1) 