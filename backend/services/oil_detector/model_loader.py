import torch
import segmentation_models_pytorch as smp
from pathlib import Path
import subprocess
import sys

MODEL_PATH = Path("models/fine_tuned/best_model.pth")
MIN_MODEL_SIZE = 1_000_000  # 1MB - LFS pointers are ~133 bytes


def _is_lfs_pointer(filepath: Path) -> bool:
    """Check if file is a Git LFS pointer (small text file starting with 'version')."""
    try:
        if not filepath.exists():
            return True
        if filepath.stat().st_size > MIN_MODEL_SIZE:
            return False
        with open(filepath, 'rb') as f:
            header = f.read(8)
        return header.startswith(b'version')
    except Exception:
        return True


def _run_git_lfs_pull() -> bool:
    """Attempt to download model via git lfs. Returns True on success."""
    commands = [
        ["git", "lfs", "pull"],
        ["git", "lfs", "fetch", "--all"],
        ["git", "lfs", "checkout"],
    ]
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 min timeout
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            continue
    return False


def _ensure_model_downloaded() -> bool:
    """Ensure the actual model file exists. Download via LFS if needed."""
    if MODEL_PATH.exists() and not _is_lfs_pointer(MODEL_PATH):
        return True  # Already have the real model

    print(f"[ModelLoader] Model not found or is LFS pointer. Downloading via Git LFS...")
    print(f"[ModelLoader] Running: git lfs pull")

    if _run_git_lfs_pull():
        if MODEL_PATH.exists() and not _is_lfs_pointer(MODEL_PATH):
            size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
            print(f"[ModelLoader] Model downloaded successfully ({size_mb:.1f} MB)")
            return True

    # If we get here, download failed
    print(f"[ModelLoader] ERROR: Failed to download model via Git LFS.")
    print(f"[ModelLoader] Please run manually:")
    print(f"    git lfs install")
    print(f"    git lfs pull")
    return False


def load_model():
    """
    Load the U-Net model with ResNet34 encoder.
    Automatically downloads model from Git LFS if needed.
    """
    # Ensure model is downloaded before attempting to load
    if not _ensure_model_downloaded():
        raise RuntimeError(
            "Model file not available. Run 'git lfs pull' in the project root "
            "to download the model from Git LFS."
        )

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1,
    )

    state_dict = torch.load(
        MODEL_PATH,
        map_location="cpu",
        weights_only=False  # Required for this model format
    )

    model.load_state_dict(state_dict)
    model.eval()

    return model


# Backward compatibility
model = load_model()