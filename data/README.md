# 💾 Data

## Purpose

This directory stores **runtime data** generated and consumed by the ColonSightAI application during operation. All subdirectories contain `.gitkeep` files to preserve the directory structure in Git while excluding actual data files.

## Structure

```
data/
├── uploads/       ← Uploaded histopathology images (from web form)
├── heatmaps/      ← Generated Grad-CAM heatmap overlays
├── reports/       ← Generated PDF diagnostic reports
├── models/        ← Trained model weight files (.h5, .keras)
└── database/      ← SQLite database files
```

## Storage Policy

- All data files are **excluded from Git** via `.gitignore`.
- Only `.gitkeep` files are tracked to preserve directory structure.
- Backup data directories regularly in production.
