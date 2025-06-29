"""
Sample test data fixtures for HunyuanVideo-Avatar-minimal tests.
Provides reusable test data for various test scenarios.
"""

import numpy as np
from pathlib import Path
import json
import tempfile
import torch


# Sample configuration data
SAMPLE_CONFIGS = {
    "ultra_low_vram": {
        "image_size": 256,
        "video_length": 8,
        "num_inference_steps": 10,
        "guidance_scale": 6.0,
        "cpu_offload": True,
        "mixed_precision": True,
        "batch_size": 1,
        "infer_min": True
    },
    "low_vram": {
        "image_size": 256,
        "video_length": 16,
        "num_inference_steps": 15,
        "guidance_scale": 7.0,
        "cpu_offload": True,
        "mixed_precision": True,
        "batch_size": 1,
        "infer_min": True
    },
    "balanced": {
        "image_size": 512,
        "video_length": 16,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "cpu_offload": False,
        "mixed_precision": True,
        "batch_size": 1,
        "infer_min": False
    }
}

# Sample input data
SAMPLE_INPUT_DATA = {
    "csv_content": """videoid,image,audio,prompt,fps
test_001,assets/image/sample.png,assets/audio/sample.wav,A person speaking clearly,25
test_002,assets/image/sample.png,assets/audio/sample.wav,Another test prompt,30
test_003,assets/image/sample.png,assets/audio/sample.wav,Third test case,24
""",
    "prompts": [
        "A person speaking clearly into the camera",
        "Someone giving a presentation", 
        "A woman talking on the phone",
        "A man explaining something",
        "An interview conversation"
    ],
    "fps_values": [24, 25, 30],
    "image_sizes": [256, 512, 1024]
}

# Sample model architectures for testing
SAMPLE_MODEL_CONFIGS = {
    "transformer": {
        "hidden_size": 1024,
        "num_layers": 12,
        "num_heads": 16,
        "intermediate_size": 4096,
        "max_position_embeddings": 512
    },
    "vae": {
        "in_channels": 3,
        "out_channels": 3,
        "down_block_types": ["DownEncoderBlock2D"] * 4,
        "up_block_types": ["UpDecoderBlock2D"] * 4,
        "block_out_channels": [128, 256, 512, 512],
        "latent_channels": 16
    },
    "text_encoder": {
        "vocab_size": 50257,
        "hidden_size": 768,
        "num_hidden_layers": 12,
        "num_attention_heads": 12,
        "intermediate_size": 3072,
        "max_position_embeddings": 512
    }
}


def create_sample_image(size=(256, 256), channels=3):
    """Create a sample image for testing."""
    if channels == 3:
        # RGB image
        return np.random.randint(0, 255, (*size, channels), dtype=np.uint8)
    else:
        # Grayscale image
        return np.random.randint(0, 255, size, dtype=np.uint8)


