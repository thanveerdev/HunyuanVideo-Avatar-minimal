"""
Unit tests for hymm_sp/inference.py module.
Tests model loading, device management, and inference pipeline.
"""

import pytest
import torch
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hymm_sp.inference import Inference


class TestInference:
    """Test suite for Inference class."""

    def test_inference_initialization(self, mock_inference_args, mock_device):
        """Test Inference class initialization."""
        mock_vae = MagicMock()
        mock_text_encoder = MagicMock()
        mock_model = MagicMock()
        
        inference = Inference(
            args=mock_inference_args,
            vae=mock_vae,
            vae_kwargs={"s_ratio": 1, "t_ratio": 1},
            text_encoder=mock_text_encoder,
            model=mock_model,
            device=mock_device
        )
        
        assert inference.vae == mock_vae
        assert inference.text_encoder == mock_text_encoder
        assert inference.model == mock_model
        assert inference.device == mock_device
        assert inference.args == mock_inference_args

    def test_inference_initialization_with_defaults(self, mock_inference_args):
        """Test Inference initialization with default device."""
        mock_vae = MagicMock()
        mock_text_encoder = MagicMock()
        mock_model = MagicMock()
        
        with patch('torch.cuda.is_available', return_value=True):
            inference = Inference(
                args=mock_inference_args,
                vae=mock_vae,
                vae_kwargs={"s_ratio": 1, "t_ratio": 1},
                text_encoder=mock_text_encoder,
                model=mock_model
            )
            
            assert str(inference.device) == "cuda"

    def test_inference_initialization_cpu_fallback(self, mock_inference_args):
        """Test Inference initialization falls back to CPU when CUDA unavailable."""
        mock_vae = MagicMock()
        mock_text_encoder = MagicMock()
        mock_model = MagicMock()
        
        with patch('torch.cuda.is_available', return_value=False):
            inference = Inference(
                args=mock_inference_args,
                vae=mock_vae,
                vae_kwargs={"s_ratio": 1, "t_ratio": 1},
                text_encoder=mock_text_encoder,
                model=mock_model
            )
            
            assert str(inference.device) == "cpu"

    def test_parse_size_integer(self):
        """Test parse_size with integer input."""
        result = Inference.parse_size(256)
        assert result == [256, 256]

    def test_parse_size_list(self):
        """Test parse_size with list input."""
        result = Inference.parse_size([256, 512])
        assert result == [256, 512]

    def test_parse_size_tuple(self):
        """Test parse_size with tuple input."""
        result = Inference.parse_size((256, 512))
        assert result == [256, 512]

    def test_parse_size_single_element_list(self):
        """Test parse_size with single element list."""
        result = Inference.parse_size([256])
        assert result == [256, 256]

    def test_parse_size_invalid_type(self):
        """Test parse_size with invalid type."""
        with pytest.raises(ValueError, match="Size must be an integer or"):
            Inference.parse_size("invalid")

    def test_parse_size_invalid_length(self):
        """Test parse_size with invalid length."""
        with pytest.raises(ValueError, match="Size must be an integer or"):
            Inference.parse_size([256, 512, 128])

    @patch('torch.load')
    def test_load_state_dict_success(self, mock_torch_load, mock_inference_args):
        """Test successful state dict loading."""
        mock_model = MagicMock()
        mock_state_dict = {"model": {"key": "value"}}
        mock_torch_load.return_value = mock_state_dict
        
        mock_inference_args.load_key = "model"
        
        result = Inference.load_state_dict(mock_inference_args, mock_model, "test_path.pt")
        
        assert result == mock_model
        mock_model.load_state_dict.assert_called_once_with({"key": "value"}, strict=False)

    @patch('torch.load')
    def test_load_state_dict_dot_key(self, mock_torch_load, mock_inference_args):
        """Test state dict loading with dot key."""
        mock_model = MagicMock()
        mock_state_dict = {"key": "value"}
        mock_torch_load.return_value = mock_state_dict
        
        mock_inference_args.load_key = "."
        
        result = Inference.load_state_dict(mock_inference_args, mock_model, "test_path.pt")
        
        assert result == mock_model
        mock_model.load_state_dict.assert_called_once_with(mock_state_dict, strict=False)

    @patch('torch.load')
    def test_load_state_dict_missing_key(self, mock_torch_load, mock_inference_args):
        """Test state dict loading with missing key."""
        mock_model = MagicMock()
        mock_state_dict = {"other_key": "value"}
        mock_torch_load.return_value = mock_state_dict
        
        mock_inference_args.load_key = "missing_key"
        
        with pytest.raises(KeyError, match="Key 'missing_key' not found"):
            Inference.load_state_dict(mock_inference_args, mock_model, "test_path.pt")

    @patch('torch.load')
    @patch('pathlib.Path.glob')
    @patch('pathlib.Path.is_dir')
    def test_load_state_dict_directory_path(self, mock_is_dir, mock_glob, mock_torch_load, mock_inference_args):
        """Test state dict loading from directory path."""
        mock_model = MagicMock()
        mock_state_dict = {"model": {"key": "value"}}
        mock_torch_load.return_value = mock_state_dict
        
        mock_is_dir.return_value = True
        mock_glob.return_value = [Path("test_model_states.pt")]
        mock_inference_args.load_key = "model"
        
        result = Inference.load_state_dict(mock_inference_args, mock_model, "test_dir")
        
        assert result == mock_model
        mock_model.load_state_dict.assert_called_once_with({"key": "value"}, strict=False)

    @patch('hymm_sp.vae.load_vae')
    @patch('hymm_sp.modules.load_model')
    @patch('hymm_sp.text_encoder.TextEncoder')
    @patch('torch.cuda.is_available')
    def test_from_pretrained_basic(self, mock_cuda, mock_text_encoder, mock_load_model, mock_load_vae, mock_inference_args):
        """Test basic from_pretrained functionality."""
        mock_cuda.return_value = True
        
        # Mock VAE loading
        mock_vae = MagicMock()
        mock_load_vae.return_value = (mock_vae, None, 1, 1)
        
        # Mock model loading
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock text encoder
        mock_text_encoder_instance = MagicMock()
        mock_text_encoder.return_value = mock_text_encoder_instance
        
        with patch.object(Inference, 'load_state_dict', return_value=mock_model):
            inference = Inference.from_pretrained("test_path", mock_inference_args)
            
            assert inference.vae == mock_vae
            assert inference.model == mock_model
            assert inference.text_encoder == mock_text_encoder_instance

    @patch('hymm_sp.vae.load_vae')
    @patch('hymm_sp.modules.load_model')
    @patch('hymm_sp.text_encoder.TextEncoder')
    @patch('torch.cuda.is_available')
    def test_from_pretrained_cpu_offload(self, mock_cuda, mock_text_encoder, mock_load_model, mock_load_vae, mock_inference_args):
        """Test from_pretrained with CPU offload."""
        mock_cuda.return_value = True
        mock_inference_args.cpu_offload = True
        
        # Mock VAE loading
        mock_vae = MagicMock()
        mock_load_vae.return_value = (mock_vae, None, 1, 1)
        
        # Mock model loading
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock text encoder
        mock_text_encoder_instance = MagicMock()
        mock_text_encoder.return_value = mock_text_encoder_instance
        
        with patch.object(Inference, 'load_state_dict', return_value=mock_model):
            with patch('torch.cuda.empty_cache') as mock_empty_cache:
                inference = Inference.from_pretrained("test_path", mock_inference_args)
                
                # Check CPU offload was applied
                mock_model.to.assert_called_with('cpu')
                mock_empty_cache.assert_called()

    @patch('hymm_sp.vae.load_vae')
    @patch('hymm_sp.modules.load_model')
    @patch('hymm_sp.text_encoder.TextEncoder')
    @patch('torch.cuda.is_available')
    def test_from_pretrained_fp8_optimization(self, mock_cuda, mock_text_encoder, mock_load_model, mock_load_vae, mock_inference_args):
        """Test from_pretrained with FP8 optimization."""
        mock_cuda.return_value = True
        mock_inference_args.use_fp8 = True
        
        # Mock VAE loading
        mock_vae = MagicMock()
        mock_load_vae.return_value = (mock_vae, None, 1, 1)
        
        # Mock model loading
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock text encoder
        mock_text_encoder_instance = MagicMock()
        mock_text_encoder.return_value = mock_text_encoder_instance
        
        with patch.object(Inference, 'load_state_dict', return_value=mock_model):
            with patch('hymm_sp.modules.fp8_optimization.convert_fp8_linear') as mock_fp8_convert:
                inference = Inference.from_pretrained("test_path", mock_inference_args)
                
                # Check FP8 optimization was applied
                mock_fp8_convert.assert_called_once()

    def test_get_exp_dir_and_ckpt_id_standard_path(self):
        """Test extracting experiment directory from standard checkpoint path."""
        inference = Inference(
            args=MagicMock(),
            vae=MagicMock(),
            vae_kwargs={},
            text_encoder=MagicMock(),
            model=MagicMock()
        )
        inference.ckpt = Path("/path/to/exp/checkpoints/step_1000/model.pt")
        
        with patch.object(Path, 'parents') as mock_parents:
            # Mock the path hierarchy
            mock_parents.__getitem__.side_effect = lambda x: {
                1: MagicMock(name="checkpoints"),
                2: Path("/path/to/exp")
            }[x]
            
            exp_dir, ckpt_id = inference.get_exp_dir_and_ckpt_id()
            
            assert exp_dir == Path("/path/to/exp")
            assert ckpt_id == "step_1000"

    def test_get_exp_dir_and_ckpt_id_no_checkpoint(self):
        """Test error when no checkpoint path provided."""
        inference = Inference(
            args=MagicMock(),
            vae=MagicMock(),
            vae_kwargs={},
            text_encoder=MagicMock(),
            model=MagicMock()
        )
        inference.ckpt = None
        
        with pytest.raises(ValueError, match="checkpoint path is not provided"):
            inference.get_exp_dir_and_ckpt_id()

    def test_get_exp_dir_and_ckpt_id_invalid_path(self):
        """Test error with invalid checkpoint path."""
        inference = Inference(
            args=MagicMock(),
            vae=MagicMock(),
            vae_kwargs={},
            text_encoder=MagicMock(),
            model=MagicMock()
        )
        inference.ckpt = Path("/invalid/path/model.pt")
        
        with patch.object(Path, 'parents') as mock_parents:
            mock_parents.__getitem__.side_effect = lambda x: {
                1: MagicMock(name="not_checkpoints"),
                2: Path("/invalid/path")
            }[x]
            
            with pytest.raises(ValueError, match="cannot infer the experiment directory"):
                inference.get_exp_dir_and_ckpt_id()


