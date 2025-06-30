#!/bin/bash

# Build script for HunyuanVideo-Avatar WITHOUT Flash Attention
# Fallback option for environments where flash-attn compilation fails

set -e

echo "🚀 Building HunyuanVideo-Avatar Docker image WITHOUT Flash Attention"
echo "=================================================================="
echo "Base image: nvidia/cuda:12.4.1-devel-ubuntu22.04"
echo "Flash Attention: DISABLED (fallback mode)"
echo "=================================================================="

# Configuration
IMAGE_NAME="hunyuan-video-avatar-no-flash"
IMAGE_TAG="cuda12.4-ubuntu22.04"
DOCKERFILE="Dockerfile.no-flash-attn"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Build Configuration:${NC}"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Image Tag: ${IMAGE_TAG}"
echo "  Dockerfile: ${DOCKERFILE}"
echo "  Full Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Start build
echo -e "${BLUE}🔨 Starting Docker build (no flash attention)...${NC}"
echo "This build should be much faster without flash attention compilation"
echo ""

# Build with verbose output
docker build \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -t "${IMAGE_NAME}:latest" \
    -f "${DOCKERFILE}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo -e "${GREEN}   Image: ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    
    # Test the image
    echo ""
    echo -e "${BLUE}🧪 Testing the built image...${NC}"
    
    # Test basic imports (without flash attention)
    echo "Testing basic imports..."
    if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python3 -c "import torch; print('✅ PyTorch works!')"; then
        echo -e "${GREEN}✅ Basic import tests passed!${NC}"
    else
        echo -e "${RED}❌ Basic import tests failed${NC}"
    fi
    
    # Show image info
    echo ""
    echo -e "${BLUE}📊 Image Information:${NC}"
    docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  PERFORMANCE WARNING:${NC}"
    echo "   This image runs WITHOUT Flash Attention for better compatibility"
    echo "   Performance will be significantly slower than flash-attn versions"
    echo "   Consider using build_flash_attn_docker.sh for better performance"
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "1. Run directly:"
    echo -e "   ${YELLOW}docker run --rm --gpus all -p 7860:7860 -p 80:80 ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    echo ""
    echo "2. For better performance, try:"
    echo -e "   ${YELLOW}./build_flash_attn_docker.sh${NC}"
    echo -e "   ${YELLOW}./build_precompiled_docker.sh${NC}"

else
    echo ""
    echo -e "${RED}❌ Docker build failed!${NC}"
    echo "Check the output above for error details."
    exit 1
fi 