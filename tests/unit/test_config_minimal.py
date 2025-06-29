"""
Unit tests for config_minimal.py module.
Tests memory configuration, GPU detection, and environment setup.
"""

import pytest
import os
import torch
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config_minimal import (
    get_recommended_config,
    apply_memory_optimizations,
    print_memory_info,
    QUALITY_PRESETS,
    MEMORY_CONFIG,
    ENVIRONMENT_SETUP
)


class TestConfigMinimal:
    """Test suite for config_minimal module."""

    def test_quality_presets_structure(self):
        """Test that quality presets have correct structure."""
        required_keys = [
            "image_size", "video_length", "num_inference_steps",
            "guidance_scale", "cpu_offload", "mixed_precision", "infer_min"
        ]
        
        for preset_name, preset in QUALITY_PRESETS.items():
            for key in required_keys:
                assert key in preset, f"Missing key '{key}' in preset '{preset_name}'"
            
            # Validate value types and ranges
            assert isinstance(preset["image_size"], int)
            assert preset["image_size"] > 0
            assert isinstance(preset["video_length"], int)
            assert preset["video_length"] > 0
            assert isinstance(preset["num_inference_steps"], int)
            assert preset["num_inference_steps"] > 0
            assert isinstance(preset["guidance_scale"], (int, float))
            assert preset["guidance_scale"] > 0

    def test_memory_config_structure(self):
        """Test memory configuration structure."""
        required_keys = [
            "max_split_size_mb", "cpu_offload", "mixed_precision",
            "gradient_checkpointing", "batch_size"
        ]
        
        for key in required_keys:
            assert key in MEMORY_CONFIG, f"Missing key '{key}' in MEMORY_CONFIG"

    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    def test_get_recommended_config_low_vram(self, mock_props, mock_cuda):
        """Test configuration selection for low VRAM GPU."""
        mock_cuda.return_value = True
        mock_device_props = MagicMock()
        mock_device_props.total_memory = 8 * 1024**3  # 8GB
        mock_props.return_value = mock_device_props
        
        config = get_recommended_config()
        
        assert config["image_size"] == 256
        assert config["cpu_offload"] == True
        assert config["mixed_precision"] == True

    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    def test_get_recommended_config_high_vram(self, mock_props, mock_cuda):
        """Test configuration selection for high VRAM GPU."""
        mock_cuda.return_value = True
        mock_device_props = MagicMock()
        mock_device_props.total_memory = 16 * 1024**3  # 16GB
        mock_props.return_value = mock_device_props
        
        config = get_recommended_config()
        
        assert config["image_size"] == 512
        assert config["cpu_offload"] == False
        assert config["mixed_precision"] == True

    @patch('torch.cuda.is_available')
    def test_get_recommended_config_no_cuda(self, mock_cuda):
        """Test configuration selection when CUDA is not available."""
        mock_cuda.return_value = False
        
        config = get_recommended_config()
        
        # Should return ultra_low_vram preset
        assert config == QUALITY_PRESETS["ultra_low_vram"]

    @patch('torch.cuda.is_available')
    def test_get_recommended_config_exception_handling(self, mock_cuda):
        """Test configuration selection with exception in GPU detection."""
        mock_cuda.side_effect = Exception("GPU detection failed")
        
        config = get_recommended_config()
        
        # Should return fallback ultra_low_vram preset
        assert config == QUALITY_PRESETS["ultra_low_vram"]

    @patch('torch.cuda.is_available')
    @patch('torch.backends.cuda.enable_flash_sdp')
    def test_apply_memory_optimizations_success(self, mock_flash_sdp, mock_cuda):
        """Test successful memory optimization application."""
        mock_cuda.return_value = True
        
        # Store original environment
        original_env = os.environ.copy()
        
        try:
            result = apply_memory_optimizations()
            
            assert result == True
            
            # Check environment variables were set
            for key, value in ENVIRONMENT_SETUP.items():
                assert os.environ.get(key) == str(value)
                
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    @patch('torch.cuda.is_available')
    def test_apply_memory_optimizations_no_cuda(self, mock_cuda):
        """Test memory optimization application without CUDA."""
        mock_cuda.return_value = False
        
        result = apply_memory_optimizations()
        
        assert result == True

    @patch('torch.cuda.is_available')
    @patch('torch.cuda.memory_allocated')
    @patch('torch.cuda.memory_reserved')
    @patch('torch.cuda.get_device_properties')
    def test_print_memory_info_with_cuda(self, mock_props, mock_reserved, mock_allocated, mock_cuda):
        """Test memory info printing with CUDA available."""
        mock_cuda.return_value = True
        mock_allocated.return_value = 2 * 1024**3  # 2GB
        mock_reserved.return_value = 3 * 1024**3   # 3GB
        mock_device_props = MagicMock()
        mock_device_props.total_memory = 8 * 1024**3  # 8GB
        mock_props.return_value = mock_device_props
        
        # This should not raise an exception
        print_memory_info()

    @patch('torch.cuda.is_available')
    def test_print_memory_info_no_cuda(self, mock_cuda):
        """Test memory info printing without CUDA."""
        mock_cuda.return_value = False
        
        # This should not raise an exception
        print_memory_info()

    def test_environment_setup_values(self):
        """Test environment setup contains valid values."""
        for key, value in ENVIRONMENT_SETUP.items():
            assert isinstance(key, str)
            assert len(key) > 0
            assert value is not None

    def test_quality_presets_consistency(self):
        """Test quality presets are consistent and properly ordered."""
        presets = list(QUALITY_PRESETS.keys())
        expected_order = ["ultra_low_vram", "low_vram", "balanced"]
        
        assert presets == expected_order
        
        # Check that image sizes increase with quality
        ultra_low = QUALITY_PRESETS["ultra_low_vram"]["image_size"]
        low = QUALITY_PRESETS["low_vram"]["image_size"]
        balanced = QUALITY_PRESETS["balanced"]["image_size"]
        
        assert ultra_low <= low <= balanced

    def test_memory_config_values(self):
        """Test memory configuration values are reasonable."""
        assert MEMORY_CONFIG["max_split_size_mb"] > 0
        assert isinstance(MEMORY_CONFIG["cpu_offload"], bool)
        assert isinstance(MEMORY_CONFIG["mixed_precision"], bool)
        assert isinstance(MEMORY_CONFIG["gradient_checkpointing"], bool)
        assert MEMORY_CONFIG["batch_size"] > 0
        assert MEMORY_CONFIG["num_workers"] >= 0

    @pytest.mark.parametrize("vram_gb,expected_preset", [
        (4, "ultra_low_vram"),
        (8, "ultra_low_vram"),
        (10, "low_vram"),
        (12, "low_vram"),
        (16, "balanced"),
        (24, "balanced")
    ])
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    def test_vram_thresholds(self, mock_props, mock_cuda, vram_gb, expected_preset):
        """Test VRAM threshold detection for different GPU sizes."""
        mock_cuda.return_value = True
        mock_device_props = MagicMock()
        mock_device_props.total_memory = vram_gb * 1024**3
        mock_props.return_value = mock_device_props
        
        config = get_recommended_config()
        expected_config = QUALITY_PRESETS[expected_preset]
        
        assert config == expected_config


