import torch


def dice_score(prediction, target, smooth=1e-6):
    prediction = torch.sigmoid(prediction)
    prediction = (prediction > 0.5).float()

    prediction = prediction.view(-1)
    target = target.view(-1)

    intersection = (prediction * target).sum()

    dice = (
        2 * intersection + smooth
    ) / (
        prediction.sum() + target.sum() + smooth
    )

    return dice.item()


def iou_score(prediction, target, smooth=1e-6):
    prediction = torch.sigmoid(prediction)
    prediction = (prediction > 0.5).float()

    prediction = prediction.view(-1)
    target = target.view(-1)

    intersection = (prediction * target).sum()

    union = prediction.sum() + target.sum() - intersection

    iou = (
        intersection + smooth
    ) / (
        union + smooth
    )

    return iou.item()


def precision_score(prediction, target, smooth=1e-6):
    prediction = torch.sigmoid(prediction)
    prediction = (prediction > 0.5).float()

    tp = (prediction * target).sum()

    fp = (prediction * (1 - target)).sum()

    precision = (
        tp + smooth
    ) / (
        tp + fp + smooth
    )

    return precision.item()


def recall_score(prediction, target, smooth=1e-6):
    prediction = torch.sigmoid(prediction)
    prediction = (prediction > 0.5).float()

    tp = (prediction * target).sum()

    fn = ((1 - prediction) * target).sum()

    recall = (
        tp + smooth
    ) / (
        tp + fn + smooth
    )

    return recall.item()