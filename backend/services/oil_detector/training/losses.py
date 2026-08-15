import torch
import torch.nn as nn


class DiceLoss(nn.Module):
    """
    Dice Loss for binary segmentation.
    """

    def __init__(self, smooth=1):
        super().__init__()
        self.smooth = smooth

    def forward(self, prediction, target):

        prediction = torch.sigmoid(prediction)

        prediction = prediction.view(-1)
        target = target.view(-1)

        intersection = (prediction * target).sum()

        dice = (
            2.0 * intersection + self.smooth
        ) / (
            prediction.sum() + target.sum() + self.smooth
        )

        return 1 - dice


class BCEDiceLoss(nn.Module):
    """
    BCE + Dice Loss
    """

    def __init__(self):
        super().__init__()

        self.bce = nn.BCEWithLogitsLoss()

        self.dice = DiceLoss()

    def forward(self, prediction, target):

        bce_loss = self.bce(
            prediction,
            target
        )

        dice_loss = self.dice(
            prediction,
            target
        )

        return bce_loss + dice_loss