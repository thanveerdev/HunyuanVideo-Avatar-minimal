#!/bin/bash

# FastAPI Server Startup Script for HunyuanVideo-Avatar
# Initializes models and starts the backend API server

set -e

echo "🔌 Starting HunyuanVideo-Avatar FastAPI Server..."
echo "================================================"

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

# Check if models are available
if [ ! -f "/workspace/weights/.models_downloaded" ] && [ ! -d "weights/ckpts" ]; then
    print_error "Models not found! FastAPI server requires models to be downloaded."
    print_error "Please run the container with model download first."
    exit 1
fi

# Set environment variables
export MODEL_BASE=${MODEL_BASE:-$(pwd)}
export PYTHONPATH=./

# GPU memory optimization
GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "8192")
if [ "$GPU_MEMORY" -lt 8192 ]; then
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256"
    export IMAGE_SIZE=256
elif [ "$GPU_MEMORY" -lt 12288 ]; then
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
    export IMAGE_SIZE=384
else
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024"
    export IMAGE_SIZE=512
fi

print_status "GPU Memory: ${GPU_MEMORY}MB (${IMAGE_SIZE}px mode)"

# Create temp directory
mkdir -p temp

print_status "Initializing FastAPI server with model loading..."
print_warning "This may take 2-5 minutes depending on GPU and models..."

# Start the FastAPI server
python3 hymm_gradio/fastapi_server.py 