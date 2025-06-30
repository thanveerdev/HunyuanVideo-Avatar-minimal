# HunyuanVideo-Avatar Docker Container for RunPod
# Optimized for single GPU deployment with model weights downloaded on first run

FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

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

# Install system dependencies including ninja for flash_attn compilation
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavutil-dev \
    libavdevice-dev \
    libavfilter-dev \
    libpostproc-dev \
    build-essential \
    cmake \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements first (for better Docker layer caching)
COPY requirements-minimal.txt requirements.txt ./

# Install Python dependencies with optimized flash_attn installation
RUN pip3 install --no-cache-dir --upgrade pip --verbose && \
    pip3 install --no-cache-dir torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124 --verbose && \
    pip3 install --no-cache-dir packaging ninja --verbose && \
    (pip3 install --no-cache-dir flash-attn==2.6.3 --find-links https://flash-attention.s3.amazonaws.com/releases/ --verbose || \
     TORCH_CUDA_ARCH_LIST="8.0" MAX_JOBS=2 NVCC_THREADS=2 pip3 install --no-cache-dir flash-attn==2.6.3 --no-build-isolation --timeout 7200 --verbose) && \
    pip3 install --no-cache-dir -r requirements.txt --verbose && \
    pip3 install --no-cache-dir huggingface-hub[cli] --verbose

# Copy application code
COPY hymm_sp/ ./hymm_sp/
COPY hymm_gradio/ ./hymm_gradio/
COPY assets/ ./assets/
COPY config_minimal.py ./
COPY *.sh ./
COPY README.md LICENSE ./

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