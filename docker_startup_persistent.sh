#!/bin/bash

# HunyuanVideo-Avatar Persistent Docker Startup Script for RunPod
# Enhanced version that prevents container stopping

set -e

echo "🚀 Starting HunyuanVideo-Avatar on RunPod (Persistent Mode)"
echo "============================================"

# Function to print colored output
print_status() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

# Enhanced error handling
handle_error() {
    print_error "Error occurred: $1"
    print_warning "Container will remain running for debugging"
    print_status "Connect via SSH to investigate: ssh root@runpod"
    # Keep container alive instead of exiting
    tail -f /dev/null
}

# Trap errors to prevent container stopping
trap 'handle_error "Unexpected error occurred"' ERR

# Check if we're running on RunPod
if [ ! -z "$RUNPOD_POD_ID" ]; then
    print_status "Running on RunPod Pod: $RUNPOD_POD_ID"
    if [ ! -z "$RUNPOD_PUBLIC_IP" ]; then
        print_status "Public IP: $RUNPOD_PUBLIC_IP"
    fi
fi

# Check GPU availability with enhanced error handling
print_status "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits; then
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        print_status "GPU detected with ${GPU_MEMORY}MB memory"
    else
        print_error "GPU detected but nvidia-smi failed"
        handle_error "GPU access issue"
    fi
else
    print_error "No GPU detected! This application requires NVIDIA GPU"
    handle_error "No GPU found"
fi

# Enhanced memory optimization based on GPU memory
if [ "$GPU_MEMORY" -lt 8192 ]; then
    print_warning "Low GPU memory detected (${GPU_MEMORY}MB). Using ultra-low VRAM mode"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:64,garbage_collection_threshold:0.3,expandable_segments:True"
    export IMAGE_SIZE=256
elif [ "$GPU_MEMORY" -lt 12288 ]; then
    print_status "Medium GPU memory detected (${GPU_MEMORY}MB). Using low VRAM mode"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.5,expandable_segments:True"
    export IMAGE_SIZE=384
else
    print_status "High GPU memory detected (${GPU_MEMORY}MB). Using extreme optimization mode"
    # HunyuanVideoGP-inspired extreme optimizations for 24GB GPU
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.5,expandable_segments:True"
    export PYTORCH_NO_CUDA_MEMORY_CACHING=1
    export CUDA_CACHE_DISABLE=1
    export PYTORCH_JIT=0
    export OMP_NUM_THREADS=1
    export MKL_NUM_THREADS=1
    export CUDA_MODULE_LOADING=LAZY
    export IMAGE_SIZE=512
    print_status "Applied HunyuanVideoGP-style extreme memory optimizations"
fi

# Set persistent mode
export PERSISTENT_MODE=1

# Apply TorchVision compatibility fix automatically
print_status "Applying TorchVision compatibility fix..."
cd /workspace
if python3 apply_torchvision_fix.py; then
    print_status "TorchVision compatibility fix applied successfully"
else
    print_warning "TorchVision fix had issues, but continuing with fallback mode"
fi

# Model download with error handling
MODEL_CHECK_FILE="/workspace/weights/.models_downloaded"
if [ ! -f "$MODEL_CHECK_FILE" ]; then
    print_status "First run detected - downloading model weights..."
    print_warning "This may take 10-30 minutes depending on your connection"
    
    cd /workspace/weights
    
    if timeout 3600 huggingface-cli download tencent/HunyuanVideo-Avatar --local-dir ./; then
        print_status "Models downloaded successfully!"
        touch "$MODEL_CHECK_FILE"
        echo "Models downloaded at: $(date)" > "$MODEL_CHECK_FILE"
    else
        print_error "Model download failed or timed out!"
        handle_error "Model download failure"
    fi
    
    cd /workspace
else
    print_status "Models already downloaded, skipping download"
fi

# Create sample input file
if [ ! -f "/workspace/test_input.csv" ]; then
    print_status "Creating sample input file..."
    echo "videoid,image,audio,prompt,fps" > /workspace/test_input.csv
    echo "test1,assets/image/1.png,assets/audio/2.WAV,A person speaking naturally,25" >> /workspace/test_input.csv
    print_status "Sample input created: test_input.csv"
