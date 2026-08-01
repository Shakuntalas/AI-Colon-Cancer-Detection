# 🔬 Preprocessing

## Purpose

This directory contains the **image preprocessing pipeline** for histopathology images before they are fed into the EfficientNetB0 model.

## Structure

```
preprocessing/
├── __init__.py
├── image_preprocessor.py      ← Core preprocessing pipeline
├── augmentation.py            ← Data augmentation strategies
├── color_normalization.py     ← Stain normalization for histopathology
├── quality_checker.py         ← Image quality validation
└── README.md
```

## Preprocessing Pipeline

```
Raw Image (768×768 JPEG)
    │
    ▼
┌──────────────────────┐
│  Quality Validation  │ ← Check resolution, blur, artifacts
├──────────────────────┤
│  Color Normalization │ ← Stain normalization (Macenko/Reinhard)
├──────────────────────┤
│  Resize to 224×224   │ ← EfficientNetB0 input dimensions
├──────────────────────┤
│  Pixel Normalization │ ← Scale to [0, 1] range
├──────────────────────┤
│  Batch Dimension     │ ← Expand dims for inference
└──────────────────────┘
    │
    ▼
Model-Ready Tensor (1, 224, 224, 3)
```

## Data Augmentation (Training Only)

| Augmentation | Range |
|---|---|
| Horizontal Flip | 50% probability |
| Vertical Flip | 50% probability |
| Rotation | ±20° |
| Zoom | ±10% |
| Brightness | ±15% |
| Contrast | ±10% |
