#!/bin/bash

# HunyuanVideo Avatar Docker Startup Script for Root Mount
# Container disk mounted at / with network volume at /network_volume

set -e

echo "🚀 Starting HunyuanVideo Avatar (Root Mount + Network Volume)..."
echo "================================================================"

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

print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

# Set working directory to root where application files are mounted
cd /

# Create network volume directories if they don't exist
echo "📁 Setting up network volume directories..."
mkdir -p /network_volume/outputs
mkdir -p /network_volume/outputs/videos
mkdir -p /network_volume/outputs/audio
mkdir -p /network_volume/outputs/temp
mkdir -p /network_volume/logs
mkdir -p /network_volume/cache

# Set proper permissions for network volume
echo "🔧 Setting network volume permissions..."
chmod -R 755 /network_volume
chown -R root:root /network_volume

# Create symbolic links for outputs to network volume
echo "🔗 Creating symbolic links..."
if [ ! -L "/outputs" ]; then
    ln -sf /network_volume/outputs /outputs
fi

# Set environment variables for network volume
export OUTPUT_BASE="/network_volume/outputs"
export PERSISTENT_STORAGE="/network_volume"
export CACHE_DIR="/network_volume/cache"
export LOG_DIR="/network_volume/logs"

# Apply TorchVision compatibility fix automatically
print_status "Applying TorchVision compatibility fix..."
if python3 apply_torchvision_fix.py; then
    print_status "TorchVision compatibility fix applied successfully"
else
    print_warning "TorchVision fix had issues, but continuing with fallback mode"
fi

# Check GPU and set optimizations
print_status "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    
    print_status "GPU: $GPU_NAME"
    print_status "VRAM: ${GPU_MEMORY}MB"
    
    # Set VRAM mode based on detected memory
    if [ "$GPU_MEMORY" -le 6144 ]; then
        export VRAM_MODE="ultra_minimal"
        print_status "Using Ultra-Minimal mode (≤6GB VRAM)"
    elif [ "$GPU_MEMORY" -le 8192 ]; then
        export VRAM_MODE="ultra_low"
        print_status "Using Ultra-Low mode (6-8GB VRAM)"
    elif [ "$GPU_MEMORY" -le 12288 ]; then
        export VRAM_MODE="low"
        print_status "Using Low mode (8-12GB VRAM)"
    elif [ "$GPU_MEMORY" -le 16384 ]; then
        export VRAM_MODE="balanced"
        print_status "Using Balanced mode (12-16GB VRAM)"
    else
        export VRAM_MODE="high"
        print_status "Using High Performance mode (16GB+ VRAM)"
    fi
else
    print_warning "No GPU detected, using CPU fallback"
    export VRAM_MODE="ultra_minimal"
fi

# Memory optimization setup
print_status "Setting up memory optimizations..."
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256,garbage_collection_threshold:0.6,expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=1
export OMP_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false
export CUDA_MODULE_LOADING=LAZY

# Fix Python path for root mount
print_status "Setting up Python environment..."
export PYTHONPATH="/:${PYTHONPATH}"

# Log startup information to network volume
print_status "Logging startup info to network volume..."
{
    echo "=== HunyuanVideo Avatar Startup - $(date) ==="
    echo "Mount Configuration: Root (/) + Network Volume (/network_volume)"
    echo "Output Directory: $OUTPUT_BASE"
    echo "Cache Directory: $CACHE_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "GPU Info:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits || echo "No GPU detected"
    echo "Disk Space:"
    df -h /network_volume
    echo "================================"
} >> /network_volume/logs/startup.log

# Create a welcome message in the outputs directory
cat > /network_volume/outputs/README.txt << EOF
🎉 Welcome to HunyuanVideo Avatar (Root Mount Configuration)!

This directory is persistent across pod restarts and contains all your generated videos.

Mount Configuration:
- Container Disk (100GB): Mounted at / (root filesystem)
- Network Volume (10GB): Mounted at /network_volume (persistent storage)

Directory Structure:
├── videos/          - Generated avatar videos (.mp4)
├── audio/           - Processed audio files
├── temp/           - Temporary processing files (auto-cleaned)
└── README.txt      - This file

File Organization:
- Videos are saved with timestamps: YYYYMMDD_HHMMSS_video.mp4
- Audio files follow the same pattern: YYYYMMDD_HHMMSS_audio.wav
- Each generation creates a folder with all related files

Storage Usage:
- Container Disk: Models, application files, temporary processing
- Network Volume: Generated outputs, logs, cache (persistent)

Current Usage: $(du -sh /network_volume/outputs | cut -f1)

Generated on: $(date)
Pod ID: ${RUNPOD_POD_ID:-"local"}
EOF

print_status "Starting application..."

# Start the application based on RUN_MODE
case "${RUN_MODE:-web}" in
    "web")
        print_status "Starting Web Interface on port 7860..."
        python3 hymm_gradio/web_demo.py &
        
        print_status "Starting FastAPI Server on port 80..."
        python3 -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80 &
        
        # Keep the container running
        wait
        ;;
    "api")
        print_status "Starting FastAPI Server only..."
        python3 -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80
        ;;
    "minimal")
        print_status "Starting minimal inference mode..."
        bash run_minimal.sh
        ;;
    *)
        print_status "Unknown RUN_MODE: ${RUN_MODE}. Starting web interface..."
        python3 hymm_gradio/web_demo.py &
        python3 -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80 &
        wait
        ;;
esac

print_status "🎉 HunyuanVideo Avatar startup complete!" 