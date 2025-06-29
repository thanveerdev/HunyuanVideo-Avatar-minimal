# 🐳 HunyuanVideo-Avatar Docker Deployment for RunPod

This Docker container is optimized for RunPod deployment with automatic model downloading on first run.

## 🚀 Quick RunPod Deployment

### Option 1: Using Pre-built Image (Recommended)
```bash
# Pull the pre-built image
docker pull your-registry/hunyuan-avatar:latest
```

### Option 2: Build Your Own Image
```bash
# Clone the repository
git clone <your-repo-url>
cd HunyuanVideo-Avatar-minimal

# Build the Docker image
docker build -t hunyuan-avatar:latest .
```

## 📦 RunPod Template Configuration

Use the provided `runpod_template.json` or create a pod with these settings:

### Minimum Requirements
- **GPU**: NVIDIA RTX 3060 Ti or better (8GB+ VRAM)
- **Container Disk**: 50GB
- **Volume**: 100GB (for model storage and outputs)
- **Ports**: `7860/http,8000/http`

### Recommended GPUs for RunPod
- **Budget**: RTX 3080 (10GB VRAM) - $0.34/hr
- **Balanced**: RTX A4000 (16GB VRAM) - $0.61/hr  
- **High-end**: RTX 4090 (24GB VRAM) - $1.69/hr

## 🛠️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_BASE` | `/workspace` | Base directory for models |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device to use |
| `PYTORCH_CUDA_ALLOC_CONF` | `max_split_size_mb:512` | Memory allocation strategy |
| `IMAGE_SIZE` | Auto-detected | Output image resolution |

## 📁 Volume Mounting

### RunPod Network Volume (Recommended)
The container automatically detects RunPod network volumes:
- **Models**: Cached in container (first download only)
- **Outputs**: Saved to `/runpod-volume/outputs`
- **Logs**: Saved to `/runpod-volume/logs`

### Local Development
```bash
docker-compose up --build
```

## 🎯 Usage Modes

### 1. Interactive Mode (Default)
Container starts with bash shell for manual control:
```bash
# Ultra low VRAM (6-8GB)
bash run_minimal.sh

# Standard low memory (8-12GB)  
bash run_low_memory.sh

# Custom inference
python3 -m hymm_sp.low_memory_inference --help
```

### 2. Batch Mode
Place your `input.csv` in `/workspace/inputs/` and the container will process automatically.

## 📋 Input Format

Create `/workspace/inputs/input.csv`:
```csv
videoid,image,audio,prompt,fps
video1,/path/to/image1.jpg,/path/to/audio1.wav,A person speaking,25
video2,/path/to/image2.png,/path/to/audio2.wav,A person smiling,30
```

## 📊 Performance Expectations

| GPU Model | VRAM | Est. Cost/Hour | Generation Time* |
|-----------|------|---------------|------------------|
| RTX 3060 Ti | 8GB | $0.22 | 90-120s |
| RTX 3080 | 10GB | $0.34 | 70-90s |
| RTX A4000 | 16GB | $0.61 | 60-80s |
| RTX 4080 | 16GB | $1.16 | 50-70s |
| RTX 4090 | 24GB | $1.69 | 40-60s |

*Times for 5-second video at 256px resolution

## 🔧 Troubleshooting

### First Run Taking Long?
- Model download is ~10GB and happens on first run
- Check logs: `docker logs <container-id>`
- Progress shown in container output

### Out of Memory Errors?
```bash
# Check GPU memory in container
nvidia-smi

# The container auto-adjusts settings based on available VRAM
# Manual override:
export IMAGE_SIZE=128  # Smallest size
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256"
```

### Models Not Downloading?
```bash
# Check HuggingFace access
huggingface-cli whoami

# Manual download in container
cd /workspace/weights
huggingface-cli download tencent/HunyuanVideo-Avatar --local-dir ./
```

## 🐛 Development

### Local Testing
```bash
# Build and run locally
docker-compose up --build

# Access container
docker exec -it hunyuan-avatar bash
```

### Debugging
```bash
# View container logs
docker logs hunyuan-avatar

# Monitor GPU usage
docker exec hunyuan-avatar nvidia-smi -l 1

# Check disk usage
docker exec hunyuan-avatar df -h
```

## 📈 Optimization Tips

### For RunPod Cost Efficiency
1. **Use Spot Instances**: Up to 50% cheaper
2. **Choose Right GPU**: RTX 3080 offers best price/performance
3. **Network Volume**: Persist models between sessions
4. **Batch Processing**: Process multiple videos in one session

### For Best Performance
1. **Use NVMe Storage**: Faster model loading
2. **Latest CUDA**: Ensure CUDA 12.4+ support
3. **Monitor Memory**: Check `nvidia-smi` regularly
4. **Optimize Input**: Use 16kHz audio, optimize image sizes

## 🆘 Support

### Quick Diagnostics
```bash
# Test GPU and memory
python3 config_minimal.py

# Check model files
ls -la /workspace/weights/ckpts/

# View recent logs
tail -50 /workspace/logs/*.log
```

### Common Solutions
- **Slow Download**: Use RunPod datacenter with good HuggingFace connectivity
- **Memory Issues**: Container auto-detects and adjusts VRAM settings
- **Missing Models**: First run downloads take 10-30 minutes
- **Permission Errors**: Ensure proper volume mounting

## 🎉 Success Indicators

### ✅ Container Ready When:
- [ ] GPU detected with nvidia-smi
- [ ] Models downloaded (check `/workspace/weights/.models_downloaded`)
- [ ] Sample input.csv created
- [ ] No CUDA out of memory errors

### ✅ Generation Working When:
- [ ] Video files appear in `/workspace/outputs/`
- [ ] Audio synchronized with video
- [ ] No error messages in logs
- [ ] Completion under expected time

---

🏁 **Ready to generate high-quality avatar videos on RunPod with minimal setup!** 