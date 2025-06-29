# 🌐 HunyuanVideo-Avatar Web Interface Guide

This guide covers how to use the **Gradio Web Interface** for HunyuanVideo-Avatar, making it easy to create avatar videos through a browser.

## 🎯 Overview

The web interface provides:
- **User-friendly UI**: Upload images and audio through your browser
- **Real-time processing**: Monitor generation progress
- **Automatic optimization**: GPU memory management based on your hardware
- **Instant results**: View generated videos directly in the browser

## 🚀 Quick Start

### Option 1: Docker with Web Interface
```bash
# Build the Docker image
docker build -t hunyuan-avatar .

# Run with web interface
docker run --rm -it --gpus all \
  -p 7860:7860 -p 80:80 \
  -e RUN_MODE=web \
  hunyuan-avatar
```

### Option 2: Docker Compose
```bash
# Start with web interface enabled
docker-compose up --build

# Access at: http://localhost:7860
```

### Option 3: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start web interface
bash run_web_demo.sh
```

## 🌐 Web Interface Components

### 1. Gradio Frontend (Port 7860)
- **Upload interface**: Drag and drop files
- **Parameter controls**: Adjust generation settings
- **Progress monitoring**: Real-time generation status
- **Result display**: Video playback and download

### 2. FastAPI Backend (Port 80)
- **Model inference**: Core video generation
- **API endpoints**: RESTful interface
- **Memory management**: GPU optimization
- **Error handling**: Graceful failure recovery

## 🎛️ Using the Interface

### Step 1: Access the Web UI
Open your browser and go to:
- **Local**: `http://localhost:7860`
- **RunPod**: `https://[pod-id]-7860.proxy.runpod.net`
- **Remote**: `http://[server-ip]:7860`

### Step 2: Upload Your Content
1. **Reference Image**: 
   - Upload a clear photo of a person's face
   - Supported formats: PNG, JPG, JPEG
   - Recommended size: 512x512 to 1024x1024

2. **Audio File**:
   - Upload speech audio to sync with
   - Supported formats: WAV, MP3
   - Recommended: 16kHz, mono, < 30 seconds

3. **Text Prompt** (Optional):
   - Describe the desired video style
   - Example: "A person speaking naturally"

### Step 3: Generate Video
1. Click the **"Generate"** button
2. Wait for processing (30-120 seconds depending on GPU)
3. View the result in the output panel
4. Download the generated MP4 file

## ⚙️ Configuration Options

### GPU Memory Modes
The system automatically detects your GPU and optimizes settings:

| GPU Memory | Mode | Quality | Speed |
|------------|------|---------|-------|
| < 8GB | Ultra-low VRAM | 256px | Fast |
| 8-12GB | Low VRAM | 384px | Balanced |
| > 12GB | Balanced | 512px | High Quality |

### Manual Override
Set environment variables to force specific settings:
```bash
export IMAGE_SIZE=256  # Force lower resolution
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256  # Aggressive memory saving
```

## 🔧 Architecture

```
Browser --> Gradio (7860) --> FastAPI (80) --> AI Models --> GPU
    ^                                                        |
    |                                                        |
    +-- Generated Video <-- Base64 Encoding <-- Video Output
```

### Data Flow:
1. **User uploads** image + audio via Gradio
2. **Gradio encodes** files to base64 and sends to FastAPI
3. **FastAPI processes** data and initializes AI models
4. **AI pipeline** generates video using GPU
5. **Result encoded** to base64 and returned to Gradio
6. **Browser displays** the generated video

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Connection Refused" Error
```bash
# Check if FastAPI is running
curl http://localhost:80/docs

# Restart FastAPI server
pkill -f fastapi_server
bash run_fastapi_server.sh &
```

#### 2. "CUDA Out of Memory"
```bash
# Reduce image size
export IMAGE_SIZE=128

# Enable aggressive memory saving
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

#### 3. "Models Not Found"
```bash
# Check if models are downloaded
ls -la /workspace/weights/ckpts/

# Download models manually
cd /workspace/weights
huggingface-cli download tencent/HunyuanVideo-Avatar --local-dir ./
```

#### 4. Web Interface Not Loading
```bash
# Check Gradio process
ps aux | grep gradio

# Check port availability
netstat -tulpn | grep 7860

# Restart web interface
bash run_web_demo.sh
```

### Advanced Debugging

#### View Logs
```bash
# FastAPI logs
tail -f /workspace/logs/fastapi_*.log

# Gradio logs
tail -f /workspace/logs/gradio_*.log

# GPU monitoring
nvidia-smi -l 1
```

#### Test API Directly
```bash
# Test FastAPI health
curl -X GET http://localhost:80/docs

# Test inference endpoint
curl -X POST http://localhost:80/predict2 \
  -H "Content-Type: application/json" \
  -d '{"image_buffer": "base64_data", "audio_buffer": "base64_data", "text": "test"}'
```

## 🌟 Features

### Current Capabilities
- ✅ **Face animation**: Realistic lip-sync with audio
- ✅ **Quality control**: Automatic resolution adjustment
- ✅ **Memory optimization**: Works on 6-8GB GPUs
- ✅ **Format support**: Multiple image/audio formats
- ✅ **Real-time preview**: Browser-based interface

### Planned Features
- 🔄 **Batch processing**: Multiple videos at once
- 🔄 **Style transfer**: Different animation styles
- 🔄 **Voice cloning**: Custom voice synthesis
- 🔄 **Background replacement**: Green screen effects

## 📱 Mobile Support

The web interface is responsive and works on mobile devices:
- **Upload**: Camera capture or file selection
- **Processing**: Cloud-based GPU inference
- **Download**: Direct video download to device

## 🔒 Security Considerations

### Production Deployment
- Use HTTPS for secure file uploads
- Implement authentication if needed
- Set file size limits
- Monitor GPU usage and costs

### Privacy
- Files are processed locally (no external API calls)
- Temporary files are cleaned up automatically
- No data is stored permanently unless configured

## 🚀 Performance Tips

### For Best Results
1. **High-quality reference images**: Clear, well-lit faces
2. **Clean audio**: Minimal background noise
3. **Appropriate length**: 5-30 seconds for best quality
4. **Stable connection**: Avoid interrupting during generation

### For Faster Processing
1. **Lower resolution**: Use 256px for speed
2. **Shorter audio**: < 15 seconds processes faster
3. **Optimal GPU**: RTX 3080+ for best performance
4. **SSD storage**: Faster model loading

---

🎉 **Enjoy creating realistic avatar videos with the web interface!** 

For technical support, check the logs or refer to the main README.md file. 