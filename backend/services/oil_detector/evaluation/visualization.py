from pathlib import Path

import matplotlib.pyplot as plt
import torch


class PredictionVisualizer:

    def __init__(self, save_dir="reports/sample_predictions"):

        self.save_dir = Path(save_dir)

        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_prediction(
        self,
        image,
        ground_truth,
        prediction,
        filename
    ):

        image = image.cpu().permute(1, 2, 0).numpy()

        ground_truth = (
            ground_truth.cpu()
            .squeeze()
            .numpy()
        )

        prediction = torch.sigmoid(
            prediction
        )

        prediction = (
            prediction > 0.5
        ).float()

        prediction = (
            prediction.cpu()
            .squeeze()
            .numpy()
        )

        fig, axes = plt.subplots(
            1,
            3,
            figsize=(12, 4)
        )

        axes[0].imshow(image)
        axes[0].set_title("Original")

        axes[1].imshow(
            ground_truth,
            cmap="gray"
        )
        axes[1].set_title("Ground Truth")

        axes[2].imshow(
            prediction,
            cmap="gray"
        )
        axes[2].set_title("Prediction")

        for ax in axes:
            ax.axis("off")

        plt.tight_layout()

        plt.savefig(
            self.save_dir / filename
        )

        plt.close()