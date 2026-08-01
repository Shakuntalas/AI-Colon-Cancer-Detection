# 🔥 Heatmaps

## Purpose

This directory stores **Grad-CAM heatmap overlay images** generated during the prediction pipeline. Each heatmap visually highlights the regions of the histopathology image that most influenced the AI model's classification decision.

## Output Format

- **Format**: PNG (lossless, for clinical accuracy)
- **Resolution**: Same as original upload (typically 224×224 after processing)
- **Colormap**: Jet (blue → green → yellow → red, where red = highest activation)
- **Overlay Alpha**: 0.4 (40% heatmap, 60% original image)

## File Naming Convention

```
gradcam_{prediction_uid}_{timestamp}.png
```

Example: `gradcam_CSAI-20240815-a1b2c3_20240815143022.png`

## Visual Guide

```
Blue   → Low activation   (model ignored this region)
Green  → Medium activation
Yellow → High activation
Red    → Highest activation (most influential for prediction)
```

## Storage Policy

- Heatmaps are generated alongside predictions and stored here.
- This directory is excluded from Git tracking (see `.gitignore`).
- Heatmaps can be regenerated from original images if needed.
