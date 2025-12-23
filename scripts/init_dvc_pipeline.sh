#!/bin/bash
# DVC Pipeline Initialization Script

set -e  # Exit on error

echo "🚀 Initializing DVC Pipeline for Cat vs Dog Classification"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "catvsdog_model/train_model.py" ]; then
    echo -e "${RED}Error: Please run this script from the catvsdog/ directory${NC}"
    exit 1
fi

echo ""
echo "📋 Step 1: Checking prerequisites..."
echo "------------------------------------"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository exists${NC}"
fi

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo -e "${RED}✗ DVC not found. Installing...${NC}"
    pip install dvc dvc-s3
else
    echo -e "${GREEN}✓ DVC is installed ($(dvc version))${NC}"
fi

echo ""
echo "📋 Step 2: Initializing DVC..."
echo "------------------------------"

# Initialize DVC if not already done
if [ ! -d ".dvc" ]; then
    dvc init
    echo -e "${GREEN}✓ DVC initialized${NC}"
else
    echo -e "${GREEN}✓ DVC already initialized${NC}"
fi

echo ""
echo "📋 Step 3: Configuring DVC remote storage..."
echo "--------------------------------------------"

# Check if remote exists
if ! dvc remote list | grep -q "local_storage"; then
    echo "Setting up local remote storage..."
    mkdir -p ../dvc-storage
    dvc remote add -d local_storage ../dvc-storage
    echo -e "${GREEN}✓ Local remote storage configured at ../dvc-storage${NC}"
else
    echo -e "${GREEN}✓ Remote storage already configured${NC}"
fi

echo ""
echo "📋 Step 4: Creating necessary directories..."
echo "-------------------------------------------"

mkdir -p data/processed
mkdir -p metrics
mkdir -p scripts

echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo "📋 Step 5: Tracking data with DVC..."
echo "------------------------------------"

# Track dataset if .dvc file doesn't exist
if [ ! -f "catvsdog_model/datasets/data.dvc" ]; then
    if [ -d "catvsdog_model/datasets/data" ]; then
        echo "Tracking dataset..."
        dvc add catvsdog_model/datasets/data
        git add catvsdog_model/datasets/data.dvc catvsdog_model/datasets/.gitignore
        echo -e "${GREEN}✓ Dataset tracked with DVC${NC}"
    else
        echo -e "${YELLOW}⚠ Dataset directory not found, skipping tracking${NC}"
    fi
else
    echo -e "${GREEN}✓ Dataset already tracked${NC}"
fi

echo ""
echo "📋 Step 6: Validating pipeline configuration..."
echo "-----------------------------------------------"

# Check if dvc.yaml exists
if [ -f "dvc.yaml" ]; then
    echo "Validating pipeline..."
    dvc dag
    echo -e "${GREEN}✓ Pipeline configuration valid${NC}"
else
    echo -e "${RED}✗ dvc.yaml not found${NC}"
    exit 1
fi

echo ""
echo "📋 Step 7: Checking params.yaml..."
echo "----------------------------------"

if [ -f "params.yaml" ]; then
    echo -e "${GREEN}✓ params.yaml exists${NC}"
    echo "Parameters configured:"
    grep -E "^[a-z_]+:" params.yaml | head -10
else
    echo -e "${RED}✗ params.yaml not found${NC}"
    exit 1
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✅ DVC Pipeline initialization complete!${NC}"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Review params.yaml and adjust parameters as needed"
echo "2. Run the pipeline: dvc repro"
echo "3. Check status: dvc status"
echo "4. View metrics: dvc metrics show"
echo ""
echo "For more information, see DVC_PIPELINE_README.md"
echo ""
echo "Quick start:"
echo "  $ dvc repro              # Run the complete pipeline"
echo "  $ dvc dag                # View pipeline structure"
echo "  $ dvc exp run -n test    # Run an experiment"
echo ""