fi

# Enhanced RunPod support
if [ -d "/runpod-volume" ]; then
    print_status "RunPod network volume detected - setting up persistence"
    mkdir -p /runpod-volume/{outputs,logs,models}
    
    # Link directories
    ln -sf /runpod-volume/outputs /workspace/outputs
    ln -sf /runpod-volume/logs /workspace/logs
    
    print_status "Persistent storage configured"
fi

# Test configuration with error handling
print_status "Testing configuration..."
if timeout 30 python3 config_minimal.py; then
    print_status "Configuration test passed"
else
    print_warning "Configuration test failed or timed out - continuing anyway"
fi

# Memory monitoring function
monitor_memory() {
    while true; do
        if command -v nvidia-smi &> /dev/null; then
            MEMORY_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
            MEMORY_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
            USAGE_PERCENT=$((MEMORY_USED * 100 / MEMORY_TOTAL))
            
            if [ $USAGE_PERCENT -gt 90 ]; then
                print_warning "High VRAM usage: ${USAGE_PERCENT}% (${MEMORY_USED}MB/${MEMORY_TOTAL}MB)"
            fi
        fi
        sleep 30
    done
}

# Start background memory monitoring
monitor_memory &
MONITOR_PID=$!

# Print startup information
echo ""
echo "🎯 HunyuanVideo-Avatar Ready (Persistent Mode)!"
echo "============================================="
echo "GPU Memory: ${GPU_MEMORY}MB"
echo "Image Size: ${IMAGE_SIZE}px"
echo "Persistent Mode: Enabled"
echo "Monitor PID: $MONITOR_PID"
echo ""
echo "🌐 Available Modes:"
echo "1. Interactive: bash run_low_memory.sh"
echo "2. Web Interface: bash run_web_demo.sh (Port 7860)"
echo "3. Custom Input: Modify test_input.csv"
echo ""

# Determine run mode with enhanced logic
RUN_MODE=${RUN_MODE:-"persistent"}

case "$RUN_MODE" in
    "web")
        print_status "Web interface mode - starting Gradio UI"
        exec bash run_web_demo.sh
        ;;
    "batch")
        print_status "Batch mode - running inference with persistence"
        
        # Run inference with error handling
        if timeout 3600 python3 -m hymm_sp.low_memory_inference \
            --ckpt /workspace/weights \
            --input /workspace/test_input.csv \
            --save-path /workspace/outputs \
            --cpu-offload \
            --infer-min \
            --image-size "$IMAGE_SIZE" \
            --sample-n-frames 129 \
            --seed 128 \
            --cfg-scale 7.5 \
            --infer-steps 50 \
            --use-fp8 \
            2>&1 | tee /workspace/logs/inference_$(date +%Y%m%d_%H%M%S).log; then
            
            print_status "Inference completed successfully!"
            print_status "Results saved to /workspace/outputs"
        else
            print_error "Inference failed or timed out"
        fi
        
        # Keep container running after batch completion
        print_status "Batch complete - entering persistent mode"
        print_status "Container will remain running for additional tasks"
        print_status "Connect via SSH or modify RUN_MODE to restart"
        
        # Keep alive
        tail -f /dev/null
        ;;
    "interactive"|"persistent"|*)
        print_status "Persistent interactive mode"
        echo "Available commands:"
        echo "  1. bash run_minimal.sh          - Ultra low VRAM mode"
        echo "  2. bash run_low_memory.sh       - Standard low memory mode" 
        echo "  3. bash run_web_demo.sh         - Web interface (Port 7860)"
        echo "  4. python3 test_mmgp_integration.py - Test MMGP integration"
        echo ""
        echo "🔄 Container will remain running indefinitely"
        echo "💡 To run inference: bash run_low_memory.sh"
        echo "🌐 For web UI: bash run_web_demo.sh"
        echo ""
        
        # Keep container alive indefinitely
        exec /bin/bash
        ;;
esac 