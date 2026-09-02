import cv2
import numpy as np
from pathlib import Path


def generate_overlay(image_path, mask):
    """
    Saves:
    1. Original image
    2. Binary mask
    3. Overlay image

    Returns all three paths.
    """

    image = cv2.imread(image_path)

    image = cv2.resize(image, (256, 256))

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    original_path = output_dir / "original.png"
    mask_path = output_dir / "mask.png"
    overlay_path = output_dir / "overlay.png"

    cv2.imwrite(str(original_path), image)

    mask_img = (mask * 255).astype(np.uint8)

    cv2.imwrite(str(mask_path), mask_img)

    overlay = image.copy()

    overlay[mask == 1] = [0, 0, 255]

    result = cv2.addWeighted(
        image,
        0.7,
        overlay,
        0.3,
        0
    )

    cv2.imwrite(str(overlay_path), result)

    return {

        "original": str(original_path),

        "mask": str(mask_path),

        "overlay": str(overlay_path),

    }