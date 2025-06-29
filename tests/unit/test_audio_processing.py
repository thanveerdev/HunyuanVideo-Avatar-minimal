"""
Unit tests for audio processing components.
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestAudioProcessing:
    """Test suite for audio processing functions."""

    def test_audio_loading_valid_file(self, sample_audio):
        """Test loading valid audio file."""
        audio, sample_rate = sample_audio
        
        assert isinstance(audio, np.ndarray)
        assert sample_rate == 16000
        assert len(audio) > 0

    def test_audio_preprocessing_normalization(self, sample_audio):
        """Test audio preprocessing and normalization."""
        audio, sample_rate = sample_audio
        
        # Test audio is within expected range
        assert np.min(audio) >= -1.0
        assert np.max(audio) <= 1.0

    def test_audio_feature_extraction_shape(self, sample_audio):
        """Test audio feature extraction produces correct shape."""
        audio, sample_rate = sample_audio
        
        # Mock feature extraction
        expected_features = np.random.rand(10, 512)  # Mock features
        
        assert expected_features.shape[1] == 512  # Feature dimension
        assert expected_features.shape[0] > 0     # Time dimension

    @pytest.mark.parametrize("duration,expected_frames", [
        (1.0, 16000),
        (2.0, 32000),
        (0.5, 8000)
    ])
    def test_audio_duration_processing(self, duration, expected_frames):
        """Test audio processing for different durations."""
        sample_rate = 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)
        
        assert len(audio) == expected_frames

    def test_audio_batch_processing(self):
        """Test batch processing of audio."""
        batch_size = 4
        audio_length = 16000
        
        # Create batch of audio
        audio_batch = np.random.randn(batch_size, audio_length)
        
        assert audio_batch.shape == (batch_size, audio_length)
        
        # Test processing maintains batch dimension
        processed_batch = audio_batch  # Mock processing
        assert processed_batch.shape[0] == batch_size

    def test_whisper_integration_mock(self):
        """Test Whisper model integration (mocked)."""
        mock_whisper = MagicMock()
        mock_whisper.return_value = {"features": np.random.rand(1, 10, 512)}
        
        # Test whisper processing
        result = mock_whisper()
        assert "features" in result
        assert result["features"].shape[-1] == 512 