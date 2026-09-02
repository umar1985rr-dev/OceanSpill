import albumentations as A


def get_training_augmentation():
    """
    Augmentations applied only during training.
    """

    return A.Compose(
        [
            A.HorizontalFlip(p=0.5),

            A.VerticalFlip(p=0.5),

            A.RandomRotate90(p=0.5),

            A.Rotate(
                limit=20,
                p=0.5
            ),

            A.RandomBrightnessContrast(
                brightness_limit=0.2,
                contrast_limit=0.2,
                p=0.5
            ),

            A.GaussNoise(
                p=0.3
            )
        ]
    )


def get_validation_augmentation():
    """
    Validation images should NOT be randomly augmented.
    Only return the image as-is.
    """

    return A.Compose([])