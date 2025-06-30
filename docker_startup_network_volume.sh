#!/bin/bash

# HunyuanVideo Avatar Docker Startup Script with Network Volume Support
# This script sets up the environment and initializes the network volume for persistent storage

set -e

echo "🚀 Starting HunyuanVideo Avatar with 'videostore' Network Volume Support..."

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

# Create symbolic links for backward compatibility
echo "🔗 Creating symbolic links..."
if [ ! -L "/workspace/outputs" ]; then
    ln -sf /network_volume/outputs /workspace/outputs
fi

# Set environment variables for network volume
export OUTPUT_BASE="/network_volume/outputs"
export PERSISTENT_STORAGE="/network_volume"
export CACHE_DIR="/network_volume/cache"
export LOG_DIR="/network_volume/logs"

# Log startup information to network volume
echo "📝 Logging startup info to network volume..."
{
    echo "=== HunyuanVideo Avatar Startup - $(date) ==="
    echo "Network Volume Path: /network_volume"
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
🎉 Welcome to HunyuanVideo Avatar 'videostore' Network Volume!

This directory is persistent across pod restarts and contains all your generated videos.

Directory Structure:
├── videos/          - Generated avatar videos (.mp4)
├── audio/           - Processed audio files
├── temp/           - Temporary processing files (auto-cleaned)
└── README.txt      - This file

File Organization:
- Videos are saved with timestamps: YYYYMMDD_HHMMSS_video.mp4
- Audio files follow the same pattern: YYYYMMDD_HHMMSS_audio.wav
- Each generation creates a folder with all related files

Storage Capacity: 10GB
Current Usage: $(du -sh /network_volume/outputs | cut -f1)

Generated on: $(date)
Pod ID: ${RUNPOD_POD_ID:-"local"}
EOF

# Memory optimization setup
echo "🧠 Setting up memory optimizations..."
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256,garbage_collection_threshold:0.6,expandable_segments:True"
export CUDA_LAUNCH_BLOCKING=1
export OMP_NUM_THREADS=4
export TOKENIZERS_PARALLELISM=false
export CUDA_MODULE_LOADING=LAZY

# Auto-detect VRAM and set optimal configuration
echo "🔍 Detecting GPU configuration..."
if command -v nvidia-smi &> /dev/null; then
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    
    echo "🎮 Detected GPU: $GPU_NAME"
    echo "💾 GPU Memory: ${GPU_MEMORY}MB"
    
    # Set VRAM mode based on detected memory
    if [ "$GPU_MEMORY" -le 6144 ]; then
        export VRAM_MODE="ultra_minimal"
        echo "⚡ Using Ultra-Minimal mode (≤6GB VRAM)"
    elif [ "$GPU_MEMORY" -le 8192 ]; then
        export VRAM_MODE="ultra_low"
        echo "⚡ Using Ultra-Low mode (6-8GB VRAM)"
    elif [ "$GPU_MEMORY" -le 12288 ]; then
        export VRAM_MODE="low"
        echo "⚡ Using Low mode (8-12GB VRAM)"
    elif [ "$GPU_MEMORY" -le 16384 ]; then
        export VRAM_MODE="balanced"
        echo "⚡ Using Balanced mode (12-16GB VRAM)"
    else
        export VRAM_MODE="high"
        echo "⚡ Using High Performance mode (16GB+ VRAM)"
    fi
else
    echo "⚠️  No GPU detected, using CPU fallback"
    export VRAM_MODE="ultra_minimal"
fi

# Apply comprehensive deep TorchVision fix
echo "🔧 Applying comprehensive deep TorchVision and Gradio compatibility fix..."
cd /workspace

# Run the deep fix that handles all import issues at the library level
if python3 fix_deep_torchvision_import.py; then
    echo "✅ Deep TorchVision and Gradio compatibility fix applied successfully"
else
    echo "⚠️  Deep fix had issues, falling back to individual fixes..."
    
    # Fallback to individual fixes
    if python3 fix_transformers_torchvision.py; then
        echo "✅ Fallback transformers fix applied"
    fi
    
    if python3 apply_torchvision_fix.py; then
        echo "✅ Fallback environment fix applied"
    fi
fi

# Fix Python path for imports
echo "🔧 Setting up Python environment..."
export PYTHONPATH="/workspace:${PYTHONPATH}"

# Start the application based on RUN_MODE
echo "🌐 Starting application..."
case "${RUN_MODE:-web}" in
    "web")
        echo "Starting Web Interface on port 7860..."
        python hymm_gradio/web_demo.py &
        
        echo "Starting FastAPI Server on port 80..."
        python -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80 &
        
        # Keep the container running
        wait
        ;;
    "api")
        echo "Starting FastAPI Server only..."
        python -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80
        ;;
    "minimal")
        echo "Starting minimal inference mode..."
        bash run_minimal.sh
        ;;
    *)
        echo "Unknown RUN_MODE: ${RUN_MODE}. Starting web interface..."
        python hymm_gradio/web_demo.py &
        python -m uvicorn hymm_gradio.fastapi_server:app --host 0.0.0.0 --port 80 &
        wait
        ;;
esac

echo "🎉 HunyuanVideo Avatar startup complete!" 