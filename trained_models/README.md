# 🏋️ Trained Models

## Purpose

This directory stores **trained deep learning model weight files** (`.h5`, `.keras`, `.tflite`) used by ColonSightAI for inference.

## Expected Files

| File | Description | Size (Approx.) |
|---|---|---|
| `efficientnetb0_colon.h5` | Primary EfficientNetB0 classifier | ~20 MB |
| `efficientnetb0_colon.keras` | Keras native format (alternative) | ~20 MB |
| `efficientnetb0_colon.tflite` | TensorFlow Lite (mobile/edge) | ~15 MB |

## How to Obtain Model Weights

### Option 1: Train from scratch
```bash
python scripts/train_model.py
```

### Option 2: Download pre-trained weights
```bash
# (Future) Download from project releases
# Place the .h5 file directly in this directory
```

## Model Versioning

| Version | Date | Accuracy | Notes |
|---|---|---|---|
| v1.0.0 | — | — | Initial EfficientNetB0 transfer learning |

## Storage Policy

- **This directory is excluded from Git tracking** (model files are too large).
- Model weights should be shared via cloud storage or Git LFS.
- Keep at least the latest stable version available locally.
- The application checks `MODEL_PATH` config for the active model.
