#!/usr/bin/env python3
"""
FastAPI Server for HunyuanVideo-Avatar
CRITICAL: Apply TorchVision fix before any other imports to prevent circular import
"""

# =============================================================================
# CRITICAL: TorchVision Circular Import Fix
# This MUST be applied before any imports of transformers, diffusers, or HunyuanVideoSampler
# =============================================================================
import sys
import os
from unittest.mock import MagicMock

def apply_immediate_torchvision_fix():
    """Apply TorchVision fix immediately to prevent circular import"""
    print("🔧 Applying immediate TorchVision circular import fix...")
    
    # Set environment variables first
    os.environ['TORCH_OPERATOR_REGISTRATION_DISABLED'] = '1'
    os.environ['TORCHVISION_DISABLE_VIDEO_API'] = '1'
    os.environ['TORCHVISION_DISABLE_CUDA_OPS'] = '1'
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    
    # Only create mock if torchvision isn't already properly loaded
    if 'torchvision' not in sys.modules or not hasattr(sys.modules.get('torchvision', {}), '__version__'):
        print("   📦 Creating comprehensive TorchVision mock...")
        
        # Create the mock torchvision module
        mock_torchvision = MagicMock()
        
        # Mock the problematic extension module
        mock_extension = MagicMock()
        mock_extension._has_ops = MagicMock(return_value=False)
        mock_extension.nms = MagicMock()
        mock_extension.roi_align = MagicMock()
        mock_torchvision.extension = mock_extension
        
        # Mock transforms submodule with proper InterpolationMode
        mock_transforms = MagicMock()
        mock_transforms.InterpolationMode = type('InterpolationMode', (), {
            'BILINEAR': 2,
            'NEAREST': 0,
            'BICUBIC': 3
        })()
        mock_transforms.Compose = MagicMock()
        mock_transforms.Resize = MagicMock()
        mock_transforms.CenterCrop = MagicMock()
        mock_transforms.ToTensor = MagicMock()
        mock_transforms.Normalize = MagicMock()
        mock_transforms.ToPILImage = MagicMock()
        mock_torchvision.transforms = mock_transforms
        
        # Mock _meta_registrations to prevent the circular import
        mock_meta = MagicMock()
        mock_torchvision._meta_registrations = mock_meta
        
        # Mock other commonly used modules
        mock_torchvision.datasets = MagicMock()
        mock_torchvision.io = MagicMock()
        mock_torchvision.models = MagicMock()
        mock_torchvision.ops = MagicMock()
        mock_torchvision.utils = MagicMock()
        
        # Set version and spec to prevent version checks from failing
        mock_torchvision.__version__ = "0.16.0"
        mock_torchvision.__spec__ = MagicMock()
        mock_torchvision.__spec__.name = "torchvision"
        
        # Install the mock in sys.modules
        sys.modules['torchvision'] = mock_torchvision
        sys.modules['torchvision.extension'] = mock_extension
        sys.modules['torchvision.transforms'] = mock_transforms
        sys.modules['torchvision._meta_registrations'] = mock_meta
        sys.modules['torchvision.ops'] = mock_torchvision.ops
        sys.modules['torchvision.models'] = mock_torchvision.models
        sys.modules['torchvision.utils'] = mock_torchvision.utils
        sys.modules['torchvision.datasets'] = mock_torchvision.datasets
        sys.modules['torchvision.io'] = mock_torchvision.io
        
        print("   ✅ TorchVision mock installed successfully")
    
    print("   ✅ Immediate TorchVision fix applied successfully")
    return True

# Apply the fix immediately
apply_immediate_torchvision_fix()

# =============================================================================
# Safe imports after TorchVision fix
# =============================================================================
import numpy as np
import torch
import warnings
import threading
import traceback
import uvicorn
from fastapi import FastAPI, Body
from pathlib import Path
from datetime import datetime
import torch.distributed as dist

