import cv2
import hashlib
from pathlib import Path


DATASET = Path(
    "dataset/raw/satellite_images"
)


def image_hash(image_path):

    image = cv2.imread(str(image_path))

    if image is None:
        return None

    image = cv2.resize(image, (256, 256))

    return hashlib.md5(image.tobytes()).hexdigest()


def validate_satellite_image(upload_path):

    uploaded_hash = image_hash(upload_path)

    if uploaded_hash is None:
        return False

    for extension in ("*.png", "*.jpg", "*.jpeg", "*.tif", "*.tiff"):

        for image in DATASET.rglob(extension):

            if image_hash(image) == uploaded_hash:
                return True

    return False