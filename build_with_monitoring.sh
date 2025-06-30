#!/bin/bash

# Monitored Docker Build Script for HunyuanVideo-Avatar
# Detects and handles stuck flash attention compilation

set -e

# Configuration
BUILD_TYPE="${1:-precompiled}"  # precompiled, flash-attn, or no-flash
TIMEOUT_MINUTES=45  # Max time to wait for flash attention compilation
CHECK_INTERVAL=60   # Check every 60 seconds

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to monitor build progress
monitor_build() {
    local build_pid=$1
    local start_time=$(date +%s)
    local last_output_time=$start_time
    local build_log="build_monitor.log"
    
    print_info "Monitoring build process (PID: $build_pid)"
    print_info "Timeout: $TIMEOUT_MINUTES minutes"
    
    while kill -0 $build_pid 2>/dev/null; do
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        elapsed_minutes=$((elapsed / 60))
        
        # Check if we've exceeded timeout
        if [ $elapsed_minutes -gt $TIMEOUT_MINUTES ]; then
            print_error "Build timed out after $TIMEOUT_MINUTES minutes"
            print_warning "This usually means flash attention compilation is stuck"
            print_info "Killing build process..."
            kill -TERM $build_pid 2>/dev/null || true
            sleep 5
            kill -KILL $build_pid 2>/dev/null || true
            
            echo ""
            print_warning "Build was terminated due to timeout"
            print_info "Recommendations:"
            echo "  1. Try precompiled build: ./build_precompiled_docker.sh"
            echo "  2. Try no-flash-attn build: ./build_no_flash_attn_docker.sh"
            echo "  3. Increase system memory if possible"
            echo "  4. Reduce MAX_JOBS in Dockerfile"
            
            return 1
        fi
        
        # Print progress every few minutes
        if [ $((elapsed % 300)) -eq 0 ] && [ $elapsed -gt 0 ]; then
            print_info "Build running for $elapsed_minutes minutes..."
            
            # Check if flash attention compilation is happening
            if docker logs $(docker ps -q --filter ancestor=temp-build 2>/dev/null) 2>/dev/null | grep -q "Building wheel for flash-attn"; then
                print_info "Flash attention compilation in progress..."
            fi
        fi
        
        sleep $CHECK_INTERVAL
    done
    
    # Build finished, check exit code
    wait $build_pid
    return $?
}

# Function to build with monitoring
build_with_monitoring() {
    local dockerfile=$1
    local image_name=$2
    local build_tag=$3
    
    print_info "Starting monitored build..."
    print_info "Dockerfile: $dockerfile"
    print_info "Image: $image_name:$build_tag"
    
    # Start build in background
    docker build \
        -t "$image_name:$build_tag" \
        -f "$dockerfile" \
        --progress=plain \
        . > build_output.log 2>&1 &
    
    local build_pid=$!
    
    # Monitor the build
    if monitor_build $build_pid; then
        print_status "Build completed successfully!"
        
        # Test the built image
        print_info "Testing the built image..."
        if [ "$BUILD_TYPE" != "no-flash" ]; then
            if docker run --rm "$image_name:$build_tag" python3 -c "import flash_attn; print('✅ Flash Attention works!')" 2>/dev/null; then
                print_status "Flash Attention test passed!"
            else
                print_warning "Flash Attention test failed (may need GPU at runtime)"
            fi
        fi
        
        return 0
    else
        print_error "Build failed or timed out"
        return 1
    fi
}

# Main execution
echo "🚀 HunyuanVideo-Avatar Monitored Build"
echo "====================================="

case $BUILD_TYPE in
    "flash-attn")
        print_info "Building with Flash Attention compilation (high risk of timeout)"
        if build_with_monitoring "Dockerfile.flash-attn" "hunyuan-video-avatar-flash-attn" "latest"; then
            print_status "Flash Attention build completed!"
        else
            print_warning "Flash Attention build failed, trying precompiled..."
            BUILD_TYPE="precompiled"
            build_with_monitoring "Dockerfile.precompiled" "hunyuan-avatar-precompiled" "latest"
        fi
        ;;
    "precompiled")
        print_info "Building with precompiled Flash Attention wheels (low risk)"
        if build_with_monitoring "Dockerfile.precompiled" "hunyuan-avatar-precompiled" "latest"; then
            print_status "Precompiled build completed!"
        else
            print_warning "Precompiled build failed, trying no-flash-attn..."
            BUILD_TYPE="no-flash"
            build_with_monitoring "Dockerfile.no-flash-attn" "hunyuan-video-avatar-no-flash" "latest"
        fi
        ;;
    "no-flash")
        print_info "Building without Flash Attention (no timeout risk)"
        build_with_monitoring "Dockerfile.no-flash-attn" "hunyuan-video-avatar-no-flash" "latest"
        ;;
    *)
        print_error "Invalid build type: $BUILD_TYPE"
        echo "Usage: $0 [flash-attn|precompiled|no-flash]"
        exit 1
        ;;
esac

echo ""
print_status "Build process completed!"
echo ""
print_info "Available commands:"
echo "  Monitor build:     $0 precompiled    # Recommended"
echo "  Fast build:        $0 no-flash       # If having issues"  
echo "  Performance build: $0 flash-attn     # May timeout" 