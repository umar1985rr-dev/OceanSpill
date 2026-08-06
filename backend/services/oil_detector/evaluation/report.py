import json
from pathlib import Path


class ReportGenerator:

    def __init__(self, save_dir="reports"):

        self.save_dir = Path(save_dir)

        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_json(self, metrics):

        with open(
            self.save_dir / "model_metrics.json",
            "w"
        ) as f:

            json.dump(
                metrics,
                f,
                indent=4
            )

    def save_markdown(self, metrics):

        report = f"""# Model Evaluation Report

## Performance Metrics

| Metric | Value |
|---------|-------|
| Dice | {metrics['Dice']:.4f} |
| IoU | {metrics['IoU']:.4f} |
| Precision | {metrics['Precision']:.4f} |
| Recall | {metrics['Recall']:.4f} |

## Status

✅ Model Successfully Evaluated

"""

        with open(
            self.save_dir / "evaluation_report.md",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(report)