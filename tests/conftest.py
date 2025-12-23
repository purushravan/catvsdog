"""
Pytest configuration and fixtures for Cat vs Dog classifier tests
"""
import pytest
import sys
from pathlib import Path
import numpy as np

# Add project root to path
root = Path(__file__).parents[1]
sys.path.append(str(root))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture
def dummy_image():
    """Fixture providing a dummy image array"""
    from catvsdog_model.config.core import config
    return np.random.rand(*config.model_cfg.input_shape).astype(np.float32)


@pytest.fixture
def dummy_batch():
    """Fixture providing a batch of dummy images"""
    from catvsdog_model.config.core import config
    batch_size = 4
    return np.random.rand(batch_size, *config.model_cfg.input_shape).astype(np.float32)


@pytest.fixture
def dummy_labels():
    """Fixture providing dummy labels"""
    batch_size = 4
    return np.random.randint(0, 2, size=(batch_size, 1)).astype(np.float32)


@pytest.fixture(scope="session")
def model_config():
    """Fixture providing model configuration"""
    from catvsdog_model.config.core import config
    return config


@pytest.fixture(scope="session")
def classifier_model():
    """Fixture providing the classifier model"""
    from catvsdog_model.model import classifier
    return classifier


@pytest.fixture
def temp_model_path(tmp_path):
    """Fixture providing a temporary path for model saving"""
    model_path = tmp_path / "test_model.keras"
    return model_path
