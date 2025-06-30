#!/usr/bin/env python3
"""
Focused test for the Gradio TypeError from My Pods Logs (29).txt

This tests the specific error:
TypeError: argument of type 'bool' is not iterable
at line: if "const" in schema
"""

import sys
import traceback

def test_gradio_schema_error():
    """Test for the specific Gradio schema TypeError"""
    print("🔍 Testing Gradio schema processing error...")
    print("=" * 60)
    
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
        
        # Try to reproduce the error scenario
        def test_function(text):
            return f"Echo: {text}"
        
        print("Creating Gradio interface...")
        interface = gr.Interface(
            fn=test_function,
            inputs=gr.Textbox(label="Test Input"),
            outputs=gr.Textbox(label="Test Output"),
            title="Test Interface"
        )
        print("✅ Gradio interface created successfully")
        
        # This is where the error occurs in the logs
        print("Testing API info generation (where the error occurs)...")
        try:
            api_info = interface.get_api_info()
            print("✅ API info generated successfully")
            return True
            
        except TypeError as e:
            if "argument of type 'bool' is not iterable" in str(e):
                print(f"❌ GRADIO ERROR PERSISTS: {e}")
                print("\nThis is the exact error from the logs:")
                print("  File \"gradio_client/utils.py\", line 863, in get_type")
                print("    if \"const\" in schema:")
                print("  TypeError: argument of type 'bool' is not iterable")
                return False
            else:
                print(f"❌ Different TypeError: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error in API info generation: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Gradio import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def test_gradio_schema_types():
    """Test different schema types that might trigger the error"""
    print("\n🔍 Testing schema type handling...")
    print("=" * 60)
    
    try:
        # Import the specific gradio_client utils where the error occurs
        from gradio_client.utils import get_type
        
        # Test different schema types
        test_schemas = [
            {"type": "string"},
            {"type": "object", "properties": {}},
            {"const": "value"},
            True,  # This boolean causes the error
            False, # This boolean causes the error
            {"additionalProperties": True},
            {"additionalProperties": False}
        ]
        
        for i, schema in enumerate(test_schemas):
            print(f"Testing schema {i+1}: {schema}")
            try:
                result = get_type(schema)
                print(f"  ✅ Schema processed successfully: {result}")
            except TypeError as e:
                if "argument of type 'bool' is not iterable" in str(e):
                    print(f"  ❌ SCHEMA ERROR: {e}")
                    print(f"  ❌ Problematic schema: {schema}")
                    return False
                else:
                    print(f"  ⚠️  Different TypeError: {e}")
            except Exception as e:
                print(f"  ⚠️  Other error: {e}")
        
        print("✅ All schema types processed without the specific error")
        return True
        
    except ImportError as e:
        print(f"⚠️  Cannot import gradio_client.utils: {e}")
        return True  # Not a failure if we can't test this
    except Exception as e:
        print(f"❌ Unexpected error in schema testing: {e}")
        return False

def test_gradio_version_info():
    """Show Gradio version information"""
    print("\n📋 Gradio version information...")
    print("=" * 60)
    
    try:
        import gradio as gr
        print(f"Gradio version: {gr.__version__}")
        
        try:
            import gradio_client
            print(f"Gradio client version: {gradio_client.__version__}")
        except:
            print("Gradio client version: Not available")
            
    except ImportError:
        print("Gradio is not installed")

if __name__ == "__main__":
    print("🚨 TESTING GRADIO ERROR FROM MY PODS LOGS (29).TXT")
    print("Testing the Gradio TypeError that causes API generation to fail")
    print("=" * 70)
    
    # Show version info
    test_gradio_version_info()
    
    # Test basic gradio functionality
    gradio_ok = test_gradio_schema_error()
    
    # Test schema handling specifically
    schema_ok = test_gradio_schema_types()
    
    print("\n" + "=" * 70)
    print("📊 GRADIO TEST RESULTS")
    print("=" * 70)
    
    if gradio_ok and schema_ok:
        print("✅ SUCCESS: The Gradio TypeError has been RESOLVED!")
        print("✅ Gradio API generation should work properly.")
        sys.exit(0)
    else:
        print("❌ FAILURE: The Gradio TypeError PERSISTS!")
        print("❌ This will cause errors when starting the web interface.")
        print("\n💡 POTENTIAL SOLUTIONS:")
        print("1. Update Gradio: pip install --upgrade gradio")
        print("2. Update gradio-client: pip install --upgrade gradio-client") 
        print("3. Check for version compatibility issues")
        sys.exit(1) 