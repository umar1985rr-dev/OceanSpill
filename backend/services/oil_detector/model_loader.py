import torch
import segmentation_models_pytorch as smp
from pathlib import Path
import subprocess
import sys
import shutil

MODEL_PATH = Path("models/fine_tuned/best_model.pth")
MIN_MODEL_SIZE = 1_000_000  # 1MB - LFS pointers are ~133 bytes

MODEL_URL = "https://github.com/umar1985rr-dev/OceanSpill/releases/download/v1.0.0-model/best_model.pth"


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


def _download_model_direct() -> bool:
    """Download model directly from GitHub Release using urllib/curl."""
    # Try curl first (Windows 10 1803+ has it built-in)
    curl_path = shutil.which("curl")
    if curl_path:
        try:
            result = subprocess.run(
                [curl_path, "-L", "-o", str(MODEL_PATH), MODEL_URL,
                 "--progress-bar", "--retry", "3", "--retry-delay", "5", "--connect-timeout", "30"],
                timeout=300,
            )
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    # Try Python urllib as last resort
    try:
        import urllib.request
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        print(f"[ModelLoader] Downloading model from {MODEL_URL}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        return True
    except Exception as e:
        print(f"[ModelLoader] Direct download failed: {e}")
        return False


def _ensure_model_downloaded() -> bool:
    """Ensure the actual model file exists. Download via direct URL first, then LFS fallback."""
    if MODEL_PATH.exists() and not _is_lfs_pointer(MODEL_PATH):
        return True  # Already have the real model

    print(f"[ModelLoader] Model not found or is LFS pointer. Downloading from GitHub Release...")
    print(f"[ModelLoader] URL: {MODEL_URL}")

    # Try direct download first (more reliable, doesn't need git)
    if _download_model_direct():
        if MODEL_PATH.exists() and not _is_lfs_pointer(MODEL_PATH):
            size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
            print(f"[ModelLoader] Model downloaded successfully ({size_mb:.1f} MB)")
            return True

    print(f"[ModelLoader] Direct download failed. Trying Git LFS as fallback...")

    # Check if git is available before trying LFS
    if not shutil.which("git"):
        print(f"[ModelLoader] ERROR: Git not found in PATH. Cannot use Git LFS fallback.")
        print(f"[ModelLoader] Please install Git from https://git-scm.com/")
        print(f"[ModelLoader] Or manually download the model from:")
        print(f"    {MODEL_URL}")
        print(f"    and place it at: {MODEL_PATH}")
        return False

    if _run_git_lfs_pull():
        if MODEL_PATH.exists() and not _is_lfs_pointer(MODEL_PATH):
            size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
            print(f"[ModelLoader] Model downloaded successfully via Git LFS ({size_mb:.1f} MB)")
            return True

    # If we get here, download failed
    print(f"[ModelLoader] ERROR: Failed to download model via Git LFS.")
    print(f"[ModelLoader] Please run manually:")
    print(f"    git lfs install")
    print(f"    git lfs pull")
    print(f"[ModelLoader] Or manually download from: {MODEL_URL}")
    return False


def load_model():
    """
    Load the U-Net model with ResNet34 encoder.
    Automatically downloads model from GitHub Release (primary) or Git LFS (fallback) if needed.
    """
    # Ensure model is downloaded before attempting to load
    if not _ensure_model_downloaded():
        raise RuntimeError(
            "Model file not available. "
            f"Run 'git lfs pull' in the project root to download the model from Git LFS, "
            f"or manually download from {MODEL_URL} and place at {MODEL_PATH}."
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