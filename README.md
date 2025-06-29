# HunyuanVideo-Avatar - Minimal Low VRAM Deployment

This is a minimal deployment version optimized for running HunyuanVideo-Avatar on single GPU with lowest VRAM requirements.

## 🎯 Purpose
- **Minimal footprint**: Only essential files included
- **Low VRAM optimized**: Configured for GPUs with limited memory
- **Single GPU setup**: No multi-GPU dependencies
- **Easy deployment**: Simplified setup process

## 📋 Requirements

### System Requirements
- **GPU**: NVIDIA GPU with ≥8GB VRAM (minimum)
- **RAM**: ≥16GB system memory
- **Storage**: ≥20GB free space
- **OS**: Linux (Ubuntu 18.04+) or Windows with WSL2

### Software Requirements
- Python 3.8+
- CUDA 11.7+ or 12.x
- PyTorch 2.0+
- Git

## 🚀 Quick Setup

### 1. Clone and Install
```bash
# Navigate to this directory
cd HunyuanVideo-Avatar-minimal

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export MODEL_BASE=$(pwd)
export CUDA_VISIBLE_DEVICES=0  # Use single GPU
```

### 2. Download Models
```bash
# Download required model weights (see weights/README.md for details)
cd weights
# Follow instructions in README.md to download models
cd ..
```

### 3. Prepare Input Data
```bash
# Create test CSV file
echo "videoid,image,audio,prompt,fps" > test_input.csv
echo "test1,assets/image/1.png,assets/audio/2.WAV,A person speaking,25" >> test_input.csv
```

## 🔧 Low VRAM Configuration

### Memory Optimization Features
- **CPU Offloading**: Automatically moves unused model parts to CPU
- **Mixed Precision**: Uses FP16 to reduce memory usage
- **Gradient Checkpointing**: Reduces memory at cost of speed
- **Sequential Processing**: Processes one frame at a time
- **Minimal Batch Size**: Batch size = 1

### Recommended Settings
```bash
# For 8GB VRAM
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_LAUNCH_BLOCKING=1

# For 12GB+ VRAM (better quality)
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
```

## 🎬 Usage

### Low Memory Inference (Recommended)
```bash
# Using the optimized low memory script
bash run_low_memory.sh
```

### Single Inference (Alternative)
```bash
# Using single inference mode
bash run_single_inference.sh
```

### Manual Execution
```bash
python -m hymm_sp.low_memory_inference \
    --ckpt ./weights \
    --input ./test_input.csv \
    --save_path ./outputs \
    --cpu_offload \
    --infer_min \
    --batch_size 1 \
    --image_size 256
```

## ⚙️ Configuration Options

### Low VRAM Parameters
- `--cpu_offload`: Enable CPU offloading (reduces VRAM usage)
- `--infer_min`: Use minimum inference length (faster)
- `--batch_size 1`: Process one video at a time
- `--image_size 256`: Use smaller resolution (512 for better quality)
- `--mixed_precision`: Enable FP16 computation

### Quality vs Speed Trade-offs
```bash
# Fastest, lowest VRAM (4-6GB VRAM)
--image_size 256 --infer_min --cpu_offload --mixed_precision

# Balanced (8-10GB VRAM)
--image_size 384 --cpu_offload

# Best quality (12GB+ VRAM)
--image_size 512 --batch_size 2
```

## 📁 Directory Structure
```
HunyuanVideo-Avatar-minimal/
├── hymm_sp/                    # Core inference modules
│   ├── low_memory_inference.py # Main low VRAM script
│   ├── config.py              # Configuration
│   ├── modules/               # Neural network modules
│   ├── vae/                   # Video autoencoder
│   └── diffusion/             # Diffusion models
├── assets/                    # Sample test data
│   ├── image/1.png           # Test image
│   └── audio/2.WAV           # Test audio
├── weights/                   # Model weights (download required)
├── run_low_memory.sh         # Low VRAM launch script
├── run_single_inference.sh   # Single inference script
└── requirements.txt          # Python dependencies
```

## 🔍 Troubleshooting

### Out of Memory Errors
1. **Reduce image size**: Use `--image_size 256` or `--image_size 128`
2. **Enable CPU offloading**: Add `--cpu_offload` flag
3. **Set memory fraction**: `export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256`
4. **Clear GPU cache**: Add `torch.cuda.empty_cache()` calls

### Performance Issues
1. **Use mixed precision**: Add `--mixed_precision` flag
2. **Optimize CUDA settings**: Set `CUDA_LAUNCH_BLOCKING=0`
3. **Increase batch size** (if VRAM allows): `--batch_size 2`

### Common Errors
- **CUDA out of memory**: Reduce `--image_size` or enable `--cpu_offload`
- **Model not found**: Check weights directory and download models
- **Audio format**: Ensure audio files are WAV format, 16kHz sampling rate

## 📊 Performance Expectations

### VRAM Usage (Approximate)
- **Minimum**: 4-6GB VRAM (256px, CPU offload)
- **Recommended**: 8-12GB VRAM (384px, mixed settings)
- **Optimal**: 16GB+ VRAM (512px, best quality)

### Generation Speed
- **RTX 3070/4060**: ~60-90 seconds per 5-second video
- **RTX 3080/4070**: ~45-60 seconds per 5-second video  
- **RTX 4080/4090**: ~30-45 seconds per 5-second video

## 🆘 Support
- Check `weights/README.md` for model download instructions
- Monitor GPU memory usage: `nvidia-smi -l 1`
- For issues, ensure CUDA and PyTorch versions are compatible

## 📄 License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details. 