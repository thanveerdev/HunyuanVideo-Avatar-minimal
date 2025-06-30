"""
Minimal Configuration for Low VRAM Deployment
Optimized settings for single GPU with memory constraints
Support for 4GB+ VRAM cards with aggressive optimizations
"""

# Memory Optimization Settings
MEMORY_CONFIG = {
    # GPU Memory Management
    "max_split_size_mb": 256,  # Ultra-aggressive splitting for 4-6GB VRAM
    "cpu_offload": True,       # Move unused models to CPU
    "mixed_precision": True,   # Use FP16 to save memory
    "gradient_checkpointing": True,  # Trade compute for memory
    
    # Batch Processing
    "batch_size": 1,           # Process one item at a time
    "max_sequence_length": 77, # Standard CLIP text length
    "num_workers": 1,          # Minimal workers for ultra-low VRAM
    
    # Sequential Processing
    "enable_sequential_cpu_offload": True,
    "enable_model_cpu_offload": True,
    "enable_vae_slicing": True,
    "enable_vae_tiling": True,
    "enable_attention_slicing": True,
    "enable_model_offloading": True,
    
    # Advanced Memory Techniques
    "use_8bit_quantization": True,
    "enable_cpu_cache": True,
    "memory_efficient_attention": True,
    "low_mem_conv": True,
}

# Quality vs Performance Settings - Enhanced for Ultra-Low VRAM
QUALITY_PRESETS = {
    "ultra_minimal_4gb": {
        "image_size": 128,
        "video_length": 8,
        "num_inference_steps": 15,
        "guidance_scale": 6.0,
        "cpu_offload": True,
        "mixed_precision": True,
        "infer_min": True,
        "enable_8bit": True,
        "enable_cpu_cache": True,
        "max_split_size_mb": 128,
        "vae_slice_size": 1,
        "attention_slice_size": 1,
    },
    
    "ultra_low_vram": {
        "image_size": 256,
        "video_length": 16,
        "num_inference_steps": 20,
        "guidance_scale": 7.5,
        "cpu_offload": True,
        "mixed_precision": True,
        "infer_min": True,
        "enable_8bit": False,
        "max_split_size_mb": 256,
        "vae_slice_size": 2,
        "attention_slice_size": 2,
    },
    
    "low_vram": {
        "image_size": 384,
        "video_length": 32,
        "num_inference_steps": 25,
        "guidance_scale": 7.5,
        "cpu_offload": True,
        "mixed_precision": True,
        "infer_min": False,
        "max_split_size_mb": 512,
        "vae_slice_size": 4,
        "attention_slice_size": 4,
    },
    
    "balanced": {
        "image_size": 512,
        "video_length": 64,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "cpu_offload": True,  # Force CPU offloading even for high VRAM
        "mixed_precision": True,
        "infer_min": False,
        "max_split_size_mb": 1024,
        "vae_slice_size": 8,
        "attention_slice_size": 8,
    }
}

