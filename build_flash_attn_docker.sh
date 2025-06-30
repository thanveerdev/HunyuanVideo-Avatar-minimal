#!/bin/bash

# Build script for HunyuanVideo-Avatar with Flash Attention support
# Using nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

set -e

echo "🚀 Building HunyuanVideo-Avatar Docker image with Flash Attention support"
echo "============================================================================="
echo "Base image: nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04"
echo "Flash Attention: Enabled with proper CUDA 12.4 + cuDNN support"
echo "============================================================================="

# Configuration
IMAGE_NAME="hunyuan-video-avatar-flash-attn"
IMAGE_TAG="cuda12.4-cudnn-ubuntu22.04"
DOCKERFILE="Dockerfile.flash-attn"

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

# Check if nvidia-docker is available (for GPU support)
if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}⚠️  WARNING: nvidia-docker or GPU support may not be available${NC}"
    echo -e "${YELLOW}   Make sure you have nvidia-container-toolkit installed${NC}"
fi

echo -e "${BLUE}📋 Build Configuration:${NC}"
echo "  Image Name: ${IMAGE_NAME}"
echo "  Image Tag: ${IMAGE_TAG}"
echo "  Dockerfile: ${DOCKERFILE}"
echo "  Full Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Start build
echo -e "${BLUE}🔨 Starting Docker build...${NC}"
echo "This may take 20-30 minutes (Flash Attention compilation is slow)"
echo ""

# Build with verbose output and build args
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
    
    # Test Flash Attention import
    echo "Testing Flash Attention import..."
    if docker run --rm --gpus all "${IMAGE_NAME}:${IMAGE_TAG}" python3 -c "import flash_attn; print('✅ Flash Attention works!')"; then
        echo -e "${GREEN}✅ Flash Attention test passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Flash Attention test failed (may need GPU at runtime)${NC}"
    fi
    
    # Test application imports
    echo "Testing application imports..."
    if docker run --rm "${IMAGE_NAME}:${IMAGE_TAG}" python3 test_flash_attn_error.py; then
        echo -e "${GREEN}✅ Application import tests passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Some application tests failed (expected without GPU)${NC}"
    fi
    
    # Show image info
    echo ""
    echo -e "${BLUE}📊 Image Information:${NC}"
    docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo ""
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}🚀 Next steps:${NC}"
    echo "1. Run with docker-compose:"
    echo -e "   ${YELLOW}docker-compose -f docker-compose.flash-attn.yml up${NC}"
    echo ""
    echo "2. Or run directly:"
    echo -e "   ${YELLOW}docker run --rm --gpus all -p 7860:7860 -p 80:80 ${IMAGE_NAME}:${IMAGE_TAG}${NC}"
    echo ""
    echo "3. Test error persistence:"
    echo -e "   ${YELLOW}docker run --rm --gpus all ${IMAGE_NAME}:${IMAGE_TAG} ./run_error_persistence_tests.sh${NC}"

else
    echo ""
    echo -e "${RED}❌ Docker build failed!${NC}"
    echo "Check the output above for error details."
    exit 1
fi 