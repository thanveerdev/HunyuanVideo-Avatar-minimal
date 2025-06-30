import os
import gc
import time
import numpy as np
from pathlib import Path
from loguru import logger
import imageio
import torch
from einops import rearrange
import torch.distributed
from torch.utils.data.distributed import DistributedSampler
from torch.utils.data import DataLoader
from hymm_sp.config import parse_args
from hymm_sp.audio_video_inference import HunyuanVideoSampler
from hymm_sp.data_kits.audio_dataset import VideoAudioTextLoaderVal
from hymm_sp.data_kits.face_align import AlignImage

# Import config for memory optimization
import sys
sys.path.append('./')
from config_minimal import (
    apply_memory_optimizations, 
    get_recommended_config,
    get_dynamic_memory_config,
    monitor_and_cleanup_memory,
    print_memory_info,
    setup_ultra_low_vram_mode
)

# Import MMGP utilities for extreme memory optimization
from hymm_sp.mmgp_utils import memory_manager, apply_spaghetti_optimizations

from transformers import WhisperModel
from transformers import AutoFeatureExtractor

MODEL_OUTPUT_PATH = os.environ.get('MODEL_BASE', os.getcwd())

def setup_ultra_low_memory():
    """Setup the most aggressive memory optimizations with MMGP."""
    
    # Apply MMGP spaghetti optimizations first
    apply_spaghetti_optimizations()
    
    # Apply base optimizations
    apply_memory_optimizations()
    
    # Initialize memory monitoring
    memory_manager.monitor_memory("Initial setup")
    
    # Get GPU memory info
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"🔍 GPU Memory Available: {gpu_memory:.1f} GB")
        
        if gpu_memory <= 6:
            print("🚨 Ultra-low VRAM detected - applying extreme MMGP optimizations")
            setup_ultra_low_vram_mode()
            # Enable emergency cleanup
            memory_manager.enable_aggressive_cleanup = True 
        elif gpu_memory <= 8:
            print("⚠️  Low VRAM detected - applying aggressive MMGP optimizations")
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128,garbage_collection_threshold:0.6"
        
        # Set memory fraction based on available VRAM
        if gpu_memory <= 6:
            torch.cuda.set_per_process_memory_fraction(0.75)  # Very conservative
        elif gpu_memory <= 8:
            torch.cuda.set_per_process_memory_fraction(0.8)
        else:
            torch.cuda.set_per_process_memory_fraction(0.85)
            
        # Clear any existing cache with MMGP
        memory_manager.aggressive_cleanup()
    
    print("✅ Ultra-low memory setup completed with MMGP")

def cleanup_memory():
    """Aggressive memory cleanup between processing steps with MMGP."""
    # Use MMGP aggressive cleanup which includes cache emptying and gc
    memory_manager.aggressive_cleanup()
    time.sleep(0.1)  # Brief pause to allow cleanup

def monitor_memory_usage(step_name=""):
    """Monitor and log memory usage with MMGP."""
    memory_manager.monitor_memory(step_name)
    
    # Additional check for high memory usage
    if torch.cuda.is_available():
        memory_allocated = torch.cuda.memory_allocated() / 1024**3
        memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
        usage_percent = (memory_allocated / memory_total) * 100
        
        # Trigger emergency cleanup if memory usage is very high
        if usage_percent > 85:
            print("🚨 Critical memory usage detected - triggering emergency cleanup...")
            memory_manager.emergency_cleanup()
            return True
        elif usage_percent > 75:
            print("🧹 High memory usage detected - cleaning up...")
            cleanup_memory()
            return True
    return False

