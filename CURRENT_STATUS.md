# DVC Pipeline - Current Status & Next Steps

## ✅ What's Working

### Stage 1: prepare_data - **COMPLETED** ✓
- Successfully validated dataset
- Created processed data structure
- Generated statistics:
  - **Train:** 1,000 images (500 cats, 500 dogs)
  - **Validation:** 500 images (250 cats, 250 dogs)
  - **Test:** 500 images (250 cats, 250 dogs)

## 📦 Dependencies Installed

✅ DVC and DVC-S3
✅ TensorFlow 2.20.0
✅ Pandas, NumPy
✅ Scikit-learn
✅ Matplotlib, Seaborn
✅ PyYAML, StrictYAML

## 🔧 Fixes Applied

1. **Fixed dvc.yaml syntax** - Corrected plots configuration
2. **Changed python to python3** - macOS compatibility
3. **Updated training script path** - Using enhanced `scripts/train_with_dvc.py`
4. **Installed all dependencies** - Ready for training

## 🚀 Ready to Train!

The pipeline is now ready to run. Here's what will happen:

### Stage 2: train_model (Next)
```bash
cd "/Users/sarva/Study/AIML Infra/Day 4/catvsdog"
dvc repro train_model
```

**This will:**
- Load the 2,000 processed images
- Train a CNN model for 10 epochs (configurable)
- Save model to `catvsdog_model/trained_models/`
- Generate metrics in `metrics/`
- Track everything with DVC

**Expected outputs:**
- `catvsdog_model/trained_models/catvsdog__model_output_v0.0.1.keras`
- `metrics/training_metrics.json`
- `metrics/training_history.csv`

### Stage 3: evaluate_model (After training)
Automatically runs after training to:
- Evaluate on test set
- Generate confusion matrix
- Create classification report

## ⚡ Quick Commands

```bash
# Navigate to project
cd "/Users/sarva/Study/AIML Infra/Day 4/catvsdog"

# Run complete pipeline (all 3 stages)
dvc repro

# Or run stages individually
dvc repro prepare_data    # ✓ Already done
dvc repro train_model     # ← Run this next
dvc repro evaluate_model  # ← Runs after training

# Check status
dvc status

# View pipeline structure
dvc dag

# View metrics (after training)
cat metrics/training_metrics.json
dvc metrics show
```

## 📊 Pipeline Overview

```
 prepare_data (✓ DONE)
      ↓
 train_model (← READY TO RUN)
      ↓
 evaluate_model
```

## ⚙️ Training Configuration

Current settings in `params.yaml`:

```yaml
train:
  epochs: 10              # Training epochs
  optimizer: rmsprop      # Optimizer (try 'adam')
  learning_rate: 0.001    # Learning rate

preprocessing:
  batch_size: 32          # Batch size
  image_size: [180, 180]  # Image dimensions

model:
  filters: [32, 64, 128, 256, 256]  # CNN architecture
  dropout_rate: 0.5                  # Dropout
```

## 🧪 Want to Experiment?

Try different configurations:

```bash
# More epochs
dvc exp run --set-param train.epochs=20

# Different optimizer
dvc exp run --set-param train.optimizer=adam

# Larger batch size
dvc exp run --set-param preprocessing.batch_size=64

# Compare experiments
dvc exp show
```

## ⏱️ Expected Training Time

With the default configuration (10 epochs, batch size 32):
- **With GPU:** ~5-10 minutes
- **CPU only:** ~20-30 minutes

## 📁 File Structure

```
catvsdog/
├── data/
│   └── processed/          ← ✓ Created by prepare_data
│       ├── train/
│       ├── validation/
│       ├── test/
│       └── *.json
├── metrics/                ← Will be created by training
│   ├── training_metrics.json
│   ├── training_history.csv
│   ├── evaluation_metrics.json
│   └── confusion_matrix.png
├── catvsdog_model/
│   └── trained_models/     ← Model will be saved here
└── dvc.lock                ← DVC state file
```

##  Running the Pipeline

**Option 1: Run Everything** (Recommended)
```bash
dvc repro
```
This runs all stages. Stage 1 (prepare_data) will be skipped since it's cached.

**Option 2: Run Training Only**
```bash
dvc repro train_model
```
Runs training + evaluation.

**Option 3: Watch Progress**
The training will show:
- Epoch progress
- Loss and accuracy per epoch
- Validation metrics
- Final test results

## 🎯 What Happens Next

When you run `dvc repro train_model`:

1. **Loads data** from `data/processed/`
2. **Creates CNN model** with data augmentation
3. **Trains for 10 epochs** (shows progress bar)
4. **Saves best model** based on validation loss
5. **Generates metrics**:
   - Training loss/accuracy
   - Validation loss/accuracy
   - Best metrics achieved
6. **Evaluates on test set**
7. **Creates visualizations**

All outputs are tracked by DVC and can be reproduced exactly!

## 🐛 Troubleshooting

### If training fails with import errors:
```bash
pip3 install -r requirements/requirements.txt
```

### If MLflow connection fails:
Training will continue without MLflow. To use MLflow:
```bash
# In a separate terminal
mlflow server --host 127.0.0.1 --port 5000
```

### To restart from scratch:
```bash
dvc repro --force
```

## 📚 Documentation

- [README_DVC_PIPELINE.md](README_DVC_PIPELINE.md) - Main index
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md) - Complete documentation
- [TROUBLESHOOTING_FIXES.md](TROUBLESHOOTING_FIXES.md) - Issues fixed

---

**Ready to train?** Run: `dvc repro train_model`

🎉 Everything is set up and ready to go!
