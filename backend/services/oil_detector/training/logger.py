import json
from pathlib import Path


class TrainingLogger:

    def __init__(self):

        self.history = {
            "train_loss": [],
            "val_loss": [],
            "dice": [],
            "iou": [],
            "precision": [],
            "recall": []
        }

    def log(
        self,
        train_loss,
        val_loss,
        dice,
        iou,
        precision,
        recall
    ):

        self.history["train_loss"].append(train_loss)
        self.history["val_loss"].append(val_loss)
        self.history["dice"].append(dice)
        self.history["iou"].append(iou)
        self.history["precision"].append(precision)
        self.history["recall"].append(recall)

    def save(
        self,
        filepath="models/fine_tuned/training_history.json"
    ):

        Path(filepath).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(filepath, "w") as f:

            json.dump(
                self.history,
                f,
                indent=4
            )