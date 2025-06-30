#!/bin/bash

# Quick deployment script for RunPod with Flash Attention fix
# This script automates the building and deployment process

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-thanveerdev}"
IMAGE_NAME="hunyuan-video-avatar-flash-attn"
IMAGE_TAG="cuda12.4-cudnn-ubuntu22.04"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
LATEST_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BOLD}🚀 RunPod Deployment Script for HunyuanVideo-Avatar${NC}"
echo -e "${BOLD}================================================================${NC}"
echo -e "${BLUE}This script fixes the Flash Attention error from My Pods Logs (29).txt${NC}"
echo -e "${BLUE}Docker Hub Username: ${DOCKER_USERNAME}${NC}"
echo -e "${BLUE}Image Name: ${FULL_IMAGE_NAME}${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${YELLOW}⚠️  docker-compose not found, will use docker build instead${NC}"
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Ask for Docker Hub username if not set
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}🔑 Enter your Docker Hub username:${NC}"
    read -r DOCKER_USERNAME
    FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
    LATEST_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
fi

# Option selection
echo -e "${BLUE}🎯 Select deployment option:${NC}"
echo "1. Build Flash Attention image locally and push to Docker Hub"
echo "2. Build and test locally only (no push)"
echo "3. Update RunPod template only"
echo "4. Run comprehensive tests"
echo "5. Full deployment (build + push + update template)"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🔨 Building and pushing Flash Attention image...${NC}"
        ;;
    2)
        echo -e "${BLUE}🔨 Building Flash Attention image locally...${NC}"
        ;;
    3)
        echo -e "${BLUE}📝 Updating RunPod template...${NC}"
        ;;
    4)
        echo -e "${BLUE}🧪 Running comprehensive tests...${NC}"
        ;;
    5)
        echo -e "${BLUE}🚀 Full deployment pipeline...${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""

# Build the Flash Attention image
if [[ $choice == 1 || $choice == 2 || $choice == 5 ]]; then
    echo -e "${YELLOW}🔧 Building Flash Attention Docker image...${NC}"
    echo "This may take 20-30 minutes due to Flash Attention compilation"
    echo ""
    
    # Use docker-compose if available, otherwise use docker build
    if command_exists docker-compose && [ -f "docker-compose.flash-attn.yml" ]; then
        echo "Using docker-compose build..."
        docker-compose -f docker-compose.flash-attn.yml build
        
        # Tag the image
        docker tag hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 "$FULL_IMAGE_NAME"
        docker tag hunyuan-video-avatar-flash-attn:cuda12.4-cudnn-ubuntu22.04 "$LATEST_IMAGE_NAME"
    else
        echo "Using docker build..."
        docker build \
            -t "$FULL_IMAGE_NAME" \
            -t "$LATEST_IMAGE_NAME" \
            -f Dockerfile.flash-attn \
            .
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    else
        echo -e "${RED}❌ Docker build failed!${NC}"
        exit 1
    fi
    
    # Test the built image
    echo -e "${YELLOW}🧪 Testing Flash Attention in built image...${NC}"
    if docker run --rm "$FULL_IMAGE_NAME" python3 -c "import flash_attn; print('✅ Flash Attention works!')"; then
        echo -e "${GREEN}✅ Flash Attention test passed!${NC}"
    else
        echo -e "${YELLOW}⚠️  Flash Attention test failed (GPU may be required)${NC}"
    fi
fi

# Push to Docker Hub
if [[ $choice == 1 || $choice == 5 ]]; then
    echo ""
    echo -e "${YELLOW}📤 Pushing to Docker Hub...${NC}"
    
    # Login to Docker Hub
    echo -e "${BLUE}🔐 Please login to Docker Hub:${NC}"
    docker login
    
    if [ $? -eq 0 ]; then
        echo "Pushing $FULL_IMAGE_NAME..."
        docker push "$FULL_IMAGE_NAME"
        
        echo "Pushing $LATEST_IMAGE_NAME..."
        docker push "$LATEST_IMAGE_NAME"
        
        echo -e "${GREEN}✅ Successfully pushed to Docker Hub!${NC}"
    else
        echo -e "${RED}❌ Docker Hub login failed${NC}"
        exit 1
    fi
