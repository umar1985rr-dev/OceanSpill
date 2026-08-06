import torch
from pathlib import Path


class CheckpointManager:

    def __init__(
        self,
        save_dir="models/fine_tuned"
    ):

        self.save_dir = Path(save_dir)

        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_best(
        self,
        model
    ):

        torch.save(
            model.state_dict(),
            self.save_dir / "best_model.pth"
        )

    def save_checkpoint(
        self,
        model,
        optimizer,
        epoch,
        best_loss
    ):

        checkpoint = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "best_loss": best_loss,
        }

        torch.save(
            checkpoint,
            self.save_dir / "last_checkpoint.pth"
        )

    def load_checkpoint(
        self,
        model,
        optimizer
    ):

        checkpoint_path = self.save_dir / "last_checkpoint.pth"

        if not checkpoint_path.exists():
            return None

        checkpoint = torch.load(
            checkpoint_path,
            map_location="cpu",
            weights_only=False
        )

        model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )

        return checkpoint