# HunyuanVideo-Avatar-minimal Test Suite

This directory contains a comprehensive test suite for the HunyuanVideo-Avatar-minimal project, designed to ensure reliability, performance, and functionality across different hardware configurations and use cases.

## 📋 Test Structure

```
tests/
├── conftest.py                     # Global test configuration and fixtures
├── fixtures/                      # Test data and mock files
├── unit/                          # Unit tests for individual components
│   ├── test_config_minimal.py     # Configuration system tests
│   ├── test_inference.py          # Core inference functionality
│   └── test_audio_processing.py   # Audio processing components
├── integration/                   # Integration tests for component interaction
│   └── test_end_to_end.py         # End-to-end pipeline tests
├── performance/                   # Performance and memory tests
│   └── test_memory_usage.py       # Memory optimization validation
└── system/                        # System and deployment tests
    ├── test_user_workflows.py     # User workflow validation
    └── test_docker_integration.py # Docker deployment tests
```

## 🚀 Quick Start

### Running Tests Locally

1. **Quick Tests** (Unit tests only):
   ```bash
   ./run_tests.sh quick
   # or
   python run_tests.py --suite quick
   ```

2. **All Tests**:
   ```bash
   ./run_tests.sh all
   # or
   python run_tests.py --suite all
   ```

3. **Specific Test Suite**:
   ```bash
   ./run_tests.sh unit
   ./run_tests.sh integration
   ./run_tests.sh performance
   ./run_tests.sh system
   ```

### Installing Dependencies

```bash
# Install test dependencies
./run_tests.sh install
# or
python run_tests.py --install-deps

# Manual installation
pip install -r test-requirements.txt
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Tests individual components in isolation:
- **Configuration Management**: Memory optimization, GPU detection
- **Inference Engine**: Model loading, device management
- **Audio Processing**: Feature extraction, synchronization
- **VAE/Diffusion**: Core model components

**Run with:**
```bash
pytest tests/unit/ -v --cov=hymm_sp
```

### Integration Tests (`tests/integration/`)
Tests component interaction and data flow:
- **End-to-End Pipeline**: Complete inference workflow
- **Memory Optimization**: CPU offloading, mixed precision
- **Audio-Video Sync**: Temporal alignment validation

**Run with:**
```bash
pytest tests/integration/ -v -m "not slow"
```

### Performance Tests (`tests/performance/`)
Tests memory usage, speed, and optimization:
- **Memory Limits**: 4GB, 8GB, 16GB+ scenarios
- **VRAM Management**: GPU memory optimization
- **Speed Benchmarks**: Inference performance metrics
- **Memory Leak Detection**: Long-running stability

**Run with:**
```bash
pytest tests/performance/ -v --benchmark-skip -m "not gpu"
```

### System Tests (`tests/system/`)
Tests complete user workflows and deployment:
- **User Workflows**: Setup, configuration, execution
- **Script Validation**: Shell script functionality
- **Docker Integration**: Container deployment scenarios
- **File System**: Directory structure, permissions

**Run with:**
```bash
pytest tests/system/ -v -m "not docker and not gpu"
```

## 🔧 Test Configuration

### Environment Variables
Tests automatically set these environment variables:
```bash
MODEL_BASE=./weights
PYTHONPATH=.
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

### Test Markers
Use pytest markers to categorize and filter tests:

```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run only GPU tests (requires GPU)
pytest -m gpu

# Skip Docker tests
pytest -m "not docker"

# Run benchmark tests
pytest -m benchmark --benchmark-only
```

Available markers:
- `unit`: Unit tests
- `integration`: Integration tests  
- `performance`: Performance tests
- `system`: System tests
- `gpu`: Tests requiring GPU
- `slow`: Slow running tests
- `docker`: Tests requiring Docker
- `benchmark`: Performance benchmarks

## 📊 Coverage Reports

Tests generate coverage reports in multiple formats:

1. **Terminal Output**: Shows missing lines during test run
2. **HTML Report**: Detailed coverage at `htmlcov/index.html`
3. **XML Report**: For CI/CD integration at `coverage.xml`

