# DVC Pipeline for Cat vs Dog Classification

This document explains the DVC pipeline setup for training and evaluating the cat vs dog classification model.

## 📋 Table of Contents

- [Overview](#overview)
- [Pipeline Stages](#pipeline-stages)
- [Setup Instructions](#setup-instructions)
- [Running the Pipeline](#running-the-pipeline)
- [Experiment Tracking](#experiment-tracking)
- [File Structure](#file-structure)
- [Key Concepts](#key-concepts)

## 🎯 Overview

This DVC pipeline automates the complete ML workflow:
1. **Data Preparation** - Validates and prepares training data
2. **Model Training** - Trains the CNN model with data augmentation
3. **Model Evaluation** - Evaluates performance and generates metrics

## 🔄 Pipeline Stages

### Stage 1: prepare_data
**Purpose:** Validate data and create processed dataset structure

**Dependencies:**
- `scripts/prepare_data.py`
- `catvsdog_model/datasets/data/`
- Parameters from `params.yaml` (preprocessing, data)

**Outputs:**
- `data/processed/` - Symbolic links or copies of train/val/test data
- `data/processed/data_stats.json` - Dataset statistics
- `data/processed/metadata.json` - Preprocessing configuration

**Command:**
```bash
dvc repro prepare_data
```

### Stage 2: train_model
**Purpose:** Train the CNN model on prepared data

**Dependencies:**
- Training scripts and model files
- `data/processed/` from previous stage
- Parameters: train, model, augmentation, callbacks

**Outputs:**
- `catvsdog_model/trained_models/catvsdog__model_output_v{version}.keras` - Trained model
- `metrics/training_metrics.json` - Training summary metrics
- `metrics/training_history.csv` - Epoch-by-epoch training history

**Command:**
```bash
dvc repro train_model
```

### Stage 3: evaluate_model
**Purpose:** Evaluate model on test set and generate reports

**Dependencies:**
- `scripts/evaluate_model.py`
- Trained model from previous stage
- `data/processed/`

**Outputs:**
- `metrics/evaluation_metrics.json` - Test set performance
- `metrics/confusion_matrix.png` - Visual confusion matrix
- `metrics/classification_report.json` - Per-class metrics

**Command:**
```bash
dvc repro evaluate_model
```

## 🚀 Setup Instructions

### 1. Initialize DVC (if not already done)

```bash
cd catvsdog

# Initialize DVC in the repository
dvc init

# Add a remote storage (example with local storage)
dvc remote add -d local_storage /path/to/dvc/storage

# For cloud storage (S3 example):
# dvc remote add -d s3remote s3://mybucket/catvsdog-dvc
```

### 2. Track Large Files

```bash
# Track the dataset
dvc add catvsdog_model/datasets/data

# Track the trained model (if exists)
dvc add catvsdog_model/trained_models/catvsdog__model_output_v0.0.1.keras

# Commit .dvc files to git
git add catvsdog_model/datasets/data.dvc .gitignore
git commit -m "Track dataset with DVC"
```

### 3. Install Dependencies

```bash
pip install dvc dvc-s3  # or dvc-gs, dvc-azure as needed
pip install -r requirements/requirements.txt
```

## 🏃 Running the Pipeline

### Run Complete Pipeline

```bash
# Run all stages from scratch
dvc repro

# Force rerun all stages (ignore cache)
dvc repro --force
```

### Run Specific Stages

```bash
# Run only data preparation
dvc repro prepare_data

# Run training and everything downstream
dvc repro train_model
```

### Check Pipeline Status

```bash
# Check what needs to be rerun
dvc status

# Visualize pipeline DAG
dvc dag

# View pipeline dependencies
dvc dag --md  # Markdown format
```

## 🧪 Experiment Tracking

### Running Experiments

```bash
# Experiment 1: More epochs
dvc exp run --set-param train.epochs=20

# Experiment 2: Different batch size
dvc exp run --set-param preprocessing.batch_size=64

# Experiment 3: Different optimizer
dvc exp run --set-param train.optimizer=adam

# Experiment 4: Multiple parameter changes
dvc exp run \
  --set-param train.epochs=15 \
  --set-param train.optimizer=adam \
  --set-param preprocessing.batch_size=16
```

### Viewing Experiments

```bash
# Show all experiments with metrics
dvc exp show

# Show specific metrics
dvc exp show --include-params train.epochs,train.optimizer

# Compare experiments
dvc exp diff
```

### Managing Experiments

```bash
# Apply best experiment
dvc exp apply <experiment-name>

# Create a branch from experiment
dvc exp branch <experiment-name> feature/best-model

# Remove experiments
dvc exp remove <experiment-name>

# Push experiments to remote
dvc exp push origin
```

## 📁 File Structure

```
catvsdog/
├── dvc.yaml                    # Pipeline definition
├── params.yaml                 # Pipeline parameters
├── .dvc/                       # DVC configuration
│   ├── config                  # DVC remote config
│   └── cache/                  # Local cache
├── scripts/                    # Pipeline scripts
│   ├── prepare_data.py        # Data preparation
│   ├── train_with_dvc.py      # Training with DVC metrics
│   └── evaluate_model.py      # Model evaluation
├── data/
│   └── processed/             # Processed data (DVC tracked)
├── metrics/                   # Metrics and plots (Git tracked)
│   ├── training_metrics.json
│   ├── training_history.csv
│   ├── evaluation_metrics.json
│   ├── confusion_matrix.png
│   └── classification_report.json
├── catvsdog_model/
│   ├── datasets/
│   │   └── data/              # Raw data (DVC tracked)
│   ├── trained_models/        # Model files (DVC tracked)
│   ├── train_model.py         # Original training script
│   ├── model.py               # Model architecture
│   └── processing/            # Data processing utilities
└── dvc.lock                   # Pipeline lock file (Git tracked)
```

## 🔑 Key Concepts

### Parameters (params.yaml)
All configurable values are centralized in `params.yaml`:
- Data paths and preprocessing settings
- Model architecture parameters
- Training hyperparameters
- Callback configurations

Changes to parameters trigger pipeline reruns for affected stages.

### Metrics Tracking
- **Training metrics** (`metrics/training_metrics.json`) - cached: false
- **Evaluation metrics** (`metrics/evaluation_metrics.json`) - cached: false
- **Plots** (`metrics/training_history.csv`) - for DVC plots visualization

### Data Versioning
- Dataset changes are tracked via `.dvc` files
- Model files are cached and versioned
- Git tracks lightweight `.dvc` pointers, not the actual data

### Caching and Reproducibility
- DVC caches stage outputs based on input hashes
- Unchanged stages are skipped (cache hit)
- `dvc.lock` ensures exact reproducibility

## 📊 Viewing Metrics

### Training History Plot

```bash
dvc plots show metrics/training_history.csv
```

### Custom Plots

```bash
# Compare experiments
dvc plots diff $(dvc exp list --name-only | head -2)

# Show specific metrics
dvc plots show --x epoch --y loss,val_loss metrics/training_history.csv
```

### Metrics Comparison

```bash
# Show metrics table
dvc metrics show

# Compare metrics across experiments
dvc metrics diff
```

## 🔄 Typical Workflow

### 1. Initial Training
```bash
# Run the complete pipeline
dvc repro

# Commit results
git add dvc.lock metrics/
git commit -m "Initial training run"
dvc push  # Push data/models to remote
git push  # Push code/metrics to git
```

### 2. Experiment with Hyperparameters
```bash
# Try different configurations
dvc exp run --set-param train.epochs=20 -n "more-epochs"
dvc exp run --set-param train.optimizer=adam -n "adam-optimizer"

# Compare results
dvc exp show

# Apply best experiment
dvc exp apply <best-experiment-name>
git add dvc.lock params.yaml metrics/
git commit -m "Apply best experiment: <description>"
```

### 3. Update Data
```bash
# After adding new training images
dvc add catvsdog_model/datasets/data
git add catvsdog_model/datasets/data.dvc
git commit -m "Update dataset with new images"

# Retrain with new data
dvc repro
```

## 🐛 Troubleshooting

### Pipeline won't run
```bash
# Check status
dvc status

# Validate pipeline
dvc dag

# Force rerun
dvc repro --force
```

### Cache issues
```bash
# Check cache status
dvc cache dir

# Pull missing data
dvc pull

# Verify file integrity
dvc checkout
```

### Metrics not updating
- Ensure `cache: false` is set for metric files in `dvc.yaml`
- Check that metrics are written to the correct path
- Verify stage dependencies are correct

## 📚 Additional Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC Pipelines Guide](https://dvc.org/doc/user-guide/project-structure/pipelines-files)
- [DVC Experiments](https://dvc.org/doc/user-guide/experiment-management)
- [DVC Metrics and Plots](https://dvc.org/doc/command-reference/metrics)

## 🎓 Next Steps

1. Set up remote storage (S3, GCS, Azure, or SSH)
2. Configure CI/CD to run `dvc repro` automatically
3. Integrate with MLflow for additional experiment tracking
4. Set up DVC Studio for web-based visualization
5. Create automated model validation tests

---

**Happy Experimenting! 🚀**
