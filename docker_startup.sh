#!/bin/bash

# HunyuanVideo-Avatar Docker Startup Script for RunPod
# Downloads models on first run and starts the application

set -e

echo "🚀 Starting HunyuanVideo-Avatar on RunPod"
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

# Check if we're running on RunPod
if [ ! -z "$RUNPOD_POD_ID" ]; then
    print_status "Running on RunPod Pod: $RUNPOD_POD_ID"
    if [ ! -z "$RUNPOD_PUBLIC_IP" ]; then
        print_status "Public IP: $RUNPOD_PUBLIC_IP"
    fi
fi

# Check GPU availability
print_status "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    print_status "GPU detected with ${GPU_MEMORY}MB memory"
else
    print_error "No GPU detected! This application requires NVIDIA GPU"
    exit 1
fi

# Set up memory optimization based on GPU memory
if [ "$GPU_MEMORY" -lt 8192 ]; then
    print_warning "Low GPU memory detected (${GPU_MEMORY}MB). Using ultra-low VRAM mode"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256"
    export IMAGE_SIZE=256
elif [ "$GPU_MEMORY" -lt 12288 ]; then
    print_status "Medium GPU memory detected (${GPU_MEMORY}MB). Using low VRAM mode"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
    export IMAGE_SIZE=384
else
    print_status "High GPU memory detected (${GPU_MEMORY}MB). Using balanced mode"
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024"
    export IMAGE_SIZE=512
fi

# Check if models are already downloaded
MODEL_CHECK_FILE="/workspace/weights/.models_downloaded"

if [ ! -f "$MODEL_CHECK_FILE" ]; then
    print_status "First run detected - downloading model weights..."
    print_warning "This may take 10-30 minutes depending on your connection"
    
    cd /workspace/weights
    
    # Download HunyuanVideo-Avatar models
    print_status "Downloading HunyuanVideo-Avatar models from HuggingFace..."
    if huggingface-cli download tencent/HunyuanVideo-Avatar --local-dir ./; then
        print_status "Models downloaded successfully!"
        touch "$MODEL_CHECK_FILE"
        echo "Models downloaded at: $(date)" > "$MODEL_CHECK_FILE"
    else
        print_error "Failed to download models!"
        print_warning "Attempting to continue with partial download..."
    fi
    
    cd /workspace
else
    print_status "Models already downloaded, skipping download"
    print_status "Download info: $(cat $MODEL_CHECK_FILE)"
fi

# Verify critical model files exist
print_status "Verifying model files..."
REQUIRED_MODELS=("ckpts/hunyuan-video-t2v-720p" "ckpts/text_encoder_2" "ckpts/whisper-tiny")
MISSING_MODELS=()

for model in "${REQUIRED_MODELS[@]}"; do
    if [ ! -d "/workspace/weights/$model" ]; then
        MISSING_MODELS+=("$model")
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    print_warning "Some models are missing:"
    for model in "${MISSING_MODELS[@]}"; do
        echo "  - $model"
    done
    print_warning "The application may not work correctly"
else
    print_status "All critical models verified"
fi

# Create sample input file if it doesn't exist
if [ ! -f "/workspace/test_input.csv" ]; then
    print_status "Creating sample input file..."
    echo "videoid,image,audio,prompt,fps" > /workspace/test_input.csv
    echo "test1,assets/image/1.png,assets/audio/2.WAV,A person speaking naturally,25" >> /workspace/test_input.csv
    print_status "Sample input created: test_input.csv"
fi

# Set up RunPod network volume support (if available)
if [ -d "/runpod-volume" ]; then
    print_status "RunPod network volume detected"
    # Link outputs to network volume for persistence
    if [ ! -L "/workspace/outputs" ]; then
        rm -rf /workspace/outputs
        ln -s /runpod-volume/outputs /workspace/outputs
        mkdir -p /runpod-volume/outputs
    fi
    
    # Link logs to network volume
    if [ ! -L "/workspace/logs" ]; then
        rm -rf /workspace/logs
        ln -s /runpod-volume/logs /workspace/logs
        mkdir -p /runpod-volume/logs
    fi
    
    print_status "Outputs and logs linked to network volume"
fi

# Test configuration
print_status "Testing configuration..."
if python3 config_minimal.py; then
    print_status "Configuration test passed"
else
    print_warning "Configuration test failed, but continuing..."
fi

# Check available disk space
DISK_SPACE=$(df /workspace --output=avail --block-size=1G | tail -1 | xargs)
print_status "Available disk space: ${DISK_SPACE}GB"

if [ "$DISK_SPACE" -lt 5 ]; then
    print_warning "Low disk space detected (${DISK_SPACE}GB). This may cause issues."
fi

# Print startup information
echo ""
echo "🎯 HunyuanVideo-Avatar Ready!"
echo "=============================="
echo "GPU Memory: ${GPU_MEMORY}MB"
echo "Image Size: ${IMAGE_SIZE}px"
echo "Model Base: $MODEL_BASE"
echo "Outputs: /workspace/outputs"
echo "Sample Input: test_input.csv"
echo ""

# Check if this is an interactive session or batch mode
if [ -t 0 ]; then
    # Interactive mode
    print_status "Interactive mode detected"
    echo "Available commands:"
    echo "  1. bash run_minimal.sh          - Ultra low VRAM mode"
    echo "  2. bash run_low_memory.sh       - Standard low memory mode"
    echo "  3. python3 -m hymm_sp.low_memory_inference --help - Manual mode"
    echo ""
    echo "To start generation, run one of the above commands"
    echo "or modify test_input.csv with your own inputs"
    echo ""
    
    # Keep container running
    exec /bin/bash
else
    # Batch mode - run automatic inference
    print_status "Batch mode detected - starting automatic inference"
    
    if [ -f "/workspace/inputs/input.csv" ]; then
        INPUT_FILE="/workspace/inputs/input.csv"
        print_status "Using custom input file: $INPUT_FILE"
    else
        INPUT_FILE="/workspace/test_input.csv"
        print_status "Using sample input file: $INPUT_FILE"
    fi
    
    # Run inference with appropriate settings
    python3 -m hymm_sp.low_memory_inference \
        --ckpt /workspace/weights \
        --input "$INPUT_FILE" \
        --save_path /workspace/outputs \
        --cpu_offload \
        --mixed_precision \
        --infer_min \
        --batch_size 1 \
        --image_size "$IMAGE_SIZE" \
        2>&1 | tee /workspace/logs/inference_$(date +%Y%m%d_%H%M%S).log
    
    print_status "Inference completed! Check /workspace/outputs for results"
fi 