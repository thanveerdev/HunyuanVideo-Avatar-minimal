#!/bin/bash

# HunyuanVideo-Avatar Web Demo Startup Script
# Universal VRAM Support: 4GB to 24GB+ with automatic optimization

set -e

echo "🌐 Starting HunyuanVideo-Avatar Web Interface..."
echo "=============================================="

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

# Check if we're in the correct directory
if [ ! -d "hymm_gradio" ]; then
    print_error "hymm_gradio directory not found. Please run from project root."
    exit 1
fi

# Check if models are available
if [ ! -f "/workspace/weights/.models_downloaded" ] && [ ! -d "weights/ckpts" ]; then
    print_warning "Models not found. Web interface may not work properly."
    print_warning "Make sure to download models first or run the container with model download."
fi

# Set environment variables
export MODEL_BASE=${MODEL_BASE:-$(pwd)}
export PYTHONPATH=./

# Advanced GPU memory detection and optimization
detect_and_optimize_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "4096")
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "Unknown GPU")
        GPU_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "0")
        GPU_FREE=$((GPU_MEMORY - GPU_USED))
        
        print_status "GPU: $GPU_NAME"
        print_status "VRAM: ${GPU_MEMORY}MB total, ${GPU_FREE}MB available"
        
        # Ultra-comprehensive VRAM optimization
        if [ "$GPU_MEMORY" -lt 6144 ]; then
            # 4-6GB VRAM: Ultra-minimal mode
            export VRAM_MODE="ultra_minimal"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:64,garbage_collection_threshold:0.5,expandable_segments:True"
            export IMAGE_SIZE=128
            export VIDEO_LENGTH=8
            export BATCH_SIZE=1
            export INFERENCE_STEPS=15
            export ENABLE_8BIT=true
            export CPU_OFFLOAD=true
            export MIXED_PRECISION=true
            export INFER_MIN=true
            export VAE_SLICE_SIZE=1
            export ATTENTION_SLICE_SIZE=1
            print_warning "Ultra-minimal mode (4-6GB): Extreme optimizations enabled"
            
        elif [ "$GPU_MEMORY" -lt 8192 ]; then
            # 6-8GB VRAM: Ultra-low mode
            export VRAM_MODE="ultra_low"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:128,garbage_collection_threshold:0.6,expandable_segments:True"
            export IMAGE_SIZE=256
            export VIDEO_LENGTH=16
            export BATCH_SIZE=1
            export INFERENCE_STEPS=20
            export ENABLE_8BIT=false
            export CPU_OFFLOAD=true
            export MIXED_PRECISION=true
            export INFER_MIN=true
            export VAE_SLICE_SIZE=2
            export ATTENTION_SLICE_SIZE=2
            print_status "Ultra-low VRAM mode (6-8GB): Aggressive optimizations enabled"
            
        elif [ "$GPU_MEMORY" -lt 12288 ]; then
            # 8-12GB VRAM: Low mode
            export VRAM_MODE="low"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:256,garbage_collection_threshold:0.7,expandable_segments:True"
            export IMAGE_SIZE=384
            export VIDEO_LENGTH=32
            export BATCH_SIZE=1
            export INFERENCE_STEPS=25
            export CPU_OFFLOAD=true
            export MIXED_PRECISION=true
            export INFER_MIN=false
            export VAE_SLICE_SIZE=4
            export ATTENTION_SLICE_SIZE=4
            print_status "Low VRAM mode (8-12GB): Balanced optimizations enabled"
            
        elif [ "$GPU_MEMORY" -lt 16384 ]; then
            # 12-16GB VRAM: Balanced mode
            export VRAM_MODE="balanced"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512,garbage_collection_threshold:0.8"
            export IMAGE_SIZE=512
            export VIDEO_LENGTH=64
            export BATCH_SIZE=2
            export INFERENCE_STEPS=30
            export CPU_OFFLOAD=false
            export MIXED_PRECISION=true
            export INFER_MIN=false
            export VAE_SLICE_SIZE=8
            export ATTENTION_SLICE_SIZE=8
            print_status "Balanced mode (12-16GB): Standard optimizations enabled"
            
        elif [ "$GPU_MEMORY" -lt 24576 ]; then
            # 16-24GB VRAM: High performance mode
            export VRAM_MODE="high_performance"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024,garbage_collection_threshold:0.9"
            export IMAGE_SIZE=704
            export VIDEO_LENGTH=128
            export BATCH_SIZE=2
            export INFERENCE_STEPS=35
            export CPU_OFFLOAD=false
            export MIXED_PRECISION=true
            export INFER_MIN=false
            export VAE_SLICE_SIZE=16
            export ATTENTION_SLICE_SIZE=16
            print_status "High performance mode (16-24GB): Enhanced quality enabled"
            
        else
            # 24GB+ VRAM: Maximum quality mode
            export VRAM_MODE="maximum_quality"
            export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:2048,garbage_collection_threshold:0.95"
            export IMAGE_SIZE=1024
            export VIDEO_LENGTH=256
            export BATCH_SIZE=4
            export INFERENCE_STEPS=50
            export CPU_OFFLOAD=false
            export MIXED_PRECISION=false
            export INFER_MIN=false
            export VAE_SLICE_SIZE=32
            export ATTENTION_SLICE_SIZE=32
            print_status "Maximum quality mode (24GB+): Full precision and quality enabled"
        fi
        
        # Additional optimizations for all modes
        export OMP_NUM_THREADS=4
        export CUDA_LAUNCH_BLOCKING=1
        export TOKENIZERS_PARALLELISM=false
        export CUDA_MODULE_LOADING=LAZY
        
        # Ultra-low VRAM specific optimizations
        if [ "$VRAM_MODE" = "ultra_minimal" ] || [ "$VRAM_MODE" = "ultra_low" ]; then
            export PYTORCH_NO_CUDA_MEMORY_CACHING=1
            export CUDA_CACHE_DISABLE=1
            export PYTORCH_JIT=0
            export OMP_NUM_THREADS=2
            print_info "Ultra-low VRAM optimizations applied"
        fi
        
    else
        print_error "NVIDIA GPU not detected!"
        print_warning "Falling back to CPU mode (will be very slow)"
        export VRAM_MODE="cpu_only"
        export IMAGE_SIZE=128
        export VIDEO_LENGTH=8
        export BATCH_SIZE=1
        export INFERENCE_STEPS=10
        export CPU_OFFLOAD=true
        export MIXED_PRECISION=false
    fi
}