# Hardware Detection - Enhanced with more granular VRAM detection
def get_recommended_config():
    """Get recommended configuration based on available GPU memory."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            
            if gpu_memory <= 6:
                return QUALITY_PRESETS["ultra_minimal_4gb"]
            elif gpu_memory <= 8:
                return QUALITY_PRESETS["ultra_low_vram"]
            elif gpu_memory <= 12:
                return QUALITY_PRESETS["low_vram"]
            else:
                return QUALITY_PRESETS["balanced"]
        else:
            # Fallback for CPU-only
            return QUALITY_PRESETS["ultra_minimal_4gb"]
    except:
        # Fallback if detection fails
        return QUALITY_PRESETS["ultra_minimal_4gb"]

def get_dynamic_memory_config():
    """Get dynamic memory configuration based on current GPU state."""
    try:
        import torch
        if torch.cuda.is_available():
            # Get current memory usage
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            memory_free = memory_total - memory_allocated
            
            # Adjust configuration based on available memory
            if memory_free < 2:
                return {
                    "max_split_size_mb": 64,
                    "force_cpu_offload": True,
                    "enable_8bit": True,
                    "image_size": 128,
                }
            elif memory_free < 4:
                return {
                    "max_split_size_mb": 128,
                    "force_cpu_offload": True,
                    "enable_8bit": False,
                    "image_size": 256,
                }
            else:
                return get_recommended_config()
    except:
        return QUALITY_PRESETS["ultra_minimal_4gb"]

# Environment Variables - Enhanced for Ultra-Low VRAM
ENVIRONMENT_SETUP = {
    "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:256,garbage_collection_threshold:0.6,expandable_segments:True",
    "CUDA_LAUNCH_BLOCKING": "1",
    "OMP_NUM_THREADS": "2",  # Reduced for lower memory usage
    "PYTORCH_NO_CUDA_MEMORY_CACHING": "1",
    "CUDA_CACHE_DISABLE": "1",
    "TOKENIZERS_PARALLELISM": "false",  # Prevent multiprocessing issues
    "CUDA_MODULE_LOADING": "LAZY",  # Lazy loading to save memory
}

# Model Paths (relative to project root)
MODEL_PATHS = {
    "base_model": "./weights",
    "vae": "./weights/vae",
    "text_encoder": "./weights/text_encoder",
    "whisper": "./weights/ckpts/whisper-tiny",
    "face_detector": "./weights/ckpts/det_align",
}

# Default Arguments for Ultra-Low VRAM
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
    "enable_vae_slicing": True,
    "enable_vae_tiling": True,
    "enable_attention_slicing": True,
}

# Monitoring and Debugging
MONITORING_CONFIG = {
    "log_memory_usage": True,
    "log_gpu_utilization": True,
    "save_intermediate_results": False,  # Save memory
    "verbose_logging": False,  # Reduce I/O overhead
    "memory_cleanup_interval": 10,  # Cleanup every N steps
    "force_gc_interval": 5,     # Force garbage collection
}

# Audio Processing Settings - Optimized for memory
AUDIO_CONFIG = {
    "sample_rate": 16000,      # Whisper standard
    "max_audio_length": 15,    # Reduced for memory savings
    "audio_channels": 1,       # Mono to save memory
    "feature_extraction_batch_size": 1,
    "enable_audio_streaming": True,  # Process audio in chunks
}

def apply_memory_optimizations():
    """Apply aggressive memory optimizations to the current environment."""
    import os
    import gc
    import torch
    
    # Set environment variables
    for key, value in ENVIRONMENT_SETUP.items():
        os.environ[key] = str(value)
    
    # Configure PyTorch for minimal memory usage
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = False  # Save memory
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.allow_tf32 = False  # More memory efficient
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        
        # Enable memory efficient attention if available
        try:
            torch.backends.cuda.enable_flash_sdp(True)
            torch.backends.cuda.enable_mem_efficient_sdp(True)
        except:
            pass
        
        # Set memory fraction to prevent OOM
        try:
            torch.cuda.set_per_process_memory_fraction(0.85)  # Use max 85% of VRAM
        except:
            pass
    
    # Force garbage collection
    gc.collect()
    
    print("✅ Ultra-low VRAM optimizations applied")
    return True

def monitor_and_cleanup_memory():
    """Monitor memory usage and perform cleanup when needed."""
    import gc
    import torch
    
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated() / 1024**3
        memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        usage_percent = (memory_allocated / memory_total) * 100
        
        # Aggressive cleanup if memory usage is high
        if usage_percent > 75:
            torch.cuda.empty_cache()
            gc.collect()
            print(f"🧹 Memory cleanup triggered at {usage_percent:.1f}% usage")
        
        return usage_percent
    return 0

def print_memory_info():
    """Print current memory usage information."""
    try:
        import torch
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            print(f"📊 GPU Memory Status:")
            print(f"   Allocated: {memory_allocated:.2f} GB ({memory_allocated/memory_total*100:.1f}%)")
            print(f"   Reserved:  {memory_reserved:.2f} GB ({memory_reserved/memory_total*100:.1f}%)")
            print(f"   Total:     {memory_total:.2f} GB")
            print(f"   Free:      {memory_total - memory_reserved:.2f} GB")
            
            # Memory efficiency recommendations
            if memory_allocated/memory_total > 0.8:
                print("⚠️  High memory usage detected. Consider:")
                print("   • Reducing image_size")
                print("   • Enabling CPU offloading")
                print("   • Using 8-bit quantization")
        else:
            print("❌ CUDA not available")
    except Exception as e:
        print(f"❌ Error checking memory: {e}")

def get_optimal_batch_size():
    """Calculate optimal batch size based on available VRAM."""
    try:
        import torch
        if torch.cuda.is_available():
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            
            if memory_total <= 6:
                return 1
            elif memory_total <= 8:
                return 1
            elif memory_total <= 12:
                return 1  # Still conservative for video generation
            else:
                return 2
        return 1
    except:
        return 1

def setup_ultra_low_vram_mode():
    """Setup the most aggressive memory optimizations for 4-6GB VRAM."""
    import os
    import torch
    
    # Most aggressive environment settings
    ultra_env = {
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:64,garbage_collection_threshold:0.5,expandable_segments:True",
        "CUDA_LAUNCH_BLOCKING": "1",
        "OMP_NUM_THREADS": "1",
        "PYTORCH_NO_CUDA_MEMORY_CACHING": "1",
        "CUDA_CACHE_DISABLE": "1",
        "TOKENIZERS_PARALLELISM": "false",
        "CUDA_MODULE_LOADING": "LAZY",
        "PYTORCH_JIT": "0",  # Disable JIT compilation to save memory
    }
    
    for key, value in ultra_env.items():
        os.environ[key] = str(value)
    
    if torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(0.8)  # Use max 80% of VRAM
        torch.cuda.empty_cache()
    
    print("🚨 Ultra-low VRAM mode activated (4-6GB optimized)")

if __name__ == "__main__":
    # Test the configuration
    print("🔧 Testing enhanced minimal configuration...")
    apply_memory_optimizations()
    print_memory_info()
    
    config = get_recommended_config()
    print(f"🎯 Recommended preset: {config}")
    
    dynamic_config = get_dynamic_memory_config()
    print(f"🔄 Dynamic configuration: {dynamic_config}")
    
    optimal_batch = get_optimal_batch_size()
    print(f"📦 Optimal batch size: {optimal_batch}")
    
    print("✅ Enhanced configuration test completed") 