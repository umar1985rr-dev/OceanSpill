import torch
from tqdm import tqdm

from backend.services.oil_detector.training.losses import BCEDiceLoss
from backend.services.oil_detector.training.metrics import (
    dice_score,
    iou_score,
    precision_score,
    recall_score,
)

from backend.services.oil_detector.training.logger import TrainingLogger
from backend.services.oil_detector.training.checkpoint import CheckpointManager
from backend.services.oil_detector.training.early_stopping import EarlyStopping


class Trainer:
    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        learning_rate=1e-4,
        device=None,
    ):
        self.device = (
            device
            if device
            else torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        )

        self.model = model.to(self.device)

        self.train_loader = train_loader
        self.val_loader = val_loader

        self.loss_fn = BCEDiceLoss()

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate,
        )

        self.logger = TrainingLogger()
        self.checkpoint = CheckpointManager()
        self.early_stopping = EarlyStopping(patience=5)
    def train_one_epoch(self):
        self.model.train()

        total_loss = 0

        progress = tqdm(
            self.train_loader,
            desc="Training"
        )

        for images, masks in progress:

            images = images.to(self.device)
            masks = masks.to(self.device)

            self.optimizer.zero_grad()

            predictions = self.model(images)

            loss = self.loss_fn(
                predictions,
                masks
            )

            loss.backward()

            self.optimizer.step()

            total_loss += loss.item()

            progress.set_postfix(
                loss=loss.item()
            )

        return total_loss / len(self.train_loader)
    def validate_one_epoch(self):
        self.model.eval()

        total_loss = 0
        total_dice = 0
        total_iou = 0
        total_precision = 0
        total_recall = 0

        with torch.no_grad():

            progress = tqdm(
                self.val_loader,
                desc="Validation"
            )

            for images, masks in progress:

                images = images.to(self.device)
                masks = masks.to(self.device)

                predictions = self.model(images)

                loss = self.loss_fn(
                    predictions,
                    masks
                )

                total_loss += loss.item()

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

        batches = len(self.val_loader)

        return (
            total_loss / batches,
            total_dice / batches,
            total_iou / batches,
            total_precision / batches,
            total_recall / batches,
        )
    def fit(self, epochs, resume=False):
        best_loss = float("inf")
        start_epoch = 0

        if resume:

            checkpoint = self.checkpoint.load_checkpoint(
                self.model,
                self.optimizer
            )

            if checkpoint is not None:

                start_epoch = checkpoint["epoch"] + 1
                best_loss = checkpoint["best_loss"]

                print(f"\n✅ Resuming from Epoch {start_epoch + 1}")

            else:

                print("\n⚠ No checkpoint found. Starting from scratch.")   

        for epoch in range(start_epoch, epochs):

            print(f"\nEpoch {epoch + 1}/{epochs}")

            train_loss = self.train_one_epoch()

            (
                val_loss,
                dice,
                iou,
                precision,
                recall,
            ) = self.validate_one_epoch()

            print(f"Train Loss : {train_loss:.4f}")
            print(f"Val Loss   : {val_loss:.4f}")
            print(f"Dice       : {dice:.4f}")
            print(f"IoU        : {iou:.4f}")
            print(f"Precision  : {precision:.4f}")
            print(f"Recall     : {recall:.4f}")

            self.logger.log(
                train_loss,
                val_loss,
                dice,
                iou,
                precision,
                recall,
            )

            if val_loss < best_loss:
                best_loss = val_loss

                self.checkpoint.save_best(
                    self.model
                )

                print("✅ Best model updated.")

            self.checkpoint.save_checkpoint(
                self.model,
                self.optimizer,
                epoch,
                best_loss
            )
            

            if self.early_stopping.should_stop(
                val_loss
            ):
                print("🛑 Early stopping triggered.")
                break

        self.logger.save()

        print("\n🎉 Training Completed.")   