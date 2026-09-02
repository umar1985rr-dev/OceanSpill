# Oil Detection Service

## Purpose

This service detects marine oil spills from Sentinel-1 SAR satellite images using a fine-tuned U-Net segmentation model.

## Workflow

Satellite Image
↓
Preprocessing
↓
U-Net Model
↓
Binary Spill Mask
↓
Post-processing
↓
Spill Area Estimation
↓
Overlay Generation

## Components

- model_loader.py
- preprocess.py
- detect.py
- postprocess.py
- overlay.py