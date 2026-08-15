import torch

from backend.services.oil_detector.preprocess import preprocess_image
from backend.services.oil_detector.model_loader import load_model

model = load_model()


def detect_oil_spill(image_path):
    """
    Runs inference using the pretrained U-Net.
    """

    image = preprocess_image(image_path)

    with torch.no_grad():
        prediction = model(image)

    return prediction