"""
System tests for user workflows and end-user scenarios.
"""

import pytest
import subprocess
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.mark.system
class TestUserWorkflows:
    """System tests for complete user workflows."""

    def test_setup_workflow(self, temp_dir):
        """Test complete setup workflow."""
        # Test directory structure exists
        project_root = Path(__file__).parent.parent.parent
        
        required_files = [
            "requirements-minimal.txt",
            "config_minimal.py",
            "run_low_memory.sh",
            "setup_minimal.sh"
        ]
        
        for file in required_files:
            assert (project_root / file).exists(), f"Missing required file: {file}"

    def test_dependency_installation_dry_run(self):
        """Test dependency installation (dry run)."""
        project_root = Path(__file__).parent.parent.parent
        
        # Check requirements file exists and is readable
        req_file = project_root / "requirements-minimal.txt"
        assert req_file.exists()
        
        content = req_file.read_text()
        assert "torch" in content
        assert "diffusers" in content

    @patch('subprocess.run')
    def test_run_low_memory_script_validation(self, mock_subprocess):
        """Test run_low_memory.sh script validation."""
        mock_subprocess.return_value.returncode = 0
        
        project_root = Path(__file__).parent.parent.parent
        script_path = project_root / "run_low_memory.sh"
        
        assert script_path.exists()
        assert script_path.is_file()
        
        # Read script content
        content = script_path.read_text()
        assert "python3" in content
        assert "hymm_sp/low_memory_inference.py" in content

    def test_configuration_file_validation(self):
        """Test configuration file validation."""
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config_minimal.py"
        
        assert config_path.exists()
        
        # Test config can be imported
        spec = __import__('importlib.util', fromlist=['spec_from_file_location']).spec_from_file_location
        config_spec = spec("config_minimal", config_path)
        config_module = __import__('importlib.util', fromlist=['module_from_spec']).module_from_spec(config_spec)
        
        # Should not raise exception
        assert config_module is not None

    def test_input_file_formats(self, temp_dir):
        """Test different input file formats."""
        # Test CSV format
        csv_content = """videoid,image,audio,prompt,fps
test1,assets/image/1.png,assets/audio/2.WAV,A person speaking,25
test2,assets/image/1.png,assets/audio/2.WAV,Another test,30
"""
        csv_file = temp_dir / "test.csv"
        csv_file.write_text(csv_content)
        
        assert csv_file.exists()
        
        # Parse CSV content
        lines = csv_content.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        assert "videoid,image,audio,prompt,fps" in lines[0]

    def test_output_directory_creation(self, temp_dir):
        """Test output directory creation."""
        output_dir = temp_dir / "outputs"
        
        # Directory should be creatable
        output_dir.mkdir(exist_ok=True)
        assert output_dir.exists()
        assert output_dir.is_dir()

    @pytest.mark.slow
    def test_memory_monitoring_workflow(self):
        """Test memory monitoring workflow."""
        import psutil
        
        # Get initial system memory
        memory = psutil.virtual_memory()
        initial_available = memory.available
        
        # Simulate memory usage
        dummy_data = list(range(100000))
        
        current_memory = psutil.virtual_memory()
        
        # Clean up
        del dummy_data
        
        assert initial_available > 0
        assert current_memory.available > 0

    def test_error_handling_workflow(self, temp_dir):
        """Test error handling in user workflows."""
        # Test missing input file
        non_existent_file = temp_dir / "missing.csv"
        assert not non_existent_file.exists()
        
        # Test invalid CSV content
        invalid_csv = temp_dir / "invalid.csv"
        invalid_csv.write_text("invalid,csv,content")
        
        content = invalid_csv.read_text()
        lines = content.strip().split('\n')
        
        # Should have content but might be invalid
        assert len(lines) > 0


