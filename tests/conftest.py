"""
Global test configuration and fixtures for HunyuanVideo-Avatar-Minimal tests.
"""

import os
import tempfile
import pytest
import torch
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup global test environment."""
    # Set environment variables
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    os.environ["MODEL_BASE"] = "./weights"
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    
    # Set torch settings for tests
    torch.set_grad_enabled(False)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    yield
    
    # Cleanup
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_device():
    """Mock device for testing."""
    if torch.cuda.is_available():
        return torch.device("cuda:0")
    else:
        return torch.device("cpu")

@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "image_size": 256,
        "video_length": 16,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "cpu_offload": True,
        "mixed_precision": True,
        "batch_size": 1,
        "infer_min": True,
    }

@pytest.fixture
def mock_gpu_properties():
    """Mock GPU properties for testing."""
    mock_props = MagicMock()
    mock_props.total_memory = 8 * 1024**3  # 8GB
    mock_props.name = "Test GPU"
    return mock_props

@pytest.fixture
def sample_image():
    """Generate sample image for testing."""
    # Create a simple RGB image
    image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
    return image

@pytest.fixture
def sample_audio():
    """Generate sample audio for testing."""
    # Create a simple audio waveform (1 second, 16kHz)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440Hz sine wave
    return audio, sample_rate

@pytest.fixture
def sample_csv_data(temp_dir):
    """Create sample CSV input file for testing."""
    csv_content = """videoid,image,audio,prompt,fps
test1,assets/image/1.png,assets/audio/2.WAV,A person speaking,25
test2,assets/image/1.png,assets/audio/2.WAV,Another test prompt,30
"""
    csv_path = temp_dir / "test_input.csv"
    csv_path.write_text(csv_content)
    return csv_path

@pytest.fixture
def mock_model_weights(temp_dir):
    """Create mock model weights directory."""
    weights_dir = temp_dir / "weights"
    weights_dir.mkdir()
    
    # Create mock checkpoint file
    checkpoint_path = weights_dir / "test_model_states.pt"
    torch.save({"model": {}}, checkpoint_path)
    
    return weights_dir

@pytest.fixture
def mock_inference_args():
    """Mock arguments for inference testing."""
    class MockArgs:
        def __init__(self):
            self.ckpt = "./weights"
            self.save_path = "./outputs"
            self.batch_size = 1
            self.image_size = 256
            self.cpu_offload = True
            self.mixed_precision = True
            self.infer_min = True
            self.precision = "fp16"
            self.latent_channels = 16
            self.use_fp8 = False
            self.vae = "test_vae"
            self.vae_precision = "fp16"
            self.text_encoder = "test_encoder"
            self.text_encoder_precision = "fp16"
            self.tokenizer = "test_tokenizer"
            self.use_attention_mask = True
            self.prompt_template_video = None
            self.text_len = 77
            self.hidden_state_skip_layer = 0
            self.apply_final_norm = True
            self.reproduce = False
            self.load_key = "model"
            self.text_encoder_2 = None
            self.text_len_2 = 77
            self.text_encoder_precision_2 = "fp16"
            self.tokenizer_2 = None
            self.seed = 42
            self.infer_steps = 20
            self.cfg_scale = 7.5
            self.num_images = 1
            self.input = "test.csv"
            self.save_path_suffix = ""
    
    return MockArgs()

@pytest.fixture(autouse=True)
def mock_cuda_memory():
    """Mock CUDA memory functions to prevent actual GPU usage in tests."""
    with patch('torch.cuda.memory_allocated', return_value=1024**3):
        with patch('torch.cuda.memory_reserved', return_value=2*1024**3):
            with patch('torch.cuda.max_memory_allocated', return_value=3*1024**3):
                with patch('torch.cuda.empty_cache'):
                    yield

@pytest.fixture
def memory_monitor():
    """Monitor memory usage during tests."""
    import psutil
    import gc
    
    class MemoryMonitor:
        def __init__(self):
            self.initial_memory = psutil.Process().memory_info().rss
            self.peak_memory = self.initial_memory
        
        def update(self):
            current_memory = psutil.Process().memory_info().rss
            self.peak_memory = max(self.peak_memory, current_memory)
        
        def get_peak_mb(self):
            return (self.peak_memory - self.initial_memory) / 1024**2
        
        def cleanup(self):
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    monitor = MemoryMonitor()
    yield monitor
    monitor.cleanup()

def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "requires_gpu: mark test as requiring GPU"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add GPU marker for GPU tests
        if "gpu" in item.nodeid.lower() or "cuda" in item.nodeid.lower():
            item.add_marker(pytest.mark.gpu)
        
        # Add slow marker for performance tests
        if "performance" in item.nodeid.lower() or "benchmark" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
        
        # Skip GPU tests if CUDA not available
        if "gpu" in [mark.name for mark in item.iter_markers()]:
            if not torch.cuda.is_available():
                item.add_marker(pytest.mark.skip(reason="CUDA not available"))

@pytest.fixture
def skip_if_no_gpu():
    """Skip test if GPU is not available."""
    if not torch.cuda.is_available():
        pytest.skip("GPU not available")

@pytest.fixture
def skip_if_no_weights():
    """Skip test if model weights are not available."""
    weights_path = Path("./weights")
    if not weights_path.exists():
        pytest.skip("Model weights not available") 