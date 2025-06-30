# HunyuanVideo-Avatar Directory Data Flow Structure

## 📁 **Input Data Flow**
```
📂 assets/
├── 📂 image/
│   └── 1.png ➜ [Face Detection] ➜ hymm_sp/data_kits/face_align/
└── 📂 audio/
    └── 2.WAV ➜ [Audio Processing] ➜ hymm_sp/data_kits/audio_dataset.py
```

## 🌐 **Web Interface Data Flow**
```
📂 hymm_gradio/
├── web_demo.py ➜ [Gradio UI] ➜ User Interface (Port 7860)
├── fastapi_server.py ➜ [REST API] ➜ API Endpoints (Port 80)
└── pipeline_utils.py ➜ [Utility Functions] ➜ Processing Pipeline
```

## ⚙️ **Configuration Data Flow**
```
config_minimal.py ➜ [Base Config] ➜ hymm_sp/config.py ➜ [Runtime Config] ➜ Processing Modules
                                          ├── constants.py ➜ [System Constants]
                                          └── Global Configuration State
```

## 🧠 **Model Weights Data Flow**
```
📂 weights/
└── 📂 ckpts/
    ├── 📂 hunyuan-video-t2v-720p/
    │   ├── transformers/mp_rank_00_model_states.pt ➜ [Transformer Model] ➜ Core Diffusion
    │   └── vae/pytorch_model.pt ➜ [VAE Weights] ➜ Video Encoding/Decoding
    ├── 📂 llava_llama_image/ ➜ [Vision-Language Model] ➜ Image Understanding
    ├── 📂 text_encoder_2/ ➜ [Text Encoder] ➜ Prompt Processing
    ├── 📂 whisper-tiny/ ➜ [Audio Transcription] ➜ Audio Analysis
    └── 📂 det_align/detface.pt ➜ [Face Detection] ➜ Face Alignment
```

## 🔄 **Core Processing Pipeline Data Flow**
```
📂 hymm_sp/
├── audio_video_inference.py ➜ [Main Inference] ➜ Video Generation
├── inference.py ➜ [Core Logic] ➜ Model Orchestration
├── low_memory_inference.py ➜ [Memory Optimization] ➜ Resource Management
└── batch_inference.py ➜ [Batch Processing] ➜ Multiple Inputs
```

## 🎭 **Data Processing Modules Flow**
```
📂 hymm_sp/data_kits/
├── face_align/
│   ├── detface.py ➜ [Face Detection] ➜ Face Coordinates
│   └── align.py ➜ [Face Alignment] ➜ Normalized Face Data
├── audio_dataset.py ➜ [Audio Loading] ➜ Audio Tensors
├── audio_preprocessor.py ➜ [Audio Processing] ➜ Feature Extraction
└── data_tools.py ➜ [Data Utilities] ➜ Data Manipulation
```

## 🧬 **Neural Network Modules Flow**
```
📂 hymm_sp/modules/
├── models_audio.py ➜ [Core Model] ➜ HYVideoDiffusionTransformer
├── attn_layers.py ➜ [Attention Mechanisms] ➜ Self/Cross Attention
├── audio_adapters.py ➜ [Audio Integration] ➜ Audio-Visual Fusion
├── embed_layers.py ➜ [Embeddings] ➜ Feature Representations
├── mlp_layers.py ➜ [Feed Forward] ➜ Feature Transformation
├── norm_layers.py ➜ [Normalization] ➜ Training Stability
├── activation_layers.py ➜ [Activations] ➜ Nonlinear Functions
├── modulate_layers.py ➜ [Modulation] ➜ Conditional Generation
├── posemb_layers.py ➜ [Position Embeddings] ➜ Spatial/Temporal Info
├── token_refiner.py ➜ [Token Processing] ➜ Feature Refinement
├── fp8_optimization.py ➜ [Memory Optimization] ➜ Reduced Precision
└── parallel_states.py ➜ [Parallel Processing] ➜ Multi-GPU Support
```

