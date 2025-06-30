# Flash Attention Docker Setup for HunyuanVideo-Avatar

This setup provides a Docker container optimized for Flash Attention with `nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04`, specifically designed to resolve the critical errors identified in **My Pods Logs (29).txt**.

## 🚨 Problems This Solves

This Docker setup addresses the **PRIMARY ERROR** that prevents the application from starting:

```
ModuleNotFoundError: No module named 'flash_attn'
```

Plus additional dependency issues:
- Missing `gradio`, `fastapi`, `diffusers` packages
- TorchVision compatibility problems  
- CUDA/cuDNN optimization for Flash Attention

---

## 🏗️ Docker Configuration

### **Base Image**: `nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04`

**Why this image?**
- ✅ **CUDA 12.4.1**: Compatible with latest PyTorch and Flash Attention
- ✅ **cuDNN included**: Essential for deep learning optimizations
- ✅ **Development tools**: Includes compilation tools for Flash Attention
- ✅ **Ubuntu 22.04**: Stable, well-supported base

### **Flash Attention Version**: `2.6.3`
- Optimized for CUDA 12.4
- Compatible with PyTorch 2.4.0
- Includes all necessary CUDA kernels

---

## 📋 Files Overview

| File | Purpose |
|------|---------|
| `Dockerfile.flash-attn` | Main Dockerfile with Flash Attention support |
| `build_flash_attn_docker.sh` | Build script with testing |
| `docker-compose.flash-attn.yml` | Docker Compose configuration |
| `test_flash_attn_error.py` | Test for Flash Attention availability |
| `run_error_persistence_tests.sh` | Comprehensive error testing |

---

## 🚀 Quick Start

### **Option 1: Using Docker Compose (Recommended)**

```bash
# Build and run with docker-compose
docker-compose -f docker-compose.flash-attn.yml up --build

# Or run in background
docker-compose -f docker-compose.flash-attn.yml up -d --build
```

### **Option 2: Using Build Script**

```bash
# Make build script executable
chmod +x build_flash_attn_docker.sh

# Build the image (takes 20-30 minutes)
./build_flash_attn_docker.sh

# Run the container
docker run --rm --gpus all -p 7860:7860 -p 80:80 \
  hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04
```

### **Option 3: Direct Docker Build**

```bash
# Build manually
docker build -t hunyuan-flash-attn -f Dockerfile.flash-attn .

# Run manually  
docker run --rm --gpus all -p 7860:7860 -p 80:80 hunyuan-flash-attn
```

---

## 🧪 Testing the Setup

### **Test Flash Attention Installation**
```bash
# Test inside container
docker run --rm --gpus all hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 \
  python3 -c "import flash_attn; print('✅ Flash Attention works!')"

# Run our specific error tests
docker run --rm --gpus all hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 \
  python3 test_flash_attn_error.py
```

### **Run Comprehensive Error Tests**
```bash
# Test all errors from the log file
docker run --rm --gpus all hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 \
  ./run_error_persistence_tests.sh
```

---

## 🔧 Environment Variables

### **Flash Attention Optimizations**
```bash
FLASH_ATTENTION_FORCE_BUILD=TRUE
FLASH_ATTENTION_FORCE_CUT=TRUE
TORCH_CUDA_ARCH_LIST=8.0;8.6;8.9;9.0
MAX_JOBS=8
```

### **CUDA/cuDNN Optimizations**
```bash
CUDA_HOME=/usr/local/cuda
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
CUDNN_ALLOW_TF32=1
TORCH_ALLOW_TF32_CUBLAS_OVERRIDE=1
TORCH_CUDNN_V8_API_ENABLED=1
```

### **Memory Optimizations**
```bash
CUDA_LAUNCH_BLOCKING=1
CUDA_CACHE_DISABLE=1
OMP_NUM_THREADS=4
PYTORCH_NO_CUDA_MEMORY_CACHING=1
```

---

## 📊 Expected Performance

### **Build Time**
- **First build**: 20-30 minutes (Flash Attention compilation)
- **Rebuild**: 2-5 minutes (Docker layer caching)

