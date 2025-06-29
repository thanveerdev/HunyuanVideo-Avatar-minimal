#!/bin/bash

# HunyuanVideo-Avatar Ultra-Low VRAM Mode
# Optimized for 4GB - 8GB VRAM GPUs with extreme memory conservation

set -e

echo "🚨 Ultra-Low VRAM Mode for HunyuanVideo-Avatar"
echo "=============================================="
echo "🎯 Target: 4GB - 8GB VRAM GPUs"
echo "⚙️  Mode: Maximum memory conservation"
echo ""

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

# Check if models exist
if [ ! -d "weights" ]; then
    print_error "Model weights not found!"
    print_info "Please download models first:"
    print_info "1. Check weights/README.md for download instructions"
    print_info "2. Or run in Docker with automatic model download"
    exit 1
fi

# Detect GPU and set ultra-aggressive optimizations
detect_gpu_and_optimize() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "4096")
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "Unknown GPU")
        GPU_FREE=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 || echo "2048")
        
        print_status "GPU: $GPU_NAME"
        print_status "VRAM: ${GPU_MEMORY}MB total, ${GPU_FREE}MB available"
        
        # Ultra-aggressive settings based on available VRAM
        if [ "$GPU_MEMORY" -lt 4096 ]; then
            print_error "Less than 4GB VRAM detected! This may not work."
            print_warning "Consider using CPU-only mode instead."
            export MODE="emergency"
            export IMAGE_SIZE=96
            export VIDEO_LENGTH=4
            export AUDIO_LENGTH=8
            export INFERENCE_STEPS=10
            export MEMORY_SPLIT=32
            
        elif [ "$GPU_MEMORY" -lt 6144 ]; then
            print_warning "4-6GB VRAM: Emergency ultra-minimal mode"
            export MODE="ultra_minimal"
            export IMAGE_SIZE=128
            export VIDEO_LENGTH=8
            export AUDIO_LENGTH=15
            export INFERENCE_STEPS=15
            export MEMORY_SPLIT=64
            
        elif [ "$GPU_MEMORY" -lt 8192 ]; then
            print_status "6-8GB VRAM: Ultra-low mode with quality balance"
            export MODE="ultra_low"
            export IMAGE_SIZE=256
            export VIDEO_LENGTH=16
            export AUDIO_LENGTH=20
            export INFERENCE_STEPS=20
            export MEMORY_SPLIT=128
            
        else
            print_status "8GB+ VRAM: Using optimized low mode"
            export MODE="low_optimized"
            export IMAGE_SIZE=384
            export VIDEO_LENGTH=32
            export AUDIO_LENGTH=30
            export INFERENCE_STEPS=25
            export MEMORY_SPLIT=256
        fi
        
    else
        print_error "No NVIDIA GPU detected!"
        print_warning "Falling back to CPU mode (extremely slow)"
        export MODE="cpu_only"
        export IMAGE_SIZE=96
        export VIDEO_LENGTH=4
        export AUDIO_LENGTH=8
        export INFERENCE_STEPS=8
        export MEMORY_SPLIT=64
    fi
}

# Set ultra-aggressive environment variables
setup_memory_optimizations() {
    # Core PyTorch optimizations
    export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:${MEMORY_SPLIT},garbage_collection_threshold:0.5,expandable_segments:True"
    export CUDA_LAUNCH_BLOCKING=1
    export PYTORCH_NO_CUDA_MEMORY_CACHING=1
    export CUDA_CACHE_DISABLE=1
    export PYTORCH_JIT=0
    
    # Reduce CPU usage to save memory
    export OMP_NUM_THREADS=1
    export MKL_NUM_THREADS=1
    export NUMBA_NUM_THREADS=1
    
    # Disable unnecessary features
    export TOKENIZERS_PARALLELISM=false
    export CUDA_MODULE_LOADING=LAZY
    export HF_DATASETS_OFFLINE=1
    export TRANSFORMERS_OFFLINE=1
    
    # Force memory efficient attention
    export XFORMERS_FLASH_ATTENTION=1
    
    print_status "Ultra-aggressive memory optimizations applied"
    print_info "Memory split: ${MEMORY_SPLIT}MB"
    print_info "CPU threads: 1"
    print_info "CUDA caching: Disabled"
}

# Create optimized input file
create_ultra_low_input() {
    local input_file="${1:-ultra_low_input.csv}"
    
    if [ ! -f "$input_file" ]; then
        print_info "Creating optimized input file: $input_file"
        echo "videoid,image,audio,prompt,fps" > "$input_file"
        
        # Find sample files
        local image_file="assets/image/1.png"
        local audio_file="assets/audio/2.WAV"
        
        if [ ! -f "$image_file" ]; then
            image_file=$(find . -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | head -1)
        fi
        
        if [ ! -f "$audio_file" ]; then
            audio_file=$(find . -name "*.wav" -o -name "*.mp3" | head -1)
        fi
        
        if [ -f "$image_file" ] && [ -f "$audio_file" ]; then
            echo "ultra_low_test,$image_file,$audio_file,A person speaking naturally,25" >> "$input_file"
            print_status "Input file created with sample data"
        else
            print_warning "Sample files not found. Please create $input_file manually."
            print_info "Format: videoid,image_path,audio_path,prompt,fps"
        fi
    fi
    
    echo "$input_file"
}

