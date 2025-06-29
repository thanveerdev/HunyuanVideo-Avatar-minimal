# 🚀 VPS Build & Deploy Commands

## Complete commands to build HunyuanVideo-Avatar with Ultra-Low VRAM support on your VPS

### 📋 Prerequisites
Make sure your VPS has:
- Docker installed
- Git installed
- NVIDIA GPU with drivers (for GPU support)
- At least 20GB free disk space

---

## 🔧 Step 1: Initial VPS Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git if not already installed
sudo apt install git -y

# Logout and login again for Docker group changes to take effect
exit
```

---

## 📁 Step 2: Clone Repository

```bash
# Clone the repository with ultra-low VRAM implementation
git clone https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git

# Navigate to project directory
cd HunyuanVideo-Avatar-minimal

# Verify the ultra-low VRAM files are present
ls -la run_*.sh ULTRA_LOW_VRAM_GUIDE.md hymm_gradio/
```

---

## 🐳 Step 3: Build Docker Image

```bash
# Make build script executable
chmod +x build_docker.sh

# Option A: Quick build (recommended)
./build_docker.sh

# Option B: Manual build with custom tag
docker build -t hunyuan-video-avatar:ultra-low-vram .

# Option C: Build with specific VRAM optimization
docker build \
  --build-arg INSTALL_TYPE=full \
  --build-arg ENABLE_WEB=true \
  -t hunyuan-video-avatar:latest .

# Verify image was built successfully
docker images | grep hunyuan
```

---

## 🔍 Step 4: Test Docker Image Locally

```bash
# Test the web interface locally first
docker run -it --rm \
  --gpus all \
  -p 7860:7860 \
  -p 80:80 \
  -e RUN_MODE=web \
  -e VRAM_MODE=auto \
  hunyuan-video-avatar:latest

# Open browser to http://your-vps-ip:7860 to test

# Or test with docker-compose
docker-compose up --build
```

---

## 🏷️ Step 5: Tag Image for DockerHub

```bash
# Replace 'yourusername' with your actual DockerHub username
DOCKERHUB_USERNAME="yourusername"
IMAGE_NAME="hunyuan-video-avatar"
VERSION="v1.0-ultra-low-vram"

# Tag the image
docker tag hunyuan-video-avatar:latest ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
docker tag hunyuan-video-avatar:latest ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

# Verify tags
docker images | grep ${DOCKERHUB_USERNAME}
```

---

## 🚀 Step 6: Push to DockerHub

```bash
# Login to DockerHub
docker login

# Push specific version
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}

# Push latest tag
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

# Verify push was successful
echo "✅ Image pushed to: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/${IMAGE_NAME}"
```

---

## 🎯 Step 7: Complete Build & Push Script

Create a single script to automate everything:

```bash
# Create automated build script
cat > build_and_push.sh << 'EOF'
#!/bin/bash

# Configuration
DOCKERHUB_USERNAME="yourusername"  # CHANGE THIS
IMAGE_NAME="hunyuan-video-avatar"
VERSION="v1.0-ultra-low-vram"

echo "🚀 Building HunyuanVideo-Avatar with Ultra-Low VRAM support"
echo "============================================================"

# Build the image
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Tag images
echo "🏷️  Tagging images..."
docker tag ${IMAGE_NAME}:latest ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
docker tag ${IMAGE_NAME}:latest ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

# Login to DockerHub
echo "🔐 Logging into DockerHub..."
docker login

# Push images
echo "🚀 Pushing to DockerHub..."
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest

echo ""
echo "✅ Build and push completed successfully!"
echo "🔗 Image available at: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/${IMAGE_NAME}"
echo ""
echo "📋 Usage commands:"
echo "docker pull ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
echo "docker run --gpus all -p 7860:7860 -e RUN_MODE=web ${DOCKERHUB_USERNAME}/${IMAGE_NAME}:latest"
EOF

# Make script executable
chmod +x build_and_push.sh

# Run the script
./build_and_push.sh
```

---

## 🌐 Step 8: Deploy & Run

After pushing to DockerHub, you can deploy anywhere:

```bash
# Pull and run from DockerHub
docker pull yourusername/hunyuan-video-avatar:latest

# Run with web interface
docker run -d \
  --name hunyuan-avatar \
  --gpus all \
  -p 7860:7860 \
  -p 80:80 \
  -e RUN_MODE=web \
  -e VRAM_MODE=auto \
  --restart unless-stopped \
  yourusername/hunyuan-video-avatar:latest

# Check if running
docker ps

# View logs
docker logs hunyuan-avatar

# Access web interface
echo "🌐 Web interface: http://your-vps-ip:7860"
```

---

## 📊 Step 9: Monitor & Manage

```bash
# Monitor GPU usage
watch nvidia-smi

# Monitor Docker container
docker stats hunyuan-avatar

# Update image
docker pull yourusername/hunyuan-video-avatar:latest
docker stop hunyuan-avatar
docker rm hunyuan-avatar
# Run the docker run command from Step 8 again

