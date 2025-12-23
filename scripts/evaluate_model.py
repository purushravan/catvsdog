"""
Model evaluation script for DVC pipeline
Evaluates trained model and generates metrics and plots
"""
import sys
from pathlib import Path
import yaml
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
file = Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import confusion_matrix, classification_report


def load_params():
    """Load parameters from params.yaml"""
    params_path = root / "params.yaml"
    with open(params_path, 'r') as f:
        params = yaml.safe_load(f)
    return params


def load_test_data(params):
    """Load test dataset"""
    test_path = Path(params['data']['test_path'])
    image_size = tuple(params['preprocessing']['image_size'])
    batch_size = params['preprocessing']['batch_size']

    test_dataset = keras.preprocessing.image_dataset_from_directory(
        test_path,
        image_size=image_size,
        batch_size=batch_size,
        shuffle=False
    )

    return test_dataset


def evaluate_model():
    """
    Evaluate the trained model on test data
    """
    params = load_params()

    # Load model
    version = params['versioning']['version']
    model_prefix = params['versioning']['model_prefix']
    model_path = root / f"catvsdog_model/trained_models/{model_prefix}{version}.keras"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {model_path}")

    print(f"Loading model from {model_path}...")
    model = keras.models.load_model(model_path)

    # Load test data
    print("Loading test data...")
    test_dataset = load_test_data(params)

    # Evaluate model
    print("Evaluating model...")
    test_loss, test_accuracy = model.evaluate(test_dataset)

    print(f"\nTest Results:")
    print(f"  Loss: {test_loss:.4f}")
    print(f"  Accuracy: {test_accuracy:.4f}")

    # Get predictions
    print("\nGenerating predictions...")
    y_true = []
    y_pred = []

    for images, labels in test_dataset:
        predictions = model.predict(images, verbose=0)
        y_true.extend(labels.numpy())
        y_pred.extend((predictions > 0.5).astype(int).flatten())

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Classification report
    class_names = ['cat', 'dog']
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

    # Save evaluation metrics
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)

    evaluation_metrics = {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "total_samples": int(len(y_true)),
        "correct_predictions": int(np.sum(y_true == y_pred)),
        "per_class_metrics": {
            "cat": {
                "precision": float(report['cat']['precision']),
                "recall": float(report['cat']['recall']),
                "f1-score": float(report['cat']['f1-score']),
                "support": int(report['cat']['support'])
            },
            "dog": {
                "precision": float(report['dog']['precision']),
                "recall": float(report['dog']['recall']),
                "f1-score": float(report['dog']['f1-score']),
                "support": int(report['dog']['support'])
            }
        }
    }

    metrics_file = metrics_dir / "evaluation_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(evaluation_metrics, f, indent=2)
    print(f"✓ Saved evaluation metrics to {metrics_file}")

    # Save classification report
    report_file = metrics_dir / "classification_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Saved classification report to {report_file}")

    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    cm_file = metrics_dir / "confusion_matrix.png"
    plt.savefig(cm_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved confusion matrix to {cm_file}")

    print("\n✅ Model evaluation complete!")
    print(f"\n📊 Summary:")
    print(f"   Accuracy: {test_accuracy*100:.2f}%")
    print(f"   Cat - Precision: {report['cat']['precision']:.3f}, Recall: {report['cat']['recall']:.3f}")
    print(f"   Dog - Precision: {report['dog']['precision']:.3f}, Recall: {report['dog']['recall']:.3f}")


if __name__ == "__main__":
    evaluate_model()
