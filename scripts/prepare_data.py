"""
Data preparation script for DVC pipeline
Validates and prepares data for training
"""
import sys
from pathlib import Path
import yaml
import shutil
import json

# Add project root to path
file = Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))


def load_params():
    """Load parameters from params.yaml"""
    params_path = root / "params.yaml"
    with open(params_path, 'r') as f:
        params = yaml.safe_load(f)
    return params


def prepare_data():
    """
    Prepare data for training by validating paths and copying to processed directory
    """
    params = load_params()

    # Get paths from parameters
    train_path = Path(params['data']['train_path'])
    val_path = Path(params['data']['validation_path'])
    test_path = Path(params['data']['test_path'])

    # Output directory
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Validate that source directories exist
    for path_name, path in [("train", train_path), ("validation", val_path), ("test", test_path)]:
        if not path.exists():
            raise FileNotFoundError(f"{path_name} directory not found at {path}")
        print(f"✓ Found {path_name} data at {path}")

    # Count images in each split
    stats = {}
    for split_name, split_path in [("train", train_path), ("validation", val_path), ("test", test_path)]:
        # Count files
        image_files = list(split_path.rglob("*.jpg")) + list(split_path.rglob("*.jpeg")) + list(split_path.rglob("*.png"))
        stats[split_name] = {
            "num_images": len(image_files),
            "path": str(split_path)
        }

        # Count per class if subdirectories exist
        subdirs = [d for d in split_path.iterdir() if d.is_dir()]
        if subdirs:
            stats[split_name]["classes"] = {}
            for subdir in subdirs:
                class_images = list(subdir.glob("*.jpg")) + list(subdir.glob("*.jpeg")) + list(subdir.glob("*.png"))
                stats[split_name]["classes"][subdir.name] = len(class_images)

        print(f"  - {split_name}: {stats[split_name]['num_images']} images")
        if "classes" in stats[split_name]:
            for class_name, count in stats[split_name]["classes"].items():
                print(f"    • {class_name}: {count}")

    # Create symbolic links or copy data to processed directory
    for split_name in ["train", "validation", "test"]:
        target = processed_dir / split_name
        if target.exists():
            shutil.rmtree(target)

        # Create symbolic link to original data
        source = Path(stats[split_name]["path"])
        try:
            target.symlink_to(source.absolute(), target_is_directory=True)
            print(f"✓ Created symlink: {target} -> {source}")
        except OSError:
            # If symlink fails (e.g., on Windows), copy instead
            shutil.copytree(source, target)
            print(f"✓ Copied: {source} -> {target}")

    # Save data statistics
    stats_file = processed_dir / "data_stats.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n✓ Saved data statistics to {stats_file}")

    # Save preparation metadata
    metadata = {
        "preprocessing_params": params['preprocessing'],
        "augmentation_params": params['augmentation'],
        "data_stats": stats
    }
    metadata_file = processed_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved metadata to {metadata_file}")

    print("\n✅ Data preparation complete!")


if __name__ == "__main__":
    prepare_data()
