#!/bin/bash

# HunyuanVideo-Avatar Docker Build Script - Precompiled Flash Attention Version
# FAST BUILD - Uses precompiled wheels instead of compilation

set -e

# Configuration
IMAGE_NAME="hunyuan-avatar-precompiled"
TAG="latest"
DOCKERFILE="Dockerfile.precompiled"
REGISTRY=""  # Set your Docker Hub username here

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

echo "🚀 HunyuanVideo-Avatar FAST Docker Build (Precompiled Flash Attention)"
echo "======================================================================"
print_info "This build uses precompiled flash attention wheels - MUCH FASTER!"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if we're in the right directory
if [ ! -f "$DOCKERFILE" ]; then
    print_error "$DOCKERFILE not found. Make sure you're in the project directory."
    exit 1
fi

print_status "$DOCKERFILE found"

# Build the image
print_info "Building Docker image with precompiled flash attention..."
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Dockerfile: ${DOCKERFILE}"

# Start timing
start_time=$(date +%s)

if docker build -f "$DOCKERFILE" -t "${IMAGE_NAME}:${TAG}" .; then
    end_time=$(date +%s)
    build_time=$((end_time - start_time))
    print_status "Docker image built successfully in ${build_time} seconds!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Show image size
IMAGE_SIZE=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "${IMAGE_NAME}" | grep "${TAG}" | awk '{print $3}')
print_info "Image size: ${IMAGE_SIZE}"

# Quick test of flash attention in the image
print_info "Testing flash attention in built image..."
if docker run --rm "${IMAGE_NAME}:${TAG}" python3 -c "import flash_attn; print('✅ Flash Attention works!')"; then
    print_status "Flash Attention verification passed!"
else
    print_warning "Flash Attention test failed, but image was built"
fi

# Ask if user wants to test the image
echo ""
read -p "🧪 Do you want to test the image locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Testing image locally..."
    print_warning "This will download ~10GB of models on first run"
    print_info "Press Ctrl+C to stop the container"
    
    # Create test directories
    mkdir -p ./test_outputs ./test_logs ./test_inputs
    
    docker run --rm -it \
        --gpus all \
        -e NVIDIA_VISIBLE_DEVICES=0 \
        -v ./test_outputs:/workspace/outputs \
        -v ./test_logs:/workspace/logs \
        -v ./test_inputs:/workspace/inputs \
        "${IMAGE_NAME}:${TAG}"
fi

# Ask if user wants to push to registry
if [ ! -z "$REGISTRY" ]; then
    echo ""
    read -p "📤 Do you want to push to registry? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
        
        print_info "Tagging image for registry..."
        docker tag "${IMAGE_NAME}:${TAG}" "${FULL_IMAGE_NAME}"
        
        print_info "Pushing to registry: ${FULL_IMAGE_NAME}"
        if docker push "${FULL_IMAGE_NAME}"; then
            print_status "Image pushed successfully!"
            print_info "Registry image: ${FULL_IMAGE_NAME}"
        else
            print_error "Failed to push image"
            exit 1
        fi
    fi
else
    print_warning "No registry configured. Set REGISTRY variable in this script to push images."
fi

echo ""
print_status "FAST Build Complete!"
print_info "Local image: ${IMAGE_NAME}:${TAG}"

if [ ! -z "$REGISTRY" ]; then
    print_info "Registry image: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
fi

echo ""
echo "⚡ FAST BUILD ADVANTAGES:"
echo "- Uses precompiled flash attention wheels"
echo "- No compilation time (saves 10-30 minutes)"
echo "- More reliable builds"
echo "- Compatible with CUDA 12.4 + cuDNN"
echo ""
echo "💻 VPS Commands:"
echo "1. Clone: git clone -b wan2gp https://github.com/thanveerdev/HunyuanVideo-Avatar-minimal.git"
echo "2. Build: docker build -f Dockerfile.precompiled -t hunyuan-avatar:latest ."
echo "3. Run: docker run --gpus all -p 7860:7860 -p 8000:8000 hunyuan-avatar:latest" 