import torch
import segmentation_models_pytorch as smp
from pathlib import Path

MODEL_PATH = Path("models/fine_tuned/best_model.pth")


def load_model():

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=3,
        classes=1,
    )

    model.load_state_dict(
        torch.load(
            MODEL_PATH,
            map_location="cpu",
            weights_only=False
        )
    )

    model.eval()

    return model