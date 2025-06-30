# HunyuanVideo-Avatar Dependency Tree Structure

## 🌳 **Core Dependency Tree - Organized by Folders**

```
HunyuanVideo-Avatar-minimal/
│
├── 📂 **ROOT LEVEL FILES**
│   ├── 🚀 **Entry Points**
│   │   ├── run_web_demo.sh ──────────────┐
│   │   ├── run_low_memory.sh ────────────┤
│   │   ├── run_minimal.sh ───────────────┤
│   │   ├── run_fastapi_server.sh ────────┤
│   │   ├── run_single_inference.sh ──────┤
│   │   └── run_ultra_low_vram.sh ────────┤
│   │                                     │
│   ├── ⚙️ **Configuration Files**         │
│   │   ├── config_minimal.py ────────────┤
│   │   ├── docker-compose.yml ───────────┤
│   │   ├── Dockerfile ──────────────────┤
│   │   ├── requirements.txt ─────────────┤
│   │   ├── requirements-minimal.txt ─────┤
│   │   └── pytest.ini ──────────────────┤
│   │                                     │
│   ├── 🔧 **Utility Scripts**            │
│   │   ├── apply_torchvision_fix.py ─────┤
│   │   ├── fix_imports.py ───────────────┤
│   │   ├── fix_torchvision_compatibility.py ┤
│   │   ├── network_volume_utils.py ──────┤
│   │   ├── start_fastapi_with_fix.py ────┤
│   │   └── test_*.py (various test files) ┤
│   │                                     │
│   └── 📝 **Documentation**              │
│       ├── README.md ───────────────────┤
│       ├── LICENSE ─────────────────────┤
│       └── *.md (various documentation) ┤
│                                         │
├── 📂 **assets/** ◄─────────────────────┘
│   ├── 📂 **image/**
│   │   └── 1.png ──── [Face Input] ──────┐
│   └── 📂 **audio/**                     │
│       └── 2.WAV ─── [Audio Input] ──────┤
│                                         │
├── 📂 **hymm_gradio/** ◄────────────────┘
│   ├── __init__.py
│   ├── web_demo.py ──── [Gradio UI] ─────┐
│   ├── fastapi_server.py ─ [REST API] ───┤
│   └── pipeline_utils.py ─ [Utils] ──────┤
│                                         │
├── 📂 **hymm_sp/** ◄────────────────────┘
│   ├── 📁 **Root Level**
│   │   ├── __init__.py
│   │   ├── config.py ──── [Runtime Config] ┐
│   │   ├── constants.py ─ [Constants] ─────┤
│   │   ├── helpers.py ─── [Helper Utils] ──┤
│   │   ├── mmgp_utils.py ─ [MMGP Utils] ───┤
│   │   ├── audio_video_inference.py ──────┤
│   │   ├── inference.py ─ [Core Logic] ────┤
│   │   ├── low_memory_inference.py ───────┤
│   │   └── batch_inference.py ────────────┤
│   │                                      │
│   ├── 📂 **data_kits/**                 │
│   │   ├── __init__.py                   │
│   │   ├── audio_dataset.py ──────────────┤
│   │   ├── audio_preprocessor.py ─────────┤
│   │   ├── data_tools.py ────────────────┤
│   │   └── 📂 **face_align/**            │
│   │       ├── __init__.py               │
│   │       ├── detface.py ── [Face Detection] ┐
│   │       └── align.py ─── [Face Alignment] ─┤
│   │                                           │
│   ├── 📂 **modules/** ⚠️ CRITICAL             │
│   │   ├── __init__.py                        │
│   │   ├── models_audio.py ── [Core Model] ──┤ ⚠️ REQUIRES: flash_attn
│   │   ├── attn_layers.py ── [Attention] ─────┤
│   │   ├── audio_adapters.py ─ [Audio Fusion] ┤
│   │   ├── embed_layers.py ── [Embeddings] ───┤
│   │   ├── mlp_layers.py ─── [Feed Forward] ──┤
│   │   ├── norm_layers.py ── [Normalization] ─┤
│   │   ├── activation_layers.py ─ [Activations] ┤
│   │   ├── modulate_layers.py ─ [Modulation] ──┤
│   │   ├── posemb_layers.py ── [Position Emb] ┤
│   │   ├── token_refiner.py ─ [Token Process] ─┤
│   │   ├── fp8_optimization.py ─ [Memory Opt] ┤
│   │   └── parallel_states.py ─ [Multi-GPU] ──┤
│   │                                           │
│   ├── 📂 **vae/**                            │
│   │   ├── __init__.py                        │
│   │   ├── autoencoder_kl_causal_3d.py ──────┤
│   │   ├── vae.py ──── [VAE Interface] ───────┤
│   │   └── unet_causal_3d_blocks.py ─────────┤
│   │                                           │
│   ├── 📂 **diffusion/**                      │
│   │   ├── __init__.py                        │
│   │   ├── 📂 **pipelines/**                  │
│   │   │   ├── __init__.py                    │
│   │   │   └── pipeline_hunyuan_video_audio.py ┤
│   │   └── 📂 **schedulers/**                 │
│   │       ├── __init__.py                    │
│   │       └── scheduling_flow_match_discrete.py ┤
│   │                                              │
│   └── 📂 **text_encoder/**                      │
│       └── __init__.py ── [Text Processing] ─────┤
│                                                  │
├── 📂 **weights/** ◄────────────────────────────┘
│   ├── README.md
│   └── 📂 **ckpts/**
│       ├── 📂 **hunyuan-video-t2v-720p/**
│       │   ├── 📂 **transformers/**
│       │   │   ├── mp_rank_00_model_states.pt
│       │   │   ├── mp_rank_00_model_states_fp8.pt
│       │   │   └── mp_rank_00_model_states_fp8_map.pt
│       │   └── 📂 **vae/**
│       │       ├── pytorch_model.pt
│       │       └── config.json
│       ├── 📂 **llava_llama_image/**
│       │   ├── model-00001-of-00004.safetensors
│       │   ├── model-00002-of-00004.safetensors
│       │   ├── model-00003-of-00004.safetensors
│       │   ├── model-00004-of-00004.safetensors
│       │   ├── model.safetensors.index.json
│       │   └── config.json
│       ├── 📂 **text_encoder_2/**
│       │   ├── model.safetensors
│       │   ├── pytorch_model.bin
│       │   ├── tokenizer.json
│       │   ├── vocab.json
│       │   └── config.json
│       ├── 📂 **whisper-tiny/**
│       │   ├── model.safetensors
│       │   ├── pytorch_model.bin
│       │   ├── tokenizer.json
│       │   └── config.json
│       └── 📂 **det_align/**
│           └── detface.pt
│
├── 📂 **tests/** ◄──────────────────────────────
│   ├── README.md
│   ├── conftest.py
│   ├── 📂 **fixtures/**
│   │   └── sample_data.py
│   ├── 📂 **unit/**
│   │   ├── test_inference.py
│   │   ├── test_config_minimal.py
│   │   ├── test_audio_processing.py
│   │   ├── 📂 **test_audio/**
│   │   ├── 📂 **test_config/**
│   │   ├── 📂 **test_diffusion/**
│   │   ├── 📂 **test_face/**
│   │   ├── 📂 **test_inference/**
│   │   └── 📂 **test_vae/**
│   ├── 📂 **integration/**
│   │   └── test_end_to_end.py
│   ├── 📂 **performance/**
│   │   └── test_memory_usage.py
│   ├── 📂 **system/**
│   │   ├── test_docker_integration.py
│   │   └── test_user_workflows.py
│   └── 📂 **compatibility/**
│
└── 📂 **docker/** (Configuration Files at Root)
    ├── docker_startup.sh
    ├── docker_startup_persistent.sh
    ├── docker_startup_network_volume.sh
    ├── docker_startup_original.sh
    ├── docker_startup_root_mount.sh
    ├── build_docker.sh
    └── runpod_template.json
```