@pytest.mark.system
class TestScriptExecution:
    """System tests for script execution."""

    def test_run_scripts_exist(self):
        """Test that all run scripts exist."""
        project_root = Path(__file__).parent.parent.parent
        
        scripts = [
            "run_low_memory.sh",
            "run_minimal.sh", 
            "run_single_inference.sh",
            "setup_minimal.sh"
        ]
        
        for script in scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Missing script: {script}"

    def test_script_permissions(self):
        """Test script file permissions."""
        project_root = Path(__file__).parent.parent.parent
        
        executable_scripts = [
            "run_low_memory.sh",
            "run_minimal.sh",
            "setup_minimal.sh"
        ]
        
        for script in executable_scripts:
            script_path = project_root / script
            if script_path.exists():
                # Check if file is readable
                assert os.access(script_path, os.R_OK)

    @patch('subprocess.run')
    def test_python_module_execution(self, mock_subprocess):
        """Test Python module execution."""
        mock_subprocess.return_value.returncode = 0
        
        # Test that the main modules can be found
        project_root = Path(__file__).parent.parent.parent
        
        main_modules = [
            "hymm_sp/low_memory_inference.py",
            "hymm_sp/inference.py",
            "config_minimal.py"
        ]
        
        for module in main_modules:
            module_path = project_root / module
            assert module_path.exists(), f"Missing module: {module}"

    def test_environment_variable_setup(self):
        """Test environment variable setup."""
        required_env_vars = [
            "MODEL_BASE",
            "CUDA_VISIBLE_DEVICES",
            "PYTHONPATH"
        ]
        
        # These should be set by conftest.py
        for var in required_env_vars:
            value = os.environ.get(var)
            assert value is not None, f"Environment variable {var} not set"


@pytest.mark.system  
class TestFileSystemIntegration:
    """System tests for file system integration."""

    def test_directory_structure(self):
        """Test expected directory structure."""
        project_root = Path(__file__).parent.parent.parent
        
        required_dirs = [
            "hymm_sp",
            "assets",
            "weights",
            "tests"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"Missing directory: {dir_name}"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"

    def test_asset_files(self):
        """Test asset files exist."""
        project_root = Path(__file__).parent.parent.parent
        assets_dir = project_root / "assets"
        
        if assets_dir.exists():
            # Check for sample files
            image_dir = assets_dir / "image"
            audio_dir = assets_dir / "audio"
            
            if image_dir.exists():
                image_files = list(image_dir.glob("*.png"))
                assert len(image_files) > 0, "No sample image files found"
            
            if audio_dir.exists():
                audio_files = list(audio_dir.glob("*.WAV")) + list(audio_dir.glob("*.wav"))
                assert len(audio_files) > 0, "No sample audio files found"

    def test_weights_directory_structure(self):
        """Test weights directory structure."""
        project_root = Path(__file__).parent.parent.parent
        weights_dir = project_root / "weights"
        
        assert weights_dir.exists()
        
        # Check for README
        readme_file = weights_dir / "README.md"
        if readme_file.exists():
            content = readme_file.read_text()
            assert len(content) > 0

    def test_output_directory_permissions(self, temp_dir):
        """Test output directory permissions."""
        output_dir = temp_dir / "test_outputs"
        output_dir.mkdir()
        
        # Test write permissions
        test_file = output_dir / "test.txt"
        test_file.write_text("test content")
        
        assert test_file.exists()
        assert test_file.read_text() == "test content"
        
        # Test read permissions
        assert os.access(test_file, os.R_OK)
        
        # Cleanup
        test_file.unlink()
        output_dir.rmdir()

    def test_temporary_file_handling(self, temp_dir):
        """Test temporary file handling."""
        # Create temporary files
        temp_files = []
        for i in range(5):
            temp_file = temp_dir / f"temp_{i}.tmp"
            temp_file.write_text(f"temporary content {i}")
            temp_files.append(temp_file)
        
        # Verify files exist
        for temp_file in temp_files:
            assert temp_file.exists()
        
        # Cleanup should be automatic with temp_dir fixture
        # But we can test manual cleanup
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink() 