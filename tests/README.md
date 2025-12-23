# Cat vs Dog Classifier - Test Suite

## Overview

This directory contains the test suite for the Cat vs Dog image classifier project. Tests are written using pytest and cover model architecture, configuration, and data processing.

## Test Structure

```
tests/
├── __init__.py           # Test package marker
├── conftest.py          # Pytest fixtures and configuration
├── test_model.py        # Model architecture and prediction tests
├── test_config.py       # Configuration management tests
└── test_processing.py   # Data processing and features tests
```

## Running Tests

### Quick Start

Run all tests:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ -v --cov=catvsdog_model --cov-report=html
```

Run only fast tests (skip slow tests):
```bash
pytest tests/ -v -m "not slow"
```

### Specific Test Categories

Run only unit tests:
```bash
pytest tests/ -v -m unit
```

Run only integration tests:
```bash
pytest tests/ -v -m integration
```

Run tests in a specific file:
```bash
pytest tests/test_model.py -v
```

Run a specific test class:
```bash
pytest tests/test_model.py::TestModelArchitecture -v
```

Run a specific test:
```bash
pytest tests/test_model.py::TestModelArchitecture::test_model_exists -v
```

### Advanced Options

Run with detailed output:
```bash
pytest tests/ -vv --tb=long
```

Run and stop at first failure:
```bash
pytest tests/ -v -x
```

Run last failed tests:
```bash
pytest tests/ -v --lf
```

Generate HTML report:
```bash
pytest tests/ -v --html=test-report.html --self-contained-html
```

Run with coverage and open report:
```bash
pytest tests/ --cov=catvsdog_model --cov-report=html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Categories

### Model Tests (`test_model.py`)

**TestModelArchitecture**
- Model initialization and structure
- Input/output shape validation
- Layer composition
- Model compilation status

**TestModelPrediction**
- Prediction shape and range validation
- Batch processing
- Output format verification

**TestModelConfiguration**
- Configuration loading
- Parameter validation
- Optimizer and loss settings

**TestModelIntegration**
- Model summary generation
- Trainable parameters
- Single training step (slow test)

### Configuration Tests (`test_config.py`)

**TestConfigPaths**
- Package root validation
- Model directory paths
- Path absoluteness checks

**TestModelConfig**
- Input shape configuration
- Optimizer settings
- Loss function configuration
- Metric configuration

**TestAppConfig**
- Application settings
- Package name validation

**TestConfigIntegrity**
- Singleton behavior
- Immutability checks
- Required attributes validation

### Processing Tests (`test_processing.py`)

**TestDataAugmentation**
- Data augmentation imports
- Augmentation callable check

**TestDataManager**
- Data manager function imports
- Callbacks function validation

**TestImagePreprocessing**
- Image shape validation
- Scaling factor checks

**TestDatasetLoading** (slow)
- Dataset loader structure
- All loaders existence

**TestModelPersistence** (slow)
- Model saving capability
- Model loading capability

## Test Markers

Tests are marked with the following markers:

- `@pytest.mark.unit` - Unit tests (fast)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (model training, I/O operations)
- `@pytest.mark.gpu` - Tests requiring GPU

### Using Markers

Run only fast tests:
```bash
pytest tests/ -v -m "not slow"
```

Run only slow tests:
```bash
pytest tests/ -v -m slow
```

Run unit tests only:
```bash
pytest tests/ -v -m unit
```

## Fixtures

Common fixtures available in `conftest.py`:

- `dummy_image` - Single random image array
- `dummy_batch` - Batch of random images
- `dummy_labels` - Random binary labels
- `model_config` - Model configuration (session scope)
- `classifier_model` - Classifier model instance (session scope)
- `temp_model_path` - Temporary path for model saving

### Using Fixtures

```python
def test_example(dummy_image, model_config):
    """Test using fixtures"""
    assert dummy_image.shape == model_config.model_cfg.input_shape
```

## Coverage Reports