# Monitor memory usage during generation
monitor_memory() {
    if command -v nvidia-smi &> /dev/null; then
        while true; do
            sleep 5
            USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
            UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1)
            echo "🔍 [$(date '+%H:%M:%S')] VRAM: ${USED}MB, GPU: ${UTIL}%"
        done
    fi
}

# Main execution
main() {
    print_status "Starting ultra-low VRAM detection..."
    detect_gpu_and_optimize
    
    print_status "Applying memory optimizations..."
    setup_memory_optimizations
    
    # Set up directories
    export MODEL_BASE=$(pwd)
    mkdir -p outputs logs temp
    
    # Create input file
    INPUT_FILE=$(create_ultra_low_input)
    
    if [ ! -f "$INPUT_FILE" ]; then
        print_error "Input file not found: $INPUT_FILE"
        exit 1
    fi
    
    # Display configuration
    echo ""
    print_info "🔧 Ultra-Low VRAM Configuration:"
    print_info "   Mode: $MODE"
    print_info "   Image size: ${IMAGE_SIZE}px"
    print_info "   Video length: $VIDEO_LENGTH frames"
    print_info "   Audio length: ${AUDIO_LENGTH}s max"
    print_info "   Inference steps: $INFERENCE_STEPS"
    print_info "   Memory split: ${MEMORY_SPLIT}MB"
    print_info "   Input file: $INPUT_FILE"
    echo ""
    
    # Start memory monitoring in background
    monitor_memory &
    MONITOR_PID=$!
    
    # Cleanup function
    cleanup() {
        print_info "Cleaning up..."
        kill $MONITOR_PID 2>/dev/null || true
        # Force GPU memory cleanup
        python3 -c "
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print('GPU cache cleared')
" 2>/dev/null || true
        exit 0
    }
    
    trap cleanup SIGINT SIGTERM
    
    # Run the ultra-low memory inference
    print_status "Starting ultra-low VRAM inference..."
    print_warning "This may take longer due to aggressive memory optimizations"
    echo ""
    
    # Choose inference script based on availability
    if [ -f "hymm_sp/low_memory_inference.py" ]; then
        INFERENCE_SCRIPT="hymm_sp.low_memory_inference"
    else
        print_error "Low memory inference script not found!"
        print_info "Expected: hymm_sp/low_memory_inference.py"
        cleanup
        exit 1
    fi
    
    # Run inference with ultra-low settings
    python3 -m $INFERENCE_SCRIPT \
        --ckpt ./weights \
        --input "$INPUT_FILE" \
        --save_path ./outputs \
        --cpu_offload \
        --infer_min \
        --batch_size 1 \
        --image_size $IMAGE_SIZE \
        --mixed_precision \
        --save_path_suffix "ultra_low_vram" \
        --enable_sequential_cpu_offload \
        2>&1 | tee "logs/ultra_low_vram_$(date +%Y%m%d_%H%M%S).log"
    
    # Check results
    if [ $? -eq 0 ]; then
        echo ""
        print_status "🎉 Ultra-low VRAM generation completed successfully!"
        print_info "📁 Check outputs/ directory for results"
        print_info "📊 Final memory status:"
        nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader,nounits 2>/dev/null || true
        
        # Show generated files
        echo ""
        print_info "📺 Generated videos:"
        ls -la outputs/*ultra_low_vram* 2>/dev/null || print_warning "No output files found"
        
    else
        echo ""
        print_error "❌ Generation failed!"
        print_info "💡 Troubleshooting suggestions:"
        print_info "   • Reduce image size further (try 96px)"
        print_info "   • Use shorter audio clips (5-10 seconds)"
        print_info "   • Close other GPU applications"
        print_info "   • Try CPU-only mode if available"
        print_info "   • Check log file for detailed errors"
    fi
    
    cleanup
}

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Ultra-Low VRAM Mode for HunyuanVideo-Avatar"
    echo ""
    echo "Usage: $0 [input_file.csv]"
    echo ""
    echo "This script automatically detects your GPU and applies the most"
    echo "aggressive memory optimizations possible for 4GB-8GB VRAM cards."
    echo ""
    echo "Modes:"
    echo "  Emergency (≤4GB):     96px,  4 frames,  8s audio"
    echo "  Ultra-minimal (4-6GB): 128px, 8 frames, 15s audio"  
    echo "  Ultra-low (6-8GB):    256px, 16 frames, 20s audio"
    echo "  Low-optimized (8GB+): 384px, 32 frames, 30s audio"
    echo ""
    echo "Requirements:"
    echo "  • Model weights in ./weights/ directory"
    echo "  • Input CSV with: videoid,image,audio,prompt,fps"
    echo "  • NVIDIA GPU with 4GB+ VRAM (recommended)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use auto-generated input"
    echo "  $0 my_input.csv       # Use custom input file"
    echo ""
    exit 0
fi

# Run main function
main "$@" 