# Run GPU detection and optimization
detect_and_optimize_gpu

# Create necessary directories
mkdir -p temp logs outputs

# Function to cleanup background processes
cleanup() {
    print_info "Cleaning up background processes..."
    if [ ! -z "$FASTAPI_PID" ]; then
        kill $FASTAPI_PID 2>/dev/null || true
    fi
    if [ ! -z "$GRADIO_PID" ]; then
        kill $GRADIO_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if ports are available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port is already in use"
        return 1
    fi
    return 0
}

# Find available ports
GRADIO_PORT=7860
FASTAPI_PORT=80

if ! check_port $GRADIO_PORT; then
    GRADIO_PORT=7861
    print_info "Using alternative Gradio port: $GRADIO_PORT"
fi

if ! check_port $FASTAPI_PORT; then
    FASTAPI_PORT=8000
    print_info "Using alternative FastAPI port: $FASTAPI_PORT"
fi

export GRADIO_PORT
export FASTAPI_PORT

# Display configuration summary
print_info "Configuration Summary:"
print_info "  VRAM Mode: $VRAM_MODE"
print_info "  Image Size: ${IMAGE_SIZE}px"
print_info "  Video Length: $VIDEO_LENGTH frames"
print_info "  Batch Size: $BATCH_SIZE"
print_info "  CPU Offload: $CPU_OFFLOAD"
print_info "  Mixed Precision: $MIXED_PRECISION"
print_info "  Gradio Port: $GRADIO_PORT"
print_info "  FastAPI Port: $FASTAPI_PORT"

# Start FastAPI backend
print_status "Starting FastAPI backend server..."
cd hymm_gradio
python -m uvicorn fastapi_server:app --host 0.0.0.0 --port $FASTAPI_PORT --log-level warning &
FASTAPI_PID=$!
cd ..

# Wait for FastAPI to start
sleep 3

# Check if FastAPI started successfully
if ! kill -0 $FASTAPI_PID 2>/dev/null; then
    print_error "FastAPI server failed to start"
    exit 1
fi

print_status "FastAPI server started (PID: $FASTAPI_PID)"

# Start Gradio frontend
print_status "Starting Gradio web interface..."

# Create environment variables for Gradio
export ENABLE_QUEUE=true
export GRADIO_CONCURRENCY_COUNT=1
export GRADIO_MAX_THREADS=2

