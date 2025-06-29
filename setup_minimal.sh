#!/bin/bash

# HunyuanVideo-Avatar Minimal Setup Script
# Automated setup for low VRAM deployment

echo "🔧 HunyuanVideo-Avatar Minimal Setup"
echo "===================================="

# Check if running on supported OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ Linux detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS detected (limited GPU support)"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    echo "✅ Windows detected"
else
    echo "⚠️  Unknown OS: $OSTYPE"
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ "$python_version" < "3.8" ]]; then
    echo "❌ Python 3.8+ required, found: $python_version"
    exit 1
else
    echo "✅ Python $python_version detected"
fi

# Check CUDA availability
echo "🔍 Checking CUDA availability..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  NVIDIA GPU not detected - CPU-only mode"
fi

# Create virtual environment (optional)
read -p "🌐 Create virtual environment? (y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_minimal
    source venv_minimal/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install PyTorch first (GPU version if available)
echo "⚡ Installing PyTorch..."
if command -v nvidia-smi &> /dev/null; then
    # Install CUDA version
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    # Install CPU version
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install other requirements
echo "📦 Installing additional requirements..."
if [ -f "requirements-minimal.txt" ]; then
    pip install -r requirements-minimal.txt
elif [ -f "requirements.txt" ]; then
    echo "⚠️  Using standard requirements.txt"
    pip install -r requirements.txt
else
    echo "❌ No requirements file found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p outputs logs

# Set up environment variables
echo "🔧 Setting up environment..."
export MODEL_BASE=$(pwd)
export CUDA_VISIBLE_DEVICES=0

# Create sample input if assets exist
if [ -d "assets" ]; then
    echo "📝 Creating sample input file..."
    echo "videoid,image,audio,prompt,fps" > test_input.csv
    
    # Find first available image and audio
    image_file=$(find assets/image -name "*.png" -o -name "*.jpg" | head -1)
    audio_file=$(find assets/audio -name "*.wav" -o -name "*.WAV" | head -1)
    
    if [ -n "$image_file" ] && [ -n "$audio_file" ]; then
        echo "test1,$image_file,$audio_file,A person speaking naturally,25" >> test_input.csv
        echo "✅ Sample input created with: $image_file, $audio_file"
    else
        echo "⚠️  No sample assets found in assets/ directory"
    fi
fi

# Test GPU memory
echo "🧪 Testing GPU configuration..."
python3 -c "
import torch
if torch.cuda.is_available():
    print(f'✅ CUDA available: {torch.cuda.get_device_name(0)}')
    print(f'📊 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
    
    # Test memory allocation
    try:
        test_tensor = torch.randn(1000, 1000, device='cuda')
        del test_tensor
        torch.cuda.empty_cache()
        print('✅ GPU memory test passed')
    except Exception as e:
        print(f'⚠️  GPU memory test failed: {e}')
else:
    print('❌ CUDA not available - running on CPU')
"

# Check if weights directory exists
if [ ! -d "weights" ] || [ -z "$(ls -A weights)" ]; then
    echo ""
    echo "📥 MODEL WEIGHTS REQUIRED:"
    echo "   The weights/ directory is empty or missing."
    echo "   Please download the model weights:"
    echo "   1. See weights/README.md for download instructions"
    echo "   2. Or run: bash download_models.sh (if available)"
    echo ""
    echo "   Required files:"
    echo "   - HunyuanVideo transformer model"
    echo "   - VAE model"
    echo "   - Text encoders"
    echo "   - Whisper model (whisper-tiny)"
    echo "   - Face detection model"
fi

# Create configuration test
echo "⚙️  Testing configuration..."
python3 config_minimal.py

echo ""
echo "🎉 Setup completed!"
echo "=================================="
echo "📋 Next steps:"
echo "   1. Download model weights (see above)"
echo "   2. Run: bash run_minimal.sh"
echo "   3. Check outputs/ directory for results"
echo ""
echo "💡 For low VRAM issues:"
echo "   - Reduce --image_size to 128 or 256"
echo "   - Enable --cpu_offload"
echo "   - Monitor GPU memory: nvidia-smi -l 1"
echo ""
echo "🏁 Ready for minimal VRAM inference!" 