#!/bin/bash
echo "🔍 Verifying DVC Pipeline Files..."
echo ""

files=(
  "dvc.yaml:Pipeline definition"
  "params.yaml:Parameters configuration"
  ".dvcignore:DVC ignore patterns"
  "scripts/init_dvc_pipeline.sh:Setup script"
  "scripts/prepare_data.py:Data preparation script"
  "scripts/train_with_dvc.py:Training script"
  "scripts/evaluate_model.py:Evaluation script"
  "README_DVC_PIPELINE.md:Main documentation"
  "QUICK_START.md:Quick start guide"
  "DVC_PIPELINE_README.md:Detailed documentation"
  "DVC_PIPELINE_SUMMARY.md:Summary"
  "PIPELINE_ARCHITECTURE.md:Architecture diagrams"
)

all_found=true

for item in "${files[@]}"; do
  file="${item%%:*}"
  desc="${item##*:}"
  
  if [ -f "$file" ]; then
    echo "✓ $file - $desc"
  else
    echo "✗ $file - MISSING"
    all_found=false
  fi
done

echo ""
if [ "$all_found" = true ]; then
  echo "✅ All pipeline files are present!"
  echo ""
  echo "Next steps:"
  echo "1. Run: ./scripts/init_dvc_pipeline.sh"
  echo "2. Then: dvc repro"
else
  echo "⚠️  Some files are missing. Please check the setup."
fi