View HTML coverage report:
```bash
pytest tests/unit/ --cov=hymm_sp --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## 🎯 Test Scenarios

### Memory Optimization Testing
- **4GB VRAM**: Ultra-low memory mode, maximum CPU offloading
- **8GB VRAM**: Balanced mode, selective CPU offloading  
- **16GB+ VRAM**: High quality mode, minimal offloading
- **CPU-only**: Full CPU inference testing

### Hardware Compatibility
- **CUDA Available**: GPU-accelerated inference
- **CUDA Unavailable**: CPU fallback testing
- **Mixed Precision**: FP16/FP8 optimization validation
- **Memory Constraints**: Various VRAM limitations

### User Workflow Testing
- **First-time Setup**: Dependency installation, environment setup
- **Configuration**: Preset selection, custom settings
- **Input Processing**: CSV parsing, file validation
- **Output Generation**: Video creation, file saving
- **Error Handling**: Invalid inputs, insufficient resources

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH=.
   # or run from project root
   ```

2. **Missing Dependencies**:
   ```bash
   pip install -r test-requirements.txt
   ```

3. **GPU Tests Failing**:
   ```bash
   # Skip GPU tests if no GPU available
   pytest -m "not gpu"
   ```

4. **Memory Errors**:
   ```bash
   # Increase available memory or skip memory-intensive tests
   pytest -m "not slow"
   ```

### Test Data Issues
- Test fixtures are automatically created in `tests/fixtures/`
- Mock data is generated for audio/video processing
- Model weights are mocked for testing

### Docker Test Issues
```bash
# Ensure Docker is running
docker --version

# Build test image if needed
docker build -t hunyuan-avatar-test .
```

## 📝 Writing New Tests

### Test Structure
```python
import pytest
from unittest.mock import patch, MagicMock

class TestNewFeature:
    """Test suite for new feature."""
    
    def test_basic_functionality(self, sample_config):
        """Test basic functionality."""
        # Arrange
        input_data = sample_config
        
        # Act
        result = process_input(input_data)
        
        # Assert
        assert result is not None
        assert result.status == "success"
    
    @pytest.mark.gpu
    def test_gpu_functionality(self, skip_if_no_gpu):
        """Test GPU-specific functionality."""
        # This test will be skipped if no GPU
        pass
    
    @pytest.mark.slow
    def test_performance_intensive(self):
        """Test that takes a long time to run."""
        # Will be skipped in quick test runs
        pass
```

### Using Fixtures
```python
def test_with_fixtures(self, temp_dir, sample_audio, mock_model):
    """Test using multiple fixtures."""
    # temp_dir: Temporary directory for test files
    # sample_audio: Generated audio data
    # mock_model: Mocked model for testing
    pass
```

### Mocking External Dependencies
```python
@patch('torch.cuda.is_available')
def test_cuda_detection(self, mock_cuda):
    """Test CUDA availability detection."""
    mock_cuda.return_value = True
    # Test with CUDA available
    
    mock_cuda.return_value = False  
    # Test with CUDA unavailable
```

## 🔄 Continuous Integration

### GitHub Actions
The test suite is integrated with GitHub Actions for automated testing:
- **Unit Tests**: Run on every push/PR
- **Integration Tests**: Run on main branch
- **Performance Tests**: Run on schedule
- **Docker Tests**: Run on container changes

### Local CI Simulation
```bash
# Run the same tests as CI
./run_tests.sh all

# Check code quality
./run_tests.sh lint
```

## 📈 Performance Benchmarks

Performance tests include benchmarks for:
- **Inference Speed**: Time per frame generation
- **Memory Usage**: Peak VRAM/RAM consumption
- **Throughput**: Batch processing performance
- **Initialization Time**: Model loading speed

View benchmark results:
```bash
pytest tests/performance/ --benchmark-only --benchmark-json=results.json
```

## 🎓 Best Practices

1. **Write Tests First**: Follow TDD principles
2. **Use Descriptive Names**: Test names should explain what they test
3. **Mock External Dependencies**: Don't rely on external services
4. **Test Edge Cases**: Include boundary conditions and error cases
5. **Keep Tests Fast**: Use mocks and fixtures appropriately
6. **Organize by Functionality**: Group related tests in classes
7. **Use Appropriate Markers**: Tag tests for easy filtering
8. **Document Complex Tests**: Add docstrings for complex test logic

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [PyTorch Testing Best Practices](https://pytorch.org/docs/stable/notes/cuda.html#best-practices) 