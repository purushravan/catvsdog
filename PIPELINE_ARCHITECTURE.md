# DVC Pipeline Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DVC PIPELINE SYSTEM                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   params.yaml   │────────>│    dvc.yaml      │<────────│  dvc.lock    │
│  (Parameters)   │         │  (Pipeline Def)  │         │  (State)     │
└─────────────────┘         └──────────────────┘         └──────────────┘
                                     │
                                     │ defines
                                     v
        ┌────────────────────────────────────────────────────────┐
        │                    PIPELINE STAGES                     │
        └────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STAGE 1: prepare_data                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    INPUT:
    ├── catvsdog_model/datasets/data/train/      [DVC tracked]
    ├── catvsdog_model/datasets/data/validation/ [DVC tracked]
    ├── catvsdog_model/datasets/data/test/       [DVC tracked]
    └── scripts/prepare_data.py

    PARAMETERS:
    ├── preprocessing.image_size
    ├── preprocessing.batch_size
    ├── preprocessing.random_state
    └── data.{train,validation,test}_path

    PROCESS:
    ├── Validates data directories exist
    ├── Counts images per split and class
    ├── Creates symlinks to processed/ directory
    └── Generates metadata and statistics

    OUTPUT:
    ├── data/processed/train/           [DVC tracked]
    ├── data/processed/validation/      [DVC tracked]
    ├── data/processed/test/            [DVC tracked]
    ├── data/processed/data_stats.json  [DVC tracked]
    └── data/processed/metadata.json    [DVC tracked]

                            ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STAGE 2: train_model                                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    INPUT:
    ├── data/processed/                          [from Stage 1]
    ├── catvsdog_model/train_model.py
    ├── catvsdog_model/model.py
    ├── catvsdog_model/processing/features.py
    └── catvsdog_model/processing/data_manager.py

    PARAMETERS:
    ├── train.epochs
    ├── train.optimizer
    ├── train.loss
    ├── train.metrics
    ├── model.input_shape
    ├── model.filters
    ├── model.dropout_rate
    ├── augmentation.rotation
    ├── augmentation.zoom
    ├── augmentation.flip
    ├── callbacks.early_stopping
    └── callbacks.model_checkpoint

    PROCESS:
    ┌──────────────────────────────────────┐
    │ 1. Load Data                         │
    │    ├── Train dataset                 │
    │    ├── Validation dataset            │
    │    └── Test dataset                  │
    ├──────────────────────────────────────┤
    │ 2. Create Model                      │
    │    ├── Data augmentation layer       │
    │    ├── 5 Conv2D + MaxPooling layers  │
    │    ├── Flatten                       │
    │    ├── Dropout (0.5)                 │
    │    └── Dense output (sigmoid)        │
    ├──────────────────────────────────────┤
    │ 3. Compile Model                     │
    │    ├── Optimizer: RMSprop/Adam       │
    │    ├── Loss: binary_crossentropy     │
    │    └── Metrics: accuracy             │
    ├──────────────────────────────────────┤
    │ 4. Train                             │
    │    ├── Fit on train_data             │
    │    ├── Validate on val_data          │
    │    ├── Track metrics per epoch       │
    │    └── Save best weights             │
    ├──────────────────────────────────────┤
    │ 5. Evaluate                          │
    │    └── Test on test_data             │
    └──────────────────────────────────────┘

    MLflow INTEGRATION:
    ├── Tracking URI: http://127.0.0.1:5000/
    ├── Experiment: Cat-vs-Dog Classification
    └── Auto-logs: params, metrics, model

    OUTPUT:
    ├── catvsdog_model/trained_models/
    │   └── catvsdog__model_output_v{version}.keras [DVC tracked]
    ├── metrics/training_metrics.json               [Git tracked]
    │   ├── final_loss
    │   ├── final_accuracy
    │   ├── final_val_loss
    │   ├── final_val_accuracy
    │   ├── total_epochs
    │   ├── best_val_accuracy
    │   └── best_val_loss
    └── metrics/training_history.csv                [Git tracked]
        └── epoch, loss, accuracy, val_loss, val_accuracy

                            ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ STAGE 3: evaluate_model                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    INPUT:
    ├── catvsdog_model/trained_models/
    │   └── catvsdog__model_output_v{version}.keras [from Stage 2]
    ├── data/processed/test/                        [from Stage 1]
    └── scripts/evaluate_model.py

    PARAMETERS:
    ├── preprocessing.image_size
    ├── preprocessing.batch_size
    ├── versioning.version
    └── versioning.model_prefix

    PROCESS:
    ┌──────────────────────────────────────┐
    │ 1. Load Model                        │
    │    └── Load .keras file              │
    ├──────────────────────────────────────┤
    │ 2. Load Test Data                    │
    │    └── Create test dataset           │
    ├──────────────────────────────────────┤
    │ 3. Evaluate                          │
    │    ├── Calculate test loss           │
    │    └── Calculate test accuracy       │
    ├──────────────────────────────────────┤
    │ 4. Generate Predictions              │
    │    ├── Predict on all test samples   │
    │    └── Convert to binary (>0.5)      │
    ├──────────────────────────────────────┤
    │ 5. Calculate Metrics                 │
    │    ├── Confusion matrix              │
    │    ├── Classification report         │
    │    ├── Per-class precision/recall    │
    │    └── F1-scores                     │
    ├──────────────────────────────────────┤
    │ 6. Generate Visualizations           │
    │    └── Plot confusion matrix         │
    └──────────────────────────────────────┘

    OUTPUT:
    ├── metrics/evaluation_metrics.json          [Git tracked]
    │   ├── test_loss
    │   ├── test_accuracy
    │   ├── total_samples
    │   ├── correct_predictions
    │   └── per_class_metrics (precision, recall, f1, support)
    ├── metrics/classification_report.json       [Git tracked]
    │   └── Full scikit-learn classification report
    └── metrics/confusion_matrix.png             [Git tracked]
        └── Heatmap visualization
