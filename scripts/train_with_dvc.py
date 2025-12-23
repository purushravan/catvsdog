"""
Enhanced training script for DVC pipeline
Extends the original train_model.py with DVC-compatible metrics tracking
"""
import sys
from pathlib import Path
import yaml
import json
import pandas as pd

# Add project root to path
file = Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

try:
    from catvsdog_model.config.core import config
    from catvsdog_model.model import classifier
    from catvsdog_model.processing.data_manager import (
        load_train_dataset,
        load_validation_dataset,
        load_test_dataset,
        callbacks_and_save_model
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def load_params():
    """Load parameters from params.yaml"""
    params_path = root / "params.yaml"
    with open(params_path, 'r') as f:
        params = yaml.safe_load(f)
    return params


class DVCMetricsCallback:
    """Callback to save metrics in DVC-compatible format"""

    def __init__(self, metrics_dir="metrics"):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)
        self.history = []

    def on_epoch_end(self, epoch, logs=None):
        """Save metrics after each epoch"""
        logs = logs or {}
        epoch_metrics = {"epoch": epoch + 1}
        epoch_metrics.update({k: float(v) for k, v in logs.items()})
        self.history.append(epoch_metrics)

    def save_metrics(self):
        """Save all metrics to files"""
        # Save training history as CSV for plots
        history_df = pd.DataFrame(self.history)
        history_file = self.metrics_dir / "training_history.csv"
        history_df.to_csv(history_file, index=False)
        print(f"✓ Saved training history to {history_file}")

        # Save final metrics as JSON
        if self.history:
            final_metrics = {
                "final_loss": self.history[-1].get("loss"),
                "final_accuracy": self.history[-1].get("accuracy"),
                "final_val_loss": self.history[-1].get("val_loss"),
                "final_val_accuracy": self.history[-1].get("val_accuracy"),
                "total_epochs": len(self.history),
                "best_val_accuracy": max(h.get("val_accuracy", 0) for h in self.history),
                "best_val_loss": min(h.get("val_loss", float('inf')) for h in self.history)
            }

            metrics_file = self.metrics_dir / "training_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(final_metrics, f, indent=2)
            print(f"✓ Saved training metrics to {metrics_file}")


def run_training() -> None:
    """
    Train the model with DVC metrics tracking
    """
    params = load_params()

    print("Loading datasets...")
    train_data = load_train_dataset()
    val_data = load_validation_dataset()
    test_data = load_test_dataset()

    # Initialize DVC metrics callback
    dvc_metrics = DVCMetricsCallback()

    # MLFlow tracking (if enabled)
    if params.get('mlflow', {}).get('tracking_uri'):
        try:
            import mlflow
            mlflow.set_tracking_uri(params['mlflow']['tracking_uri'])
            mlflow.set_experiment(params['mlflow']['experiment_name'])
            mlflow.tensorflow.autolog()
            print("✓ MLflow tracking enabled")
        except Exception as e:
            print(f"⚠ MLflow tracking disabled: {e}")

    # Get training callbacks
    model_callbacks = callbacks_and_save_model()

    # Add custom callback for DVC metrics
    import tensorflow as tf

    class DVCCallback(tf.keras.callbacks.Callback):
        def __init__(self, dvc_metrics_callback):
            super().__init__()
            self.dvc_metrics = dvc_metrics_callback

        def on_epoch_end(self, epoch, logs=None):
            self.dvc_metrics.on_epoch_end(epoch, logs)

    model_callbacks.append(DVCCallback(dvc_metrics))

    # Train model
    print(f"\nTraining model for {params['train']['epochs']} epochs...")
    print(f"Optimizer: {params['train']['optimizer']}")
    print(f"Batch size: {params['preprocessing']['batch_size']}")

    history = classifier.fit(
        train_data,
        epochs=params['train']['epochs'],
        validation_data=val_data,
        callbacks=model_callbacks,
        verbose=params['train']['verbose']
    )

    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_loss, test_acc = classifier.evaluate(test_data)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")

    # Save DVC metrics
    dvc_metrics.save_metrics()

    print("\n✅ Training complete!")


if __name__ == "__main__":
    run_training()
