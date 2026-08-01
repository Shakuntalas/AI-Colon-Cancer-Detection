"""
ColonSightAI — AI Pipeline Package
=====================================

This package encapsulates the entire deep learning pipeline:

Modules:
    - **model_config** — Hyperparameters, paths, class labels
    - **model_loader** — Load and cache EfficientNetB0 weights
    - **preprocessor** — Image preprocessing (resize, normalize, augment)
    - **predictor** — Run inference and return structured results
    - **gradcam** — Generate Grad-CAM heatmap overlays for explainability

Pipeline Flow:
    Upload → Validate → Preprocess → EfficientNetB0 → Predict
    → Grad-CAM → Confidence Score → Database → PDF Report
"""
