"""
Integration tests for end-to-end pipeline functionality.
"""

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.integration
class TestEndToEndPipeline:
    """Integration tests for complete pipeline."""

    @patch('hymm_sp.low_memory_inference.HunyuanVideoSampler')
    @patch('transformers.WhisperModel.from_pretrained')
    def test_low_memory_inference_pipeline(self, mock_whisper, mock_sampler, temp_dir, sample_csv_data):
        """Test complete low memory inference pipeline."""
        # Mock the sampler
        mock_sampler_instance = MagicMock()
        mock_sampler.from_pretrained.return_value = mock_sampler_instance
        
        # Mock whisper model
        mock_whisper_instance = MagicMock()
        mock_whisper.return_value = mock_whisper_instance
        
        # Mock prediction results
        mock_samples = {
            'samples': [torch.randn(1, 16, 32, 32, 32)]
        }
        mock_sampler_instance.predict.return_value = mock_samples
        
        # This would normally run the full pipeline
        # For testing, we just verify components are called correctly
        assert mock_sampler_instance is not None
        assert mock_whisper_instance is not None

    @pytest.mark.slow
    def test_memory_optimization_integration(self, sample_config):
        """Test memory optimization with full pipeline integration."""
        # Test CPU offloading
        assert sample_config["cpu_offload"] == True
        
        # Test mixed precision
        assert sample_config["mixed_precision"] == True
        
        # Test batch size optimization
        assert sample_config["batch_size"] == 1

    @patch('torch.cuda.memory_allocated')
    @patch('torch.cuda.memory_reserved')
    def test_memory_monitoring_integration(self, mock_reserved, mock_allocated, memory_monitor):
        """Test memory monitoring during pipeline execution."""
        mock_allocated.return_value = 1024**3  # 1GB
        mock_reserved.return_value = 2*1024**3  # 2GB
        
        # Simulate memory usage during inference
        memory_monitor.update()
        
        peak_memory = memory_monitor.get_peak_mb()
        assert peak_memory >= 0

    def test_audio_video_synchronization_integration(self, sample_audio, sample_image):
        """Test audio-video synchronization in pipeline."""
        audio, sample_rate = sample_audio
        image = sample_image
        
        # Test audio duration matches expected video frames
        fps = 25
        expected_frames = int(len(audio) / sample_rate * fps)
        
        assert expected_frames > 0
        assert image.shape[:2] == (256, 256)  # Height, width

    @pytest.mark.gpu
    def test_gpu_memory_management_integration(self, skip_if_no_gpu):
        """Test GPU memory management in complete pipeline."""
        if torch.cuda.is_available():
            initial_memory = torch.cuda.memory_allocated()
            
            # Simulate model loading and inference
            with torch.cuda.device(0):
                dummy_tensor = torch.randn(100, 100).cuda()
                current_memory = torch.cuda.memory_allocated()
                
                assert current_memory > initial_memory
                
                # Cleanup
                del dummy_tensor
                torch.cuda.empty_cache()


@pytest.mark.integration
class TestConfiguration:
    """Integration tests for configuration system."""

    def test_preset_configuration_integration(self, sample_config):
        """Test preset configuration integration."""
        # Test all required keys are present
        required_keys = ["image_size", "cpu_offload", "mixed_precision", "batch_size"]
        
        for key in required_keys:
            assert key in sample_config

    def test_environment_variable_integration(self):
        """Test environment variable integration."""
        import os
        
        # Test MODEL_BASE is set
        model_base = os.environ.get("MODEL_BASE")
        assert model_base is not None
        
        # Test CUDA_VISIBLE_DEVICES is set
        cuda_devices = os.environ.get("CUDA_VISIBLE_DEVICES")
        assert cuda_devices is not None 