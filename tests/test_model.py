"""
Unit tests for the Cat vs Dog classifier model
"""
import pytest
import sys
from pathlib import Path
import numpy as np

# Add project root to path
root = Path(__file__).parents[1]
sys.path.append(str(root))

from catvsdog_model.config.core import config
from catvsdog_model.model import classifier, create_model


class TestModelArchitecture:
    """Test model architecture and configuration"""

    def test_model_exists(self):
        """Test that the model is properly initialized"""
        assert classifier is not None
        assert hasattr(classifier, 'layers')

    def test_model_input_shape(self):
        """Test that model has correct input shape"""
        expected_shape = config.model_cfg.input_shape
        actual_shape = list[int](classifier.input_shape[1:])  # Skip batch dimension
        assert actual_shape == expected_shape, f"Expected {expected_shape}, got {actual_shape}"

    def test_model_output_shape(self):
        """Test that model has correct output shape for binary classification"""
        output_shape = classifier.output_shape
        assert output_shape[-1] == 1, "Output should be single value for binary classification"

    def test_model_is_compiled(self):
        """Test that model is compiled with optimizer and loss"""
        assert classifier.optimizer is not None, "Model should be compiled with an optimizer"
        assert classifier.loss is not None, "Model should be compiled with a loss function"

    def test_model_layers(self):
        """Test that model has expected number of layers"""
        # Model should have multiple Conv2D, MaxPooling2D, and Dense layers
        layer_types = [type(layer).__name__ for layer in classifier.layers]
        assert 'Conv2D' in layer_types, "Model should contain Conv2D layers"
        assert 'MaxPooling2D' in layer_types, "Model should contain MaxPooling2D layers"
        assert 'Dense' in layer_types, "Model should contain Dense layers"
        assert 'Dropout' in layer_types, "Model should contain Dropout layers"

    def test_create_model_function(self):
        """Test that create_model function works properly"""
        test_model = create_model(
            input_shape=config.model_cfg.input_shape,
            optimizer=config.model_cfg.optimizer,
            loss=config.model_cfg.loss,
            metrics=[config.model_cfg.accuracy_metric]
        )
        assert test_model is not None
        assert list[int](test_model.input_shape[1:]) == config.model_cfg.input_shape


class TestModelPrediction:
    """Test model prediction capabilities"""

    def test_model_predict_shape(self):
        """Test that model prediction returns correct shape"""
        # Create dummy input
        batch_size = 1
        dummy_input = np.random.rand(batch_size, *config.model_cfg.input_shape).astype(np.float32)

        # Get prediction
        prediction = classifier.predict(dummy_input, verbose=0)

        # Check shape
        assert prediction.shape == (batch_size, 1), f"Expected shape (1, 1), got {prediction.shape}"

    def test_model_predict_range(self):
        """Test that model prediction is in valid range [0, 1]"""
        # Create dummy input
        dummy_input = np.random.rand(2, *config.model_cfg.input_shape).astype(np.float32)

        # Get prediction
        predictions = classifier.predict(dummy_input, verbose=0)

        # Check range
        assert np.all(predictions >= 0), "Predictions should be >= 0"
        assert np.all(predictions <= 1), "Predictions should be <= 1"

    def test_model_predict_batch(self):
        """Test that model can handle batch predictions"""
        batch_sizes = [1, 4, 8]

        for batch_size in batch_sizes:
            dummy_input = np.random.rand(batch_size, *config.model_cfg.input_shape).astype(np.float32)
            predictions = classifier.predict(dummy_input, verbose=0)
            assert predictions.shape[0] == batch_size, f"Expected {batch_size} predictions"


class TestModelConfiguration:
    """Test model configuration settings"""

    def test_config_exists(self):
        """Test that configuration is properly loaded"""
        assert config is not None
        assert config.model_cfg is not None

    def test_input_shape_valid(self):
        """Test that input shape is valid"""
        assert len(config.model_cfg.input_shape) == 3, "Input shape should be 3D (height, width, channels)"
        assert config.model_cfg.input_shape[2] == 3, "Images should have 3 channels (RGB)"

    def test_optimizer_config(self):
        """Test that optimizer is properly configured"""
        assert config.model_cfg.optimizer is not None
        assert isinstance(config.model_cfg.optimizer, str), "Optimizer should be a string"

    def test_loss_config(self):
        """Test that loss function is properly configured"""
        assert config.model_cfg.loss is not None
        assert isinstance(config.model_cfg.loss, str), "Loss should be a string"


class TestModelIntegration:
    """Integration tests for the complete model"""

    def test_model_summary(self):
        """Test that model summary can be generated without errors"""
        try:
            # Capture summary
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            classifier.summary()

            output = buffer.getvalue()
            sys.stdout = old_stdout

            # Check that summary contains expected information
            assert 'Total params' in output or 'trainable params' in output.lower()
            assert len(output) > 0
        except Exception as e:
            pytest.fail(f"Model summary failed: {e}")

    def test_model_trainable_params(self):
        """Test that model has trainable parameters"""
        trainable_count = sum([np.prod(w.shape) for w in classifier.trainable_weights])
        assert trainable_count > 0, "Model should have trainable parameters"

    @pytest.mark.slow
    def test_model_single_training_step(self):
        """Test that model can perform a single training step (slow test)"""
        # Create dummy data
        batch_size = 2
        dummy_x = np.random.rand(batch_size, *config.model_cfg.input_shape).astype(np.float32)
        dummy_y = np.random.randint(0, 2, size=(batch_size, 1)).astype(np.float32)

        # Get initial loss
        initial_loss = classifier.evaluate(dummy_x, dummy_y, verbose=0)[0]

        # Train for one step
        history = classifier.fit(dummy_x, dummy_y, epochs=1, verbose=0)

        # Check that training completed
        assert history is not None
        assert 'loss' in history.history

        # Loss should be a valid number
        final_loss = history.history['loss'][0]
        assert isinstance(final_loss, (float, np.floating))
        assert not np.isnan(final_loss), "Loss should not be NaN"
