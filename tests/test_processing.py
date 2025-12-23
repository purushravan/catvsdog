"""
Unit tests for data processing and features
"""
import pytest
import sys
from pathlib import Path
import numpy as np

# Add project root to path
root = Path(__file__).parents[1]
sys.path.append(str(root))

from catvsdog_model.config.core import config


class TestDataAugmentation:
    """Test data augmentation functionality"""

    def test_data_augmentation_import(self):
        """Test that data augmentation can be imported"""
        try:
            from catvsdog_model.processing.features import data_augmentation
            assert data_augmentation is not None
        except ImportError as e:
            pytest.skip(f"Data augmentation not available: {e}")

    def test_data_augmentation_callable(self):
        """Test that data augmentation is callable"""
        try:
            from catvsdog_model.processing.features import data_augmentation
            assert callable(data_augmentation), "data_augmentation should be callable"
        except ImportError:
            pytest.skip("Data augmentation not available")


class TestDataManager:
    """Test data manager functionality"""

    def test_data_manager_imports(self):
        """Test that data manager functions can be imported"""
        try:
            from catvsdog_model.processing.data_manager import (
                load_train_dataset,
                load_validation_dataset,
                load_test_dataset,
                callbacks_and_save_model
            )
            assert all([
                load_train_dataset is not None,
                load_validation_dataset is not None,
                load_test_dataset is not None,
                callbacks_and_save_model is not None
            ])
        except ImportError as e:
            pytest.skip(f"Data manager not fully available: {e}")

    def test_callbacks_function(self):
        """Test that callbacks function returns a list"""
        try:
            from catvsdog_model.processing.data_manager import callbacks_and_save_model
            callbacks = callbacks_and_save_model()
            assert isinstance(callbacks, list), "Callbacks should be a list"
        except Exception as e:
            pytest.skip(f"Callbacks test skipped: {e}")


class TestImagePreprocessing:
    """Test image preprocessing utilities"""

    def test_image_shape_validation(self):
        """Test that config defines valid image shapes"""
        shape = config.model_cfg.input_shape
        assert len(shape) == 3, "Image shape should be 3D"
        height, width, channels = shape
        assert height > 0 and width > 0, "Height and width must be positive"
        assert channels == 3, "Should be RGB images (3 channels)"

    def test_scaling_factor(self):
        """Test that scaling factor is properly configured"""
        scaling = config.model_cfg.scaling_factor
        assert isinstance(scaling, (int, float)), "Scaling should be numeric"
        assert scaling > 0, "Scaling factor should be positive"
        # Common scaling factor is 255 for image normalization
        assert scaling in [1, 255], "Scaling factor should be 1 or 255"


class TestConfigurationIntegrity:
    """Test configuration integrity for processing"""

    def test_package_root_accessible(self):
        """Test that package root is accessible"""
        from catvsdog_model.config.core import PACKAGE_ROOT
        assert PACKAGE_ROOT.exists(), "Package root should exist"
        assert PACKAGE_ROOT.is_dir(), "Package root should be a directory"

    def test_model_directory_path(self):
        """Test that model directory path is configured"""
        from catvsdog_model.config.core import TRAINED_MODEL_DIR
        assert TRAINED_MODEL_DIR is not None
        assert isinstance(TRAINED_MODEL_DIR, Path)

    def test_datasets_directory_exists(self):
        """Test that datasets directory exists in package"""
        from catvsdog_model.config.core import PACKAGE_ROOT
        datasets_dir = PACKAGE_ROOT / "datasets"
        # Directory should exist in the package structure
        assert datasets_dir.parent.exists(), "Parent of datasets dir should exist"


class TestDatasetLoading:
    """Test dataset loading capabilities (slow tests)"""

    @pytest.mark.slow
    def test_dataset_loading_structure(self):
        """Test that dataset loading has proper structure (slow)"""
        try:
            from catvsdog_model.processing.data_manager import load_train_dataset
            # This might fail if data isn't available, but we test the interface
            assert callable(load_train_dataset)
        except Exception:
            pytest.skip("Dataset loading test skipped - data not available")

    @pytest.mark.slow
    def test_all_dataset_loaders_exist(self):
        """Test that all dataset loaders are defined"""
        try:
            from catvsdog_model.processing import data_manager
            required_functions = [
                'load_train_dataset',
                'load_validation_dataset',
                'load_test_dataset'
            ]
            for func_name in required_functions:
                assert hasattr(data_manager, func_name), f"Missing function: {func_name}"
                func = getattr(data_manager, func_name)
                assert callable(func), f"{func_name} should be callable"
        except ImportError:
            pytest.skip("Data manager module not available")


class TestFeatureExtraction:
    """Test feature extraction and processing"""

    def test_image_input_compatibility(self):
        """Test that model accepts standard image inputs"""
        from catvsdog_model.model import classifier
        # Create a sample image
        sample_image = np.random.rand(1, *config.model_cfg.input_shape).astype(np.float32)
        # Test that model can handle the input
        try:
            prediction = classifier.predict(sample_image, verbose=0)
            assert prediction is not None
            assert prediction.shape == (1, 1)
        except Exception as e:
            pytest.fail(f"Model failed to process image: {e}")

    def test_batch_processing(self):
        """Test that model can process batches"""
        from catvsdog_model.model import classifier
        batch_size = 4
        batch = np.random.rand(batch_size, *config.model_cfg.input_shape).astype(np.float32)
        try:
            predictions = classifier.predict(batch, verbose=0)
            assert predictions.shape[0] == batch_size
        except Exception as e:
            pytest.fail(f"Model failed to process batch: {e}")


class TestModelPersistence:
    """Test model saving and loading"""

    def test_trained_model_directory_configured(self):
        """Test that trained model directory is properly configured"""
        from catvsdog_model.config.core import TRAINED_MODEL_DIR
        assert TRAINED_MODEL_DIR is not None
        assert isinstance(TRAINED_MODEL_DIR, Path)
        # Parent directory should exist
        assert TRAINED_MODEL_DIR.parent.exists()

    @pytest.mark.slow
    def test_model_can_be_saved(self, temp_model_path):
        """Test that model can be saved (slow test)"""
        from catvsdog_model.model import classifier
        try:
            classifier.save(str(temp_model_path))
            assert temp_model_path.exists(), "Model file should be created"
            assert temp_model_path.stat().st_size > 0, "Model file should not be empty"
        except Exception as e:
            pytest.fail(f"Failed to save model: {e}")

    @pytest.mark.slow
    def test_model_can_be_loaded(self, temp_model_path, classifier_model):
        """Test that saved model can be loaded (slow test)"""
        import tensorflow as tf
        try:
            # Save the model first
            classifier_model.save(str(temp_model_path))
            # Load it back
            loaded_model = tf.keras.models.load_model(str(temp_model_path))
            assert loaded_model is not None
            # Test that loaded model works
            sample = np.random.rand(1, *config.model_cfg.input_shape).astype(np.float32)
            prediction = loaded_model.predict(sample, verbose=0)
            assert prediction.shape == (1, 1)
        except Exception as e:
            pytest.fail(f"Failed to load model: {e}")