# Add workspace to Python path to fix import issues
sys.path.insert(0, '/workspace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now safe to import our modules
from hymm_gradio.pipeline_utils import *
from hymm_sp.config import parse_args
from hymm_sp.audio_video_inference import HunyuanVideoSampler

from hymm_sp.modules.parallel_states import (
    initialize_distributed,
    nccl_info,
)

from transformers import WhisperModel
from transformers import AutoFeatureExtractor
from hymm_sp.data_kits.face_align import AlignImage


warnings.filterwarnings("ignore")
MODEL_OUTPUT_PATH = os.environ.get('MODEL_BASE')
app = FastAPI()
rlock = threading.RLock()



@app.api_route('/predict2', methods=['GET', 'POST'])
def predict(data=Body(...)):
    is_acquire = False
    error_info = ""
    try:
        is_acquire = rlock.acquire(blocking=False)
        if is_acquire:
            res = predict_wrap(data)
            return res
    except Exception as e:
        error_info = traceback.format_exc()
        print(error_info)
    finally:
        if is_acquire:
            rlock.release()
    return {"errCode": -1, "info": "broken"}

def predict_wrap(input_dict={}):
    if nccl_info.sp_size > 1:
        device = torch.device(f"cuda:{torch.distributed.get_rank()}")
        rank = local_rank = torch.distributed.get_rank()
        print(f"sp_size={nccl_info.sp_size}, rank {rank} local_rank {local_rank}")
    try:
        print(f"----- rank = {rank}")
        if rank == 0:
            input_dict = process_input_dict(input_dict)

            print('------- start to predict -------')
            # Parse input arguments
            image_path = input_dict["image_path"]
            driving_audio_path = input_dict["audio_path"]

            prompt = input_dict["prompt"]

            save_fps = input_dict.get("save_fps", 25)


            ret_dict = None
            if image_path is None or driving_audio_path is None:
                ret_dict = {
                    "errCode": -3, 
                    "content": [
                        {
                            "buffer": None
                        },
                    ], 
                    "info": "input content is not valid", 
                }

                print(f"errCode: -3, input content is not valid!")
                return ret_dict

            # Preprocess input batch
            torch.cuda.synchronize()

            a = datetime.now()
            
            try:
                model_kwargs_tmp = data_preprocess_server(
                                        args, image_path, driving_audio_path, prompt, feature_extractor
                                        )
            except:
                ret_dict = {
                    "errCode": -2,         
                    "content": [
                            {
                                "buffer": None
                            },
                        ],
                    "info": "failed to preprocess input data"
                }
                print(f"errCode: -2, preprocess failed!")
                return ret_dict

            text_prompt = model_kwargs_tmp["text_prompt"]
            audio_path = model_kwargs_tmp["audio_path"]
            image_path = model_kwargs_tmp["image_path"]
            fps = model_kwargs_tmp["fps"]
            audio_prompts = model_kwargs_tmp["audio_prompts"]
            audio_len = model_kwargs_tmp["audio_len"]
            motion_bucket_id_exps = model_kwargs_tmp["motion_bucket_id_exps"]
            motion_bucket_id_heads = model_kwargs_tmp["motion_bucket_id_heads"]
            pixel_value_ref = model_kwargs_tmp["pixel_value_ref"]
            pixel_value_ref_llava = model_kwargs_tmp["pixel_value_ref_llava"]
            


            torch.cuda.synchronize()
            b = datetime.now()
            preprocess_time = (b - a).total_seconds()
            print("="*100)
            print("preprocess time :", preprocess_time)
            print("="*100)
            
        else:
            text_prompt = None
            audio_path = None
            image_path = None
            fps = None
            audio_prompts = None
            audio_len = None
            motion_bucket_id_exps = None
            motion_bucket_id_heads = None
            pixel_value_ref = None
            pixel_value_ref_llava = None

    except:
        traceback.print_exc()
        if rank == 0:
            ret_dict = {
                "errCode": -1,         # Failed to generate video
                "content":[
                    {
                        "buffer": None
                    }
                ],
                "info": "failed to preprocess",
            }
            return ret_dict

    try:
        broadcast_params = [
            text_prompt,
            audio_path,
            image_path,
            fps,
            audio_prompts,
            audio_len,
            motion_bucket_id_exps,
            motion_bucket_id_heads,
            pixel_value_ref,
            pixel_value_ref_llava,
        ]
        dist.broadcast_object_list(broadcast_params, src=0)
        outputs = generate_image_parallel(*broadcast_params)

        if rank == 0:
            samples = outputs["samples"]
            sample = samples[0].unsqueeze(0)

            sample = sample[:, :, :audio_len[0]]
            
            video = sample[0].permute(1, 2, 3, 0).clamp(0, 1).numpy()
            video = (video * 255.).astype(np.uint8)

            output_dict = {
                "err_code": 0, 
                "err_msg": "succeed", 
                "video": video, 
                "audio": input_dict.get("audio_path", None), 
                "save_fps": save_fps, 
            }

            ret_dict = process_output_dict(output_dict)
            return ret_dict
    
    except:
        traceback.print_exc()
        if rank == 0:
            ret_dict = {
                "errCode": -1,         # Failed to generate video
                "content":[
                    {
                        "buffer": None
                    }
                ],
                "info": "failed to generate video",
            }
            return ret_dict
        
    return None
    
def generate_image_parallel(text_prompt,
                    audio_path,
                    image_path,
                    fps,
                    audio_prompts,
                    audio_len,
                    motion_bucket_id_exps,
                    motion_bucket_id_heads,
                    pixel_value_ref,
                    pixel_value_ref_llava
                    ):
    if nccl_info.sp_size > 1:
        device = torch.device(f"cuda:{torch.distributed.get_rank()}")

    batch = {
        "text_prompt": text_prompt,
        "audio_path": audio_path,
        "image_path": image_path,
        "fps": fps,
        "audio_prompts": audio_prompts,
        "audio_len": audio_len,
        "motion_bucket_id_exps": motion_bucket_id_exps,
        "motion_bucket_id_heads": motion_bucket_id_heads,
        "pixel_value_ref": pixel_value_ref,
        "pixel_value_ref_llava": pixel_value_ref_llava
    }

    samples = hunyuan_sampler.predict(args, batch, wav2vec, feature_extractor, align_instance)
    return samples

def worker_loop():
    while True:
        predict_wrap()
        

if __name__ == "__main__":
    audio_args = parse_args()
    initialize_distributed(audio_args.seed)
    hunyuan_sampler = HunyuanVideoSampler.from_pretrained(
        audio_args.ckpt, args=audio_args)
    args = hunyuan_sampler.args
    
    rank = local_rank = 0
    device = torch.device("cuda")
    if nccl_info.sp_size > 1:
        device = torch.device(f"cuda:{torch.distributed.get_rank()}")
        rank = local_rank = torch.distributed.get_rank()

    feature_extractor = AutoFeatureExtractor.from_pretrained(f"{MODEL_OUTPUT_PATH}/ckpts/whisper-tiny/")
    wav2vec = WhisperModel.from_pretrained(f"{MODEL_OUTPUT_PATH}/ckpts/whisper-tiny/").to(device=device, dtype=torch.float32)
    wav2vec.requires_grad_(False)


    BASE_DIR = f'{MODEL_OUTPUT_PATH}/ckpts/det_align/'
    det_path = os.path.join(BASE_DIR, 'detface.pt')    
    align_instance = AlignImage("cuda", det_path=det_path)



    if rank == 0:
        uvicorn.run(app, host="0.0.0.0", port=80)
    else:
        worker_loop()
    
