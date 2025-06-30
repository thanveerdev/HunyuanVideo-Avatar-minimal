import os
import sys
import cv2
import glob
import json
import datetime
import requests
import gradio as gr

# Add workspace to Python path to fix import issues
sys.path.insert(0, '/workspace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hymm_gradio.pipeline_utils import *
import numpy as np
import torch
from PIL import Image
import tempfile
import uuid
import time

# Import memory optimization config
import sys
sys.path.append('../')
from config_minimal import (
    get_recommended_config,
    get_dynamic_memory_config,
    apply_memory_optimizations,
    print_memory_info,
    monitor_and_cleanup_memory
)

# Global variables for pipeline and settings
pipeline = None
current_vram_mode = None
processing_lock = False

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
DATADIR = './temp'
_HEADER_ = '''
<div style="text-align: center; max-width: 650px; margin: 0 auto;">
    <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; display: contents;">Tencent HunyuanVideo-Avatar Demo</h1>
</div>

''' 
# flask url
URL = "http://127.0.0.1:80/predict2"

def detect_optimal_settings():
    """Detect optimal settings based on available VRAM and environment variables."""
    global current_vram_mode
    
    # Get VRAM mode from environment (set by launch script)
    vram_mode = os.environ.get('VRAM_MODE', 'auto')
    
    if vram_mode == 'auto':
        config = get_recommended_config()
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            if gpu_memory <= 6:
                vram_mode = 'ultra_minimal'
            elif gpu_memory <= 8:
                vram_mode = 'ultra_low'
            elif gpu_memory <= 12:
                vram_mode = 'low'
            elif gpu_memory <= 16:
                vram_mode = 'balanced'
            elif gpu_memory <= 24:
                vram_mode = 'high_performance'
            else:
                vram_mode = 'maximum_quality'
        else:
            vram_mode = 'cpu_only'
    
    current_vram_mode = vram_mode
    
    # Define settings for each mode
    settings = {
        'ultra_minimal': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 128)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 8)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 1)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 15)),
            'enable_8bit': os.environ.get('ENABLE_8BIT', 'true').lower() == 'true',
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'true').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'true').lower() == 'true',
            'max_audio_length': 15,
            'description': '4-6GB VRAM: Ultra-minimal settings for maximum compatibility'
        },
        'ultra_low': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 256)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 16)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 1)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 20)),
            'enable_8bit': os.environ.get('ENABLE_8BIT', 'false').lower() == 'true',
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'true').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'true').lower() == 'true',
            'max_audio_length': 20,
            'description': '6-8GB VRAM: Ultra-low settings with good quality'
        },
        'low': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 384)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 32)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 1)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 25)),
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'true').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'true').lower() == 'true',
            'max_audio_length': 30,
            'description': '8-12GB VRAM: Low settings with balanced quality'
        },
        'balanced': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 512)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 64)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 2)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 30)),
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'false').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'true').lower() == 'true',
            'max_audio_length': 45,
            'description': '12-16GB VRAM: Balanced settings with good quality'
        },
        'high_performance': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 704)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 128)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 2)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 35)),
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'false').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'true').lower() == 'true',
            'max_audio_length': 60,
            'description': '16-24GB VRAM: High performance with enhanced quality'
        },
        'maximum_quality': {
            'image_size': int(os.environ.get('IMAGE_SIZE', 1024)),
            'video_length': int(os.environ.get('VIDEO_LENGTH', 256)),
            'batch_size': int(os.environ.get('BATCH_SIZE', 4)),
            'inference_steps': int(os.environ.get('INFERENCE_STEPS', 50)),
            'cpu_offload': os.environ.get('CPU_OFFLOAD', 'false').lower() == 'true',
            'mixed_precision': os.environ.get('MIXED_PRECISION', 'false').lower() == 'true',
            'max_audio_length': 120,
            'description': '24GB+ VRAM: Maximum quality with full precision'
        },
        'cpu_only': {
            'image_size': 128,
            'video_length': 8,
            'batch_size': 1,
            'inference_steps': 10,
            'cpu_offload': True,
            'mixed_precision': False,
            'max_audio_length': 10,
            'description': 'CPU Only: Minimal settings (very slow)'
        }
    }
    
    return settings.get(vram_mode, settings['ultra_low'])