class TestInferenceIntegration:
    """Integration tests for Inference class."""

    @patch('hymm_sp.vae.load_vae')
    @patch('hymm_sp.modules.load_model')
    @patch('hymm_sp.text_encoder.TextEncoder')
    @patch('torch.cuda.is_available')
    @patch('torch.set_grad_enabled')
    def test_complete_initialization_flow(self, mock_grad, mock_cuda, mock_text_encoder, mock_load_model, mock_load_vae, mock_inference_args):
        """Test complete initialization flow."""
        mock_cuda.return_value = True
        
        # Mock all components
        mock_vae = MagicMock()
        mock_load_vae.return_value = (mock_vae, None, 1, 1)
        
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        mock_text_encoder_instance = MagicMock()
        mock_text_encoder.return_value = mock_text_encoder_instance
        
        with patch.object(Inference, 'load_state_dict', return_value=mock_model):
            inference = Inference.from_pretrained("test_path", mock_inference_args)
            
            # Verify all components were initialized
            assert inference.vae is not None
            assert inference.model is not None
            assert inference.text_encoder is not None
            
            # Verify gradient was disabled
            mock_grad.assert_called_with(False)

    @patch('hymm_sp.vae.load_vae')
    @patch('hymm_sp.modules.load_model')
    @patch('hymm_sp.text_encoder.TextEncoder')
    @patch('torch.cuda.is_available')
    def test_dual_text_encoder_setup(self, mock_cuda, mock_text_encoder, mock_load_model, mock_load_vae, mock_inference_args):
        """Test setup with dual text encoders."""
        mock_cuda.return_value = True
        mock_inference_args.text_encoder_2 = "second_encoder"
        
        # Mock VAE loading
        mock_vae = MagicMock()
        mock_load_vae.return_value = (mock_vae, None, 1, 1)
        
        # Mock model loading
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model
        
        # Mock text encoders
        mock_text_encoder_instance_1 = MagicMock()
        mock_text_encoder_instance_2 = MagicMock()
        mock_text_encoder.side_effect = [mock_text_encoder_instance_1, mock_text_encoder_instance_2]
        
        with patch.object(Inference, 'load_state_dict', return_value=mock_model):
            inference = Inference.from_pretrained("test_path", mock_inference_args)
            
            assert inference.text_encoder == mock_text_encoder_instance_1
            assert inference.text_encoder_2 == mock_text_encoder_instance_2
            
            # Verify both text encoders were created
            assert mock_text_encoder.call_count == 2 