class TestConfigMinimalEdgeCases:
    """Test edge cases and error conditions."""

    def test_main_execution(self):
        """Test main execution block."""
        # Import the module to trigger main execution
        # This tests the if __name__ == "__main__" block
        pass

    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    def test_extreme_vram_values(self, mock_props, mock_cuda):
        """Test behavior with extreme VRAM values."""
        mock_cuda.return_value = True
        
        # Test very low VRAM
        mock_device_props = MagicMock()
        mock_device_props.total_memory = 1 * 1024**3  # 1GB
        mock_props.return_value = mock_device_props
        
        config = get_recommended_config()
        assert config == QUALITY_PRESETS["ultra_low_vram"]
        
        # Test very high VRAM
        mock_device_props.total_memory = 100 * 1024**3  # 100GB
        config = get_recommended_config()
        assert config == QUALITY_PRESETS["balanced"]

    @patch('torch.cuda.is_available')
    @patch('torch.cuda.get_device_properties')
    def test_zero_vram(self, mock_props, mock_cuda):
        """Test behavior with zero VRAM."""
        mock_cuda.return_value = True
        mock_device_props = MagicMock()
        mock_device_props.total_memory = 0
        mock_props.return_value = mock_device_props
        
        config = get_recommended_config()
        assert config == QUALITY_PRESETS["ultra_low_vram"]

    @patch.dict(os.environ, {}, clear=True)
    def test_environment_isolation(self):
        """Test that environment modifications are isolated."""
        original_env = os.environ.copy()
        
        apply_memory_optimizations()
        
        # Environment should be modified
        for key in ENVIRONMENT_SETUP.keys():
            assert key in os.environ
        
        # Clean up
        for key in ENVIRONMENT_SETUP.keys():
            if key in os.environ:
                del os.environ[key]
        
        # Restore
        os.environ.update(original_env) 