### **Memory Requirements**
- **Build**: 16GB+ RAM recommended
- **Runtime**: 8GB+ GPU VRAM, 16GB+ system RAM
- **Container**: ~8GB Docker image size

### **GPU Compatibility**
- **Minimum**: CUDA Compute Capability 8.0+
- **Recommended**: RTX 30/40 series, A100, H100
- **Supported**: Any CUDA 12.4 compatible GPU

---

## ⚡ Usage Examples

### **Start Web Interface**
```bash
# Using docker-compose
docker-compose -f docker-compose.flash-attn.yml up

# Access at:
# - Gradio UI: http://localhost:7860
# - FastAPI: http://localhost:8000  
# - HTTP: http://localhost:80
```

### **Run Single Inference**
```bash
docker run --rm --gpus all \
  -v $(pwd)/inputs:/workspace/inputs \
  -v $(pwd)/outputs:/workspace/outputs \
  hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 \
  python3 -m hymm_sp.inference --input /workspace/inputs/test.jpg
```

### **Development Mode**
```bash
# Mount source code for development
docker run --rm --gpus all \
  -p 7860:7860 -p 80:80 \
  -v $(pwd)/hymm_sp:/workspace/hymm_sp \
  -v $(pwd)/hymm_gradio:/workspace/hymm_gradio \
  hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04
```

---

## 🐛 Troubleshooting

### **Flash Attention Build Fails**
```bash
# Check CUDA version
nvidia-smi

# Ensure you have enough disk space (20GB+)
df -h

# Try building with more memory
docker build --memory=16g -f Dockerfile.flash-attn .
```

### **GPU Not Detected**
```bash
# Install nvidia-container-toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### **Out of Memory During Build**
```bash
# Use Docker BuildKit with memory limits
export DOCKER_BUILDKIT=1
docker build --memory=16g --memory-swap=32g -f Dockerfile.flash-attn .
```

### **Test Failures**
```bash
# Check container logs
docker logs hunyuan-avatar-flash-attn

# Run debug mode
docker run --rm --gpus all -it hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 bash
```

---

## 📈 Optimization Tips

### **Faster Builds**
1. **Use BuildKit**: `export DOCKER_BUILDKIT=1`
2. **Multi-stage builds**: Leverage Docker layer caching
3. **Parallel jobs**: Adjust `MAX_JOBS` environment variable

### **Better Performance**
1. **Enable TF32**: `CUDNN_ALLOW_TF32=1`
2. **Optimize memory**: `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512`
3. **Use cuDNN**: Already included in base image

### **Resource Management**
1. **Set memory limits**: Prevents OOM kills
2. **Use tmpfs**: For temporary build files
3. **Clean layers**: Remove unnecessary files in same RUN command

---

## 🔄 CI/CD Integration

### **GitHub Actions Example**
```yaml
name: Build Flash Attention Docker
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: ./build_flash_attn_docker.sh
      - name: Test Flash Attention
        run: |
          docker run --rm hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 \
            python3 test_flash_attn_error.py
```

---

## 📚 References

- [Flash Attention GitHub](https://github.com/Dao-AILab/flash-attention)
- [NVIDIA CUDA Docker Images](https://hub.docker.com/r/nvidia/cuda)
- [PyTorch CUDA Compatibility](https://pytorch.org/get-started/locally/)
- [Docker GPU Support](https://docs.docker.com/config/containers/resource_constraints/#gpu)

---

## ⚠️ Important Notes

1. **Build Time**: Initial build takes 20-30 minutes due to Flash Attention compilation
2. **GPU Required**: Flash Attention requires CUDA-compatible GPU for runtime
3. **Memory**: Ensure sufficient RAM (16GB+) during build process
4. **CUDA Version**: Must match between host driver and container (12.4+)
5. **cuDNN**: Included in base image for optimal performance

---

*This setup resolves the PRIMARY error from My Pods Logs (29).txt and provides a production-ready Flash Attention environment.* 