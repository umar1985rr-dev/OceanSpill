import torch


def dice_score(predictions, targets, smooth=1e-6):

    predictions = torch.sigmoid(predictions)
    predictions = (predictions > 0.5).float()

    intersection = (predictions * targets).sum()

    union = predictions.sum() + targets.sum()

    return (
        (2 * intersection + smooth)
        /
        (union + smooth)
    ).item()


def iou_score(predictions, targets, smooth=1e-6):

    predictions = torch.sigmoid(predictions)
    predictions = (predictions > 0.5).float()

    intersection = (predictions * targets).sum()

    union = (
        predictions.sum()
        +
        targets.sum()
        -
        intersection
    )

    return (
        (intersection + smooth)
        /
        (union + smooth)
    ).item()


def precision_score(predictions, targets, smooth=1e-6):

    predictions = torch.sigmoid(predictions)
    predictions = (predictions > 0.5).float()

    true_positive = (predictions * targets).sum()

    predicted_positive = predictions.sum()

    return (
        (true_positive + smooth)
        /
        (predicted_positive + smooth)
    ).item()


def recall_score(predictions, targets, smooth=1e-6):

    predictions = torch.sigmoid(predictions)
    predictions = (predictions > 0.5).float()

    true_positive = (predictions * targets).sum()

    actual_positive = targets.sum()

    return (
        (true_positive + smooth)
        /
        (actual_positive + smooth)
    ).item()