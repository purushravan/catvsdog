# 🎯 DVC Pipeline for Cat vs Dog Classification - Index

Welcome! This directory contains a complete DVC (Data Version Control) pipeline for training and evaluating the cat vs dog classification model.

## 📚 Documentation Index

Start here based on your needs:

### 🚀 **Just Want to Get Started?**
→ Read [QUICK_START.md](QUICK_START.md) (5 minutes)

Quick commands:
```bash
./scripts/init_dvc_pipeline.sh  # Setup
dvc repro                       # Run pipeline
dvc metrics show                # View results
```

### 📖 **Want Full Details?**
→ Read [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md) (Complete guide)

Covers:
- Detailed pipeline stages
- Setup instructions
- Experiment tracking
- Troubleshooting
- Best practices

### 📋 **Want a Quick Overview?**
→ Read [DVC_PIPELINE_SUMMARY.md](DVC_PIPELINE_SUMMARY.md) (Summary)

Includes:
- What was created
- Pipeline overview
- Key features
- Usage examples
- Customization guide

### 🏗️ **Want to Understand the Architecture?**
→ Read [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) (Architecture diagrams)

Shows:
- System architecture
- Data flow diagrams
- Dependency graphs
- Integration points
- Version control strategy

## 📁 File Structure

```
catvsdog/
├── README_DVC_PIPELINE.md          ← You are here! 👋
├── QUICK_START.md                  ← 5-minute quick start
├── DVC_PIPELINE_README.md          ← Complete documentation
├── DVC_PIPELINE_SUMMARY.md         ← Overview and summary
├── PIPELINE_ARCHITECTURE.md        ← Architecture diagrams
│
├── dvc.yaml                        ← Pipeline definition
├── params.yaml                     ← All parameters
├── .dvcignore                      ← DVC ignore patterns
│
├── scripts/                        ← Pipeline scripts
│   ├── init_dvc_pipeline.sh       ← Automated setup
│   ├── prepare_data.py            ← Stage 1: Data prep
│   ├── train_with_dvc.py          ← Stage 2: Training (alternative)
│   └── evaluate_model.py          ← Stage 3: Evaluation
│
├── catvsdog_model/                 ← Original codebase
│   ├── train_model.py             ← Original training script
│   ├── model.py                   ← Model architecture
│   ├── datasets/                  ← Data (DVC tracked)
│   └── trained_models/            ← Models (DVC tracked)
│
├── data/                           ← Pipeline data
│   └── processed/                 ← Processed data (DVC tracked)
│
└── metrics/                        ← Output metrics (Git tracked)
    ├── training_metrics.json
    ├── training_history.csv
    ├── evaluation_metrics.json
    ├── confusion_matrix.png
    └── classification_report.json
```

## 🎯 What is This Pipeline?

A **3-stage DVC pipeline** that automates:

1. **Data Preparation** - Validates and prepares training data
2. **Model Training** - Trains CNN with configurable parameters
3. **Model Evaluation** - Evaluates and generates metrics

**Key Benefits:**
- ✅ Reproducible experiments
- ✅ Version controlled data and models
- ✅ Easy parameter tuning
- ✅ Automated metrics tracking
- ✅ Team collaboration

## 🚀 Quick Commands Reference

```bash
# Setup (one-time)
./scripts/init_dvc_pipeline.sh

# Run complete pipeline
dvc repro

# Check status
dvc status
dvc dag

# View metrics
dvc metrics show
cat metrics/training_metrics.json

# Run experiments
dvc exp run --set-param train.epochs=20
dvc exp show

# Push/pull data
dvc push
dvc pull
```

## 🎓 Learning Path

**New to DVC?**
1. Read the training material: [`../DVC_Training_Material.docx.pdf`](../DVC_Training_Material.docx.pdf)
2. Follow [QUICK_START.md](QUICK_START.md)
3. Experiment with parameters
4. Read [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md) for details

**Experienced with DVC?**
1. Review [params.yaml](params.yaml)
2. Check [dvc.yaml](dvc.yaml) pipeline definition
3. Run `dvc repro`
4. Explore experiments: `dvc exp run --set-param ...`

## 🔑 Key Concepts

### Pipeline Stages
```
prepare_data → train_model → evaluate_model
```

### Parameters ([params.yaml](params.yaml))
All configurable values in one place:
- Data paths
- Image size, batch size
- Model architecture
- Training hyperparameters
- Callbacks configuration

### Outputs
- **DVC tracked**: datasets, models, processed data
- **Git tracked**: metrics, plots, configuration
- **Cached**: intermediate results for fast reruns

## 🎨 Typical Workflows

### Initial Training
```bash
dvc repro
git add dvc.lock metrics/
git commit -m "Baseline model"
```

### Experiment with Hyperparameters
```bash
dvc exp run --set-param train.epochs=20 -n "20-epochs"
dvc exp run --set-param train.optimizer=adam -n "adam"
dvc exp show
dvc exp apply <best-experiment>
```

### Team Collaboration
```bash
# Push your changes
dvc push
git push

# Pull teammate's changes
git pull
dvc pull
dvc repro  # Should use cache
```

## 🆘 Need Help?

| Question | See |
|----------|-----|
| How do I get started? | [QUICK_START.md](QUICK_START.md) |
| How does the pipeline work? | [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md) |
| What files were created? | [DVC_PIPELINE_SUMMARY.md](DVC_PIPELINE_SUMMARY.md) |
| How is it architected? | [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) |
| How do I run experiments? | [DVC_PIPELINE_README.md#experiment-tracking](DVC_PIPELINE_README.md#experiment-tracking) |
| How do I change parameters? | Edit [params.yaml](params.yaml) or use `dvc exp run --set-param` |
| Pipeline not working? | [DVC_PIPELINE_README.md#troubleshooting](DVC_PIPELINE_README.md#troubleshooting) |
| What is DVC? | [`../DVC_Training_Material.docx.pdf`](../DVC_Training_Material.docx.pdf) |

## 🌟 Features

- ✨ **3-stage pipeline**: Data prep → Training → Evaluation
- ⚙️ **Parameterized**: All settings in `params.yaml`
- 📊 **Metrics tracking**: JSON metrics + CSV history + plots
- 🧪 **Experiment management**: Easy A/B testing
- 💾 **Data versioning**: Track datasets and models
- 🚀 **Reproducible**: `dvc.lock` ensures exact replication
- 🤝 **Collaborative**: Share data via remotes
- 🔄 **Caching**: Skip unchanged stages
- 📈 **MLflow integration**: Automatic experiment tracking
- 🎯 **Production-ready**: CI/CD compatible

## 📞 Support

- **DVC Documentation**: https://dvc.org/doc
- **Training Material**: See [`../DVC_Training_Material.docx.pdf`](../DVC_Training_Material.docx.pdf)
- **Issues**: Check [troubleshooting section](DVC_PIPELINE_README.md#troubleshooting)

## 🎉 Ready to Start?

```bash
# 1. Setup
cd /Users/sarva/Study/AIML\ Infra/Day\ 4/catvsdog
./scripts/init_dvc_pipeline.sh

# 2. Run
dvc repro

# 3. Explore
dvc metrics show
dvc dag
```

**That's it! Happy experimenting! 🚀**

---

*Created as an example DVC pipeline based on the DVC Training Material*
