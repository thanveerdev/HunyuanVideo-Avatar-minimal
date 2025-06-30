# HunyuanVideo-Avatar Docker Container for RunPod
# Optimized for single GPU deployment with model weights downloaded on first run

# Use GPU-optimized version that runs on 10GB VRAM instead of 80GB
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git wget curl \
    ffmpeg libsm6 libxext6 libxrender-dev \
    libgl1-mesa-glx libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124 && \
    pip3 install mmgp==3.4.9 && \
    pip3 install transformers diffusers accelerate && \
    pip3 install librosa soundfile && \
    pip3 install opencv-python-headless Pillow imageio && \
    pip3 install huggingface-hub[cli] loguru

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Flash Attention compilation environment
ENV FLASH_ATTENTION_FORCE_BUILD=TRUE
ENV FLASH_ATTENTION_FORCE_CUT=TRUE
ENV NVCC_PREPEND_FLAGS='--keep --keep-dir /tmp'
ENV TORCH_CUDA_ARCH_LIST="8.0"

# Official image should have all system dependencies
# RUN apt-get update && apt-get install -y <additional-packages> && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements first (for better Docker layer caching)
COPY requirements-minimal.txt requirements.txt ./

# Install project-specific dependencies (most dependencies already in base image)
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir huggingface-hub[cli]

# Copy application code
COPY hymm_sp/ ./hymm_sp/
COPY hymm_gradio/ ./hymm_gradio/
COPY assets/ ./assets/
COPY config_minimal.py ./
COPY *.sh ./
COPY README.md LICENSE ./

# Copy TorchVision compatibility fix files (essential only)
COPY apply_torchvision_fix.py ./
COPY fix_torchvision_compatibility.py ./
COPY fix_transformers_torchvision.py ./
COPY setup_auto_torchvision_fix.sh ./

# Create necessary directories
RUN mkdir -p /workspace/weights /workspace/outputs /workspace/logs /workspace/inputs

# Copy startup script and make it executable
COPY docker_startup.sh /workspace/
RUN chmod +x /workspace/docker_startup.sh
RUN chmod +x /workspace/*.sh

# Set environment variables for memory optimization
ENV MODEL_BASE=/workspace
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV CUDA_LAUNCH_BLOCKING=1
ENV OMP_NUM_THREADS=4
ENV PYTORCH_NO_CUDA_MEMORY_CACHING=1
ENV CUDA_CACHE_DISABLE=1

# RunPod specific environment
ENV RUNPOD_POD_ID=${RUNPOD_POD_ID:-""}
ENV RUNPOD_PUBLIC_IP=${RUNPOD_PUBLIC_IP:-""}

# Expose ports for web interface
EXPOSE 7860 8000 80

# Set startup command
CMD ["/workspace/docker_startup.sh"] 