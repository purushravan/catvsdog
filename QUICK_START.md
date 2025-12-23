# Quick Start Guide - DVC Pipeline

This guide will get you up and running with the DVC pipeline in 5 minutes.

## 🚀 Quick Setup (3 steps)

### 1. Initialize the Pipeline

```bash
cd catvsdog
./scripts/init_dvc_pipeline.sh
```

This script will:
- Initialize DVC in your repository
- Configure local storage for data versioning
- Track your dataset with DVC
- Validate pipeline configuration

### 2. Review Parameters (Optional)

Open [params.yaml](params.yaml) and adjust training parameters if needed:

```yaml
train:
  epochs: 10          # Change to 20 for better results
  optimizer: rmsprop  # Try 'adam' for faster convergence

preprocessing:
  batch_size: 32      # Adjust based on your GPU memory
```

### 3. Run the Pipeline

```bash
# Run the complete pipeline
dvc repro

# This will:
# 1. Prepare data → data/processed/
# 2. Train model → catvsdog_model/trained_models/
# 3. Evaluate model → metrics/
```

## 📊 View Results

```bash
# Show all metrics
dvc metrics show

# View training history
cat metrics/training_metrics.json

# Check confusion matrix
open metrics/confusion_matrix.png  # macOS
# or
xdg-open metrics/confusion_matrix.png  # Linux
```

## 🧪 Run Experiments

```bash
# Experiment with different epochs
dvc exp run --set-param train.epochs=20 -n "20-epochs"

# Try a different optimizer
dvc exp run --set-param train.optimizer=adam -n "adam-opt"

# View all experiments
dvc exp show

# Compare experiments
dvc exp diff
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `dvc.yaml` | Pipeline definition (stages, dependencies, outputs) |
| `params.yaml` | All configurable parameters |
| `dvc.lock` | Pipeline state (auto-generated, commit to git) |
| `metrics/` | Training and evaluation metrics |
| `data/processed/` | Prepared data (DVC tracked) |

## 🔄 Common Commands

```bash
# Check what will run
dvc status

# View pipeline structure
dvc dag

# Run only data preparation
dvc repro prepare_data

# Force rerun everything
dvc repro --force

# Push data to remote
dvc push

# Pull data from remote
dvc pull
```

## 💡 Pro Tips

1. **Commit often**: Always commit `dvc.lock` and metrics after successful runs
   ```bash
   git add dvc.lock metrics/ params.yaml
   git commit -m "Training run with X epochs"
   ```

2. **Use experiments**: Don't modify params.yaml directly, use `dvc exp run`
   ```bash
   dvc exp run --set-param train.epochs=15
   ```

3. **Track changes**: Use meaningful experiment names
   ```bash
   dvc exp run -n "high-lr-experiment" --set-param train.learning_rate=0.01
   ```

4. **Visualize**: Use DVC plots for comparing runs
   ```bash
   dvc plots show metrics/training_history.csv
   ```

## 🐛 Troubleshooting

### Pipeline won't run
```bash
dvc status  # Check what's outdated
dvc repro --force  # Force rerun
```

### Missing data
```bash
dvc pull  # Pull from remote
dvc checkout  # Restore cached files
```

### Dependencies changed
```bash
# DVC automatically detects changes
# Just run dvc repro again
```

## 📖 Learn More

- Full documentation: [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md)
- DVC official docs: https://dvc.org/doc
- Training material: [DVC_Training_Material.docx.pdf](../DVC_Training_Material.docx.pdf)

## 🎯 Example Workflow

```bash
# 1. Initial training
dvc repro
git add dvc.lock metrics/
git commit -m "Initial training baseline"

# 2. Experiment with parameters
dvc exp run --set-param train.epochs=20 -n "more-epochs"
dvc exp run --set-param train.optimizer=adam -n "adam"

# 3. Compare results
dvc exp show

# 4. Apply best experiment
dvc exp apply exp-<best-id>
git add params.yaml dvc.lock metrics/
git commit -m "Apply best experiment: 20 epochs with Adam"

# 5. Push everything
dvc push
git push
```

---

**Need help?** Check the [full documentation](DVC_PIPELINE_README.md) or open an issue.
