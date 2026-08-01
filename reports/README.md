# 📄 Reports

## Purpose

This directory stores **generated PDF diagnostic reports** created by the ColonSightAI system. Reports are generated using ReportLab and contain comprehensive prediction summaries for clinical use.

## Report Contents

Each generated report includes:

1. **Institutional Header** — Hospital/lab branding and logo
2. **Patient Demographics** — Name, ID, DOB, referring doctor
3. **Original Image** — Uploaded histopathology slide image
4. **Prediction Results** — Classification and confidence score
5. **Grad-CAM Heatmap** — Explainability visualization
6. **Clinical Notes** — Clinician annotations and observations
7. **Model Metadata** — Model version, inference time, preprocessing info
8. **Disclaimer** — AI-assisted diagnosis advisory notice
9. **Timestamp** — Report generation date and time

## File Naming Convention

```
CSAI-REPORT-{prediction_uid}-{YYYYMMDD-HHMMSS}.pdf
```

Example: `CSAI-REPORT-a1b2c3-20240815-143022.pdf`

## Storage Policy

- Reports are generated on-demand and cached in this directory.
- Older reports can be regenerated from stored prediction data.
- This directory is excluded from Git tracking (see `.gitignore`).
