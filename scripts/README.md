# ⚙️ Scripts

## Purpose

This directory contains **utility scripts** for database management, model training, and data preparation tasks that run outside the Flask web application.

## Scripts

| Script | Purpose | Usage |
|---|---|---|
| `seed_db.py` | Populate database with initial/sample data | `python scripts/seed_db.py` |
| `train_model.py` | Train EfficientNetB0 classifier | `python scripts/train_model.py` |

## Future Scripts (Planned)

| Script | Purpose |
|---|---|
| `split_dataset.py` | Split dataset into train/val/test sets |
| `evaluate_model.py` | Run evaluation metrics on test set |
| `export_model.py` | Convert model to TFLite for deployment |
| `backup_db.py` | Backup SQLite database |
| `cleanup_uploads.py` | Remove orphaned upload files |
