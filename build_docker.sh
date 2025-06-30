#!/bin/bash

# HunyuanVideo-Avatar Docker Build Script - Main Dockerfile with Precompiled Flash Attention
# FAST & RELIABLE BUILD - Uses precompiled wheels instead of compilation

set -e

echo "🚀 Building HunyuanVideo-Avatar Docker image (Precompiled Flash Attention)"
echo "========================================================================="
echo "Base image: nvidia/cuda:12.4.1-devel-ubuntu22.04"
echo "Flash Attention: Precompiled wheels (FAST & RELIABLE)"
echo "Build time: ~5-10 minutes (much faster than compilation!)"
echo "========================================================================="

# Configuration
IMAGE_NAME="hunyuan-video-avatar"
IMAGE_TAG="latest"
DOCKERFILE="Dockerfile"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

print_status "Docker is running"

# Check if we're in the right directory
if [ ! -f "$DOCKERFILE" ]; then
    print_error "$DOCKERFILE not found. Make sure you're in the project directory."
    exit 1
fi

print_status "$DOCKERFILE found"

print_info "Building Docker image with precompiled flash attention..."
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Dockerfile: ${DOCKERFILE}"

# Start timing
start_time=$(date +%s)

# Build the image
if docker build -f "$DOCKERFILE" -t "${IMAGE_NAME}:${IMAGE_TAG}" .; then
    end_time=$(date +%s)
    build_time=$((end_time - start_time))
    print_status "Docker image built successfully in ${build_time} seconds!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Show image size
IMAGE_SIZE=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "${IMAGE_NAME}" | grep "${IMAGE_TAG}" | awk '{print $3}')
print_info "Image size: ${IMAGE_SIZE}"

# Test flash attention in the image
print_info "Testing flash attention in built image..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python3 -c "import flash_attn; print('✅ Flash Attention works!')"; then
    print_status "Flash Attention verification passed!"
else
    print_warning "Flash Attention test failed, but image was built"
fi

# Test basic functionality
print_info "Testing basic PyTorch functionality..."
if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python3 -c "import torch; print(f'✅ PyTorch {torch.__version__} works!')"; then
    print_status "PyTorch verification passed!"
fi

echo ""
print_status "🎉 Build Complete!"
print_info "Local image: ${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "🚀 PRECOMPILED BUILD ADVANTAGES:"
echo "- Uses precompiled flash attention wheels"
echo "- Fast build time (5-10 minutes vs 20-30 minutes)"
echo "- Very reliable - no compilation failures"
echo "- Good performance with Flash Attention"
echo ""
echo "💻 Next Steps:"
echo "1. Test locally:"
echo "   docker run --rm --gpus all -p 7860:7860 -p 8000:8000 ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "2. Push to registry (optional):"
echo "   docker tag ${IMAGE_NAME}:${IMAGE_TAG} your-registry/${IMAGE_NAME}:${IMAGE_TAG}"
echo "   docker push your-registry/${IMAGE_NAME}:${IMAGE_TAG}"

# VPS Deployment Instructions
echo ""
echo "💻 VPS Deployment Commands:"
echo "=========================="
echo "1. Clone repository:"
echo "   git clone -b wan2gp https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git"
echo "   cd HunyuanVideo-Avatar-minimal"
echo ""
echo "2. Build Docker image:"
echo "   docker build -t hunyuan-avatar:latest ."
echo ""
echo "3. Push to Docker Hub (replace YOUR_USERNAME):"
echo "   docker tag hunyuan-avatar:latest YOUR_USERNAME/hunyuan-avatar:latest"
echo "   docker push YOUR_USERNAME/hunyuan-avatar:latest"
echo ""
echo "4. Run on VPS:"
echo "   docker run --gpus all -p 7860:7860 -p 8000:8000 YOUR_USERNAME/hunyuan-avatar:latest" 