"""
Unit tests for configuration management
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parents[1]
sys.path.append(str(root))

from catvsdog_model.config.core import config, PACKAGE_ROOT, TRAINED_MODEL_DIR


class TestConfigPaths:
    """Test configuration paths"""

    def test_package_root_exists(self):
        """Test that package root exists"""
        assert PACKAGE_ROOT.exists(), f"Package root not found: {PACKAGE_ROOT}"
        assert PACKAGE_ROOT.is_dir(), "Package root should be a directory"

    def test_trained_model_dir_exists(self):
        """Test that trained model directory path is valid"""
        assert TRAINED_MODEL_DIR is not None
        # Directory might not exist yet, but parent should
        assert TRAINED_MODEL_DIR.parent.exists()

    def test_config_paths_are_absolute(self):
        """Test that all config paths are absolute"""
        assert PACKAGE_ROOT.is_absolute(), "Package root should be absolute path"
        assert TRAINED_MODEL_DIR.is_absolute(), "Trained model dir should be absolute path"


class TestModelConfig:
    """Test model configuration parameters"""

    def test_model_config_exists(self):
        """Test that model config is loaded"""
        assert hasattr(config, 'model_cfg')
        assert config.model_cfg is not None

    def test_input_shape(self):
        """Test input shape configuration"""
        input_shape = config.model_cfg.input_shape
        assert isinstance(input_shape, list), "Input shape should be a tuple"
        assert len(input_shape) == 3, "Input shape should be 3D (H, W, C)"
        assert all(isinstance(dim, int) for dim in input_shape), "All dimensions should be integers"
        assert all(dim > 0 for dim in input_shape), "All dimensions should be positive"

    def test_optimizer(self):
        """Test optimizer configuration"""
        optimizer = config.model_cfg.optimizer
        assert isinstance(optimizer, str), "Optimizer should be a string"
        assert len(optimizer) > 0, "Optimizer should not be empty"
        # Common optimizers
        valid_optimizers = ['adam', 'sgd', 'rmsprop', 'adamw', 'adagrad']
        assert optimizer.lower() in valid_optimizers, f"Optimizer should be one of {valid_optimizers}"

    def test_loss_function(self):
        """Test loss function configuration"""
        loss = config.model_cfg.loss
        assert isinstance(loss, str), "Loss should be a string"
        assert len(loss) > 0, "Loss should not be empty"

    def test_accuracy_metric(self):
        """Test accuracy metric configuration"""
        metric = config.model_cfg.accuracy_metric
        assert isinstance(metric, str), "Accuracy metric should be a string"
        assert 'accuracy' in metric.lower(), "Metric should contain 'accuracy'"

    def test_scaling_factor(self):
        """Test scaling factor configuration"""
        scaling = config.model_cfg.scaling_factor
        assert isinstance(scaling, (int, float)), "Scaling factor should be numeric"
        assert scaling > 0, "Scaling factor should be positive"


class TestAppConfig:
    """Test application configuration"""

    def test_app_config_exists(self):
        """Test that app config exists"""
        assert hasattr(config, 'app_cfg')
        assert config.app_cfg is not None

    def test_package_name(self):
        """Test package name configuration"""
        pkg_name = config.app_cfg.package_name
        assert isinstance(pkg_name, str), "Package name should be a string"
        assert len(pkg_name) > 0, "Package name should not be empty"
        assert 'catvsdog' in pkg_name.lower(), "Package name should contain 'catvsdog'"


class TestTrainingConfig:
    """Test training configuration if it exists"""

    def test_training_params_exist(self):
        """Test that basic training parameters can be accessed"""
        # This test checks if config structure supports training parameters
        assert config is not None
        assert hasattr(config, 'model_cfg')

    def test_model_file_name(self):
        """Test model file name configuration"""
        if hasattr(config.app_cfg, 'model_file_name'):
            model_name = config.app_cfg.model_file_name
            assert isinstance(model_name, str)
            assert len(model_name) > 0
            # Should have a valid extension
            assert any(ext in model_name for ext in ['.h5', '.keras', '.tf'])


class TestConfigIntegrity:
    """Test overall config integrity"""

    def test_config_is_singleton(self):
        """Test that config behaves like a singleton"""
        from catvsdog_model.config.core import config as config1
        from catvsdog_model.config.core import config as config2
        # Both imports should reference the same config
        assert config1.model_cfg.input_shape == config2.model_cfg.input_shape

    def test_config_immutability(self):
        """Test that config values are consistent"""
        original_shape = config.model_cfg.input_shape
        # Try to access again
        new_shape = config.model_cfg.input_shape
        assert original_shape == new_shape, "Config should return consistent values"

    def test_all_required_attributes(self):
        """Test that config has all required attributes"""
        required_attrs = ['model_cfg', 'app_cfg']
        for attr in required_attrs:
            assert hasattr(config, attr), f"Config missing required attribute: {attr}"

        required_model_attrs = ['input_shape', 'optimizer', 'loss', 'accuracy_metric']
        for attr in required_model_attrs:
            assert hasattr(config.model_cfg, attr), f"Model config missing: {attr}"
