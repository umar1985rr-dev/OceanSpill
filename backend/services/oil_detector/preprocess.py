import cv2
import numpy as np
import torch


IMAGE_SIZE = 256


def preprocess_image(image_path):
    """
    Load and preprocess a Sentinel-1 image for U-Net inference.

    Args:
        image_path (str): Path to the image.

    Returns:
        torch.Tensor: Preprocessed image tensor of shape
                      (1, 3, 256, 256)
    """

    # Read image
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Convert BGR → RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))

    # Normalize
    image = image.astype(np.float32) / 255.0

    # Convert HWC → CHW
    image = np.transpose(image, (2, 0, 1))

    # Convert to Tensor
    tensor = torch.tensor(image, dtype=torch.float32)

    # Add batch dimension
    tensor = tensor.unsqueeze(0)

    return tensor