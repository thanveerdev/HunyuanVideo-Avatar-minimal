"""
Minimal Configuration for Low VRAM Deployment
Optimized settings for single GPU with memory constraints
"""

# Memory Optimization Settings
MEMORY_CONFIG = {
    # GPU Memory Management
    "max_split_size_mb": 512,  # Reduce for 8GB VRAM, increase for 12GB+
    "cpu_offload": True,       # Move unused models to CPU
    "mixed_precision": True,   # Use FP16 to save memory
    "gradient_checkpointing": True,  # Trade compute for memory
    
    # Batch Processing
    "batch_size": 1,           # Process one item at a time
    "max_sequence_length": 77, # Standard CLIP text length
    "num_workers": 2,          # Reduce dataloader workers
    
    # Sequential Processing
    "enable_sequential_cpu_offload": True,
    "enable_model_cpu_offload": True,
    "enable_vae_slicing": True,
    "enable_vae_tiling": True,
}

# Quality vs Performance Settings
QUALITY_PRESETS = {
    "ultra_low_vram": {
        "image_size": 256,
        "video_length": 16,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "cpu_offload": True,
        "mixed_precision": True,
        "infer_min": True,
    },
    
    "low_vram": {
        "image_size": 384,
        "video_length": 32,
        "num_inference_steps": 25,
        "guidance_scale": 7.5,
        "cpu_offload": True,
        "mixed_precision": True,
        "infer_min": False,
    },
    
    "balanced": {
        "image_size": 512,
        "video_length": 64,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "cpu_offload": False,
        "mixed_precision": True,
        "infer_min": False,
    }
}

# Hardware Detection
def get_recommended_config():
    """Get recommended configuration based on available GPU memory."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            
            if gpu_memory <= 8:
                return QUALITY_PRESETS["ultra_low_vram"]
            elif gpu_memory <= 12:
                return QUALITY_PRESETS["low_vram"]
            else:
                return QUALITY_PRESETS["balanced"]
        else:
            # Fallback for CPU-only
            return QUALITY_PRESETS["ultra_low_vram"]
    except:
        # Fallback if detection fails
        return QUALITY_PRESETS["ultra_low_vram"]

# Environment Variables
ENVIRONMENT_SETUP = {
    "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
    "CUDA_LAUNCH_BLOCKING": "1",
    "OMP_NUM_THREADS": "4",
    "PYTORCH_NO_CUDA_MEMORY_CACHING": "1",
    "CUDA_CACHE_DISABLE": "1",
}

# Model Paths (relative to project root)
MODEL_PATHS = {
    "base_model": "./weights",
    "vae": "./weights/vae",
    "text_encoder": "./weights/text_encoder",
    "whisper": "./weights/ckpts/whisper-tiny",
    "face_detector": "./weights/ckpts/det_align",
}

# Default Arguments for Low VRAM
DEFAULT_ARGS = {
    "ckpt": "./weights",
    "save_path": "./outputs",
    "batch_size": 1,
    "image_size": 256,
    "cpu_offload": True,
    "mixed_precision": True,
    "infer_min": True,
    "enable_sequential_cpu_offload": True,
    "save_path_suffix": "minimal",
}

# Monitoring and Debugging
MONITORING_CONFIG = {
    "log_memory_usage": True,
    "log_gpu_utilization": True,
    "save_intermediate_results": False,  # Save memory
    "verbose_logging": False,  # Reduce I/O overhead
}

# Audio Processing Settings
AUDIO_CONFIG = {
    "sample_rate": 16000,      # Whisper standard
    "max_audio_length": 30,    # seconds
    "audio_channels": 1,       # Mono to save memory
    "feature_extraction_batch_size": 1,
}

def apply_memory_optimizations():
    """Apply memory optimizations to the current environment."""
    import os
    import torch
    
    # Set environment variables
    for key, value in ENVIRONMENT_SETUP.items():
        os.environ[key] = str(value)
    
    # Configure PyTorch
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = False  # Save memory
        torch.backends.cudnn.deterministic = True
        
        # Set memory allocation strategy
        torch.cuda.empty_cache()
        
        # Enable memory efficient attention if available
        try:
            torch.backends.cuda.enable_flash_sdp(True)
        except:
            pass
    
    print("✅ Memory optimizations applied")
    return True

def print_memory_info():
    """Print current memory usage information."""
    try:
        import torch
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            print(f"📊 GPU Memory Status:")
            print(f"   Allocated: {memory_allocated:.2f} GB")
            print(f"   Reserved:  {memory_reserved:.2f} GB")
            print(f"   Total:     {memory_total:.2f} GB")
            print(f"   Free:      {memory_total - memory_reserved:.2f} GB")
        else:
            print("❌ CUDA not available")
    except Exception as e:
        print(f"❌ Error checking memory: {e}")

if __name__ == "__main__":
    # Test the configuration
    print("🔧 Testing minimal configuration...")
    apply_memory_optimizations()
    print_memory_info()
    
    config = get_recommended_config()
    print(f"🎯 Recommended preset: {config}")
    print("✅ Configuration test completed") 