# 🧠 Models

## Purpose

This directory contains the **machine learning model architecture definitions**, training scripts, and model evaluation utilities for the ColonSightAI deep learning pipeline.

## Structure

```
models/
├── __init__.py
├── efficientnet_model.py      ← EfficientNetB0 architecture definition
├── model_builder.py           ← Model compilation and layer configuration
├── model_evaluator.py         ← Evaluation metrics, confusion matrix, ROC
├── callbacks.py               ← Custom Keras callbacks
└── README.md
```

## Notes

- **Trained model weights** (`.h5`, `.keras` files) are stored in `trained_models/`, not here.
- **Database ORM models** (User, Patient, Prediction) are in `app/models/`, not here.
- This directory is exclusively for ML/DL model architecture code.

## Key Classes (Planned)

| Module | Purpose |
|---|---|
| `efficientnet_model.py` | EfficientNetB0 with custom classification head |
| `model_builder.py` | Transfer learning setup, layer freezing, compilation |
| `model_evaluator.py` | Accuracy, precision, recall, F1, confusion matrix, ROC-AUC |
| `callbacks.py` | Early stopping, LR scheduling, model checkpoint |
