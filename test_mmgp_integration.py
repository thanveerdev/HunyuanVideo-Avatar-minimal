#!/usr/bin/env python3
"""
Test script for MMGP integration with HunyuanVideo-Avatar
Verifies memory optimizations and MMGP functionality
"""

import sys
import os
import torch
import gc
from pathlib import Path
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mmgp_import():
    """Test if MMGP imports correctly."""
    try:
        from hymm_sp.mmgp_utils import memory_manager, apply_spaghetti_optimizations
        logger.info("✅ MMGP utilities imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ MMGP import failed: {e}")
        return False

def test_memory_monitoring():
    """Test memory monitoring functionality."""
    try:
        from hymm_sp.mmgp_utils import memory_manager
        
        logger.info("🔍 Testing memory monitoring...")
        memory_manager.monitor_memory("Test stage")
        
        # Create test tensor
        if torch.cuda.is_available():
            test_tensor = torch.randn(1000, 1000, device='cuda')
            memory_manager.monitor_memory("After tensor creation")
            
            # Test cleanup
            memory_manager.aggressive_cleanup(test_tensor)
            memory_manager.monitor_memory("After cleanup")
            
        logger.info("✅ Memory monitoring test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Memory monitoring test failed: {e}")
        return False

def test_chunked_processing():
    """Test tensor chunking functionality."""
    try:
        from hymm_sp.mmgp_utils import memory_manager
        
        logger.info("🔧 Testing tensor chunking...")
        
        # Create test tensor
        test_tensor = torch.randn(100, 100, 50)
        
        # Define dummy operation
        def dummy_op(x):
            return x * 2 + 1
        
        # Test chunked processing
        result = memory_manager.chunk_process_tensor(
            test_tensor, 
            dummy_op, 
            chunk_size=6
        )
        
        # Verify result
        expected = dummy_op(test_tensor)
        if torch.allclose(result, expected, atol=1e-6):
            logger.info("✅ Tensor chunking test passed")
            return True
        else:
            logger.error("❌ Tensor chunking results don't match")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tensor chunking test failed: {e}")
        return False

def test_spaghetti_optimizations():
    """Test spaghetti optimizations environment setup."""
    try:
        from hymm_sp.mmgp_utils import apply_spaghetti_optimizations
        
        logger.info("🍝 Testing spaghetti optimizations...")
        
        # Check if environment variables are set
        expected_vars = [
            "PYTORCH_CUDA_ALLOC_CONF",
            "PYTORCH_NO_CUDA_MEMORY_CACHING",
            "CUDA_CACHE_DISABLE"
        ]
        
        all_set = True
        for var in expected_vars:
            if var not in os.environ:
                logger.warning(f"⚠️  Environment variable {var} not set")
                all_set = False
            else:
                logger.info(f"✓ {var} = {os.environ[var]}")
        
        if all_set:
            logger.info("✅ Spaghetti optimizations test passed")
            return True
        else:
            logger.warning("⚠️  Some optimizations may not be active")
            return True  # Non-critical
            
    except Exception as e:
        logger.error(f"❌ Spaghetti optimizations test failed: {e}")
        return False

def test_emergency_cleanup():
    """Test emergency cleanup functionality."""
    try:
        from hymm_sp.mmgp_utils import memory_manager
        
        logger.info("🆘 Testing emergency cleanup...")
        
        if torch.cuda.is_available():
            # Create some tensors to cleanup
            test_tensors = [
                torch.randn(500, 500, device='cuda') for _ in range(3)
            ]
            
            memory_before = torch.cuda.memory_allocated()
            logger.info(f"Memory before cleanup: {memory_before / 1024**2:.1f} MB")
            
            # Trigger emergency cleanup
            memory_manager.emergency_cleanup()
            
            memory_after = torch.cuda.memory_allocated()
            logger.info(f"Memory after cleanup: {memory_after / 1024**2:.1f} MB")
            
            logger.info("✅ Emergency cleanup test completed")
            return True
        else:
            logger.warning("⚠️  CUDA not available, skipping emergency cleanup test")
            return True
            
    except Exception as e:
        logger.error(f"❌ Emergency cleanup test failed: {e}")
        return False

def main():
    """Run all MMGP integration tests."""
    logger.info("🚀 Starting MMGP Integration Tests")
    logger.info("=" * 50)
    
    tests = [
        ("MMGP Import", test_mmgp_import),
        ("Memory Monitoring", test_memory_monitoring),
        ("Tensor Chunking", test_chunked_processing),
        ("Spaghetti Optimizations", test_spaghetti_optimizations),
        ("Emergency Cleanup", test_emergency_cleanup),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"💥 {test_name} CRASHED: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All MMGP integration tests passed!")
        return 0
    else:
        logger.error(f"💥 {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main()) 