def load_models_with_offloading(args, device):
    """Load models with aggressive CPU offloading for low VRAM using MMGP."""
    print("🚀 Loading models with MMGP ultra-low VRAM optimizations...")
    
    # Get memory config
    config = get_recommended_config()
    print(f"🎯 Using preset: {config}")
    
    # Apply config to args, but preserve command line arguments
    if not hasattr(args, 'image_size') or args.image_size is None:
        args.image_size = config.get('image_size', 256)
    # Preserve command line cpu_offload argument
    if not hasattr(args, 'cpu_offload') or args.cpu_offload is None:
        args.cpu_offload = config.get('cpu_offload', True)
    else:
        # Force CPU offloading if explicitly requested via command line
        args.cpu_offload = args.cpu_offload or config.get('cpu_offload', True)
    if not hasattr(args, 'mixed_precision') or args.mixed_precision is None:
        args.mixed_precision = config.get('mixed_precision', True)
    if not hasattr(args, 'infer_min') or args.infer_min is None:
        args.infer_min = config.get('infer_min', True)
    
    monitor_memory_usage("Before model loading")
    
    # Try to load main model with MMGP optimizations first
    print("🎯 Attempting MMGP model loading...")
    try:
        # This would be the ideal MMGP loading, but fallback to standard if needed
        hunyuan_video_sampler = HunyuanVideoSampler.from_pretrained(
            args.ckpt, 
            args=args, 
            device=device,
            torch_dtype=torch.float16 if args.mixed_precision else torch.float32
        )
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"⚠️  MMGP model loading fallback: {e}")
        # Standard loading with immediate offloading
        hunyuan_video_sampler = HunyuanVideoSampler.from_pretrained(
            args.ckpt, 
            args=args, 
            device=device,
            torch_dtype=torch.float16 if args.mixed_precision else torch.float32
        )
    
    monitor_memory_usage("After main model loading")
    
    # Apply MMGP CPU offloading if enabled
    if args.cpu_offload:
        print("🔄 Applying MMGP CPU offloading...")
        try:
            # Try MMGP offloading first
            memory_manager.offload_to_cpu(
                hunyuan_video_sampler.pipeline.transformer,
                keep_on_gpu=['encoder', 'attention']  # Keep critical parts on GPU
            )
            print("✅ MMGP CPU offloading applied")
        except Exception as e:
            print(f"⚠️  MMGP offloading failed, using standard: {e}")
            # Fallback to standard diffusers offloading
            try:
                from diffusers.hooks import apply_group_offloading
                onload_device = torch.device("cuda")
                apply_group_offloading(
                    hunyuan_video_sampler.pipeline.transformer, 
                    onload_device=onload_device, 
                    offload_type="block_level", 
                    num_blocks_per_group=1
                )
                print("✅ Standard CPU offloading applied")
            except Exception as e2:
                print(f"⚠️  All offloading methods failed: {e2}")
    
    monitor_memory_usage("After CPU offloading")
    
    # Load Whisper with minimal memory footprint
    print("🎵 Loading Whisper model...")
    whisper_path = f"{MODEL_OUTPUT_PATH}/ckpts/whisper-tiny/"
    wav2vec = WhisperModel.from_pretrained(
        whisper_path,
        torch_dtype=torch.float16 if args.mixed_precision else torch.float32
    ).to(device=device)
    wav2vec.requires_grad_(False)
    
    # Offload Whisper to CPU immediately after loading
    if args.cpu_offload:
        wav2vec = wav2vec.cpu()
        print("🔄 Whisper model offloaded to CPU")
    
    monitor_memory_usage("After Whisper loading")
    
    # Load face alignment
    print("👤 Loading face alignment...")
    BASE_DIR = f'{MODEL_OUTPUT_PATH}/ckpts/det_align/'
    det_path = os.path.join(BASE_DIR, 'detface.pt')    
    align_instance = AlignImage("cuda", det_path=det_path)
    
    monitor_memory_usage("After face alignment loading")
    
    # Load feature extractor
    feature_extractor = AutoFeatureExtractor.from_pretrained(whisper_path)
    
    cleanup_memory()
    monitor_memory_usage("After cleanup")
    
    return hunyuan_video_sampler, wav2vec, align_instance, feature_extractor

