"""
ColonSightAI — AI Model Configuration
========================================

Centralised configuration for the deep learning pipeline.
All hyperparameters, file paths, class labels, and thresholds
are defined here to avoid magic numbers scattered across the codebase.
"""

import os

# ── Project root ──────────────────────────────────────────────────────────
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# ═══════════════════════════════════════════════════════════════════════════
# Model Architecture
# ═══════════════════════════════════════════════════════════════════════════
MODEL_NAME = 'EfficientNetB0'
MODEL_VERSION = '1.0.0'
MODEL_PATH = os.path.join(_BASE_DIR, 'data', 'models', 'efficientnetb0_colon.h5')

# ═══════════════════════════════════════════════════════════════════════════
# Image Preprocessing
# ═══════════════════════════════════════════════════════════════════════════
IMAGE_SIZE = (224, 224)         # EfficientNetB0 default input size
IMAGE_CHANNELS = 3              # RGB
PIXEL_SCALE_FACTOR = 1.0 / 255  # Normalize to [0, 1]

# ═══════════════════════════════════════════════════════════════════════════
# Class Labels
# ═══════════════════════════════════════════════════════════════════════════
CLASS_LABELS = {
    0: 'colon_aca',    # Colon adenocarcinoma (cancerous)
    1: 'colon_n',      # Colon normal (benign)
}
CLASS_DISPLAY_NAMES = {
    'colon_aca': 'Colon Adenocarcinoma',
    'colon_n': 'Colon Normal Tissue',
}
NUM_CLASSES = len(CLASS_LABELS)

# ═══════════════════════════════════════════════════════════════════════════
# Prediction Thresholds
# ═══════════════════════════════════════════════════════════════════════════
CONFIDENCE_THRESHOLD = 0.5      # Minimum confidence for positive classification
HIGH_CONFIDENCE = 0.85          # Threshold for "high confidence" badge
LOW_CONFIDENCE = 0.6            # Below this → "low confidence" warning

# ═══════════════════════════════════════════════════════════════════════════
# Grad-CAM Configuration
# ═══════════════════════════════════════════════════════════════════════════
GRADCAM_LAYER_NAME = 'top_conv'    # Last convolutional layer in EfficientNetB0
GRADCAM_COLORMAP = 'jet'           # Matplotlib colormap for heatmap overlay
GRADCAM_ALPHA = 0.4                # Heatmap overlay transparency
HEATMAP_OUTPUT_DIR = os.path.join(_BASE_DIR, 'data', 'heatmaps')

# ═══════════════════════════════════════════════════════════════════════════
# Training Configuration (for future use in scripts/train_model.py)
# ═══════════════════════════════════════════════════════════════════════════
TRAINING_CONFIG = {
    'batch_size': 32,
    'epochs': 25,
    'learning_rate': 1e-4,
    'optimizer': 'adam',
    'loss': 'categorical_crossentropy',
    'metrics': ['accuracy'],
    'validation_split': 0.2,
    'early_stopping_patience': 5,
    'reduce_lr_patience': 3,
    'reduce_lr_factor': 0.5,
}

# ═══════════════════════════════════════════════════════════════════════════
# Dataset Configuration (reference only — not downloaded here)
# ═══════════════════════════════════════════════════════════════════════════
DATASET_INFO = {
    'name': 'LC25000 — Lung and Colon Cancer Histopathological Images',
    'source': 'https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images',
    'total_images': 25000,
    'colon_images': 10000,
    'classes': ['colon_aca', 'colon_n'],
    'image_size': '768×768 pixels',
    'format': 'JPEG',
}
