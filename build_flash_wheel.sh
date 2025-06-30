#!/bin/bash

# HunyuanVideo-Avatar Docker Build Script - Alternative Flash Attention Method
# Uses intelligent wheel detection and fallback

set -e

# Configuration
IMAGE_NAME="hunyuan-avatar-flash-wheel"
TAG="latest"
DOCKERFILE="Dockerfile.flash-wheel"
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

echo "🔧 HunyuanVideo-Avatar Alternative Flash Attention Build"
echo "====================================================="
print_info "This build uses intelligent flash attention wheel detection"

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
print_info "Building Docker image with intelligent flash attention detection..."
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

# Test flash attention in the image
print_info "Testing flash attention in built image..."
docker run --rm "${IMAGE_NAME}:${TAG}" python3 -c "
try:
    import flash_attn
    print('✅ Flash Attention Available:', flash_attn.__version__)
except ImportError:
    print('⚠️ Flash Attention not available - using standard attention')
    print('This is fine - the application will work with slightly reduced performance')
"

echo ""
print_status "Alternative Build Complete!"
print_info "Local image: ${IMAGE_NAME}:${TAG}"

echo ""
echo "🔧 ALTERNATIVE BUILD FEATURES:"
echo "- Intelligent flash attention wheel detection"
echo "- Multiple version fallbacks"
echo "- Graceful degradation if no wheels available"
echo "- Still uses CUDA 12.4 optimizations"
echo ""
echo "💻 Test Command:"
echo "docker run --gpus all -p 7860:7860 -p 8000:8000 ${IMAGE_NAME}:${TAG}" 