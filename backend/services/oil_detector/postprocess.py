import torch
import numpy as np


def postprocess_prediction(prediction):
    """
    Convert model output into a binary mask and
    calculate oil spill percentage.
    """

    prediction = torch.sigmoid(prediction)

    prediction = prediction.squeeze().cpu().numpy()

    mask = (prediction > 0.5).astype(np.uint8)

    spill_percentage = (
        np.sum(mask) / mask.size
    ) * 100

    return mask, spill_percentage