```

## Data Flow Diagram

```
                  ┌─────────────────────────────┐
                  │   Raw Dataset (DVC)         │
                  │  catvsdog_model/datasets/   │
                  └──────────────┬──────────────┘
                                 │
                                 │ dvc add
                                 v
                  ┌─────────────────────────────┐
                  │   .dvc Pointer File         │
                  │  datasets/data.dvc (Git)    │
                  └──────────────┬──────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        v                        v                        v
   ┌─────────┐            ┌─────────┐            ┌─────────┐
   │  Train  │            │   Val   │            │  Test   │
   └────┬────┘            └────┬────┘            └────┬────┘
        │                      │                      │
        └──────────────────────┼──────────────────────┘
                               │
                               │ prepare_data stage
                               v
                  ┌─────────────────────────────┐
                  │  Processed Data (DVC)       │
                  │    data/processed/          │
                  └──────────────┬──────────────┘
                                 │
                                 │ train_model stage
                                 v
        ┌────────────────────────┴────────────────────────┐
        │                                                  │
        v                                                  v
┌──────────────────┐                          ┌──────────────────┐
│  Trained Model   │                          │ Training Metrics │
│  (DVC tracked)   │                          │  (Git tracked)   │
│  *.keras         │                          │  *.json, *.csv   │
└────────┬─────────┘                          └──────────────────┘
         │
         │ evaluate_model stage
         v
┌────────────────────────────────────────────┐
│         Evaluation Results                 │
│         (Git tracked)                      │
├────────────────────────────────────────────┤
│  • evaluation_metrics.json                 │
│  • confusion_matrix.png                    │
│  • classification_report.json              │
└────────────────────────────────────────────┘
```

## Dependency Graph

```
params.yaml ─────┬──────────────────┬──────────────────┐
                 │                  │                  │
                 v                  v                  v
         [prepare_data]      [train_model]     [evaluate_model]
                 │                  │                  │
                 │                  │                  │
datasets/data ───┤                  │                  │
                 │                  │                  │
prepare_data.py ─┤                  │                  │
                 │                  │                  │
                 └──> data/         │                  │
                      processed ────┤                  │
                                    │                  │
train_model.py ──────────────────────┤                  │
model.py ─────────────────────────────┤                 │
features.py ──────────────────────────┤                 │
data_manager.py ──────────────────────┤                 │
                                      │                 │
                                      └──> trained_     │
                                           model ───────┤
                                                        │
evaluate_model.py ───────────────────────────────────────┤
                                                        │
                                                        └──> evaluation
                                                             metrics