# Ultra-low VRAM specific Gradio settings
if [ "$VRAM_MODE" = "ultra_minimal" ] || [ "$VRAM_MODE" = "ultra_low" ]; then
    export GRADIO_CONCURRENCY_COUNT=1
    export GRADIO_MAX_THREADS=1
    export GRADIO_QUEUE_MAX_SIZE=2
    print_info "Ultra-low VRAM Gradio settings applied"
fi

# Start Gradio with memory monitoring
python -c "
import os
import sys
sys.path.append('hymm_gradio')
sys.path.append('.')

# Import memory optimization
from config_minimal import apply_memory_optimizations, print_memory_info

# Apply optimizations
apply_memory_optimizations()
print('🔧 Memory optimizations applied')

# Print initial memory status
print_memory_info()

# Import and run Gradio
from web_demo import create_demo
demo = create_demo()

print('🌐 Starting Gradio interface...')
print(f'🔗 Local URL: http://localhost:$GRADIO_PORT')
print(f'🔗 FastAPI: http://localhost:$FASTAPI_PORT')
print('')
print('📊 VRAM Mode: $VRAM_MODE')
print('⚙️  Configuration: ${IMAGE_SIZE}px, ${VIDEO_LENGTH}f, batch=${BATCH_SIZE}')
print('')
print('🎯 Ready for avatar generation!')
print('📝 Upload an image and audio file to get started.')
print('')

# Launch with optimal settings
demo.launch(
    server_name='0.0.0.0',
    server_port=$GRADIO_PORT,
    share=False,
    debug=False,
    show_error=True,
    quiet=False,
    enable_queue=True,
    max_threads=int(os.environ.get('GRADIO_MAX_THREADS', 2)),
    auth=None,
    favicon_path=None,
    ssl_keyfile=None,
    ssl_certfile=None,
    ssl_keyfile_password=None,
    prevent_thread_lock=False
)
" &

GRADIO_PID=$!

# Wait for Gradio to start
sleep 5

# Check if Gradio started successfully
if ! kill -0 $GRADIO_PID 2>/dev/null; then
    print_error "Gradio interface failed to start"
    cleanup
    exit 1
fi

print_status "Gradio interface started (PID: $GRADIO_PID)"

# Display access information
echo ""
echo "🎉 HunyuanVideo-Avatar Web Interface is Ready!"
echo "================================================"
echo ""
echo "🌐 Access URLs:"
echo "   Local:    http://localhost:$GRADIO_PORT"
echo "   FastAPI:  http://localhost:$FASTAPI_PORT"
echo ""
echo "📊 System Configuration:"
echo "   VRAM Mode: $VRAM_MODE"
echo "   Image Size: ${IMAGE_SIZE}px"
echo "   Video Length: $VIDEO_LENGTH frames"
echo "   Batch Size: $BATCH_SIZE"
echo ""
echo "🎯 Usage Instructions:"
echo "   1. Open the web interface in your browser"
echo "   2. Upload a reference image (face photo)"
echo "   3. Upload an audio file (speech/voice)"
echo "   4. Enter a text prompt (optional)"
echo "   5. Click 'Generate Avatar Video'"
echo "   6. Download the generated MP4 video"
echo ""
echo "💡 Tips for Best Results:"
echo "   • Use clear, front-facing face photos"
echo "   • Audio should be clear speech (16kHz WAV preferred)"
echo "   • Keep audio under 30 seconds for faster processing"
echo "   • Text prompts help guide the generation"
echo ""

# Memory monitoring in background
monitor_memory() {
    while true; do
        sleep 30
        if command -v nvidia-smi &> /dev/null; then
            GPU_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "0")
            GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "0")
            echo "📊 [$(date '+%H:%M:%S')] GPU: ${GPU_USED}MB VRAM, ${GPU_UTIL}% utilization"
        fi
    done
}

# Start memory monitoring in background
monitor_memory &
MONITOR_PID=$!

# Wait for processes and handle cleanup
wait_for_processes() {
    while true; do
        if ! kill -0 $FASTAPI_PID 2>/dev/null; then
            print_error "FastAPI server stopped unexpectedly"
            break
        fi
        if ! kill -0 $GRADIO_PID 2>/dev/null; then
            print_error "Gradio interface stopped unexpectedly"
            break
        fi
        sleep 5
    done
}

# Keep the script running
print_status "Web interface running... Press Ctrl+C to stop"
wait_for_processes

# Cleanup
kill $MONITOR_PID 2>/dev/null || true
cleanup 