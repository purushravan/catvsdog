# DVC Pipeline - Issues Fixed

## Issues Encountered and Fixed

### ✅ Issue 1: DVC Not Installed
**Error:** `command not found: dvc`

**Solution:**
```bash
pip3 install dvc dvc-s3
```

### ✅ Issue 2: Invalid YAML Syntax in dvc.yaml
**Error:**
```
expected str, in stages -> train_model -> plots -> 0 ->
metrics/training_history.csv -> y, line 38, column 13
```

**Problem:** The plots section had incorrect nested YAML syntax:
```yaml
y:
  metrics/training_history.csv: [loss, val_loss]
```

**Fix:** Simplified to:
```yaml
y: loss
```

### ✅ Issue 3: Python Command Not Found
**Error:** `zsh:1: command not found: python`

**Problem:** macOS uses `python3` not `python`

**Fix:** Updated all commands in `dvc.yaml`:
- `python scripts/prepare_data.py` → `python3 scripts/prepare_data.py`
- `python catvsdog_model/train_model.py` → `python3 catvsdog_model/train_model.py`
- `python scripts/evaluate_model.py` → `python3 scripts/evaluate_model.py`

### ✅ Issue 4: DVC Lock File
**Error:** `'/Users/sarva/.../data/processed' is busy`

**Solution:**
```bash
rm -f .dvc/tmp/rwlock
```

## Current Status

✅ **Stage 1 (prepare_data)** - COMPLETED SUCCESSFULLY

Output:
- Created symlinks to train/validation/test data
- Generated data statistics: 2000 total images (1000 train, 500 val, 500 test)
- Created metadata files

Next stages:
- Stage 2: train_model (ready to run)
- Stage 3: evaluate_model (depends on stage 2)

## How to Run the Pipeline Now

```bash
cd "/Users/sarva/Study/AIML Infra/Day 4/catvsdog"

# Run complete pipeline
dvc repro

# Or run stages individually
dvc repro train_model
dvc repro evaluate_model

# Check status
dvc status

# View DAG
dvc dag
```

## What Was Created by Stage 1

```
data/processed/
├── train/           -> symlink to catvsdog_model/datasets/data/train
├── validation/      -> symlink to catvsdog_model/datasets/data/validation
├── test/            -> symlink to catvsdog_model/datasets/data/test
├── data_stats.json  - Statistics about the dataset
└── metadata.json    - Processing metadata
```

## Important Notes

1. **Always use `python3`** on macOS, not `python`
2. **DVC lock files** can be removed if a process was interrupted
3. **The pipeline is now ready** to run the remaining stages
4. **No data modification needed** - stage 1 creates symlinks to preserve originals

## Next Steps

To continue training:

```bash
# Install required dependencies if not already installed
pip3 install tensorflow pandas pyyaml scikit-learn matplotlib seaborn

# Run the training stage
dvc repro train_model

# This will:
# - Train the model for 10 epochs (configurable in params.yaml)
# - Save the model to catvsdog_model/trained_models/
# - Generate training metrics in metrics/
```

## Verify Everything

```bash
# Check that stage 1 completed
ls -la data/processed/

# View the data statistics
cat data/processed/data_stats.json

# Check DVC status
dvc status
```

All systems ready! 🚀
