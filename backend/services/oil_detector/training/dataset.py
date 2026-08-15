from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


class OilSpillDataset(Dataset):
    """
    Dataset class for Sentinel-1 oil spill segmentation.
    """

    def __init__(
        self,
        image_dir,
        mask_dir,
        transform=None,
        image_list=None
    ):

        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.transform = transform

        if image_list is None:
            self.images = sorted(self.image_dir.glob("*.png"))
        else:
            self.images = image_list

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):

        image_path = self.images[index]

        mask_path = self.mask_dir / image_path.name

        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mask = cv2.imread(
            str(mask_path),
            cv2.IMREAD_GRAYSCALE
        )

        image = image.astype(np.float32) / 255.0
        mask = mask.astype(np.float32) / 255.0

        if self.transform:

            augmented = self.transform(
                image=image,
                mask=mask
            )

            image = augmented["image"]
            mask = augmented["mask"]

        image = torch.tensor(
            image.transpose(2, 0, 1),
            dtype=torch.float32
        )

        mask = torch.tensor(
            mask,
            dtype=torch.float32
        ).unsqueeze(0)

        return image, mask