## 📋 **Complete Folder Index**

### **📂 Root Level (HunyuanVideo-Avatar-minimal/)**
```
├── 🚀 Entry Scripts
│   ├── run_web_demo.sh ────── Main web interface launcher
│   ├── run_low_memory.sh ──── Low memory mode launcher  
│   ├── run_minimal.sh ──────── Minimal configuration launcher
│   ├── run_fastapi_server.sh ─ API server launcher
│   ├── run_single_inference.sh ─ Single inference launcher
│   └── run_ultra_low_vram.sh ── Ultra low VRAM launcher
│
├── ⚙️ Configuration
│   ├── config_minimal.py ───── Main configuration file
│   ├── docker-compose.yml ──── Docker orchestration
│   ├── Dockerfile ──────────── Container definition
│   ├── requirements.txt ────── Python dependencies
│   ├── requirements-minimal.txt ─ Minimal dependencies
│   └── pytest.ini ─────────── Test configuration
│
├── 🔧 Utility Scripts
│   ├── apply_torchvision_fix.py ─ TorchVision compatibility
│   ├── fix_imports.py ─────────── Import error fixes
│   ├── fix_torchvision_compatibility.py ─ Advanced TorchVision fixes
│   ├── network_volume_utils.py ── Network storage utilities
│   ├── start_fastapi_with_fix.py ─ FastAPI with error handling
│   └── test_*.py ─────────────── Various standalone tests
│
└── 📝 Documentation
    ├── README.md ─────────────── Main documentation
    ├── LICENSE ──────────────── License information
    └── *.md files ───────────── Various documentation files
```

