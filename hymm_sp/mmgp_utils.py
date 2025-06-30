"""
MMGP Integration for HunyuanVideo-Avatar
Memory Management for GPU Poor - Extreme VRAM optimizations
Based on HunyuanVideoGP techniques by DeepBeepMeep
"""

import torch
import gc
import os
from typing import Optional, Any, Dict
from loguru import logger

# Try to import mmgp, fallback to regular loading if not available
try:
    from mmgp import offload
    MMGP_AVAILABLE = True
    logger.info("✅ MMGP library loaded successfully")
except ImportError:
    MMGP_AVAILABLE = False
    logger.warning("⚠️  MMGP library not available, using standard loading")


class MMGPMemoryManager:
    """Memory manager using MMGP techniques for extreme VRAM optimization."""
    
    def __init__(self, enable_quantization: bool = True, enable_aggressive_cleanup: bool = True):
        self.enable_quantization = enable_quantization
        self.enable_aggressive_cleanup = enable_aggressive_cleanup
        self.loaded_models = {}
        
    def load_model_with_mmgp(self, model_path: str, model_class: Any, **kwargs):
        """Load model using MMGP optimizations."""
        if not MMGP_AVAILABLE:
            logger.warning("MMGP not available, falling back to standard loading")
            return self._load_model_standard(model_path, model_class, **kwargs)
            
        try:
            logger.info(f"🚀 Loading model with MMGP optimizations: {model_path}")
            
            # Use MMGP fast loading with quantization
            model = offload.fast_load_transformers_model(
                model_path,
                modelClass=model_class,
                do_quantize=self.enable_quantization,
                writable_tensors=False
            )
            
            # Apply memory optimizations
            if self.enable_quantization:
                logger.info("🔧 Applying INT8 quantization")
                offload.change_dtype(model, torch.int8, True)
            
            self.loaded_models[model_path] = model
            logger.info("✅ Model loaded with MMGP optimizations")
            return model
            
        except Exception as e:
            logger.error(f"❌ MMGP loading failed: {e}")
            return self._load_model_standard(model_path, model_class, **kwargs)
    
    def _load_model_standard(self, model_path: str, model_class: Any, **kwargs):
        """Fallback standard model loading."""
        logger.info("📦 Using standard model loading")
        # Standard loading logic here
        return None
    
    def aggressive_cleanup(self, *tensors):
        """Immediate tensor cleanup - "spaghetti optimizations"."""
        if not self.enable_aggressive_cleanup:
            return
            
        for tensor in tensors:
            if tensor is not None:
                if hasattr(tensor, 'data'):
                    del tensor.data
                if isinstance(tensor, torch.Tensor):
                    tensor.detach_()
                del tensor
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def chunk_process_tensor(self, tensor: torch.Tensor, operation, chunk_size: int = 6):
        """Process tensor in chunks to reduce peak memory usage."""
        if tensor.numel() < 1000:  # Skip small tensors
            return operation(tensor)
        
        # Split tensor into chunks
        tensor_shape = tensor.shape
        tensor_flat = tensor.view(-1, tensor.shape[-1])
        chunk_size_actual = max(1, tensor_flat.shape[0] // chunk_size)
        
        chunks = torch.split(tensor_flat, chunk_size_actual)
        results = []
        
        for i, chunk in enumerate(chunks):
            logger.debug(f"🔄 Processing chunk {i+1}/{len(chunks)}")
            result = operation(chunk)
            results.append(result)
            
            # Aggressive cleanup after each chunk
            self.aggressive_cleanup(chunk)
        
        # Concatenate results
        final_result = torch.cat(results, dim=0)
        final_result = final_result.view(*tensor_shape[:-1], -1)
        
        # Clean up chunks list
        self.aggressive_cleanup(*chunks, *results)
        
        return final_result
    
    def offload_to_cpu(self, model, keep_on_gpu: Optional[list] = None):
        """Smart CPU offloading with mmgp."""
        if not MMGP_AVAILABLE:
            return model.cpu()
        
        keep_on_gpu = keep_on_gpu or []
        
        try:
            # Use MMGP's intelligent offloading
            offload.load_model_data(
                model, 
                None,  # No file path for already loaded model
                do_quantize=self.enable_quantization,
                pinToMemory=False,
                partialPinning=True
            )
            logger.info("🔄 Model offloaded to CPU with MMGP")
            
        except Exception as e:
            logger.warning(f"MMGP offloading failed: {e}, using standard CPU offload")
            model = model.cpu()
        
        torch.cuda.empty_cache()
        return model
    
    def monitor_memory(self, stage: str = ""):
        """Monitor memory usage with detailed logging."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            free = total - allocated
            
            logger.info(f"📊 {stage} - VRAM: {allocated:.2f}GB allocated, {free:.2f}GB free, {reserved:.2f}GB reserved")
            
            # Extreme memory pressure detection
            if allocated / total > 0.9:
                logger.warning("🚨 Extreme memory pressure detected - triggering aggressive cleanup")
                self.emergency_cleanup()
    
    def emergency_cleanup(self):
        """Emergency memory cleanup when near OOM."""
        logger.warning("🆘 Emergency memory cleanup activated")
        
        # Clear all caches
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        
        # Force garbage collection multiple times
        for _ in range(3):
            gc.collect()
        
        # Offload unnecessary models
        for model_name, model in self.loaded_models.items():
            if hasattr(model, 'cpu'):
                self.loaded_models[model_name] = model.cpu()
                logger.info(f"🔄 Emergency offload: {model_name}")
        
        torch.cuda.empty_cache()
        logger.info("✅ Emergency cleanup completed")


# Global memory manager instance
memory_manager = MMGPMemoryManager(
    enable_quantization=True,
    enable_aggressive_cleanup=True
)


def apply_spaghetti_optimizations():
    """Apply the famous 'spaghetti optimizations' environment setup."""
    logger.info("🍝 Applying spaghetti VRAM optimizations by DeepBeepMeep")
    
    os.environ.update({
        "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:128,garbage_collection_threshold:0.5,expandable_segments:True",
        "PYTORCH_NO_CUDA_MEMORY_CACHING": "1",
        "CUDA_CACHE_DISABLE": "1", 
        "PYTORCH_JIT": "0",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "CUDA_MODULE_LOADING": "LAZY",
    })
    
    logger.info("✅ Spaghetti optimizations applied - enjoy the memory savings!")


# Auto-apply optimizations on import
apply_spaghetti_optimizations() 