# View container logs
docker logs -f hunyuan-avatar

# Execute commands inside container
docker exec -it hunyuan-avatar bash
```

---

## 🚨 Step 10: RunPod/Cloud Deployment

For RunPod or other cloud platforms:

```bash
# Create RunPod template JSON
cat > runpod_template.json << 'EOF'
{
  "name": "HunyuanVideo-Avatar Ultra-Low VRAM",
  "readme": "# HunyuanVideo-Avatar with Universal VRAM Support\n\nSupports 4GB to 24GB+ VRAM with automatic optimization.\n\n## Quick Start\n1. Container starts automatically\n2. Web interface: Port 7860\n3. FastAPI: Port 80\n\n## Features\n- Automatic VRAM detection\n- Progressive quality scaling\n- Real-time memory monitoring\n- Emergency fallback modes",
  "dockerArgs": "",
  "containerDiskInGb": 50,
  "volumeInGb": 20,
  "volumeMountPath": "/workspace/models",
  "ports": "7860/http,80/http",
  "env": [
    {"key": "RUN_MODE", "value": "web"},
    {"key": "VRAM_MODE", "value": "auto"},
    {"key": "MODEL_BASE", "value": "/workspace"}
  ],
  "imageName": "yourusername/hunyuan-video-avatar:latest"
}
EOF

echo "📋 RunPod template created: runpod_template.json"
echo "🔗 Upload this to RunPod template builder"
```

---

## 🎉 Summary Commands (Copy & Paste)

Replace `yourusername` with your DockerHub username and run these commands:

```bash
# Quick setup commands
git clone https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git
cd HunyuanVideo-Avatar-minimal

# Build
docker build -t hunyuan-video-avatar:latest .

# Tag for DockerHub (CHANGE yourusername!)
docker tag hunyuan-video-avatar:latest yourusername/hunyuan-video-avatar:latest
docker tag hunyuan-video-avatar:latest yourusername/hunyuan-video-avatar:v1.0-ultra-low-vram

# Login and push
docker login
docker push yourusername/hunyuan-video-avatar:latest
docker push yourusername/hunyuan-video-avatar:v1.0-ultra-low-vram

# Deploy
docker run -d \
  --name hunyuan-avatar \
  --gpus all \
  -p 7860:7860 \
  -p 80:80 \
  -e RUN_MODE=web \
  --restart unless-stopped \
  yourusername/hunyuan-video-avatar:latest

echo "🎉 Deployment complete! Access: http://your-vps-ip:7860"
```

---

## 🔧 Troubleshooting

```bash
# If build fails
docker builder prune
docker system prune -a

# Check logs
docker logs hunyuan-avatar

# Restart container
docker restart hunyuan-avatar

# Check GPU access
docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi

# Free up space
docker system prune -a --volumes
```

**🎯 Your image will be available at:** `https://hub.docker.com/r/yourusername/hunyuan-video-avatar` 

# VPS Deployment Commands for HunyuanVideo-Avatar-minimal

Complete guide for building and deploying HunyuanVideo-Avatar on a VPS server.

## Prerequisites

### System Requirements
- **GPU**: NVIDIA GPU with 4GB+ VRAM (RTX 3060, RTX 4060, A5000, etc.)
- **RAM**: 16GB+ system RAM recommended
- **Storage**: 50GB+ free space for models and Docker layers
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **CUDA**: Compatible NVIDIA drivers (535+)

### Critical Dependencies Fixed
- **Flash Attention**: Now properly included and compiled during Docker build
- **CUDA Development Tools**: Required for flash_attn compilation
- **Build System**: Uses ninja-build for faster compilation

## 1. Initial VPS Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify GPU access in Docker
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

## 2. Clone and Build Project

```bash
# Clone the repository
git clone https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git
cd HunyuanVideo-Avatar-minimal

# Build Docker image with flash_attn support
docker build -t hunyuan-video-avatar:latest .

# Alternative: Build with specific GPU architecture (for better performance)
# docker build --build-arg TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6" -t hunyuan-video-avatar:latest .
```

### Build Options

```bash
# Minimal build (fastest, smaller image)
docker build -f Dockerfile -t hunyuan-video-avatar:minimal .

# Full build with all dependencies
docker build -t hunyuan-video-avatar:full .

# Build with custom tag
docker build -t your-username/hunyuan-video-avatar:v1.0 .
```

## 3. DockerHub Deployment

```bash
# Login to DockerHub
docker login

# Tag for DockerHub (replace 'your-username' with your actual username)
docker tag hunyuan-video-avatar:latest your-username/hunyuan-video-avatar:latest

# Push to DockerHub
docker push your-username/hunyuan-video-avatar:latest

# Optional: Push with version tags
docker tag hunyuan-video-avatar:latest your-username/hunyuan-video-avatar:v1.0
docker push your-username/hunyuan-video-avatar:v1.0
```

## 4. Local Testing

