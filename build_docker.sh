#!/bin/bash

# HunyuanVideo-Avatar Docker Build Script
# Easy deployment script for building and pushing to registry

set -e

# Configuration
IMAGE_NAME="hunyuan-avatar"
TAG="latest"
REGISTRY=""  # Set your registry here (e.g., "your-dockerhub-username" or "your-registry.com")

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

echo "🐳 HunyuanVideo-Avatar Docker Build Script"
echo "=========================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile not found. Make sure you're in the project directory."
    exit 1
fi

print_status "Dockerfile found"

# Build the image
print_info "Building Docker image..."
echo "Image: ${IMAGE_NAME}:${TAG}"

if docker build -t "${IMAGE_NAME}:${TAG}" .; then
    print_status "Docker image built successfully!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Show image size
IMAGE_SIZE=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "${IMAGE_NAME}" | grep "${TAG}" | awk '{print $3}')
print_info "Image size: ${IMAGE_SIZE}"

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
print_status "Build complete!"
print_info "Local image: ${IMAGE_NAME}:${TAG}"

if [ ! -z "$REGISTRY" ]; then
    print_info "Registry image: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Push image to your registry (Docker Hub, etc.)"
echo "2. Update runpod_template.json with your registry URL"
echo "3. Deploy on RunPod using the template"
echo ""
echo "🌐 Web Interface Usage:"
echo "- Set RUN_MODE=web to enable Gradio interface"
echo "- Access at: http://localhost:7860 (local) or pod URL (RunPod)"
echo "- See README_WEB_INTERFACE.md for detailed instructions"
echo ""
echo "📖 See README_DOCKER.md for detailed deployment instructions" 