### **📂 assets/ - Input Data**
```
├── 📂 image/
│   └── 1.png ────────────── Sample face image for testing
└── 📂 audio/  
    └── 2.WAV ────────────── Sample audio file for testing
```

### **📂 hymm_gradio/ - Web Interface**
```
├── __init__.py ──────────── Package initialization
├── web_demo.py ──────────── Gradio web interface (Port 7860)
├── fastapi_server.py ───── FastAPI REST API (Port 80)
└── pipeline_utils.py ───── Utility functions for pipeline
```

### **📂 hymm_sp/ - Core Processing Package**
```
📁 Root Level Files:
├── __init__.py ────────────── Package initialization
├── config.py ─────────────── Runtime configuration management
├── constants.py ──────────── System constants and defaults
├── helpers.py ────────────── General helper functions
├── mmgp_utils.py ─────────── MMGP integration utilities
├── audio_video_inference.py ─ Main audio-video inference engine
├── inference.py ──────────── Core inference logic
├── low_memory_inference.py ── Memory-optimized inference
└── batch_inference.py ────── Batch processing capabilities

📂 data_kits/ - Data Processing:
├── __init__.py ──────────── Package initialization
├── audio_dataset.py ────── Audio data loading and processing
├── audio_preprocessor.py ── Audio feature extraction
├── data_tools.py ──────── General data manipulation tools
└── 📂 face_align/
    ├── __init__.py ─────── Package initialization
    ├── detface.py ─────── Face detection using RetinaFace
    └── align.py ──────── Face alignment and normalization

📂 modules/ - Neural Network Components ⚠️ CRITICAL:
├── __init__.py ──────────── Package initialization
├── models_audio.py ─────── Core diffusion transformer ⚠️ REQUIRES: flash_attn
├── attn_layers.py ─────── Attention mechanism implementations
├── audio_adapters.py ──── Audio-visual fusion adapters
├── embed_layers.py ────── Embedding layer implementations
├── mlp_layers.py ──────── Multi-layer perceptron components
├── norm_layers.py ─────── Normalization layer implementations
├── activation_layers.py ── Activation function implementations
├── modulate_layers.py ─── Modulation layer for conditional generation
├── posemb_layers.py ───── Positional embedding implementations
├── token_refiner.py ───── Token processing and refinement
├── fp8_optimization.py ── FP8 precision optimization for memory
└── parallel_states.py ─── Multi-GPU parallel processing support

📂 vae/ - Video Auto-Encoder:
├── __init__.py ──────────── Package initialization
├── autoencoder_kl_causal_3d.py ─ 3D causal VAE implementation
├── vae.py ─────────────── VAE interface and utilities
└── unet_causal_3d_blocks.py ── 3D U-Net blocks for spatial-temporal processing

📂 diffusion/ - Diffusion Pipeline:
├── __init__.py ──────────── Package initialization
├── 📂 pipelines/
│   ├── __init__.py ─────── Package initialization
│   └── pipeline_hunyuan_video_audio.py ── Main diffusion pipeline
└── 📂 schedulers/
    ├── __init__.py ─────── Package initialization
    └── scheduling_flow_match_discrete.py ── Noise scheduling for diffusion

📂 text_encoder/ - Text Processing:
└── __init__.py ──────────── Package initialization (modules loaded dynamically)
```

