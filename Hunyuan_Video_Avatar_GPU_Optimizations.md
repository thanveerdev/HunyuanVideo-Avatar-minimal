# Hunyuan Video Avatar - Extreme GPU Optimizations

## Overview

This document explains the sophisticated GPU optimization techniques that enable **Hunyuan Video Avatar** to run on just **10GB VRAM** instead of the typical **80GB requirement** - achieving an **87% VRAM reduction** while maintaining high-quality avatar generation.

## 🚀 Core Memory Optimization Techniques

### 1. **MMGP Library Integration**

The system uses the **mmgp** library (version 3.4.9) for sophisticated model management:

```python
from mmgp import offload

# Fast model loading with quantization support
self.model = offload.fast_load_transformers_model(
    model_filename, 
    modelClass=WanModel,
    do_quantize=quantizeTransformer, 
    writable_tensors=False
)

# Dynamic dtype conversion
offload.change_dtype(self.model, dtype, True)

# Model data loading with quantization
offload.load_model_data(model, model_filepath, 
                       do_quantize=quantizeTransformer and not save_quantized, 
                       pinToMemory=pinToMemory, 
                       partialPinning=partialPinning)
```

### 2. **Aggressive Memory Cleanup ("Spaghetti VRAM Optimizations")**

The codebase implements extensive immediate memory cleanup throughout forward passes:

```python
##### Enjoy this spagheti VRAM optimizations done by DeepBeepMeep !
# I am sure you are a nice person and as you copy this code, you will give me officially proper credits:
# Please link to https://github.com/deepbeepmeep/HunyuanVideoGP and @deepbeepmeep on twitter  

# Example from MMDoubleStreamBlock forward pass
img_modulated = self.img_norm1(img)
img_modulated = img_modulated.to(torch.bfloat16)
# ... use img_modulated ...
del img_modulated  # Immediate cleanup

# QKV processing with aggressive cleanup
qklist = [img_q, img_k]
del img_q, img_k  # Delete originals immediately
img_q, img_k = apply_rotary_emb(qklist, freqs_cis, head_first=False)

# Clear lists after concatenation
qkv_list = [q, k, v]
del q, k, v
attn = pay_attention(qkv_list, ...)
del qkv_list  # Clear the list
```

**Key cleanup patterns:**
- **Immediate deletion** of intermediate tensors
- **Clear lists** after use: `qkv_list.clear()`, `qklist.clear()`
- **In-place operations** to avoid memory copies

### 3. **Tensor Chunking Strategy**

**MLP Processing with Chunking:**
```python
# Process large tensors in manageable chunks
x_mod_shape = x_mod.shape
x_mod = x_mod.view(-1, x_mod.shape[-1])
chunk_size = int(x_mod_shape[1]/6)  # Split into 6 chunks
x_chunks = torch.split(x_mod, chunk_size)
attn_chunks = torch.split(attn, chunk_size)

for x_chunk, attn_chunk in zip(x_chunks, attn_chunks):
    mlp_chunk = self.linear1_mlp(x_chunk)
    mlp_chunk = self.mlp_act(mlp_chunk)
    attn_mlp_chunk = torch.cat((attn_chunk, mlp_chunk), -1)
    del attn_chunk, mlp_chunk  # Clean up immediately
    x_chunk[...] = self.linear2(attn_mlp_chunk)  # In-place update
    del attn_mlp_chunk
```

### 4. **Mixed Precision + Quantization**

**Strategic Precision Management:**
```python
# BFloat16 for main computation
img_modulated = img_modulated.to(torch.bfloat16)
txt_modulated = txt_modulated.to(torch.bfloat16)

# VAE precision configuration
vae._model_dtype = torch.float32 if VAE_dtype == torch.float32 else torch.bfloat16

# Dynamic autocast for VAE operations
vae_dtype = self.vae.dtype
with torch.autocast(device_type="cuda", dtype=vae_dtype, enabled=vae_dtype != torch.float32):
    ref_latents = self.vae.encode(pixel_value_ref_for_vae).latent_dist.sample()

# INT8 quantization support
offload.load_model_data(model, model_filepath, do_quantize=quantizeTransformer)
```

**Precision Hierarchy:**
- **Main Transformer**: BFloat16
- **VAE**: Float16/Float32 (configurable)
- **Audio Models**: Float32 (on CPU)
- **Quantization**: INT8 for extreme memory savings

### 5. **Smart Model Offloading**

**CPU Offloading for Secondary Models:**
```python
# Avatar-specific optimizations
if avatar:
    # Face detection model - only load when needed
    align_instance = AlignImage("cuda", det_path="ckpts/det_align/detface.pt")
    align_instance.facedet.model.to("cpu")  # Keep on CPU by default
    
    # Audio processing models on CPU
    feature_extractor = AutoFeatureExtractor.from_pretrained("ckpts/whisper-tiny/")
    wav2vec = WhisperModel.from_pretrained("ckpts/whisper-tiny/").to(device="cpu", dtype=torch.float32)

# Dynamic GPU/CPU movement during inference
self.align_instance.facedet.model.to("cuda")  # Load only when needed
face_masks = get_facemask(pixel_value_ref.to("cuda")*255, self.align_instance, area=3.0)
self.align_instance.facedet.model.to("cpu")   # Immediately offload back to CPU
```

### 6. **Custom Attention Implementation (pay_attention)**