def create_sample_audio(duration=1.0, sample_rate=16000, frequency=440):
    """Create a sample audio waveform for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Generate sine wave with some harmonics for more realistic sound
    audio = (np.sin(2 * np.pi * frequency * t) + 
             0.3 * np.sin(2 * np.pi * frequency * 2 * t) +
             0.1 * np.sin(2 * np.pi * frequency * 3 * t))
    # Normalize to [-1, 1]
    audio = audio / np.max(np.abs(audio))
    return audio.astype(np.float32), sample_rate


def create_sample_video(frames=16, height=256, width=256, channels=3):
    """Create a sample video tensor for testing."""
    return np.random.randint(0, 255, (frames, height, width, channels), dtype=np.uint8)


def create_sample_latent(batch_size=1, channels=16, height=32, width=32, frames=16):
    """Create sample latent representation for testing."""
    return np.random.randn(batch_size, channels, frames, height, width).astype(np.float32)


def create_sample_features(sequence_length=10, feature_dim=512):
    """Create sample audio features for testing."""
    return np.random.randn(sequence_length, feature_dim).astype(np.float32)


def create_mock_model_weights():
    """Create mock model weights for testing."""
    return {
        "transformer.layers.0.attention.query.weight": torch.randn(1024, 1024),
        "transformer.layers.0.attention.key.weight": torch.randn(1024, 1024),
        "transformer.layers.0.attention.value.weight": torch.randn(1024, 1024),
        "transformer.layers.0.mlp.linear1.weight": torch.randn(4096, 1024),
        "transformer.layers.0.mlp.linear2.weight": torch.randn(1024, 4096),
        "vae.encoder.conv_in.weight": torch.randn(128, 3, 3, 3),
        "vae.decoder.conv_out.weight": torch.randn(3, 128, 3, 3),
        "text_encoder.embeddings.word_embeddings.weight": torch.randn(50257, 768)
    }


def create_sample_csv_file(temp_dir, num_entries=3):
    """Create a sample CSV input file for testing."""
    csv_path = temp_dir / "test_input.csv"
    
    entries = []
    entries.append("videoid,image,audio,prompt,fps")
    
    for i in range(num_entries):
        entry = f"test_{i:03d},assets/image/sample.png,assets/audio/sample.wav,Test prompt {i+1},25"
        entries.append(entry)
    
    csv_path.write_text("\n".join(entries))
    return csv_path


def create_test_environment(base_path):
    """Create complete test environment with all necessary files."""
    base_path = Path(base_path)
    
    # Create directory structure
    dirs = [
        "assets/image",
        "assets/audio", 
        "weights",
        "outputs",
        "tests/fixtures"
    ]
    
    for dir_path in dirs:
        (base_path / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create sample files
    files_created = []
    
    # Sample image
    image_path = base_path / "assets/image/sample.png"
    try:
        from PIL import Image
        img_array = create_sample_image()
        img = Image.fromarray(img_array)
        img.save(image_path)
        files_created.append(str(image_path))
    except ImportError:
        # Fallback: create a dummy file
        image_path.write_bytes(b"DUMMY_PNG_DATA")
        files_created.append(str(image_path))
    
    # Sample audio
    audio_path = base_path / "assets/audio/sample.wav"
    try:
        import soundfile as sf
        audio, sr = create_sample_audio()
        sf.write(audio_path, audio, sr)
        files_created.append(str(audio_path))
    except ImportError:
        # Fallback: create a dummy file
        audio_path.write_bytes(b"DUMMY_WAV_DATA")
        files_created.append(str(audio_path))
    
    # Sample CSV
    csv_path = create_sample_csv_file(base_path)
    files_created.append(str(csv_path))
    
    # Weights README
    weights_readme = base_path / "weights/README.md"
    weights_readme.write_text("# Model weights directory\n\nPlace your model checkpoint files here.\n")
    files_created.append(str(weights_readme))
    
    # Mock model weights
    model_weights_path = base_path / "weights/mock_model.pt"
    mock_weights = create_mock_model_weights()
    torch.save({"model": mock_weights}, model_weights_path)
    files_created.append(str(model_weights_path))
    
    return files_created


def get_memory_test_scenarios():
    """Get test scenarios for different memory configurations."""
    return [
        {
            "name": "4GB_VRAM",
            "vram_gb": 4,
            "config": SAMPLE_CONFIGS["ultra_low_vram"],
            "expected_behavior": {
                "cpu_offload": True,
                "mixed_precision": True,
                "max_batch_size": 1,
                "image_size": 256
            }
        },
        {
            "name": "8GB_VRAM", 
            "vram_gb": 8,
            "config": SAMPLE_CONFIGS["low_vram"],
            "expected_behavior": {
                "cpu_offload": True,
                "mixed_precision": True,
                "max_batch_size": 1,
                "image_size": 256
            }
        },
        {
            "name": "16GB_VRAM",
            "vram_gb": 16,
            "config": SAMPLE_CONFIGS["balanced"],
            "expected_behavior": {
                "cpu_offload": False,
                "mixed_precision": True,
                "max_batch_size": 2,
                "image_size": 512
            }
        }
    ]


def get_performance_benchmarks():
    """Get performance benchmark targets."""
    return {
        "inference_time": {
            "256x256_16frames": {"max_seconds": 120, "target_seconds": 60},
            "512x512_16frames": {"max_seconds": 300, "target_seconds": 180}
        },
        "memory_usage": {
            "peak_vram_4gb": {"max_mb": 3800, "target_mb": 3200},
            "peak_vram_8gb": {"max_mb": 7600, "target_mb": 6400},
            "peak_ram": {"max_mb": 8000, "target_mb": 4000}
        },
        "throughput": {
            "frames_per_second": {"min_fps": 0.1, "target_fps": 0.3},
            "batch_efficiency": {"min_speedup": 1.2, "target_speedup": 1.8}
        }
    }


# Export commonly used data
__all__ = [
    'SAMPLE_CONFIGS',
    'SAMPLE_INPUT_DATA', 
    'SAMPLE_MODEL_CONFIGS',
    'create_sample_image',
    'create_sample_audio',
    'create_sample_video',
    'create_sample_latent',
    'create_sample_features',
    'create_mock_model_weights',
    'create_sample_csv_file',
    'create_test_environment',
    'get_memory_test_scenarios',
    'get_performance_benchmarks'
] 