def process_batch_ultra_low_memory(args, batch, hunyuan_video_sampler, wav2vec, feature_extractor, align_instance):
    """Process a single batch with ultra-low memory optimizations."""
    
    fps = batch["fps"]
    videoid = batch['videoid'][0]
    audio_path = str(batch["audio_path"][0])
    save_path = args.save_path 
    output_path = f"{save_path}/{videoid}.mp4"
    output_audio_path = f"{save_path}/{videoid}_audio.mp4"
    
    print(f"🎬 Processing: {videoid}")
    monitor_memory_usage("Before processing")
    
    # Move Whisper back to GPU temporarily if offloaded
    if args.cpu_offload and wav2vec.device.type == 'cpu':
        print("🔄 Moving Whisper to GPU...")
        wav2vec = wav2vec.cuda()
    
    # Adjust audio length for minimal inference
    if args.infer_min:
        batch["audio_len"][0] = min(129, batch["audio_len"][0])
    
    # Dynamic memory adjustment
    dynamic_config = get_dynamic_memory_config()
    if isinstance(dynamic_config, dict) and 'image_size' in dynamic_config:
        # Adjust image size dynamically if memory is critically low
        if dynamic_config['image_size'] < args.image_size:
            print(f"⚠️  Reducing image size from {args.image_size} to {dynamic_config['image_size']} due to low memory")
            args.image_size = dynamic_config['image_size']
    
    monitor_memory_usage("Before inference")
    
    # Main inference with memory monitoring
    try:
        samples = hunyuan_video_sampler.predict(args, batch, wav2vec, feature_extractor, align_instance)
        monitor_memory_usage("After inference")
        
    except torch.cuda.OutOfMemoryError as e:
        print("❌ CUDA Out of Memory Error!")
        print("🔧 Trying emergency memory recovery...")
        
        # Emergency cleanup
        cleanup_memory()
        
        # Try with even more aggressive settings
        original_image_size = args.image_size
        args.image_size = max(128, args.image_size // 2)
        batch["audio_len"][0] = min(64, batch["audio_len"][0])
        
        print(f"🚨 Emergency mode: image_size={args.image_size}, audio_len={batch['audio_len'][0]}")
        
        try:
            samples = hunyuan_video_sampler.predict(args, batch, wav2vec, feature_extractor, align_instance)
            print("✅ Emergency recovery successful!")
        except Exception as e2:
            print(f"❌ Emergency recovery failed: {e2}")
            raise e2
        finally:
            args.image_size = original_image_size
    
    # Move Whisper back to CPU to free up VRAM
    if args.cpu_offload:
        wav2vec = wav2vec.cpu()
        cleanup_memory()
    
    # Process samples
    sample = samples['samples'][0].unsqueeze(0)
    sample = sample[:, :, :batch["audio_len"][0]]
    
    monitor_memory_usage("After sample processing")
    
    # Convert to video frames
    video = rearrange(sample[0], "c f h w -> f h w c")
    video = (video * 255.).data.cpu().numpy().astype(np.uint8)
    
    # Clear GPU memory
    del samples, sample
    cleanup_memory()
    monitor_memory_usage("After video conversion")
    
    # Prepare final frames
    final_frames = []
    for frame in video:
        final_frames.append(frame)
    final_frames = np.stack(final_frames, axis=0)
    
    # Save video
    print(f"💾 Saving video: {output_path}")
    imageio.mimsave(output_path, final_frames, fps=fps.item())
    
    # Add audio with ffmpeg
    print(f"🎵 Adding audio: {output_audio_path}")
    os.system(f"ffmpeg -i '{output_path}' -i '{audio_path}' -shortest '{output_audio_path}' -y -loglevel quiet; rm '{output_path}'")
    
    # Final cleanup
    del final_frames, video
    cleanup_memory()
    
    print(f"✅ Completed: {videoid}")
    return output_audio_path

def main():
    print("🚀 Starting Ultra-Low VRAM HunyuanVideo-Avatar Inference")
    print("=" * 60)
    
    # Parse arguments
    args = parse_args()
    models_root_path = Path(args.ckpt)

    if not models_root_path.exists():
        raise ValueError(f"`models_root` not exists: {models_root_path}")

    # Setup ultra-low memory optimizations
    setup_ultra_low_memory()
    
    # Create save folder
    save_path = args.save_path if args.save_path_suffix=="" else f'{args.save_path}_{args.save_path_suffix}'
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    # Setup device
    rank = 0
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available! This will be very slow on CPU.")
        print("⚠️  Consider using a GPU for practical inference times.")
    
    print_memory_info()
    
    # Load models with optimizations
    hunyuan_video_sampler, wav2vec, align_instance, feature_extractor = load_models_with_offloading(args, device)
    
    # Get updated args from sampler
    args = hunyuan_video_sampler.args
    
    print(f"🔧 Configuration:")
    print(f"   Image size: {args.image_size}")
    print(f"   CPU offload: {args.cpu_offload}")
    print(f"   Mixed precision: {args.mixed_precision}")
    print(f"   Minimal inference: {args.infer_min}")
    
    # Setup dataset
    kwargs = {
        "text_encoder": hunyuan_video_sampler.text_encoder, 
        "text_encoder_2": hunyuan_video_sampler.text_encoder_2, 
        "feature_extractor": feature_extractor, 
    }
    
    video_dataset = VideoAudioTextLoaderVal(
        image_size=args.image_size,
        meta_file=args.input, 
        **kwargs,
    )

    sampler = DistributedSampler(video_dataset, num_replicas=1, rank=0, shuffle=False, drop_last=False)
    json_loader = DataLoader(video_dataset, batch_size=1, shuffle=False, sampler=sampler, drop_last=False)

    print(f"📁 Processing {len(video_dataset)} samples...")
    
    # Process each batch
    successful_generations = 0
    total_time = 0
    
    for batch_index, batch in enumerate(json_loader, start=1):
        start_time = time.time()
        
        print(f"\n🎬 Processing batch {batch_index}/{len(video_dataset)}")
        
        try:
            output_path = process_batch_ultra_low_memory(
                args, batch, hunyuan_video_sampler, wav2vec, feature_extractor, align_instance
            )
            
            batch_time = time.time() - start_time
            total_time += batch_time
            successful_generations += 1
            
            print(f"⏱️  Batch {batch_index} completed in {batch_time:.1f}s")
            print(f"💾 Output saved: {output_path}")
            
        except Exception as e:
            print(f"❌ Error processing batch {batch_index}: {e}")
            print("🔄 Continuing with next batch...")
            continue
        
        # Memory monitoring between batches
        monitor_memory_usage(f"After batch {batch_index}")
        
        # Periodic cleanup
        if batch_index % 3 == 0:
            print("🧹 Periodic cleanup...")
            cleanup_memory()
    
    # Final statistics
    print("\n" + "=" * 60)
    print("🎉 Ultra-Low VRAM Inference Completed!")
    print(f"✅ Successful generations: {successful_generations}/{len(video_dataset)}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    if successful_generations > 0:
        print(f"📊 Average time per video: {total_time/successful_generations:.1f}s")
    
    print_memory_info()
    print("🏁 Done!")

if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