**Optimized Attention Kernel:**
```python
from wan.modules.attention import pay_attention

@torch.compiler.disable()
def pay_attention(
    qkv_list,
    dropout_p=0.,
    softmax_scale=None,
    attention_mask=None,
    q_lens=None,
    k_lens=None,
):
    # Multiple backend support: SAGE, Flash Attention, SDPA
    # Variable sequence length support
    # Automatic chunking for memory efficiency
```

**Features:**
- **Multiple attention backends** (SAGE, Flash Attention, SDPA)
- **Variable sequence length support** for memory efficiency
- **Automatic chunking** for large sequences
- **Cross-attention optimizations**

### 7. **VAE Gradient Checkpointing**

```python
class AutoencoderKLCausal3D:
    def __init__(self):
        self.gradient_checkpointing = False
    
    def forward(self, sample):
        if self.training and self.gradient_checkpointing:
            # Use gradient checkpointing to trade compute for memory
            sample = torch.utils.checkpoint.checkpoint(
                create_custom_forward(down_block), sample
            )
            sample = torch.utils.checkpoint.checkpoint(
                create_custom_forward(self.mid_block), sample
            )
```

### 8. **Frame Segmentation for Avatar**

**Segment-based Processing:**
```python
# Avatar processes in 129-frame segments instead of full sequences
segment_size = 129 if self.avatar else frame_num

if audio_prompts.shape[1] <= segment_size:
    audio_prompts = torch.cat([
        audio_prompts, 
        torch.zeros_like(audio_prompts[:, :1]).repeat(1, segment_size-audio_prompts.shape[1], 1, 1, 1)
    ], dim=1)
```

### 9. **Audio Processing Optimizations**

**Chunked Audio Feature Extraction:**
```python
def get_audio_feature(feature_extractor, audio_path, duration):
    audio_input, sampling_rate = librosa.load(audio_path, duration=duration, sr=16000)
    
    audio_features = []
    window = 750*640  # Process in chunks
    for i in range(0, len(audio_input), window):
        audio_feature = feature_extractor(
            audio_input[i:i+window], 
            sampling_rate=sampling_rate, 
            return_tensors="pt", 
            device="cuda"
        ).input_features
        audio_features.append(audio_feature)
    
    return torch.cat(audio_features, dim=-1), len(audio_input) // 640
```

### 10. **Linear Layer Splitting**

**Memory-Efficient Linear Operations:**
```python
def get_linear_split_map():
    hidden_size = 3072
    split_linear_modules_map = {
        "img_attn_qkv": {
            "mapped_modules": ["img_attn_q", "img_attn_k", "img_attn_v"], 
            "split_sizes": [hidden_size, hidden_size, hidden_size]
        },
        "linear1": {
            "mapped_modules": ["linear1_attn_q", "linear1_attn_k", "linear1_attn_v", "linear1_mlp"], 
            "split_sizes": [hidden_size, hidden_size, hidden_size, 7*hidden_size - 3*hidden_size]
        }
    }
    return split_linear_modules_map
```

## 🧠 Memory Efficiency Results

These optimizations collectively achieve:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **VRAM Usage** | 80GB | 10GB | **87% reduction** |
| **Quality** | High | High | **Maintained** |
| **Speed** | Baseline | Optimized | **Improved** |
| **Accessibility** | Enterprise GPUs | Consumer GPUs | **Democratized** |

## 📋 Implementation Guidelines

### For Developers Implementing Similar Optimizations:

1. **Immediate Memory Cleanup**
   ```python
   # Always delete intermediate tensors immediately after use
   intermediate = some_operation(input_tensor)
   result = next_operation(intermediate)
   del intermediate  # Critical for memory efficiency
   ```

2. **Chunked Processing**
   ```python
   # Process large tensors in smaller chunks
   chunk_size = total_size // num_chunks
   for chunk in torch.split(large_tensor, chunk_size):
       process_chunk(chunk)
   ```

3. **Smart Model Placement**
   ```python
   # Keep secondary models on CPU, move to GPU only when needed
   secondary_model.to("cpu")
   # ... later when needed ...
   secondary_model.to("cuda")
   result = secondary_model(input)
   secondary_model.to("cpu")  # Move back immediately
   ```

4. **Mixed Precision Strategy**
   ```python
   # Use appropriate precision for each component
   main_model = main_model.to(torch.bfloat16)  # Main computation
   vae = vae.to(torch.float16)  # VAE operations
   audio_model = audio_model.to(torch.float32)  # Audio (on CPU)
   ```

## 🎯 Key Takeaways

The **"spaghetti optimizations"** are particularly effective because they:

1. **Minimize peak memory usage** through aggressive cleanup
2. **Process in chunks** rather than full tensors
3. **Use in-place operations** wherever possible
4. **Leverage mixed precision** strategically
5. **Implement smart model offloading**

This approach makes high-quality avatar generation accessible on consumer GPUs while maintaining the model's full capability - a significant democratization of advanced AI video generation technology.

## 📚 References

- Original implementation: [HunyuanVideoGP](https://github.com/deepbeepmeep/HunyuanVideoGP)
- MMGP Library: Advanced model management and quantization
- Credits: DeepBeepMeep (@deepbeepmeep on Twitter)

---

*This optimization approach demonstrates how careful memory management and strategic architectural choices can make cutting-edge AI models accessible on consumer hardware.* 