## 🎨 **VAE Processing Flow**
```
📂 hymm_sp/vae/
├── autoencoder_kl_causal_3d.py ➜ [3D VAE] ➜ Video Encoding/Decoding
├── vae.py ➜ [VAE Interface] ➜ Latent Space Operations
└── unet_causal_3d_blocks.py ➜ [U-Net Blocks] ➜ Spatial-Temporal Processing
```

## 🌊 **Diffusion Pipeline Flow**
```
📂 hymm_sp/diffusion/
├── pipelines/
│   └── pipeline_hunyuan_video_audio.py ➜ [Main Pipeline] ➜ Video Generation
└── schedulers/
    └── scheduling_flow_match_discrete.py ➜ [Noise Schedule] ➜ Denoising Process
```

## 📝 **Text Processing Flow**
```
📂 hymm_sp/text_encoder/
└── [Text Encoding Modules] ➜ [Prompt Processing] ➜ Text Embeddings
```

## 📊 **Data Flow Sequence**

### **1. Input Processing**
```
User Upload ➜ assets/ ➜ data_kits/ ➜ Preprocessed Data
```

### **2. Model Loading**
```
weights/ckpts/ ➜ modules/ ➜ Loaded Models
```

### **3. Inference Pipeline**
```
Preprocessed Data + Models ➜ diffusion/pipelines/ ➜ Generated Video
```

### **4. Output Generation**
```
Generated Video ➜ Post-processing ➜ Final MP4 Output
```

## 🔧 **Testing and Validation Flow**
```
📂 tests/
├── unit/ ➜ [Component Testing] ➜ Individual Module Validation
├── integration/ ➜ [Pipeline Testing] ➜ End-to-End Validation
├── performance/ ➜ [Performance Testing] ➜ Memory/Speed Optimization
└── system/ ➜ [System Testing] ➜ Docker/Deployment Validation
```

## 🚀 **Deployment Flow**
```
📂 Docker Configuration
├── Dockerfile ➜ [Container Build] ➜ Production Environment
├── docker-compose.yml ➜ [Service Orchestration] ➜ Multi-container Setup
└── docker_startup.sh ➜ [Container Startup] ➜ Runtime Initialization
```

## 📈 **Memory Management Flow**
```
config_minimal.py ➜ Memory Settings ➜ fp8_optimization.py ➜ Reduced Memory Usage
                                    ├── CPU Offloading
                                    ├── Model Sharding
                                    └── Gradient Checkpointing
```

## 🔍 **Error Handling Flow**
```
Processing Errors ➜ helpers.py ➜ Error Recovery ➜ Fallback Mechanisms
                 ├── TorchVision Fixes
                 ├── Import Fallbacks
                 └── Memory Cleanup
```

## 📋 **Key Data Types**

| **Stage** | **Input** | **Output** | **Location** |
|-----------|-----------|------------|--------------|
| Face Detection | Raw Image | Face Coordinates | `data_kits/face_align/` |
| Audio Processing | WAV File | Audio Features | `data_kits/audio_dataset.py` |
| Text Encoding | Text Prompt | Text Embeddings | `text_encoder/` |
| VAE Encoding | Video Frames | Latent Vectors | `vae/` |
| Diffusion | Noise + Conditions | Denoised Latents | `diffusion/pipelines/` |
| VAE Decoding | Latent Vectors | Video Frames | `vae/` |
| Post-processing | Raw Video | Final MP4 | Output Pipeline |

## 🎯 **Critical Dependencies**

1. **flash_attn** ➜ `modules/models_audio.py` (Required for attention mechanisms)
2. **torchvision** ➜ `data_kits/` (Required for image processing)
3. **transformers** ➜ `text_encoder/` (Required for text processing)
4. **diffusers** ➜ `diffusion/` (Required for diffusion models)
5. **gradio** ➜ `hymm_gradio/` (Required for web interface)

## 💡 **Optimization Points**

- **Memory**: VAE processing with slicing (`vae_slice_size`)
- **Speed**: Parallel processing in `modules/parallel_states.py`
- **Quality**: FP8 optimization in `modules/fp8_optimization.py`
- **Stability**: Error handling in `helpers.py`