### **📂 weights/ - Model Weights (24GB+)**
```
├── README.md ─────────────── Weight documentation
└── 📂 ckpts/
    ├── 📂 hunyuan-video-t2v-720p/ ── Main diffusion model (~18GB)
    │   ├── 📂 transformers/
    │   │   ├── mp_rank_00_model_states.pt ── Main transformer weights
    │   │   ├── mp_rank_00_model_states_fp8.pt ── FP8 optimized weights
    │   │   └── mp_rank_00_model_states_fp8_map.pt ── FP8 mapping
    │   └── 📂 vae/
    │       ├── pytorch_model.pt ── VAE weights
    │       └── config.json ───── VAE configuration
    ├── 📂 llava_llama_image/ ──── Vision-language model (~7GB)
    │   ├── model-00001-of-00004.safetensors ── Model shard 1
    │   ├── model-00002-of-00004.safetensors ── Model shard 2
    │   ├── model-00003-of-00004.safetensors ── Model shard 3
    │   ├── model-00004-of-00004.safetensors ── Model shard 4
    │   ├── model.safetensors.index.json ──── Shard index
    │   └── config.json ──────────────────── Model configuration
    ├── 📂 text_encoder_2/ ────── Text encoder model (~1GB)
    │   ├── model.safetensors ── SafeTensors format weights
    │   ├── pytorch_model.bin ── PyTorch format weights
    │   ├── tokenizer.json ─── Tokenizer configuration
    │   ├── vocab.json ────── Vocabulary file
    │   └── config.json ───── Model configuration
    ├── 📂 whisper-tiny/ ──────── Audio transcription model (~150MB)
    │   ├── model.safetensors ── Model weights
    │   ├── pytorch_model.bin ── Alternative format
    │   ├── tokenizer.json ─── Tokenizer
    │   └── config.json ───── Configuration
    └── 📂 det_align/ ─────────── Face detection model (~100MB)
        └── detface.pt ────── RetinaFace model weights
```

### **📂 tests/ - Testing Framework**
```
├── README.md ─────────────── Test documentation
├── conftest.py ──────────── PyTest configuration
├── 📂 fixtures/
│   └── sample_data.py ───── Test data fixtures
├── 📂 unit/ ─────────────── Unit tests
│   ├── test_inference.py ── Core inference testing
│   ├── test_config_minimal.py ── Configuration testing
│   ├── test_audio_processing.py ── Audio processing tests
│   └── 📂 test_*/ ──────── Modular test directories
├── 📂 integration/ ──────── Integration tests
│   └── test_end_to_end.py ── Full pipeline testing
├── 📂 performance/ ──────── Performance tests
│   └── test_memory_usage.py ── Memory usage validation
├── 📂 system/ ───────────── System tests
│   ├── test_docker_integration.py ── Docker testing
│   └── test_user_workflows.py ──── User workflow testing
└── 📂 compatibility/ ────── Compatibility tests
```

### **📂 Docker Configuration (Files at Root)**
```
├── docker_startup.sh ──────── Standard Docker startup
├── docker_startup_persistent.sh ── Persistent volume startup
├── docker_startup_network_volume.sh ── Network volume startup
├── docker_startup_original.sh ── Original startup script
├── docker_startup_root_mount.sh ── Root mount startup
├── build_docker.sh ───────── Docker image build script
└── runpod_template.json ──── RunPod deployment template
```

## 🔗 **Critical Dependency Chains**