```bash
# Test the container locally
docker run --rm --gpus all \
  -v $(pwd)/outputs:/workspace/outputs \
  -v $(pwd)/inputs:/workspace/inputs \
  -p 7860:7860 \
  hunyuan-video-avatar:latest

# Test with web interface
docker run --rm --gpus all \
  -v $(pwd)/outputs:/workspace/outputs \
  -e WEB_MODE=true \
  -p 7860:7860 -p 80:80 \
  hunyuan-video-avatar:latest

# Check logs
docker logs <container_id>
```

## 5. Production Deployment

### RunPod Template Configuration

```json
{
  "name": "HunyuanVideo-Avatar Ultra-Low VRAM",
  "image": "your-username/hunyuan-video-avatar:latest",
  "ports": "7860/http,80/http",
  "volumeMountPath": "/workspace",
  "env": [
    {"key": "WEB_MODE", "value": "true"},
    {"key": "CUDA_VISIBLE_DEVICES", "value": "0"},
    {"key": "PYTORCH_CUDA_ALLOC_CONF", "value": "max_split_size_mb:512"}
  ]
}
```

### Docker Compose Deployment

```yaml
version: '3.8'
services:
  hunyuan-video-avatar:
    image: your-username/hunyuan-video-avatar:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - WEB_MODE=true
    ports:
      - "7860:7860"
      - "80:80"
    volumes:
      - ./outputs:/workspace/outputs
      - ./inputs:/workspace/inputs
      - model-cache:/workspace/weights
    restart: unless-stopped

volumes:
  model-cache:
```

## 6. Automated Build Script

```bash
#!/bin/bash
# automated_build.sh - Complete build and deployment script

set -e

echo "🚀 Starting HunyuanVideo-Avatar build and deployment..."

# Configuration
DOCKER_USERNAME="your-username"
IMAGE_NAME="hunyuan-video-avatar"
TAG="latest"

# Build
echo "📦 Building Docker image..."
docker build -t ${IMAGE_NAME}:${TAG} .

# Tag for DockerHub
echo "🏷️ Tagging for DockerHub..."
docker tag ${IMAGE_NAME}:${TAG} ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

# Push to DockerHub
echo "⬆️ Pushing to DockerHub..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

# Test locally
echo "🧪 Testing container locally..."
docker run --rm --gpus all \
  -v $(pwd)/outputs:/workspace/outputs \
  -e WEB_MODE=true \
  -p 7860:7860 \
  -d \
  --name hunyuan-test \
  ${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}

# Wait for startup
sleep 30

# Check if container is running
if docker ps | grep -q hunyuan-test; then
    echo "✅ Container started successfully!"
    echo "🌐 Web interface available at: http://localhost:7860"
    echo "📊 Check logs: docker logs hunyuan-test"
else
    echo "❌ Container failed to start"
    docker logs hunyuan-test
    exit 1
fi

echo "🎉 Build and deployment complete!"
```

## 7. Monitoring and Maintenance

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Monitor container resources
docker stats

# View container logs
docker logs -f <container_id>

# Access container shell
docker exec -it <container_id> /bin/bash

# Update container
docker pull your-username/hunyuan-video-avatar:latest
docker stop <container_id>
docker run --rm --gpus all -d your-username/hunyuan-video-avatar:latest
```

## 8. Troubleshooting

### Flash Attention Issues
```bash
# Check if flash_attn is properly installed
docker run --rm --gpus all your-username/hunyuan-video-avatar:latest python -c "import flash_attn; print('Flash Attention OK')"

# If compilation fails, rebuild with verbose output
docker build --no-cache --progress=plain -t hunyuan-video-avatar:latest .
```

### GPU Issues
```bash
# Verify GPU is accessible
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi

# Check CUDA version compatibility
docker run --rm --gpus all your-username/hunyuan-video-avatar:latest nvidia-smi
```

### Memory Issues
```bash
# Check available memory
free -h
df -h

# Monitor during build
docker system df
docker builder prune
```

## 9. Performance Optimization

### Build Optimizations
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker build -t hunyuan-video-avatar:latest .

# Multi-stage build for smaller images
docker build --target production -t hunyuan-video-avatar:optimized .

# Cache pip packages
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t hunyuan-video-avatar:latest .
```

### Runtime Optimizations
```bash
# Limit memory usage
docker run --memory=16g --gpus all hunyuan-video-avatar:latest

# Set CPU limits
docker run --cpus=4 --gpus all hunyuan-video-avatar:latest

# Use specific GPU
docker run --gpus '"device=0"' hunyuan-video-avatar:latest
```

## Support

- **GitHub Issues**: [Report problems](https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal/issues)
- **Docker Hub**: [Container images](https://hub.docker.com/r/your-username/hunyuan-video-avatar)
- **RunPod Community**: [Deployment help](https://docs.runpod.io/)

---

**Note**: The flash_attn dependency is now properly handled in the Docker build process. The container will compile flash_attn during the build phase, which may take 10-15 additional minutes depending on your hardware. 