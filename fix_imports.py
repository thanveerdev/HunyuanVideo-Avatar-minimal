#!/usr/bin/env python3
"""
Quick import fix and test script for HunyuanVideo Avatar
Run this in RunPod to diagnose and fix import issues
"""

import os
import sys

def test_imports():
    """Test all critical imports to diagnose issues."""
    print("🔍 Testing Python imports...")
    
    # Add workspace to path
    workspace_path = '/workspace'
    if workspace_path not in sys.path:
        sys.path.insert(0, workspace_path)
        print(f"✅ Added {workspace_path} to Python path")
    
    # Test basic imports
    imports_to_test = [
        ('os', 'os'),
        ('sys', 'sys'),
        ('torch', 'torch'),
        ('numpy', 'numpy as np'),
        ('gradio', 'gradio as gr'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('transformers', 'transformers'),
    ]
    
    failed_imports = []
    
    for module_name, import_statement in imports_to_test:
        try:
            exec(f"import {import_statement}")
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            print(f"❌ {module_name}: FAILED - {e}")
            failed_imports.append(module_name)
    
    # Test hymm_gradio imports specifically
    print("\n🔍 Testing hymm_gradio module imports...")
    
    try:
        from hymm_gradio import pipeline_utils
        print("✅ hymm_gradio.pipeline_utils: OK")
    except ImportError as e:
        print(f"❌ hymm_gradio.pipeline_utils: FAILED - {e}")
        failed_imports.append('hymm_gradio.pipeline_utils')
    
    try:
        import hymm_gradio.fastapi_server
        print("✅ hymm_gradio.fastapi_server: OK")
    except ImportError as e:
        print(f"❌ hymm_gradio.fastapi_server: FAILED - {e}")
        failed_imports.append('hymm_gradio.fastapi_server')
    
    try:
        import hymm_gradio.web_demo
        print("✅ hymm_gradio.web_demo: OK")
    except ImportError as e:
        print(f"❌ hymm_gradio.web_demo: FAILED - {e}")
        failed_imports.append('hymm_gradio.web_demo')
    
    return failed_imports

def check_file_structure():
    """Check if all required files exist."""
    print("\n📁 Checking file structure...")
    
    required_files = [
        '/workspace/hymm_gradio/__init__.py',
        '/workspace/hymm_gradio/pipeline_utils.py',
        '/workspace/hymm_gradio/fastapi_server.py',
        '/workspace/hymm_gradio/web_demo.py',
        '/workspace/docker_startup_network_volume.sh',
        '/workspace/config_minimal.py',
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return missing_files

def fix_permissions():
    """Fix permissions for scripts."""
    print("\n🔧 Fixing permissions...")
    
    scripts_to_fix = [
        '/workspace/docker_startup_network_volume.sh',
        '/workspace/network_volume_utils.py',
    ]
    
    for script in scripts_to_fix:
        if os.path.exists(script):
            try:
                os.chmod(script, 0o755)
                print(f"✅ Fixed permissions for {script}")
            except Exception as e:
                print(f"❌ Failed to fix permissions for {script}: {e}")

def test_network_volume():
    """Test network volume setup."""
    print("\n💾 Testing network volume...")
    
    volume_path = '/network_volume'
    
    if os.path.exists(volume_path):
        print(f"✅ Network volume mounted at {volume_path}")
        
        # Test write access
        try:
            test_file = os.path.join(volume_path, 'test_write.txt')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✅ Network volume write access: OK")
        except Exception as e:
            print(f"❌ Network volume write access: FAILED - {e}")
    else:
        print(f"❌ Network volume not found at {volume_path}")

def main():
    """Main diagnostic function."""
    print("🚀 HunyuanVideo Avatar Import Diagnostics")
    print("=" * 50)
    
    # Change to workspace directory
    os.chdir('/workspace')
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Test imports
    failed_imports = test_imports()
    
    # Check file structure
    missing_files = check_file_structure()
    
    # Fix permissions
    fix_permissions()
    
    # Test network volume
    test_network_volume()
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 30)
    
    if not failed_imports and not missing_files:
        print("🎉 All checks passed! System should work correctly.")
    else:
        print("⚠️  Issues found:")
        if failed_imports:
            print(f"   - Failed imports: {', '.join(failed_imports)}")
        if missing_files:
            print(f"   - Missing files: {', '.join(missing_files)}")
    
    print("\n🔧 Manual fixes you can try:")
    print("   - pip install missing packages")
    print("   - chmod +x /workspace/docker_startup_network_volume.sh")
    print("   - export PYTHONPATH='/workspace:$PYTHONPATH'")
    print("   - python -m hymm_gradio.web_demo (for Gradio)")
    print("   - python -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80 (for FastAPI)")

if __name__ == "__main__":
    main() 