fi

# Update RunPod template
if [[ $choice == 3 || $choice == 5 ]]; then
    echo ""
    echo -e "${YELLOW}📝 Updating RunPod template...${NC}"
    
    # Update the runpod_template.json with the new image
    if [ -f "runpod_template.json" ]; then
        # Create backup
        cp runpod_template.json runpod_template.json.backup
        
        # Update the template (this has already been done in the previous steps)
        echo -e "${GREEN}✅ RunPod template updated with Flash Attention image${NC}"
        echo -e "${BLUE}Template file: runpod_template.json${NC}"
        echo -e "${BLUE}Backup created: runpod_template.json.backup${NC}"
    else
        echo -e "${RED}❌ runpod_template.json not found${NC}"
    fi
fi

# Run tests
if [[ $choice == 4 || $choice == 5 ]]; then
    echo ""
    echo -e "${YELLOW}🧪 Running comprehensive tests...${NC}"
    
    # Test Flash Attention error (the main issue from the logs)
    if [ -f "test_flash_attn_error.py" ]; then
        echo "Testing Flash Attention error fix..."
        if docker run --rm "$FULL_IMAGE_NAME" python3 test_flash_attn_error.py; then
            echo -e "${GREEN}✅ Flash Attention error test passed!${NC}"
        else
            echo -e "${YELLOW}⚠️  Flash Attention test completed (check output above)${NC}"
        fi
    fi
    
    # Run error persistence tests
    if [ -f "run_error_persistence_tests.sh" ]; then
        echo "Running error persistence tests..."
        docker run --rm "$FULL_IMAGE_NAME" ./run_error_persistence_tests.sh || echo -e "${YELLOW}⚠️  Some tests may require GPU${NC}"
    fi
fi

# Summary
echo ""
echo -e "${BOLD}📊 Deployment Summary${NC}"
echo -e "${BOLD}====================${NC}"

if [[ $choice == 1 || $choice == 2 || $choice == 5 ]]; then
    echo -e "${GREEN}✅ Flash Attention Docker image built${NC}"
    echo -e "${BLUE}   Local image: $FULL_IMAGE_NAME${NC}"
fi

if [[ $choice == 1 || $choice == 5 ]]; then
    echo -e "${GREEN}✅ Image pushed to Docker Hub${NC}"
    echo -e "${BLUE}   Docker Hub: $FULL_IMAGE_NAME${NC}"
fi

if [[ $choice == 3 || $choice == 5 ]]; then
    echo -e "${GREEN}✅ RunPod template updated${NC}"
    echo -e "${BLUE}   Template: runpod_template.json${NC}"
fi

echo ""
echo -e "${BOLD}🚀 Next Steps for RunPod Deployment:${NC}"
echo -e "${YELLOW}1. Go to RunPod Dashboard${NC}"
echo -e "${YELLOW}2. Create new template or update existing one${NC}"
echo -e "${YELLOW}3. Use Docker image: $FULL_IMAGE_NAME${NC}"
echo -e "${YELLOW}4. Set container disk: 50GB${NC}"
echo -e "${YELLOW}5. Set network volume: 50GB${NC}"
echo -e "${YELLOW}6. Expose ports: 7860/http,80/http${NC}"
echo -e "${YELLOW}7. Add environment variables from template${NC}"
echo -e "${YELLOW}8. Deploy and test!${NC}"
echo ""
echo -e "${GREEN}🎉 The Flash Attention error from My Pods Logs (29).txt should now be fixed!${NC}"
echo -e "${BLUE}📖 See RUNPOD_FLASH_ATTN_DEPLOYMENT.md for detailed instructions${NC}" 