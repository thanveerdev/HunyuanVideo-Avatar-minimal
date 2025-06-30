# VPS Docker Deployment Workflow

Complete guide for building and deploying HunyuanVideo-Avatar Docker container on your VPS.

## ⚡ FAST BUILD OPTION (RECOMMENDED)

**NEW: Use precompiled Flash Attention for super fast builds!**

### Quick Commands for Fast Build:
```bash
# Clone repository
git clone -b wan2gp https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git
cd HunyuanVideo-Avatar-minimal

# FAST build with precompiled flash attention
chmod +x build_precompiled_docker.sh
./build_precompiled_docker.sh

# OR manual fast build
docker build -f Dockerfile.precompiled -t hunyuan-avatar:latest .
```

**Advantages of Fast Build:**
- ⚡ **10-30 minutes faster** - no flash attention compilation
- 🛡️ **More reliable** - uses tested precompiled wheels  
- 🔧 **No build tools needed** - smaller base image
- ✅ **CUDA 12.4 + cuDNN compatible** - optimized versions

---

## 🔗 Clone Repository

### Clone the wan2gp Branch
```bash
git clone -b wan2gp https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git
cd HunyuanVideo-Avatar-minimal
```

## 🐳 Docker Build Commands

### Option 1: FAST Build with Precompiled Flash Attention (RECOMMENDED)
```bash
# Use the fast build script
chmod +x build_precompiled_docker.sh
./build_precompiled_docker.sh

# OR build manually
docker build -f Dockerfile.precompiled -t hunyuan-avatar:latest .
```

### Option 2: Standard Build (Slow - compiles flash attention)
```bash
# Build the Docker image (will take longer due to compilation)
docker build -t hunyuan-avatar:latest .
```

### Option 3: Using the Enhanced Build Script
```bash
# Make the build script executable
chmod +x build_docker.sh

# Run the interactive build script
./build_docker.sh
```

## 📤 Push to Docker Hub

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username:

```bash
# Step 1: Login to Docker Hub (if not already logged in)
docker login

# Step 2: Tag the image for Docker Hub
docker tag hunyuan-avatar:latest YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest

# Step 3: Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

## 🚀 Complete VPS Deployment Workflow

### Step 1: Clone the Repository
```bash
git clone -b wan2gp https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git
cd HunyuanVideo-Avatar-minimal
```

### Step 2: Build the Docker Image
```bash
docker build -t hunyuan-avatar:latest .
```

### Step 3: Tag for Docker Hub
```bash
docker tag hunyuan-avatar:latest YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

### Step 4: Push to Docker Hub
```bash
docker push YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

### Step 5: Run on VPS (or any other server)
```bash
# Run with GPU support and web interface
docker run --gpus all -p 7860:7860 -p 8000:8000 YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

## 🌐 Access Your Application

After running the container:
- **Web Interface**: `http://your-vps-ip:7860`
- **API Endpoint**: `http://your-vps-ip:8000`

## ⚙️ Advanced Configuration

### Custom Environment Variables
```bash
docker run --gpus all \
  -p 7860:7860 -p 8000:8000 \
  -e RUN_MODE=web \
  -e IMAGE_SIZE=512 \
  -e CUDA_VISIBLE_DEVICES=0 \
  YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

### Persistent Storage (Recommended)
```bash
# Create local directories for persistence
mkdir -p ./outputs ./logs ./inputs

# Run with mounted volumes
docker run --gpus all \
  -p 7860:7860 -p 8000:8000 \
  -v ./outputs:/workspace/outputs \
  -v ./logs:/workspace/logs \
  -v ./inputs:/workspace/inputs \
  YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

### Docker Compose Deployment
```bash
# Use the provided docker-compose.yml
docker-compose up -d
```

## 🛠️ Key Features

✅ **GPU Optimized**: Automatically detects and optimizes for your GPU memory  
✅ **Memory Efficient**: Uses advanced VRAM optimization techniques  
✅ **Web Interface**: Built-in Gradio interface for easy use  
✅ **API Ready**: FastAPI backend for programmatic access  
✅ **Persistent**: Container keeps running for debugging and continuous use  
✅ **Auto-Download**: Downloads model weights (~10GB) on first run  

## 📋 System Requirements

- **GPU**: NVIDIA GPU with 8GB+ VRAM (supports lower with optimizations)
- **CUDA**: Compatible with CUDA 12.4
- **RAM**: 16GB+ system RAM recommended
- **Storage**: 20GB+ free space for models and outputs
- **Docker**: Docker with NVIDIA Container Toolkit installed

## 🔧 Troubleshooting

### GPU Issues
```bash
# Check GPU availability
nvidia-smi

# Install NVIDIA Container Toolkit if needed
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### Memory Issues
```bash
# Run with ultra-low VRAM mode
docker run --gpus all \
  -p 7860:7860 -p 8000:8000 \
  -e PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:64,garbage_collection_threshold:0.3" \
  YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

### Port Conflicts
```bash
# Use different ports if 7860/8000 are occupied
docker run --gpus all -p 7861:7860 -p 8001:8000 YOUR_DOCKERHUB_USERNAME/hunyuan-avatar:latest
```

## 📱 Usage Examples

### Web Interface
1. Start container with web mode (default)
2. Open browser to `http://your-vps-ip:7860`
3. Upload image and audio files
4. Click generate to create avatar video

### API Usage
```bash
# Test API endpoint
curl -X GET http://your-vps-ip:8000/health

# Submit generation job via API
curl -X POST http://your-vps-ip:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"image_path": "assets/image/1.png", "audio_path": "assets/audio/2.wav"}'
```

## 🎯 Production Deployment Tips

1. **Use Docker Compose** for easier management
2. **Set up reverse proxy** (nginx) for HTTPS
3. **Configure resource limits** to prevent OOM
4. **Monitor GPU memory usage** during operation
5. **Set up log rotation** for persistent logging
6. **Use health checks** for container monitoring

## 📚 Additional Resources

- `README_DOCKER.md` - Detailed Docker documentation
- `README_WEB_INTERFACE.md` - Web interface guide
- `DEPLOYMENT_GUIDE.md` - General deployment information
- `build_docker.sh` - Interactive build script with more options 