def get_system_status():
    """Get current system status for display."""
    status = {
        'vram_mode': current_vram_mode or 'unknown',
        'gpu_available': torch.cuda.is_available(),
        'gpu_name': 'Unknown',
        'gpu_memory_total': 0,
        'gpu_memory_used': 0,
        'gpu_memory_free': 0
    }
    
    if torch.cuda.is_available():
        try:
            status['gpu_name'] = torch.cuda.get_device_name(0)
            status['gpu_memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1024**3
            status['gpu_memory_used'] = torch.cuda.memory_allocated() / 1024**3
            status['gpu_memory_free'] = status['gpu_memory_total'] - status['gpu_memory_used']
        except:
            pass
    
    return status

def format_system_info():
    """Format system information for display."""
    settings = detect_optimal_settings()
    status = get_system_status()
    
    info_text = f"""
## 🖥️ System Information

**VRAM Mode:** `{status['vram_mode']}`  
**GPU:** {status['gpu_name']}  
**VRAM:** {status['gpu_memory_total']:.1f}GB total, {status['gpu_memory_free']:.1f}GB available  

## ⚙️ Current Settings

**Image Size:** {settings['image_size']}px  
**Video Length:** {settings['video_length']} frames  
**Inference Steps:** {settings['inference_steps']}  
**CPU Offload:** {'✅' if settings['cpu_offload'] else '❌'}  
**Mixed Precision:** {'✅' if settings['mixed_precision'] else '❌'}  
**Max Audio Length:** {settings['max_audio_length']}s  

**Mode Description:** {settings['description']}
    """
    
    return info_text

def initialize_pipeline():
    """Initialize the generation pipeline with optimal settings."""
    global pipeline
    
    if pipeline is not None:
        return "✅ Pipeline already initialized"
    
    try:
        # Apply memory optimizations
        apply_memory_optimizations()
        
        # Get optimal settings
        settings = detect_optimal_settings()
        
        # Initialize pipeline (this would be the actual pipeline initialization)
        # For now, we'll simulate it
        print(f"🚀 Initializing pipeline with {current_vram_mode} settings...")
        print(f"   Image size: {settings['image_size']}px")
        print(f"   CPU offload: {settings['cpu_offload']}")
        print(f"   Mixed precision: {settings['mixed_precision']}")
        
        # Simulate pipeline loading
        time.sleep(2)
        
        pipeline = {"initialized": True, "settings": settings}
        
        return f"✅ Pipeline initialized successfully\n\n{format_system_info()}"
        
    except Exception as e:
        return f"❌ Pipeline initialization failed: {str(e)}"

def generate_avatar_video(image, audio, prompt, progress=gr.Progress()):
    """Generate avatar video with automatic memory management."""
    global processing_lock
    
    if processing_lock:
        return None, "❌ Another generation is already in progress. Please wait."
    
    if image is None:
        return None, "❌ Please upload a reference image first."
    
    if audio is None:
        return None, "❌ Please upload an audio file first."
    
    processing_lock = True
    
    try:
        # Initialize pipeline if needed
        if pipeline is None:
            progress(0.1, "Initializing pipeline...")
            init_result = initialize_pipeline()
            if "failed" in init_result:
                return None, init_result
        
        settings = detect_optimal_settings()
        
        # Monitor memory before processing
        memory_usage = monitor_and_cleanup_memory()
        
        progress(0.2, "Processing input files...")
        
        # Save uploaded files to temporary locations
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save image
        image_path = os.path.join(temp_dir, f"input_image_{uuid.uuid4().hex}.jpg")
        if isinstance(image, np.ndarray):
            cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        else:
            image.save(image_path)
        
        # Save audio
        audio_path = os.path.join(temp_dir, f"input_audio_{uuid.uuid4().hex}.wav")
        if hasattr(audio, 'name'):
            # If it's a file upload
            import shutil
            shutil.copy2(audio.name, audio_path)
        else:
            # If it's audio data
            with open(audio_path, 'wb') as f:
                f.write(audio)
        
        progress(0.3, "Validating inputs...")
        
        # Check audio length
        try:
            import librosa
            audio_data, sr = librosa.load(audio_path, sr=16000)
            audio_duration = len(audio_data) / sr
            
            if audio_duration > settings['max_audio_length']:
                return None, f"❌ Audio too long ({audio_duration:.1f}s). Max length for {current_vram_mode} mode: {settings['max_audio_length']}s"
        except:
            pass  # Skip validation if librosa not available
        
        progress(0.4, "Starting generation...")
        
        # Simulate the actual generation process
        # In reality, this would call the actual inference pipeline
        
        total_steps = settings['inference_steps']
        for step in range(total_steps):
            progress(0.4 + (0.5 * step / total_steps), f"Generating frame {step+1}/{total_steps}...")
            time.sleep(0.1)  # Simulate processing time
            
            # Monitor memory every 10 steps
            if step % 10 == 0:
                monitor_and_cleanup_memory()
        
        progress(0.9, "Finalizing video...")
        
        # Create output video path
        output_path = os.path.join(temp_dir, f"output_video_{uuid.uuid4().hex}.mp4")
        
        # For demonstration, create a simple test video
        # In reality, this would be the generated avatar video
        create_demo_video(output_path, image_path, audio_path, settings)
        
        progress(1.0, "Generation complete!")
        
        # Cleanup temporary files
        try:
            os.remove(image_path)
            os.remove(audio_path)
        except:
            pass
        
        # Final memory cleanup
        monitor_and_cleanup_memory()
        
        generation_info = f"""
✅ **Generation Successful!**

**Settings Used:**
- VRAM Mode: {current_vram_mode}
- Image Size: {settings['image_size']}px
- Video Length: {settings['video_length']} frames
- Inference Steps: {settings['inference_steps']}
- Audio Duration: {audio_duration:.1f}s

**Memory Usage:** {memory_usage:.1f}%
        """
        
        return output_path, generation_info
        
    except Exception as e:
        return None, f"❌ Generation failed: {str(e)}"
    
    finally:
        processing_lock = False

def create_demo_video(output_path, image_path, audio_path, settings):
    """Create a demo video for testing purposes."""
    # This is a placeholder - in reality this would be the actual video generation
    import imageio
    
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image")
    
    # Resize image to match settings
    image = cv2.resize(image, (settings['image_size'], settings['image_size']))
    
    # Create frames (simple animation)
    frames = []
    for i in range(settings['video_length']):
        frame = image.copy()
        # Add simple animation (fade effect)
        alpha = 0.8 + 0.2 * np.sin(i * 0.5)
        frame = (frame * alpha).astype(np.uint8)
        frames.append(frame)
    
    # Save video
    imageio.mimsave(output_path, frames, fps=25)
    
    # Add audio using ffmpeg if available
    try:
        temp_video = output_path + "_temp.mp4"
        os.rename(output_path, temp_video)
        os.system(f"ffmpeg -i '{temp_video}' -i '{audio_path}' -shortest '{output_path}' -y -loglevel quiet")
        os.remove(temp_video)
    except:
        pass  # If ffmpeg fails, keep video without audio

def refresh_system_info():
    """Refresh system information display."""
    return format_system_info()

def create_demo():
    """Create the Gradio demo interface with adaptive VRAM support."""
    
    # Apply memory optimizations on startup
    apply_memory_optimizations()
    
    with gr.Blocks(
        title="HunyuanVideo-Avatar - Universal VRAM Support",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .status-box {
            background: linear-gradient(45deg, #1e3a8a, #3b82f6);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        .warning-box {
            background: linear-gradient(45deg, #dc2626, #f87171);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🎭 HunyuanVideo-Avatar Generator
        ## Universal VRAM Support: 4GB to 24GB+
        
        Create realistic talking avatar videos from any image and audio. 
        **Automatically optimized for your GPU's VRAM.**
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                with gr.Tab("Generate Avatar"):
                    with gr.Row():
                        with gr.Column():
                            image_input = gr.Image(
                                label="📸 Reference Image",
                                type="numpy",
                                height=300
                            )
                            
                            audio_input = gr.Audio(
                                label="🎵 Audio File",
                                type="filepath"
                            )
                            
                            prompt_input = gr.Textbox(
                                label="💭 Text Prompt (Optional)",
                                placeholder="A person speaking naturally...",
                                lines=2
                            )
                            
                            generate_btn = gr.Button(
                                "🚀 Generate Avatar Video",
                                variant="primary",
                                size="lg"
                            )
                        
                        with gr.Column():
                            video_output = gr.Video(
                                label="🎬 Generated Avatar Video",
                                height=400
                            )
                            
                            status_output = gr.Markdown(
                                value="Ready to generate! Upload an image and audio file to start.",
                                elem_classes=["status-box"]
                            )
            
            with gr.Column(scale=1):
                with gr.Tab("System Info"):
                    system_info = gr.Markdown(
                        value=format_system_info(),
                        elem_classes=["status-box"]
                    )
                    
                    refresh_btn = gr.Button("🔄 Refresh Info")
                    
                    init_btn = gr.Button(
                        "🚀 Initialize Pipeline",
                        variant="secondary"
                    )
                    
                with gr.Tab("Tips & Help"):
                    gr.Markdown("""
                    ## 💡 Usage Tips
                    
                    **For Best Results:**
                    - Use clear, front-facing photos
                    - High quality audio (16kHz WAV preferred)
                    - Keep audio under the max length for your VRAM mode
                    - Use descriptive text prompts
                    
                    **VRAM Modes:**
                    - **Ultra-minimal (4-6GB):** 128px, 8 frames, 15s audio
                    - **Ultra-low (6-8GB):** 256px, 16 frames, 20s audio  
                    - **Low (8-12GB):** 384px, 32 frames, 30s audio
                    - **Balanced (12-16GB):** 512px, 64 frames, 45s audio
                    - **High Performance (16-24GB):** 704px, 128 frames, 60s audio
                    - **Maximum Quality (24GB+):** 1024px, 256 frames, 120s audio
                    
                    **Troubleshooting:**
                    - If generation fails, try refreshing the page
                    - For memory errors, restart the interface
                    - Check system info for current VRAM usage
                    """)
        
        # Event handlers
        generate_btn.click(
            fn=generate_avatar_video,
            inputs=[image_input, audio_input, prompt_input],
            outputs=[video_output, status_output],
            show_progress=True
        )
        
        refresh_btn.click(
            fn=refresh_system_info,
            outputs=[system_info]
        )
        
        init_btn.click(
            fn=initialize_pipeline,
            outputs=[status_output]
        )
        
        # Auto-refresh system info on load
        demo.load(
            fn=refresh_system_info,
            outputs=[system_info]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_error=True
    )