```

## Version Control Strategy

```
┌──────────────────────────────────────────────────────────┐
│                     GIT REPOSITORY                       │
├──────────────────────────────────────────────────────────┤
│  Tracked Files:                                          │
│  ✓ Source code (*.py)                                    │
│  ✓ Pipeline definition (dvc.yaml)                        │
│  ✓ Pipeline state (dvc.lock)                             │
│  ✓ Parameters (params.yaml)                              │
│  ✓ Pointer files (*.dvc)                                 │
│  ✓ Metrics (metrics/*.json, *.csv, *.png)                │
│  ✓ Documentation (*.md)                                  │
└──────────────────────────────────────────────────────────┘
                          │
                          │ DVC tracks
                          v
┌──────────────────────────────────────────────────────────┐
│                     DVC REMOTE STORAGE                   │
├──────────────────────────────────────────────────────────┤
│  Tracked Artifacts:                                      │
│  ✓ Datasets (data/)                                      │
│  ✓ Processed data (data/processed/)                      │
│  ✓ Trained models (*.keras)                              │
│  ✓ Large binary files                                    │
└──────────────────────────────────────────────────────────┘
```

## Experiment Workflow

```
main branch
│
├── commit: "Initial pipeline setup"
│   ├── params.yaml (epochs=10)
│   └── dvc.lock (baseline)
│
├── dvc exp run --set-param train.epochs=20
│   └── [experiment-1]: epochs=20
│       └── metrics: val_acc=0.89
│
├── dvc exp run --set-param train.optimizer=adam
│   └── [experiment-2]: adam
│       └── metrics: val_acc=0.91  ← Best!
│
├── dvc exp apply experiment-2
│   └── params.yaml updated (optimizer=adam)
│
└── commit: "Apply best experiment: adam optimizer"
    ├── params.yaml (optimizer=adam)
    ├── dvc.lock (new state)
    └── metrics/ (updated)
```

## Cache & Storage Hierarchy

```
                    ┌──────────────────┐
                    │   Workspace      │
                    │  (working dir)   │
                    └────────┬─────────┘
                             │
                    ┌────────v─────────┐
                    │  Local DVC Cache │
                    │   .dvc/cache/    │
                    └────────┬─────────┘
                             │
                    ┌────────v─────────┐
                    │  Remote Storage  │
                    │   S3/GCS/Azure   │
                    └──────────────────┘

  dvc checkout ──> Copies from cache to workspace
  dvc push     ──> Uploads cache to remote
  dvc pull     ──> Downloads remote to cache
  dvc repro    ──> Generates outputs, adds to cache
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    EXISTING CODEBASE                        │
├─────────────────────────────────────────────────────────────┤
│  catvsdog_model/                                            │
│  ├── train_model.py ───────────┐                            │
│  ├── model.py ─────────────────┼── Used by                  │
│  ├── processing/               │   DVC pipeline             │
│  │   ├── data_manager.py ──────┤                            │
│  │   └── features.py ──────────┘                            │
│  └── config/                                                │
│      ├── config.yml ──────── Read by original code          │
│      └── core.py                                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Wrapped by
                           v
┌─────────────────────────────────────────────────────────────┐
│                    DVC PIPELINE LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  scripts/                                                   │
│  ├── prepare_data.py ──── New: Data validation             │
│  ├── train_with_dvc.py ── Alternative: Enhanced metrics    │
│  └── evaluate_model.py ── New: Comprehensive evaluation    │
│                                                             │
│  params.yaml ──────────── Centralized parameters            │
│  dvc.yaml ─────────────── Pipeline orchestration            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Integrates with
                           v
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SYSTEMS                         │
├─────────────────────────────────────────────────────────────┤
│  MLflow ──────────────── Experiment tracking                │
│  DVC Remote ───────────── Data/model storage                │
│  Git Remote ───────────── Code versioning                   │
│  CI/CD ────────────────── Automated pipeline runs           │
└─────────────────────────────────────────────────────────────┘
```

---

This architecture provides:
- ✅ **Reproducibility** through versioned dependencies
- ✅ **Scalability** via cloud storage integration
- ✅ **Collaboration** through shared remotes
- ✅ **Experimentation** via parameter tracking
- ✅ **Automation** through pipeline orchestration
