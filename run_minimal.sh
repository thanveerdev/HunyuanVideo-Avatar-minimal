#!/bin/bash

# HunyuanVideo-Avatar Minimal Launch Script
# Optimized for lowest VRAM usage on single GPU

echo "🚀 Starting HunyuanVideo-Avatar (Minimal VRAM Mode)"
echo "=================================================="

# Set environment variables for memory optimization
export MODEL_BASE=$(pwd)
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_LAUNCH_BLOCKING=1
export OMP_NUM_THREADS=4

# Memory optimization settings
export PYTORCH_NO_CUDA_MEMORY_CACHING=1
export CUDA_CACHE_DISABLE=1

echo "✅ Environment configured for low VRAM usage"
echo "📊 GPU Memory settings: max_split_size_mb=512"
echo "🔧 Using single GPU: $CUDA_VISIBLE_DEVICES"

# Check if models exist
if [ ! -d "weights" ]; then
    echo "❌ Error: weights/ directory not found"
    echo "📥 Please download models first (see weights/README.md)"
    exit 1
fi

# Create sample input if it doesn't exist
if [ ! -f "test_input.csv" ]; then
    echo "📝 Creating sample input file..."
    echo "videoid,image,audio,prompt,fps" > test_input.csv
    echo "test1,assets/image/1.png,assets/audio/2.WAV,A person speaking naturally,25" >> test_input.csv
    echo "✅ Created test_input.csv"
fi

# Create output directory
mkdir -p outputs
echo "📁 Output directory: ./outputs"

# Check available GPU memory
echo "🔍 Checking GPU status..."
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits

echo ""
echo "🎬 Starting video generation..."
echo "⚙️  Configuration: Ultra Low VRAM Mode"
echo "   - Image size: 256px"
echo "   - CPU offloading: Enabled"
echo "   - Mixed precision: FP16"
echo "   - Batch size: 1"
echo "   - Minimal inference: Enabled"
echo ""

# Run the minimal inference
python -m hymm_sp.low_memory_inference \
    --ckpt ./weights \
    --input ./test_input.csv \
    --save_path ./outputs \
    --cpu_offload \
    --infer_min \
    --batch_size 1 \
    --image_size 256 \
    --mixed_precision \
    --save_path_suffix "minimal" \
    --enable_sequential_cpu_offload \
    2>&1 | tee logs/minimal_run_$(date +%Y%m%d_%H%M%S).log

# Check if generation was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Video generation completed successfully!"
    echo "📁 Check outputs/ directory for results"
    echo "📊 Final GPU memory status:"
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader,nounits
else
    echo ""
    echo "❌ Video generation failed"
    echo "💡 Try reducing --image_size to 128 or check GPU memory"
    echo "🔧 For troubleshooting, see README.md"
fi

echo ""
echo "🏁 Minimal VRAM run completed" 