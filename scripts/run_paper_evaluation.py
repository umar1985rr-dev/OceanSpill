"""Run the U-Net (ResNet34) evaluation on the held-out test split and
report pixel-accumulated (global) + per-sample metrics.

Reproducibility: this is the script used to produce the numbers in the
OceanSpill IEEE paper's Results section. It evaluates on the real
held-out test set (8354-pair Kaggle Sentinel-1 spill dataset, 839 test
images) and writes a JSON + Markdown report.

Run: python scripts/run_paper_evaluation.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from backend.services.oil_detector.model_loader import load_model
from backend.services.oil_detector.training.dataset import OilSpillDataset


def main() -> None:
    # ---- paths -------------------------------------------------------
    test_images = REPO_ROOT / "dataset" / "raw" / "satellite_images" / "test"
    test_masks = REPO_ROOT / "dataset" / "raw" / "masks" / "test"

    if not test_images.exists() or not test_masks.exists():
        raise SystemExit(f"Test split missing: {test_images} / {test_masks}")

    n_images = len(list(test_images.glob("*.png")))
    print(f"[eval] model: models/fine_tuned/best_model.pth")
    print(f"[eval] test set: {n_images} image/mask pairs")

    # ---- device ------------------------------------------------------
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    print(f"[eval] device: {device}")

    # ---- model -------------------------------------------------------
    model = load_model().to(device)
    model.eval()

    # ---- data --------------------------------------------------------
    dataset = OilSpillDataset(
        image_dir=test_images,
        mask_dir=test_masks,
    )
    loader = DataLoader(
        dataset,
        batch_size=16,
        shuffle=False,
        num_workers=0,
    )

    # ---- metric accumulators ----------------------------------------
    # Global (pixel-accumulated) tallies
    g_tp = g_fp = g_fn = 0.0

    # Per-sample metric lists (mean of these = mean per-image metric)
    dice_list, iou_list, prec_list, rec_list = [], [], [], []

    start = time.time()
    with torch.no_grad():
        for images, masks in loader:
            images = images.to(device)
            masks = masks.to(device)

            logits = model(images)
            preds = (torch.sigmoid(logits) > 0.5).float()
            targets = (masks > 0.5).float()

            tp = (preds * targets).sum(dim=(1, 2, 3))
            fp = (preds * (1 - targets)).sum(dim=(1, 2, 3))
            fn = ((1 - preds) * targets).sum(dim=(1, 2, 3))

            g_tp += tp.sum().item()
            g_fp += fp.sum().item()
            g_fn += fn.sum().item()

            for t, f, n in zip(tp, fp, fn, strict=False):
                t, f, n = t.item(), f.item(), n.item()
                dice_list.append(2 * t / (2 * t + f + n + 1e-6))
                iou_list.append(t / (t + f + n + 1e-6))
                prec_list.append(t / (t + f + 1e-6))
                rec_list.append(t / (t + n + 1e-6))

    elapsed = time.time() - start

    # ---- global metrics ----------------------------------------------
    g_dice = 2 * g_tp / (2 * g_tp + g_fp + g_fn + 1e-6)
    g_iou = g_tp / (g_tp + g_fp + g_fn + 1e-6)
    g_prec = g_tp / (g_tp + g_fp + 1e-6)
    g_rec = g_tp / (g_tp + g_fn + 1e-6)

    results = {
        "test_images": n_images,
        "device": str(device),
        "elapsed_seconds": round(elapsed, 1),
        "global_metrics": {
            "Dice": round(g_dice, 4),
            "IoU": round(g_iou, 4),
            "Precision": round(g_prec, 4),
            "Recall": round(g_rec, 4),
        },
        "per_image_mean_metrics": {
            "Dice": round(sum(dice_list) / len(dice_list), 4),
            "IoU": round(sum(iou_list) / len(iou_list), 4),
            "Precision": round(sum(prec_list) / len(prec_list), 4),
            "Recall": round(sum(rec_list) / len(rec_list), 4),
        },
    }

    print()
    print("==========================================")
    print("  GLOBAL (pixel-accumulated)")
    print("  Dice      :", round(g_dice, 4))
    print("  IoU       :", round(g_iou, 4))
    print("  Precision :", round(g_prec, 4))
    print("  Recall    :", round(g_rec, 4))
    print("------------------------------------------")
    print("  PER-IMAGE MEAN")
    print("  Dice      :", results["per_image_mean_metrics"]["Dice"])
    print("  IoU       :", results["per_image_mean_metrics"]["IoU"])
    print("  Precision :", results["per_image_mean_metrics"]["Precision"])
    print("  Recall    :", results["per_image_mean_metrics"]["Recall"])
    print("==========================================")
    print(f"[eval] done in {elapsed:.1f}s over {n_images} images")

    # ---- write artifacts ---------------------------------------------
    out_dir = REPO_ROOT / "evaluation_results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "model_metrics.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    md = [
        "# OceanSpill Model Evaluation",
        "",
        f"- Test images: **{n_images}**",
        f"- Device: `{device}`",
        f"- Wall time: {elapsed:.1f}s",
        "",
        "## Global (pixel-accumulated) metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for k, v in results["global_metrics"].items():
        md.append(f"| {k} | **{v:.4f}** |")
    md += [
        "",
        "## Per-image mean metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for k, v in results["per_image_mean_metrics"].items():
        md.append(f"| {k} | **{v:.4f}** |")
    md.append("")
    (out_dir / "evaluation_report.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    print(f"[eval] wrote evaluation_results/model_metrics.json")


if __name__ == "__main__":
    main()