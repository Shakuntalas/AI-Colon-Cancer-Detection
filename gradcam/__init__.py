"""
ColonSightAI — Grad-CAM Explainability Package
=================================================

This package provides Gradient-weighted Class Activation Mapping
(Grad-CAM) for generating visual explanations of model predictions.

Modules (Planned):
    - gradcam_generator  — Core heatmap computation via gradient analysis
    - guided_gradcam     — Guided Grad-CAM for pixel-level detail
    - heatmap_overlay    — Overlay heatmaps on original images
    - visualization      — Side-by-side and comparison visualizations

For integration into the Flask app prediction pipeline,
see ``app/ai/gradcam.py``.
"""