### **1. Main Inference Chain**
```
run_web_demo.sh
    └── hymm_gradio/web_demo.py
        └── hymm_gradio/fastapi_server.py
            └── hymm_sp/audio_video_inference.py
                └── hymm_sp/inference.py
                    ├── hymm_sp/diffusion/pipelines/pipeline_hunyuan_video_audio.py
                    ├── hymm_sp/vae/autoencoder_kl_causal_3d.py
                    └── hymm_sp/modules/models_audio.py ⚠️ REQUIRES: flash_attn
```

### **2. Configuration Chain**
```
config_minimal.py
    └── hymm_sp/config.py
        └── hymm_sp/constants.py
            └── [All processing modules]
```

### **3. Data Processing Chain**
```
assets/image/1.png
    └── hymm_sp/data_kits/face_align/detface.py
        └── hymm_sp/data_kits/face_align/align.py
            └── [Normalized face data]

assets/audio/2.WAV
    └── hymm_sp/data_kits/audio_dataset.py
        └── hymm_sp/data_kits/audio_preprocessor.py
            └── [Audio features]
```

### **4. Model Loading Chain**
```
weights/ckpts/
    ├── hunyuan-video-t2v-720p/ → hymm_sp/modules/models_audio.py
    ├── det_align/detface.pt → hymm_sp/data_kits/face_align/detface.py
    ├── text_encoder_2/ → hymm_sp/text_encoder/
    └── whisper-tiny/ → Audio processing pipeline
```

## ⚠️ **Dependency Breakpoints**

### **Critical Failures**
1. **flash_attn missing** → `hymm_sp/modules/models_audio.py` fails → Entire inference pipeline broken
2. **torchvision issues** → Image processing fails → Face detection broken
3. **Model weights missing** → Core models unavailable → No generation possible

### **Non-Critical Failures**
1. **Gradio issues** → Web interface broken but API may work
2. **FastAPI issues** → API broken but direct inference may work
3. **Test failures** → Functionality works but validation unavailable

## 🎯 **Optimization Dependencies**

### **Memory Optimization Chain**
```
config_minimal.py (memory settings)
    └── hymm_sp/modules/fp8_optimization.py
        └── hymm_sp/modules/parallel_states.py
            └── [Reduced memory usage]
```

### **Performance Optimization Chain**
```
VRAM Detection
    └── Dynamic configuration
        └── Batch size optimization
            └── CPU/GPU offloading decisions
```

## 🔧 **Fix Dependencies**

### **TorchVision Fix Chain**
```
apply_torchvision_fix.py
    └── fix_torchvision_compatibility.py
        └── hymm_sp/data_kits/audio_dataset.py (defensive imports)
            └── [Compatibility fallbacks]
```

### **Import Fix Chain**
```
fix_imports.py
    └── fix_deep_torchvision_import.py
        └── [Import error recovery]
```

## 📦 **External Dependencies**

### **Python Packages**
```
requirements.txt
├── torch >= 2.0.0
├── torchvision >= 0.15.0
├── transformers >= 4.21.0
├── diffusers >= 0.21.0
├── gradio >= 4.0.0
├── fastapi >= 0.100.0
├── flash-attn >= 2.6.0 ⚠️ Critical
├── opencv-python
├── librosa
├── numpy
└── pillow
```

### **System Dependencies**
```
CUDA 12.4.1
├── GPU: NVIDIA RTX A5000 (24GB)
├── Python 3.10
├── Docker (optional)
└── FFmpeg (for video processing)
```

## 🚨 **Single Points of Failure**

1. **flash_attn module** - Breaks entire inference pipeline
2. **Model weight files** - No alternative if missing
3. **GPU memory** - System unusable if insufficient
4. **CUDA compatibility** - Breaks all GPU operations

## 💡 **Redundancy & Fallbacks**

### **Available Fallbacks**
- TorchVision → torch-only transforms
- High memory → Low memory inference mode
- FastAPI → Direct Gradio interface
- Batch processing → Single inference

### **No Fallbacks**
- flash_attn (critical dependency)
- Core model weights
- Basic Python/CUDA environment 