### Generate Coverage Report

```bash
pytest tests/ --cov=catvsdog_model --cov-report=html --cov-report=term
```

### View Coverage Report

```bash
# Terminal output shows coverage summary
# HTML report in htmlcov/index.html
open htmlcov/index.html
```

### Coverage Thresholds

Target coverage thresholds:
- Overall: 80%+
- Core modules (model.py, config/core.py): 90%+
- Processing modules: 75%+

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main
- Via Jenkins pipeline
- Via GitHub Actions (if configured)

### Jenkins Integration

The Jenkins pipeline runs:
```bash
pytest tests/ \
    --verbose \
    --cov=catvsdog_model \
    --cov-report=xml \
    --cov-report=html \
    --junit-xml=test-results.xml \
    --html=test-report.html
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test Structure

```python
"""
Module docstring describing test module
"""
import pytest

class TestFeature:
    """Test suite for specific feature"""

    def test_basic_functionality(self):
        """Test basic case"""
        assert True

    @pytest.mark.slow
    def test_expensive_operation(self):
        """Test that takes long time"""
        # Slow operation
        pass

    def test_with_fixture(self, dummy_image):
        """Test using fixture"""
        assert dummy_image is not None
```

### Best Practices

1. **Descriptive Names**: Use clear, descriptive test names
2. **Single Assertion**: Each test should ideally test one thing
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Mark Slow Tests**: Use `@pytest.mark.slow` for slow tests
5. **Use Fixtures**: Leverage fixtures for common setup
6. **Docstrings**: Add docstrings explaining what test does
7. **Error Messages**: Include helpful assertion messages

### Example Test

```python
def test_model_prediction_range(self):
    """Test that model predictions are between 0 and 1"""
    # Arrange
    dummy_input = np.random.rand(1, 180, 180, 3).astype(np.float32)

    # Act
    prediction = classifier.predict(dummy_input, verbose=0)

    # Assert
    assert np.all(prediction >= 0), "Predictions should be >= 0"
    assert np.all(prediction <= 1), "Predictions should be <= 1"
```

## Troubleshooting

### Common Issues

#### Import Errors

If you get import errors:
```bash
# Ensure you're in the project root
cd /path/to/catvsdog

# Install in development mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Module Not Found

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install requirements
pip install -r requirements/requirements.txt
```

#### TensorFlow Errors

```bash
# For M1/M2 Macs
pip install tensorflow-macos tensorflow-metal

# For other systems
pip install tensorflow
```

#### GPU Tests Fail

GPU tests are optional. Skip them if no GPU:
```bash
pytest tests/ -v -m "not gpu"
```

## Testing Locally Before Commit

Recommended pre-commit checks:

```bash
# 1. Run linting
flake8 catvsdog_model/ --max-line-length=120

# 2. Check formatting
black --check catvsdog_model/ --line-length=120

# 3. Run fast tests
pytest tests/ -v -m "not slow"

# 4. Check coverage
pytest tests/ --cov=catvsdog_model --cov-report=term-missing

# 5. If all pass, run full test suite
pytest tests/ -v
```

## Performance

### Test Execution Times

- Fast tests (no marker): ~5-10 seconds
- All tests (including slow): ~30-60 seconds
- With model training: ~10+ minutes (depending on GPU)

### Optimization Tips

1. **Skip slow tests** during development:
   ```bash
   pytest tests/ -m "not slow"
   ```

2. **Use pytest-xdist** for parallel execution:
   ```bash
   pip install pytest-xdist
   pytest tests/ -n auto
   ```

3. **Run only changed tests**:
   ```bash
   pytest tests/ --lf  # Last failed
   pytest tests/ --ff  # Failed first
   ```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [TensorFlow Testing](https://www.tensorflow.org/guide/test)

## Questions?

For issues with tests:
1. Check this README
2. Review test docstrings
3. Check Jenkins build logs
4. Review `conftest.py` for fixtures
5. Contact the development team
