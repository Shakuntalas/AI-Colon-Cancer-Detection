# 🔥 Grad-CAM — Explainable AI

## Purpose

This directory contains the **Gradient-weighted Class Activation Mapping (Grad-CAM)** implementation for generating visual explanations of the model's predictions.

## Why Grad-CAM?

In clinical settings, doctors need to understand *why* an AI model made a specific prediction. Grad-CAM highlights the regions of the histopathology image that most influenced the classification decision, building trust and enabling informed clinical decisions.

## Structure

```
gradcam/
├── __init__.py
├── gradcam_generator.py       ← Core Grad-CAM heatmap computation
├── guided_gradcam.py          ← Guided Grad-CAM for finer detail
├── heatmap_overlay.py         ← Overlay heatmap on original image
├── visualization.py           ← Side-by-side comparison visualizations
└── README.md
```

## How Grad-CAM Works

```
Input Image → Forward Pass → Target Conv Layer Output
                                       │
                                       ▼
                              Compute Gradients
                              (∂y_class / ∂A_k)
                                       │
                                       ▼
                              Global Average Pool
                              (importance weights α_k)
                                       │
                                       ▼
                              Weighted Combination
                              (ReLU(Σ α_k · A_k))
                                       │
                                       ▼
                              Resize to Input Size
                                       │
                                       ▼
                              Apply Colormap (jet)
                                       │
                                       ▼
                              Overlay on Original
```

## Configuration

| Parameter | Default | Description |
|---|---|---|
| `target_layer` | `top_conv` | Last convolutional layer in EfficientNetB0 |
| `colormap` | `jet` | Matplotlib colormap for heatmap |
| `alpha` | `0.4` | Overlay transparency |
| `output_dir` | `heatmaps/` | Directory for generated overlays |

## Reference

> Selvaraju, R.R. et al. (2017). *Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization*. ICCV 2017.
