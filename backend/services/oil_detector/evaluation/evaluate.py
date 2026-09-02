import torch
from tqdm import tqdm

from backend.services.oil_detector.evaluation.visualization import PredictionVisualizer
from backend.services.oil_detector.evaluation.metrics import (
    dice_score,
    iou_score,
    precision_score,
    recall_score,
)


class Evaluator:

    def __init__(
        self,
        model,
        dataloader,
        device=None,
    ):

        self.device = (
            device
            if device
            else torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )
        )

        self.model = model.to(self.device)

        self.dataloader = dataloader

        self.visualizer = PredictionVisualizer()

    def evaluate(self):

        self.model.eval()

        total_dice = 0
        total_iou = 0
        total_precision = 0
        total_recall = 0

        with torch.no_grad():

            progress = tqdm(
                self.dataloader,
                desc="Evaluating"
            )

            for index, (images, masks) in enumerate(progress):

                images = images.to(self.device)
                masks = masks.to(self.device)

                predictions = self.model(images)

                self.visualizer.save_prediction(
                    images[0],
                    masks[0],
                    predictions[0],
                    f"sample_{index}.png"
                )

                total_dice += dice_score(
                    predictions,
                    masks
                )

                total_iou += iou_score(
                    predictions,
                    masks
                )

                total_precision += precision_score(
                    predictions,
                    masks
                )

                total_recall += recall_score(
                    predictions,
                    masks
                )

        batches = len(self.dataloader)

        return {
            "Dice": total_dice / batches,
            "IoU": total_iou / batches,
            "Precision": total_precision / batches,
            "Recall": total_recall / batches,
        }