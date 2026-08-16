import torch

from backend.services.oil_detector.preprocess import preprocess_image
from backend.services.oil_detector.model_loader import load_model

# Lazy loading: model is loaded on first use, not at import time
_model = None


def _get_model():
    """Lazy load model on first use."""
    global _model
    if _model is None:
        _model = load_model()
    return _model


def detect_oil_spill(image_path):
    """
    Runs inference using the pretrained U-Net.
    Model is automatically downloaded from Git LFS on first use if needed.
    """
    model = _get_model()

    image = preprocess_image(image_path)

    with torch.no_grad():
        prediction = model(image)

    return prediction